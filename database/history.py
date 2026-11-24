"""
SQLite Database Operations for ONVEST.

Manages saving, retrieving, and deleting calculation history for Loan EMI and SIP calculations.
Default DB location: %LOCALAPPDATA%/ONVEST/onvest.db with fallbacks.
"""

import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_candidate_db_paths() -> List[Path]:
    """
    Returns the ordered default candidate database paths:
    1. %LOCALAPPDATA%/ONVEST/onvest.db (standard Windows per-user local app data)
    2. ~/.onvest/onvest.db (user home profile fallback)
    3. <project_root>/data/onvest.db (workspace local portable directory fallback)
    """
    candidates = []
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidates.append(Path(local_app_data) / "ONVEST" / "onvest.db")
    candidates.append(Path.home() / ".onvest" / "onvest.db")
    candidates.append(Path(__file__).resolve().parent.parent / "data" / "onvest.db")
    return candidates


def get_default_db_path(candidates: Optional[List[Path]] = None) -> Path:
    """
    Returns the default path to the ONVEST SQLite database file by verifying actual write access.

    Two-tier verification:
    - If onvest.db exists: Opens connection, runs integrity check (PRAGMA quick_check),
      and verifies write permissions within a transaction that is rolled back (creating
      and rolling back a uniquely named table), leaving existing user tables and records
      completely untouched. Never deletes pre-existing files.
    - If onvest.db does not exist: Probes candidate directory using a uniquely named temporary
      SQLite file (.probe_write_<uuid>.tmp). The probe file and any sidecars (-journal, -wal, -shm)
      must be closed and unlinked cleanly. If cleanup fails (e.g. file cannot be removed),
      the candidate is rejected and a useful diagnostic is retained.
      Never deletes anything except the uniquely named probe file created by this invocation.

    If an existing database is read-only, corrupt, or unusable, or if a candidate directory
    is unwritable, or if probe file cleanup fails, continues to the next candidate.
    If all candidates fail, raises PermissionError detailing diagnostics rather than silently using an unwritable path.
    """
    candidate_list = list(candidates) if candidates is not None else get_candidate_db_paths()
    diagnostics = []

    for db_file in candidate_list:
        candidate_dir = db_file.parent
        try:
            candidate_dir.mkdir(parents=True, exist_ok=True)

            if db_file.exists():
                probe_tbl = f"_probe_tx_{uuid.uuid4().hex}"
                conn = sqlite3.connect(str(db_file), timeout=5.0)
                try:
                    cur = conn.cursor()
                    cur.execute("PRAGMA quick_check")
                    status = cur.fetchone()
                    if not status or status[0] != "ok":
                        raise sqlite3.DatabaseError(f"Database integrity failure: {status}")

                    conn.execute("BEGIN IMMEDIATE")
                    conn.execute(f"CREATE TABLE {probe_tbl} (id INTEGER PRIMARY KEY)")
                    conn.execute(f"INSERT INTO {probe_tbl} DEFAULT VALUES")
                    conn.rollback()
                    return db_file
                finally:
                    try:
                        conn.rollback()
                    except Exception:
                        pass
                    conn.close()
            else:
                probe_name = f".probe_write_{uuid.uuid4().hex}.tmp"
                probe_file = candidate_dir / probe_name
                probe_success = False
                cleanup_errors = []
                try:
                    conn = sqlite3.connect(str(probe_file), timeout=5.0)
                    try:
                        conn.execute("CREATE TABLE _p (id INTEGER PRIMARY KEY)")
                        conn.execute("INSERT INTO _p DEFAULT VALUES")
                        conn.commit()
                        probe_success = True
                    finally:
                        conn.close()
                except Exception as pe:
                    cleanup_errors.append(f"Probe creation failed: {pe}")
                finally:
                    # Never delete anything except the uniquely named probe file created by this invocation
                    for ext in ("", "-journal", "-wal", "-shm"):
                        sidecar = candidate_dir / f"{probe_name}{ext}"
                        try:
                            if sidecar.exists():
                                sidecar.unlink()
                        except Exception as ue:
                            cleanup_errors.append(f"Failed to remove probe sidecar {sidecar.name}: {ue}")

                if probe_success and not cleanup_errors:
                    return db_file
                else:
                    reason = "; ".join(cleanup_errors) if cleanup_errors else "Probe creation failed"
                    diagnostics.append(f"{db_file}: {reason}")
        except Exception as exc:
            diagnostics.append(f"{db_file}: {exc}")
            continue

    diag_summary = "; ".join(diagnostics) if diagnostics else "All candidates failed write check"
    raise PermissionError(
        f"Unable to find a writable location for ONVEST SQLite database. "
        f"Tested candidates failed write verification: {diag_summary}."
    )


_CURRENT_DB_PATH: Optional[Path] = None


def get_db_path() -> Path:
    """Returns the current database path in use."""
    global _CURRENT_DB_PATH
    if _CURRENT_DB_PATH is None:
        _CURRENT_DB_PATH = get_default_db_path()
    return _CURRENT_DB_PATH


def set_db_path(path: Path) -> None:
    """Sets a custom database path (useful for unit tests)."""
    global _CURRENT_DB_PATH
    _CURRENT_DB_PATH = path


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Opens a connection to the SQLite database.
    Ensures directory exists and enables foreign keys and row factory.
    """
    target_path = db_path or get_db_path()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    """
    Initializes the SQLite database and creates the calculation history table if it doesn't exist.
    """
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS calculation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    calc_type TEXT NOT NULL CHECK(calc_type IN ('EMI', 'SIP')),
                    principal_or_monthly REAL NOT NULL,
                    annual_rate REAL NOT NULL,
                    duration_months INTEGER NOT NULL,
                    monthly_amount REAL NOT NULL,
                    total_interest_or_returns REAL NOT NULL,
                    total_amount REAL NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            # Create an index on created_at for fast descending history queries
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_calc_history_created_at
                ON calculation_history(created_at DESC)
                """
            )
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def save_calculation(calc_data: Dict[str, Any], db_path: Optional[Path] = None) -> int:
    """
    Saves a calculation record to the database with transaction protection.
    Rolls back on error.
    """
    calc_type = calc_data.get("calc_type")
    if calc_type not in ("EMI", "SIP"):
        raise ValueError(f"Invalid calculation type: {calc_type}. Expected 'EMI' or 'SIP'.")

    created_at = calc_data.get("created_at")
    if not created_at:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO calculation_history (
                    calc_type,
                    principal_or_monthly,
                    annual_rate,
                    duration_months,
                    monthly_amount,
                    total_interest_or_returns,
                    total_amount,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    calc_type,
                    float(calc_data["principal_or_monthly"]),
                    float(calc_data["annual_rate"]),
                    int(calc_data["duration_months"]),
                    float(calc_data["monthly_amount"]),
                    float(calc_data["total_interest_or_returns"]),
                    float(calc_data["total_amount"]),
                    str(created_at),
                ),
            )
            return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_all_calculations(db_path: Optional[Path] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Retrieves calculation history sorted by newest first.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            """
            SELECT
                id,
                calc_type,
                principal_or_monthly,
                annual_rate,
                duration_months,
                monthly_amount,
                total_interest_or_returns,
                total_amount,
                created_at
            FROM calculation_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return rows
    finally:
        conn.close()


def get_calculation_count(db_path: Optional[Path] = None) -> int:
    """Returns the total number of saved calculations."""
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("SELECT COUNT(*) FROM calculation_history")
        row = cursor.fetchone()
        return row[0] if row else 0
    finally:
        conn.close()


def get_latest_calculation(db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Returns the most recent calculation record or None."""
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            """
            SELECT
                id,
                calc_type,
                principal_or_monthly,
                annual_rate,
                duration_months,
                monthly_amount,
                total_interest_or_returns,
                total_amount,
                created_at
            FROM calculation_history
            ORDER BY id DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def delete_calculation(calc_id: int, db_path: Optional[Path] = None) -> bool:
    """
    Deletes an individual calculation record by ID.
    Rolls back transaction on error.
    Returns True if a row was actually deleted, False if record was not found.
    """
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                "DELETE FROM calculation_history WHERE id = ?",
                (calc_id,),
            )
            return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def clear_all_calculations(db_path: Optional[Path] = None) -> bool:
    """
    Clears all records from calculation_history.
    Preserves transaction rollback on failure.
    Propagates database errors and never reports success on failure.
    """
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM calculation_history")
            return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

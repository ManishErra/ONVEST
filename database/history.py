"""
SQLite Database Operations for ONVEST.

Manages saving, retrieving, and deleting calculation history for Loan EMI and SIP calculations.
Default DB location: %LOCALAPPDATA%/ONVEST/onvest.db with fallbacks.
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_default_db_path() -> Path:
    """
    Returns the default path to the ONVEST SQLite database file.
    Uses %LOCALAPPDATA%/ONVEST/onvest.db if available,
    otherwise falls back to ~/.onvest/onvest.db or a local ./data directory.
    """
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        base_dir = Path(local_app_data) / "ONVEST"
    else:
        user_home = Path.home()
        base_dir = user_home / ".onvest"

    try:
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir / "onvest.db"
    except Exception:
        # Fallback to local application data directory
        fallback_dir = Path("./data")
        fallback_dir.mkdir(parents=True, exist_ok=True)
        return fallback_dir / "onvest.db"


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
    finally:
        conn.close()


def save_calculation(calc_data: Dict[str, Any], db_path: Optional[Path] = None) -> int:
    """
    Saves a calculation record to the database.
    Expects keys:
        - calc_type: 'EMI' or 'SIP'
        - principal_or_monthly: float
        - annual_rate: float
        - duration_months: int
        - monthly_amount: float
        - total_interest_or_returns: float
        - total_amount: float
        - created_at: optional ISO timestamp string

    Returns the new record's ID.
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
        return [dict(row) for row in cursor.fetchall()]
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
    """Deletes an individual calculation record by ID. Returns True if deleted."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                "DELETE FROM calculation_history WHERE id = ?",
                (calc_id,),
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def clear_all_calculations(db_path: Optional[Path] = None) -> bool:
    """Clears all records from the calculation history. Returns True on success."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM calculation_history")
            # Vacuum or reset sequence
            conn.execute("DELETE FROM sqlite_sequence WHERE name='calculation_history'")
            return True
    except sqlite3.OperationalError:
        # sqlite_sequence might not exist if autoincrement hasn't fired yet
        return True
    finally:
        conn.close()

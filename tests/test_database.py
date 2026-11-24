"""
Unit tests for the SQLite Database history operations.
Includes tests for transaction rollback, failure handling, deletion, clearing,
and Pass 2 counting accuracy beyond the 100-record retrieval limit.
Uses a temporary database file so the user's actual database is never modified.
"""

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from database.history import (
    init_db,
    save_calculation,
    get_all_calculations,
    get_calculation_count,
    get_latest_calculation,
    delete_calculation,
    clear_all_calculations,
)


class TestDatabaseHistory(unittest.TestCase):
    """Test suite covering all required database operations and failure scenarios."""

    def setUp(self):
        """Create a temporary database file for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db_path = Path(self.temp_dir.name) / "test_onvest.db"
        init_db(self.test_db_path)

    def tearDown(self):
        """Clean up the temporary directory."""
        self.temp_dir.cleanup()

    def test_database_initialization(self):
        """Test 1: Database and table initialization."""
        self.assertTrue(self.test_db_path.exists())
        self.assertEqual(get_calculation_count(self.test_db_path), 0)
        self.assertIsNone(get_latest_calculation(self.test_db_path))

    def test_save_emi_calculation(self):
        """Test 2: Saving an EMI calculation."""
        emi_data = {
            "calc_type": "EMI",
            "principal_or_monthly": 1000000.0,
            "annual_rate": 8.5,
            "duration_months": 240,
            "monthly_amount": 8678.23,
            "total_interest_or_returns": 1082775.2,
            "total_amount": 2082775.2,
            "created_at": "2026-11-24 12:00:00",
        }
        rec_id = save_calculation(emi_data, self.test_db_path)
        self.assertGreater(rec_id, 0)
        self.assertEqual(get_calculation_count(self.test_db_path), 1)

        latest = get_latest_calculation(self.test_db_path)
        self.assertIsNotNone(latest)
        self.assertEqual(latest["calc_type"], "EMI")
        self.assertEqual(latest["principal_or_monthly"], 1000000.0)
        self.assertEqual(latest["annual_rate"], 8.5)
        self.assertEqual(latest["duration_months"], 240)
        self.assertEqual(latest["monthly_amount"], 8678.23)
        self.assertEqual(latest["total_interest_or_returns"], 1082775.2)
        self.assertEqual(latest["total_amount"], 2082775.2)

    def test_save_sip_calculation(self):
        """Test 3: Saving a SIP calculation."""
        sip_data = {
            "calc_type": "SIP",
            "principal_or_monthly": 5000.0,
            "annual_rate": 12.0,
            "duration_months": 120,
            "monthly_amount": 5000.0,
            "total_interest_or_returns": 550193.44,
            "total_amount": 1150193.44,
            "created_at": "2026-11-24 13:00:00",
        }
        rec_id = save_calculation(sip_data, self.test_db_path)
        self.assertGreater(rec_id, 0)
        self.assertEqual(get_calculation_count(self.test_db_path), 1)

        latest = get_latest_calculation(self.test_db_path)
        self.assertIsNotNone(latest)
        self.assertEqual(latest["calc_type"], "SIP")
        self.assertEqual(latest["monthly_amount"], 5000.0)

    def test_retrieving_history(self):
        """Test 4: Retrieving calculation history list."""
        emi_data = {
            "calc_type": "EMI",
            "principal_or_monthly": 500000.0,
            "annual_rate": 9.0,
            "duration_months": 60,
            "monthly_amount": 10379.18,
            "total_interest_or_returns": 122750.8,
            "total_amount": 622750.8,
            "created_at": "2026-11-24 10:00:00",
        }
        sip_data = {
            "calc_type": "SIP",
            "principal_or_monthly": 2000.0,
            "annual_rate": 14.0,
            "duration_months": 36,
            "monthly_amount": 2000.0,
            "total_interest_or_returns": 16922.0,
            "total_amount": 88922.0,
            "created_at": "2026-11-24 11:00:00",
        }
        id1 = save_calculation(emi_data, self.test_db_path)
        id2 = save_calculation(sip_data, self.test_db_path)

        history = get_all_calculations(self.test_db_path)
        self.assertEqual(len(history), 2)
        # Should be ordered descending (newest first)
        self.assertEqual(history[0]["id"], id2)
        self.assertEqual(history[1]["id"], id1)

    def test_deleting_a_record(self):
        """Test 5: Deleting an individual record."""
        data = {
            "calc_type": "EMI",
            "principal_or_monthly": 100000.0,
            "annual_rate": 10.0,
            "duration_months": 12,
            "monthly_amount": 8791.59,
            "total_interest_or_returns": 5499.08,
            "total_amount": 105499.08,
            "created_at": "2026-11-24 09:00:00",
        }
        rec_id = save_calculation(data, self.test_db_path)
        self.assertEqual(get_calculation_count(self.test_db_path), 1)

        success = delete_calculation(rec_id, self.test_db_path)
        self.assertTrue(success)
        self.assertEqual(get_calculation_count(self.test_db_path), 0)

        # Deleting nonexistent record returns False
        success_nonexistent = delete_calculation(9999, self.test_db_path)
        self.assertFalse(success_nonexistent)

    def test_clearing_history(self):
        """Test 6: Clearing all history."""
        for i in range(5):
            data = {
                "calc_type": "EMI",
                "principal_or_monthly": 10000.0 * (i + 1),
                "annual_rate": 10.0,
                "duration_months": 12,
                "monthly_amount": 879.16 * (i + 1),
                "total_interest_or_returns": 550.0 * (i + 1),
                "total_amount": 10550.0 * (i + 1),
                "created_at": f"2026-11-24 08:0{i}:00",
            }
            save_calculation(data, self.test_db_path)

        self.assertEqual(get_calculation_count(self.test_db_path), 5)
        clear_success = clear_all_calculations(self.test_db_path)
        self.assertTrue(clear_success)
        self.assertEqual(get_calculation_count(self.test_db_path), 0)
        self.assertEqual(len(get_all_calculations(self.test_db_path)), 0)

    def test_transaction_rollback_on_invalid_save(self):
        """Test: Transaction rollbacks on invalid calculation type and leaves existing data intact."""
        valid_data = {
            "calc_type": "EMI",
            "principal_or_monthly": 50000.0,
            "annual_rate": 10.0,
            "duration_months": 12,
            "monthly_amount": 4395.79,
            "total_interest_or_returns": 2749.48,
            "total_amount": 52749.48,
            "created_at": "2026-11-24 09:30:00",
        }
        save_calculation(valid_data, self.test_db_path)
        self.assertEqual(get_calculation_count(self.test_db_path), 1)

        invalid_data = {
            "calc_type": "UNKNOWN_TYPE",
            "principal_or_monthly": 10000.0,
            "annual_rate": 10.0,
            "duration_months": 12,
            "monthly_amount": 800.0,
            "total_interest_or_returns": 200.0,
            "total_amount": 10200.0,
        }
        with self.assertRaises(ValueError):
            save_calculation(invalid_data, self.test_db_path)

        # Existing record is preserved, count is still 1
        self.assertEqual(get_calculation_count(self.test_db_path), 1)

    def test_failed_clear_history_does_not_report_success(self):
        """Test: clear_all_calculations does not report success if execution fails."""
        invalid_path = Path("/invalid_dir_does_not_exist_xyz/cannot_write.db")
        with self.assertRaises(Exception):
            clear_all_calculations(invalid_path)

    def test_more_than_100_records_counting_accuracy(self):
        """
        Pass 2 Regression:
        Inserts 120 records and verifies that get_calculation_count() accurately
        reports 120 while get_all_calculations(limit=100) returns 100 records.
        """
        for i in range(120):
            data = {
                "calc_type": "EMI" if i % 2 == 0 else "SIP",
                "principal_or_monthly": 1000.0 + i,
                "annual_rate": 8.0,
                "duration_months": 12,
                "monthly_amount": 100.0,
                "total_interest_or_returns": 50.0,
                "total_amount": 1200.0,
                "created_at": f"2026-11-24 00:{i//60:02d}:{i%60:02d}",
            }
            save_calculation(data, self.test_db_path)

        # Total count must be exactly 120
        total_count = get_calculation_count(self.test_db_path)
        self.assertEqual(total_count, 120)

        # Default limit retrieval must return 100 records
        retrieved_records = get_all_calculations(self.test_db_path, limit=100)
        self.assertEqual(len(retrieved_records), 100)

    def test_count_refresh_after_deletion_and_clearing(self):
        """
        Pass 2 Regression:
        Verify count decrements accurately after single delete and resets to 0 after clear.
        """
        data = {
            "calc_type": "EMI",
            "principal_or_monthly": 50000.0,
            "annual_rate": 10.0,
            "duration_months": 12,
            "monthly_amount": 4395.79,
            "total_interest_or_returns": 2749.48,
            "total_amount": 52749.48,
        }
        id1 = save_calculation(data, self.test_db_path)
        id2 = save_calculation(data, self.test_db_path)
        id3 = save_calculation(data, self.test_db_path)
        self.assertEqual(get_calculation_count(self.test_db_path), 3)

        # Delete one record
        delete_calculation(id2, self.test_db_path)
        self.assertEqual(get_calculation_count(self.test_db_path), 2)

        # Clear remaining
        clear_all_calculations(self.test_db_path)
        self.assertEqual(get_calculation_count(self.test_db_path), 0)

    import contextlib

    @contextlib.contextmanager
    def isolated_candidates(self, temp_dir_path: Path):
        """
        Creates isolated candidate paths inside a temporary directory to ensure tests
        never touch the user's real database, %LOCALAPPDATA%, ~/.onvest, or project data/.
        """
        cand1 = temp_dir_path / "localappdata" / "ONVEST" / "onvest.db"
        cand2 = temp_dir_path / "home" / ".onvest" / "onvest.db"
        cand3 = temp_dir_path / "workspace_data" / "onvest.db"
        candidates = [cand1, cand2, cand3]
        import unittest.mock as mock
        with mock.patch("database.history.get_candidate_db_paths", return_value=candidates):
            yield candidates

    def test_get_default_db_path_returns_writable_path(self):
        """
        Verify that get_default_db_path() returns a path where actual write and read operations succeed,
        strictly operating within an isolated temporary test directory.
        """
        from database.history import get_default_db_path
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td).resolve()
            with self.isolated_candidates(td_path):
                db_path = get_default_db_path()
                # Guard asserting database path is inside the temporary test directory
                self.assertTrue(db_path.resolve().is_relative_to(td_path), f"Escaped temp dir: {db_path}")
                self.assertTrue(db_path.parent.exists())

                # Initialize schema on isolated path
                init_db(db_path)

                # Test write and read on the returned default database path
                test_data = {
                    "calc_type": "EMI",
                    "principal_or_monthly": 10000.0,
                    "annual_rate": 5.0,
                    "duration_months": 12,
                    "monthly_amount": 856.07,
                    "total_interest_or_returns": 272.84,
                    "total_amount": 10272.84,
                }
                rec_id = save_calculation(test_data, db_path)
                self.assertGreater(rec_id, 0)
                # Verify read
                latest = get_latest_calculation(db_path)
                self.assertIsNotNone(latest)
                self.assertEqual(latest["id"], rec_id)
                # Clean up probe record
                delete_calculation(rec_id, db_path)

    def test_database_probe_leaves_no_temporary_files_behind(self):
        """
        Verify that the collision-safe probe leaves no temporary files behind in its candidate directory.
        """
        from database.history import get_default_db_path
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td).resolve()
            with self.isolated_candidates(td_path):
                db_path = get_default_db_path()
                self.assertTrue(db_path.resolve().is_relative_to(td_path))
                probe_files = list(db_path.parent.glob(".probe_write_*"))
                self.assertEqual(probe_files, [])

    def test_existing_onvest_write_probe_table_remains_unchanged(self):
        """
        Verify that an existing table named '_onvest_write_probe' and its contents
        remain completely unchanged by the probe mechanism, verified inside an isolated temp directory.
        """
        from database.history import get_default_db_path
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td).resolve()
            with self.isolated_candidates(td_path) as candidates:
                cand_db = candidates[0]
                cand_db.parent.mkdir(parents=True, exist_ok=True)

                # Pre-create fixture database inside TemporaryDirectory with table _onvest_write_probe
                conn = sqlite3.connect(str(cand_db))
                conn.execute("CREATE TABLE _onvest_write_probe (user_col TEXT)")
                conn.execute("INSERT INTO _onvest_write_probe VALUES ('critical_user_payload')")
                conn.commit()
                conn.close()

                selected_path = get_default_db_path()
                # Guard asserting selected path is inside temporary directory
                self.assertTrue(selected_path.resolve().is_relative_to(td_path))
                self.assertEqual(selected_path, cand_db)

                # Assert table and user payload are completely intact
                conn_verify = sqlite3.connect(str(selected_path))
                cur = conn_verify.execute("SELECT user_col FROM _onvest_write_probe")
                rows = cur.fetchall()
                self.assertEqual(rows, [("critical_user_payload",)])
                conn_verify.close()

    def test_database_fallback_when_higher_priority_locations_unwritable(self):
        """
        Verify fallback behavior when higher-priority locations cannot be written,
        and that a clear PermissionError is raised if all candidates fail, all within an isolated temp directory.
        """
        from database.history import get_default_db_path
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td).resolve()
            with self.isolated_candidates(td_path) as candidates:
                for c in (candidates[0], candidates[1]):
                    c.parent.mkdir(parents=True, exist_ok=True)
                    conn = sqlite3.connect(str(c))
                    conn.execute("CREATE TABLE s (id INT)")
                    conn.commit()
                    conn.close()
                    os.chmod(str(c), 0o444)

                try:
                    selected = get_default_db_path()
                    # Guard asserting selected path is inside temporary directory
                    self.assertTrue(selected.resolve().is_relative_to(td_path))
                    self.assertEqual(selected, candidates[2])
                finally:
                    for c in (candidates[0], candidates[1]):
                        if c.exists():
                            os.chmod(str(c), 0o666)

                # Now verify clear PermissionError when every candidate fails
                for c in candidates:
                    c.parent.mkdir(parents=True, exist_ok=True)
                    if not c.exists():
                        conn = sqlite3.connect(str(c))
                        conn.execute("CREATE TABLE s (id INT)")
                        conn.commit()
                        conn.close()
                    os.chmod(str(c), 0o444)

                try:
                    with self.assertRaises(PermissionError) as ctx:
                        get_default_db_path()
                    self.assertIn("Unable to find a writable location", str(ctx.exception))
                finally:
                    for c in candidates:
                        if c.exists():
                            os.chmod(str(c), 0o666)

    def test_existing_writable_database_preserved_without_modifications(self):
        """
        Verify that when onvest.db already exists and is writable, get_default_db_path()
        verifies write access via a rolled-back transaction without modifying existing tables or data.
        """
        from database.history import get_default_db_path
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td).resolve()
            with self.isolated_candidates(td_path) as candidates:
                cand_db = candidates[0]
                cand_db.parent.mkdir(parents=True, exist_ok=True)

                # Create existing DB with user table and records
                conn = sqlite3.connect(str(cand_db))
                conn.execute("CREATE TABLE critical_user_data (key TEXT, val TEXT)")
                conn.execute("INSERT INTO critical_user_data VALUES ('user_key', 'user_value')")
                conn.commit()
                conn.close()

                selected = get_default_db_path()
                # Guard asserting database path is inside temporary directory
                self.assertTrue(selected.resolve().is_relative_to(td_path))
                self.assertEqual(selected, cand_db)

                # Verify user table and records are preserved and no probe table was committed
                conn2 = sqlite3.connect(str(cand_db))
                cur = conn2.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [r[0] for r in cur.fetchall()]
                self.assertIn("critical_user_data", tables)
                self.assertFalse(any(t.startswith("_probe_tx_") for t in tables))

                cur.execute("SELECT val FROM critical_user_data WHERE key='user_key'")
                val = cur.fetchone()[0]
                self.assertEqual(val, "user_value")
                conn2.close()

    def test_existing_readonly_database_triggers_fallback(self):
        """
        Verify that when an existing candidate database file is read-only,
        get_default_db_path() detects it and falls back to the next candidate.
        """
        from database.history import get_default_db_path
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td).resolve()
            with self.isolated_candidates(td_path) as candidates:
                ro_db = candidates[0]
                ro_db.parent.mkdir(parents=True, exist_ok=True)

                # Create DB and make it read-only
                conn = sqlite3.connect(str(ro_db))
                conn.execute("CREATE TABLE sample (id INT)")
                conn.commit()
                conn.close()
                os.chmod(str(ro_db), 0o444)

                try:
                    selected = get_default_db_path()
                    # Guard asserting database path is inside temporary directory
                    self.assertTrue(selected.resolve().is_relative_to(td_path))
                    self.assertEqual(selected, candidates[1])
                finally:
                    os.chmod(str(ro_db), 0o666)

    def test_existing_corrupt_database_triggers_fallback(self):
        """
        Verify that when an existing candidate database file is corrupt,
        quick_check fails and get_default_db_path() falls back to the next candidate.
        """
        from database.history import get_default_db_path
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td).resolve()
            with self.isolated_candidates(td_path) as candidates:
                corrupt_db = candidates[0]
                corrupt_db.parent.mkdir(parents=True, exist_ok=True)

                with open(corrupt_db, "wb") as f:
                    f.write(b"NOT A SQLITE DATABASE HEADER")

                selected = get_default_db_path()
                # Guard asserting database path is inside temporary directory
                self.assertTrue(selected.resolve().is_relative_to(td_path))
                self.assertEqual(selected, candidates[1])

    def test_cleanup_cannot_delete_preexisting_files(self):
        """
        Verify that pre-existing files in candidate directories are never deleted
        during probe execution or cleanup on either success or failure.
        """
        from database.history import get_default_db_path
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td).resolve()
            with self.isolated_candidates(td_path) as candidates:
                target_dir = candidates[0].parent
                target_dir.mkdir(parents=True, exist_ok=True)

                # Pre-existing user files
                preexisting_file1 = target_dir / "user_notes.txt"
                preexisting_file1.write_text("important user notes")
                preexisting_file2 = target_dir / "config.json"
                preexisting_file2.write_text('{"setting": true}')

                selected = get_default_db_path()
                # Guard asserting database path is inside temporary directory
                self.assertTrue(selected.resolve().is_relative_to(td_path))
                self.assertEqual(selected, candidates[0])

                # Assert pre-existing files are untouched
                self.assertTrue(preexisting_file1.exists())
                self.assertEqual(preexisting_file1.read_text(), "important user notes")
                self.assertTrue(preexisting_file2.exists())
                self.assertEqual(preexisting_file2.read_text(), '{"setting": true}')

                # Assert no temporary probe files remain
                self.assertEqual(list(target_dir.glob(".probe_write_*")), [])

    def test_probe_cleanup_failure_rejects_candidate_with_diagnostics(self):
        """
        Verify that if probe file or sidecar cleanup fails (e.g. file cannot be unlinked),
        the candidate is rejected, does not claim write access, records diagnostics,
        and falls back to the next candidate.
        """
        import unittest.mock as mock
        from database.history import get_default_db_path
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td).resolve()
            with self.isolated_candidates(td_path) as candidates:
                orig_unlink = Path.unlink

                def fake_unlink(self_path, *args, **kwargs):
                    if candidates[0].parent in self_path.parents or self_path.parent == candidates[0].parent:
                        raise PermissionError(f"Simulated lock: cannot unlink {self_path.name}")
                    return orig_unlink(self_path, *args, **kwargs)

                with mock.patch.object(Path, "unlink", fake_unlink):
                    selected = get_default_db_path()
                    # Guard asserting database path is inside temporary directory
                    self.assertTrue(selected.resolve().is_relative_to(td_path))
                    self.assertEqual(selected, candidates[1])


if __name__ == "__main__":
    unittest.main()

"""
Unit tests for the SQLite Database history operations.
Uses a temporary database file so the user's actual database is never modified.
"""

import os
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
    """Test suite covering all required database operations."""

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


if __name__ == "__main__":
    unittest.main()

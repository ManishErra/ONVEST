"""
Smoke and integration test for the ONVEST UI.
Tests that the CustomTkinter application and all views initialize, navigate,
and perform UI-driven calculations without crashing.
"""

import unittest
from pathlib import Path
import tempfile
from database.history import set_db_path, init_db, clear_all_calculations
from main import OnvestApp


class TestUISmoke(unittest.TestCase):
    """Integration test suite for the ONVEST desktop UI."""

    def setUp(self):
        # Use a temporary database for UI tests
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db_path = Path(self.temp_dir.name) / "test_ui.db"
        set_db_path(self.test_db_path)
        init_db(self.test_db_path)

        # Instantiate app
        self.app = OnvestApp()
        self.app.withdraw()  # Hide window during automated testing

    def tearDown(self):
        try:
            self.app.update()
            self.app.destroy()
        except Exception:
            pass
        self.temp_dir.cleanup()

    def test_app_initialization_and_pages(self):
        """Verify all 5 pages are instantiated and registered."""
        self.assertIn("dashboard", self.app.pages)
        self.assertIn("emi", self.app.pages)
        self.assertIn("sip", self.app.pages)
        self.assertIn("history", self.app.pages)
        self.assertIn("about", self.app.pages)

    def test_navigation_flow(self):
        """Verify switching between pages works without exception."""
        for key in ["dashboard", "emi", "sip", "history", "about", "dashboard"]:
            self.app.navigate_to(key)
            self.assertEqual(self.app.current_view_key, key)

    def test_emi_ui_calculation_and_save(self):
        """Test performing EMI calculation through UI inputs and saving."""
        emi_page = self.app.pages["emi"]

        # Fill inputs
        emi_page.principal_entry.delete(0, "end")
        emi_page.principal_entry.insert(0, "500000")

        emi_page.rate_entry.delete(0, "end")
        emi_page.rate_entry.insert(0, "10.5")

        emi_page.tenure_entry.delete(0, "end")
        emi_page.tenure_entry.insert(0, "3")

        # Trigger calculate
        emi_page._handle_calculate()
        self.assertIsNotNone(emi_page.last_result)
        self.assertEqual(emi_page.last_result.principal, 500000.0)
        self.assertGreater(emi_page.last_result.monthly_emi, 15000.0)

        # Trigger save
        emi_page._handle_save()
        self.assertIn("Calculation saved to history", emi_page.feedback_label.cget("text"))

        # Check dashboard and history updated
        self.app.navigate_to("dashboard")
        self.assertEqual(self.app.pages["dashboard"].count_val_label.cget("text"), "1")

        self.app.navigate_to("history")
        self.assertIn("1 saved records", self.app.pages["history"].count_badge.cget("text"))

    def test_sip_ui_calculation_and_save(self):
        """Test performing SIP calculation through UI inputs and saving."""
        sip_page = self.app.pages["sip"]

        # Fill inputs
        sip_page.monthly_entry.delete(0, "end")
        sip_page.monthly_entry.insert(0, "10000")

        sip_page.rate_entry.delete(0, "end")
        sip_page.rate_entry.insert(0, "12")

        sip_page.duration_entry.delete(0, "end")
        sip_page.duration_entry.insert(0, "5")

        # Trigger calculate
        sip_page._handle_calculate()
        self.assertIsNotNone(sip_page.last_result)
        self.assertEqual(sip_page.last_result.monthly_investment, 10000.0)
        self.assertGreater(sip_page.last_result.future_value, 600000.0)

        # Trigger save
        sip_page._handle_save()
        self.assertIn("Calculation saved to history", sip_page.feedback_label.cget("text"))

    def test_emi_ui_validation_error(self):
        """Test UI validation error handling for invalid input."""
        emi_page = self.app.pages["emi"]

        emi_page.principal_entry.delete(0, "end")
        emi_page.principal_entry.insert(0, "-500")

        emi_page.rate_entry.delete(0, "end")
        emi_page.rate_entry.insert(0, "10")

        emi_page.tenure_entry.delete(0, "end")
        emi_page.tenure_entry.insert(0, "2")

        emi_page._handle_calculate()
        self.assertIsNone(emi_page.last_result)
        self.assertIn("greater than zero", emi_page.feedback_label.cget("text"))


if __name__ == "__main__":
    unittest.main()

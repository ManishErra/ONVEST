"""
Smoke and regression tests for ONVEST UI.
Verifies page initialization, navigation, and specifically tests against
stale calculation saving when inputs are edited after calculating.
"""

import unittest
from pathlib import Path
import tempfile
from database.history import set_db_path, init_db, get_latest_calculation, get_calculation_count
from main import OnvestApp


class TestUISmokeAndRegressions(unittest.TestCase):
    """Integration and regression test suite for ONVEST desktop UI."""

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
        """
        Verify that navigating via sidebar buttons or navigate_to actually raises and grids
        the selected page, and ungrids/hides all inactive pages.
        Also verifies Dashboard quick-access navigation routes to EMI and SIP.
        """
        # Deiconify to verify window geometry and mapping
        self.app.deiconify()
        self.app.update()

        # 1. Verify all five sidebar navigation targets
        for key in ["dashboard", "emi", "sip", "history", "about", "history", "emi", "dashboard"]:
            # Trigger via sidebar button click
            self.app.nav_buttons[key].invoke()
            self.app.update()

            self.assertEqual(self.app.current_view_key, key)
            target_widget = getattr(self.app.pages[key], "_parent_frame", self.app.pages[key])

            # Confirm target page is managed by grid
            self.assertEqual(target_widget.winfo_manager(), "grid", f"Page {key} is not gridded after navigation")

            # Confirm target page is raised to the very top of content container children
            top_child = self.app.content_container.winfo_children()[-1]
            self.assertEqual(top_child, target_widget, f"Page {key} is not top child in content container")

            # Confirm all other pages are ungridded (hidden via grid_remove)
            for other_key, other_page in self.app.pages.items():
                if other_key != key:
                    other_widget = getattr(other_page, "_parent_frame", other_page)
                    self.assertEqual(
                        other_widget.winfo_manager(),
                        "",
                        f"Page {other_key} should not be gridded when active page is {key}",
                    )

        # 2. Verify Dashboard quick-access routes
        self.app.navigate_to("dashboard")
        self.app.update()
        dashboard = self.app.pages["dashboard"]

        # Route to EMI
        dashboard.navigate_callback("emi")
        self.app.update()
        self.assertEqual(self.app.current_view_key, "emi")
        emi_w = getattr(self.app.pages["emi"], "_parent_frame", self.app.pages["emi"])
        self.assertEqual(emi_w.winfo_manager(), "grid")
        self.assertEqual(self.app.content_container.winfo_children()[-1], emi_w)

        # Route back to Dashboard and then to SIP
        self.app.navigate_to("dashboard")
        self.app.update()
        dashboard.navigate_callback("sip")
        self.app.update()
        self.assertEqual(self.app.current_view_key, "sip")
        sip_w = getattr(self.app.pages["sip"], "_parent_frame", self.app.pages["sip"])
        self.assertEqual(sip_w.winfo_manager(), "grid")
        self.assertEqual(self.app.content_container.winfo_children()[-1], sip_w)

        self.app.withdraw()

    def test_emi_ui_calculation_and_save(self):
        """Test standard EMI calculation and saving."""
        emi_page = self.app.pages["emi"]

        emi_page.principal_entry.delete(0, "end")
        emi_page.principal_entry.insert(0, "500000")
        emi_page.rate_entry.delete(0, "end")
        emi_page.rate_entry.insert(0, "10.5")
        emi_page.tenure_entry.delete(0, "end")
        emi_page.tenure_entry.insert(0, "3")

        emi_page._handle_calculate()
        self.assertIsNotNone(emi_page.last_result)
        self.assertEqual(emi_page.last_result.principal, 500000.0)

        emi_page._handle_save()
        self.assertIn("Calculation saved to history", emi_page.feedback_label.cget("text"))

        latest = get_latest_calculation()
        self.assertIsNotNone(latest)
        self.assertEqual(latest["principal_or_monthly"], 500000.0)

    def test_emi_save_after_changing_inputs_prevents_stale_save(self):
        """
        Regression Test:
        Calculate using initial inputs.
        Change input fields.
        Click Save.
        Verify that database contains the result corresponding to the LATEST inputs,
        not the stale previous result.
        """
        emi_page = self.app.pages["emi"]

        # 1. Initial calculation: P = 500,000
        emi_page.principal_entry.delete(0, "end")
        emi_page.principal_entry.insert(0, "500000")
        emi_page.rate_entry.delete(0, "end")
        emi_page.rate_entry.insert(0, "10.0")
        emi_page.tenure_entry.delete(0, "end")
        emi_page.tenure_entry.insert(0, "5")

        emi_page._handle_calculate()
        self.assertEqual(emi_page.last_result.principal, 500000.0)

        # 2. User changes principal to 1,500,000 WITHOUT clicking calculate first
        emi_page.principal_entry.delete(0, "end")
        emi_page.principal_entry.insert(0, "1500000")

        # 3. User clicks Save directly
        emi_page._handle_save()
        self.assertIn("Calculation saved to history", emi_page.feedback_label.cget("text"))

        # 4. Verify saved record in DB has the NEW principal of 1,500,000
        latest = get_latest_calculation()
        self.assertIsNotNone(latest)
        self.assertEqual(latest["principal_or_monthly"], 1500000.0)
        self.assertEqual(emi_page.last_result.principal, 1500000.0)

    def test_emi_invalid_current_inputs_cannot_save_previous_result(self):
        """
        Regression Test:
        Calculate valid result.
        Change input to an invalid value (e.g. -500).
        Click Save.
        Verify that nothing is saved and an error is shown.
        """
        emi_page = self.app.pages["emi"]

        # Initial valid calculation
        emi_page.principal_entry.delete(0, "end")
        emi_page.principal_entry.insert(0, "500000")
        emi_page.rate_entry.delete(0, "end")
        emi_page.rate_entry.insert(0, "10.0")
        emi_page.tenure_entry.delete(0, "end")
        emi_page.tenure_entry.insert(0, "5")
        emi_page._handle_calculate()

        initial_count = get_calculation_count()

        # Change principal to negative
        emi_page.principal_entry.delete(0, "end")
        emi_page.principal_entry.insert(0, "-100000")

        # Click save
        emi_page._handle_save()

        # Count must not increase
        self.assertEqual(get_calculation_count(), initial_count)
        self.assertIn("greater than zero", emi_page.feedback_label.cget("text"))

    def test_sip_save_after_changing_inputs_prevents_stale_save(self):
        """
        Regression Test:
        Calculate SIP with M = 5,000.
        Change M to 25,000.
        Click Save.
        Verify that database contains 25,000.
        """
        sip_page = self.app.pages["sip"]

        # Initial calculation: M = 5,000
        sip_page.monthly_entry.delete(0, "end")
        sip_page.monthly_entry.insert(0, "5000")
        sip_page.rate_entry.delete(0, "end")
        sip_page.rate_entry.insert(0, "12.0")
        sip_page.duration_entry.delete(0, "end")
        sip_page.duration_entry.insert(0, "5")

        sip_page._handle_calculate()
        self.assertEqual(sip_page.last_result.monthly_investment, 5000.0)

        # Change to 25,000
        sip_page.monthly_entry.delete(0, "end")
        sip_page.monthly_entry.insert(0, "25000")

        # Click Save
        sip_page._handle_save()
        self.assertIn("Calculation saved to history", sip_page.feedback_label.cget("text"))

        latest = get_latest_calculation()
        self.assertIsNotNone(latest)
        self.assertEqual(latest["principal_or_monthly"], 25000.0)
        self.assertEqual(sip_page.last_result.monthly_investment, 25000.0)

    def test_sip_invalid_current_inputs_cannot_save_previous_result(self):
        """
        Regression Test:
        Calculate valid SIP.
        Change rate to invalid string 'abc'.
        Click Save.
        Verify nothing is saved and error is shown.
        """
        sip_page = self.app.pages["sip"]

        sip_page.monthly_entry.delete(0, "end")
        sip_page.monthly_entry.insert(0, "5000")
        sip_page.rate_entry.delete(0, "end")
        sip_page.rate_entry.insert(0, "12.0")
        sip_page.duration_entry.delete(0, "end")
        sip_page.duration_entry.insert(0, "5")
        sip_page._handle_calculate()

        initial_count = get_calculation_count()

        # Change rate to invalid
        sip_page.rate_entry.delete(0, "end")
        sip_page.rate_entry.insert(0, "abc")

        sip_page._handle_save()
        self.assertEqual(get_calculation_count(), initial_count)
        self.assertIn("valid number", sip_page.feedback_label.cget("text"))

    def test_history_ui_accurate_count_and_refresh(self):
        """
        Pass 2 Regression:
        Verify that history UI accurately reflects total count from get_calculation_count()
        and refreshes properly upon deletion and clear.
        """
        emi_page = self.app.pages["emi"]
        emi_page.principal_entry.delete(0, "end")
        emi_page.principal_entry.insert(0, "100000")
        emi_page.rate_entry.delete(0, "end")
        emi_page.rate_entry.insert(0, "10.0")
        emi_page.tenure_entry.delete(0, "end")
        emi_page.tenure_entry.insert(0, "1")
        emi_page._handle_save()

        sip_page = self.app.pages["sip"]
        sip_page.monthly_entry.delete(0, "end")
        sip_page.monthly_entry.insert(0, "5000")
        sip_page.rate_entry.delete(0, "end")
        sip_page.rate_entry.insert(0, "12.0")
        sip_page.duration_entry.delete(0, "end")
        sip_page.duration_entry.insert(0, "2")
        sip_page._handle_save()

        self.app.navigate_to("history")
        history_page = self.app.pages["history"]

        # Badge must report 2 saved records
        self.assertIn("2 saved records", history_page.count_badge.cget("text"))

        # Clear all
        history_page._execute_clear_all()
        self.assertIn("0 saved records", history_page.count_badge.cget("text"))
        self.assertEqual(get_calculation_count(), 0)

    def test_disclaimers_and_rounding_explanations_in_ui(self):
        """
        Verify that:
        1. EMI results page clearly explains that the final installment may differ slightly
           because monthly EMI is rounded to two decimal places.
        2. EMI results page contains the required explanatory reducing-balance disclaimer.
        3. SIP results page clearly states that projected returns are estimates, not guaranteed.
        """
        self.app.navigate_to("emi")
        emi_page = self.app.pages["emi"]

        emi_page.principal_entry.delete(0, "end")
        emi_page.principal_entry.insert(0, "100000")
        emi_page.rate_entry.delete(0, "end")
        emi_page.rate_entry.insert(0, "12")
        emi_page.tenure_entry.delete(0, "end")
        emi_page.tenure_entry.insert(0, "1")

        emi_page._handle_calculate()
        self.assertIsNotNone(emi_page.last_result)

        # 1. Rounding explanation in EMI card caption
        emi_caption = emi_page.emi_card.caption_label.cget("text")
        self.assertIn("Final installment differs slightly because monthly EMI is rounded to two decimal places", emi_caption)

        # Helper to recursively extract all text from a widget tree
        def get_all_texts(widget):
            texts = []
            if hasattr(widget, "cget"):
                try:
                    t = widget.cget("text")
                    if t:
                        texts.append(t)
                except Exception:
                    pass
            if hasattr(widget, "winfo_children"):
                for child in widget.winfo_children():
                    texts.extend(get_all_texts(child))
            return texts

        # 2. Disclaimer present on EMI results container
        combined_emi_text = " ".join(get_all_texts(emi_page.results_container))
        self.assertIn("This is an estimated reducing-balance EMI calculation", combined_emi_text)
        self.assertIn("The displayed final installment adjusts for rounding differences", combined_emi_text)

        # 3. SIP disclaimer verification
        self.app.navigate_to("sip")
        sip_page = self.app.pages["sip"]
        combined_sip_text = " ".join(get_all_texts(sip_page.results_container))
        self.assertIn("not guaranteed", combined_sip_text)
        self.assertIn("illustrative estimates", combined_sip_text)
        self.assertIn("compounding rates", combined_sip_text)


if __name__ == "__main__":
    unittest.main()

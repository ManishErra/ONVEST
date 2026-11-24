"""
Unit tests for SIP calculation logic and input validation.
"""

import unittest
from calculations.sip import calculate_sip, validate_sip_inputs, SIPCalculationResult


class TestSIPCalculator(unittest.TestCase):
    """Test suite covering all required SIP calculation scenarios."""

    def test_normal_sip_calculation(self):
        """
        Test 1: Normal SIP calculation.
        M = 10,000 / month, R = 12% annual, T = 10 years (120 months).
        i = 12 / (12 * 100) = 0.01
        FV = 10000 * (((1.01)^120 - 1) / 0.01)
        (1.01)^120 ≈ 3.30038689
        FV ≈ 10000 * 2.30038689 / 0.01 ≈ 2,300,387
        Total Invested = 10,000 * 120 = 1,200,000
        Estimated Returns = FV - 1,200,000 ≈ 1,100,387
        """
        result = calculate_sip(monthly_investment=10000.0, annual_return_rate=12.0, duration_years=10.0)
        self.assertIsInstance(result, SIPCalculationResult)
        self.assertEqual(result.monthly_investment, 10000.0)
        self.assertEqual(result.annual_return_rate, 12.0)
        self.assertEqual(result.duration_years, 10.0)
        self.assertEqual(result.duration_months, 120)
        self.assertEqual(result.total_invested, 1200000.0)
        self.assertAlmostEqual(result.future_value, 2300386.89, places=1)
        self.assertAlmostEqual(result.estimated_returns, 1100386.89, places=1)
        self.assertAlmostEqual(result.invested_ratio + result.returns_ratio, 1.0, places=2)

    def test_zero_return_calculation(self):
        """
        Test 2: Zero-return calculation.
        M = 5,000, R = 0%, T = 2 years (24 months).
        FV = 5,000 * 24 = 120,000. Returns = 0.
        """
        result = calculate_sip(monthly_investment=5000.0, annual_return_rate=0.0, duration_years=2.0)
        self.assertEqual(result.total_invested, 120000.0)
        self.assertEqual(result.future_value, 120000.0)
        self.assertEqual(result.estimated_returns, 0.0)
        self.assertEqual(result.invested_ratio, 1.0)
        self.assertEqual(result.returns_ratio, 0.0)

    def test_small_monthly_investment(self):
        """
        Test 3: Small monthly investment (e.g. 500 INR/month).
        M = 500, R = 15%, T = 1 year (12 months).
        """
        result = calculate_sip(monthly_investment=500.0, annual_return_rate=15.0, duration_years=1.0)
        self.assertEqual(result.duration_months, 12)
        self.assertEqual(result.total_invested, 6000.0)
        self.assertGreater(result.future_value, 6000.0)
        self.assertGreater(result.estimated_returns, 0.0)

    def test_long_investment_duration(self):
        """
        Test 4: Long investment duration (30 years).
        M = 5,000, R = 12%, T = 30 years (360 months).
        """
        result = calculate_sip(monthly_investment=5000.0, annual_return_rate=12.0, duration_years=30.0)
        self.assertEqual(result.duration_months, 360)
        self.assertEqual(result.total_invested, 1800000.0)
        # Power of compounding: returns far exceed invested amount
        self.assertGreater(result.estimated_returns, result.total_invested * 5)
        self.assertAlmostEqual(result.future_value, result.total_invested + result.estimated_returns, places=2)

    def test_invalid_zero_investment(self):
        """Test 5: Invalid zero investment."""
        with self.assertRaises(ValueError):
            calculate_sip(monthly_investment=0.0, annual_return_rate=12.0, duration_years=5.0)

        with self.assertRaises(ValueError):
            validate_sip_inputs("0", "12.0", "5")

    def test_invalid_negative_investment(self):
        """Test 6: Invalid negative investment."""
        with self.assertRaises(ValueError):
            calculate_sip(monthly_investment=-1000.0, annual_return_rate=12.0, duration_years=5.0)

        with self.assertRaises(ValueError):
            validate_sip_inputs("-1000", "12.0", "5")

    def test_invalid_duration(self):
        """Test 7: Invalid duration (zero, negative, or exceeding 50 years)."""
        with self.assertRaises(ValueError):
            calculate_sip(monthly_investment=5000.0, annual_return_rate=12.0, duration_years=0.0)

        with self.assertRaises(ValueError):
            calculate_sip(monthly_investment=5000.0, annual_return_rate=12.0, duration_years=-3.0)

        with self.assertRaises(ValueError):
            calculate_sip(monthly_investment=5000.0, annual_return_rate=12.0, duration_years=52.0)

        with self.assertRaises(ValueError):
            validate_sip_inputs("5000", "12.0", "0")

        with self.assertRaises(ValueError):
            validate_sip_inputs("5000", "12.0", "-2")

        with self.assertRaises(ValueError):
            validate_sip_inputs("5000", "12.0", "55")

    def test_input_validation_empty_and_alphabetic(self):
        """Additional validation checks for empty inputs and non-numeric strings."""
        with self.assertRaises(ValueError):
            validate_sip_inputs("", "12.0", "5")

        with self.assertRaises(ValueError):
            validate_sip_inputs("5000", "xyz", "5")

        with self.assertRaises(ValueError):
            validate_sip_inputs("5000", "-12.0", "5")


if __name__ == "__main__":
    unittest.main()

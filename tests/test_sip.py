"""
Unit tests for SIP calculation logic and input validation.
Includes tests for NaN, Infinity, large valid inputs, zero-return behaviour,
overflow handling, ratio bounds, and Pass 2 fractional tenure normalization.
"""

import math
import unittest
from calculations.sip import calculate_sip, validate_sip_inputs, SIPCalculationResult


class TestSIPCalculator(unittest.TestCase):
    """Test suite covering all required SIP calculation and edge-case scenarios."""

    def test_normal_sip_calculation(self):
        """Test 1: Normal SIP calculation."""
        result = calculate_sip(monthly_investment=10000.0, annual_return_rate=12.0, duration_years=10.0)
        self.assertIsInstance(result, SIPCalculationResult)
        self.assertEqual(result.monthly_investment, 10000.0)
        self.assertEqual(result.annual_return_rate, 12.0)
        self.assertEqual(result.duration_years, 10.0)
        self.assertEqual(result.duration_months, 120)
        self.assertEqual(result.total_invested, 1200000.0)
        self.assertAlmostEqual(result.future_value, 2300386.89, places=1)
        self.assertAlmostEqual(result.estimated_returns, 1100386.89, places=1)
        self.assertAlmostEqual(result.invested_ratio + result.returns_ratio, 1.0, places=4)

    def test_zero_return_calculation(self):
        """Test 2: Zero-return calculation."""
        result = calculate_sip(monthly_investment=5000.0, annual_return_rate=0.0, duration_years=2.0)
        self.assertEqual(result.total_invested, 120000.0)
        self.assertEqual(result.future_value, 120000.0)
        self.assertEqual(result.estimated_returns, 0.0)
        self.assertEqual(result.invested_ratio, 1.0)
        self.assertEqual(result.returns_ratio, 0.0)
        self.assertEqual(result.invested_ratio + result.returns_ratio, 1.0)

    def test_effective_duration_normalization_and_fractional_years(self):
        """
        Pass 2 Regression: Fractional year normalization for SIP.
        Tests 1.04 years, 1.5 years, and 2.25 years.
        1.04 yrs * 12 = 12.48 -> 12 months -> effective 1.0 yr.
        1.5 yrs * 12 = 18 months -> effective 1.5 yrs.
        2.25 yrs * 12 = 27 months -> effective 2.25 yrs.
        """
        # Case 1: 1.04 years
        res_104 = calculate_sip(monthly_investment=5000.0, annual_return_rate=12.0, duration_years=1.04)
        self.assertEqual(res_104.duration_months, 12)
        self.assertEqual(res_104.duration_years, 1.0)
        self.assertEqual(res_104.total_invested, 60000.0)

        # Case 2: 1.5 years
        res_15 = calculate_sip(monthly_investment=5000.0, annual_return_rate=12.0, duration_years=1.5)
        self.assertEqual(res_15.duration_months, 18)
        self.assertEqual(res_15.duration_years, 1.5)
        self.assertEqual(res_15.total_invested, 90000.0)

        # Case 3: 2.25 years
        res_225 = calculate_sip(monthly_investment=5000.0, annual_return_rate=12.0, duration_years=2.25)
        self.assertEqual(res_225.duration_months, 27)
        self.assertEqual(res_225.duration_years, 2.25)
        self.assertEqual(res_225.total_invested, 135000.0)

    def test_small_monthly_investment(self):
        """Test 3: Small monthly investment (e.g. 500 INR/month)."""
        result = calculate_sip(monthly_investment=500.0, annual_return_rate=15.0, duration_years=1.0)
        self.assertEqual(result.duration_months, 12)
        self.assertEqual(result.total_invested, 6000.0)
        self.assertGreater(result.future_value, 6000.0)
        self.assertGreater(result.estimated_returns, 0.0)
        self.assertEqual(result.invested_ratio + result.returns_ratio, 1.0)

    def test_long_investment_duration(self):
        """Test 4: Long investment duration (30 years)."""
        result = calculate_sip(monthly_investment=5000.0, annual_return_rate=12.0, duration_years=30.0)
        self.assertEqual(result.duration_months, 360)
        self.assertEqual(result.total_invested, 1800000.0)
        self.assertGreater(result.estimated_returns, result.total_invested * 5)
        self.assertAlmostEqual(result.future_value, result.total_invested + result.estimated_returns, places=2)
        self.assertEqual(result.invested_ratio + result.returns_ratio, 1.0)

    def test_very_large_valid_inputs(self):
        """Test 4b: Very large but valid inputs (₹1,00,00,000 / month, 30 years, 15% return)."""
        result = calculate_sip(monthly_investment=10000000.0, annual_return_rate=15.0, duration_years=30.0)
        self.assertEqual(result.duration_months, 360)
        self.assertGreater(result.future_value, result.total_invested)
        self.assertTrue(math.isfinite(result.future_value))
        self.assertTrue(math.isfinite(result.estimated_returns))
        self.assertGreaterEqual(result.invested_ratio, 0.0)
        self.assertLessEqual(result.invested_ratio, 1.0)
        self.assertGreaterEqual(result.returns_ratio, 0.0)
        self.assertLessEqual(result.returns_ratio, 1.0)
        self.assertAlmostEqual(result.invested_ratio + result.returns_ratio, 1.0, places=4)

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

    def test_nan_inputs_rejection(self):
        """Test: Reject NaN string and numeric inputs."""
        with self.assertRaises(ValueError):
            validate_sip_inputs("nan", "12.0", "5")
        with self.assertRaises(ValueError):
            validate_sip_inputs("5000", "NaN", "5")
        with self.assertRaises(ValueError):
            validate_sip_inputs("5000", "12.0", "nan")

        with self.assertRaises(ValueError):
            calculate_sip(float("nan"), 12.0, 5.0)
        with self.assertRaises(ValueError):
            calculate_sip(5000.0, float("nan"), 5.0)
        with self.assertRaises(ValueError):
            calculate_sip(5000.0, 12.0, float("nan"))

    def test_infinity_inputs_rejection(self):
        """Test: Reject Positive and Negative Infinity string and numeric inputs."""
        with self.assertRaises(ValueError):
            validate_sip_inputs("inf", "12.0", "5")
        with self.assertRaises(ValueError):
            validate_sip_inputs("-inf", "12.0", "5")
        with self.assertRaises(ValueError):
            validate_sip_inputs("5000", "+infinity", "5")
        with self.assertRaises(ValueError):
            validate_sip_inputs("5000", "-inf", "5")
        with self.assertRaises(ValueError):
            validate_sip_inputs("5000", "12.0", "inf")

        with self.assertRaises(ValueError):
            calculate_sip(float("inf"), 12.0, 5.0)
        with self.assertRaises(ValueError):
            calculate_sip(float("-inf"), 12.0, 5.0)
        with self.assertRaises(ValueError):
            calculate_sip(5000.0, float("inf"), 5.0)
        with self.assertRaises(ValueError):
            calculate_sip(5000.0, float("-inf"), 5.0)
        with self.assertRaises(ValueError):
            calculate_sip(5000.0, 12.0, float("inf"))
        with self.assertRaises(ValueError):
            calculate_sip(5000.0, 12.0, float("-inf"))

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

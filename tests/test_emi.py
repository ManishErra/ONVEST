"""
Unit tests for Loan EMI calculation logic and input validation.
"""

import unittest
from calculations.emi import calculate_emi, validate_emi_inputs, EMICalculationResult


class TestEMICalculator(unittest.TestCase):
    """Test suite covering all required EMI calculation scenarios."""

    def test_normal_loan_calculation(self):
        """
        Test 1: Normal loan calculation.
        P = 1,000,000, R = 10% annual, T = 5 years (60 months).
        r = 10 / (12 * 100) = 0.008333...
        (1+r)^60 = 1.6453089...
        EMI = 1000000 * 0.008333... * 1.6453089 / 0.6453089 = 21247.04
        """
        result = calculate_emi(principal=1000000.0, annual_rate=10.0, tenure_years=5.0)
        self.assertIsInstance(result, EMICalculationResult)
        self.assertEqual(result.principal, 1000000.0)
        self.assertEqual(result.annual_rate, 10.0)
        self.assertEqual(result.tenure_years, 5.0)
        self.assertEqual(result.tenure_months, 60)
        self.assertAlmostEqual(result.monthly_emi, 21247.04, places=1)
        self.assertAlmostEqual(result.total_repayment, result.monthly_emi * 60, places=1)
        self.assertAlmostEqual(result.total_interest, result.total_repayment - 1000000.0, places=1)
        self.assertGreater(result.principal_ratio, 0)
        self.assertGreater(result.interest_ratio, 0)
        self.assertAlmostEqual(result.principal_ratio + result.interest_ratio, 1.0, places=2)

    def test_zero_interest_loan(self):
        """
        Test 2: Zero-interest loan.
        P = 120,000, R = 0%, T = 1 year (12 months).
        EMI = 120,000 / 12 = 10,000. Interest = 0.
        """
        result = calculate_emi(principal=120000.0, annual_rate=0.0, tenure_years=1.0)
        self.assertEqual(result.monthly_emi, 10000.0)
        self.assertEqual(result.total_interest, 0.0)
        self.assertEqual(result.total_repayment, 120000.0)
        self.assertEqual(result.principal_ratio, 1.0)
        self.assertEqual(result.interest_ratio, 0.0)

    def test_small_loan_amount(self):
        """
        Test 3: Small loan amount.
        P = 5,000, R = 12%, T = 0.5 years (6 months).
        """
        result = calculate_emi(principal=5000.0, annual_rate=12.0, tenure_years=0.5)
        self.assertEqual(result.tenure_months, 6)
        self.assertGreater(result.monthly_emi, 800.0)
        self.assertLess(result.monthly_emi, 900.0)
        self.assertGreater(result.total_interest, 0.0)
        self.assertAlmostEqual(result.total_repayment, result.principal + result.total_interest, places=2)

    def test_long_loan_tenure(self):
        """
        Test 4: Long loan tenure up to max 50 years.
        P = 5,000,000, R = 8.5%, T = 30 years (360 months).
        """
        result = calculate_emi(principal=5000000.0, annual_rate=8.5, tenure_years=30.0)
        self.assertEqual(result.tenure_months, 360)
        self.assertAlmostEqual(result.monthly_emi, 38446.0, delta=10.0)
        self.assertGreater(result.total_interest, result.principal)  # Over 30 years, interest > principal
        self.assertAlmostEqual(result.total_repayment, result.principal + result.total_interest, places=1)

    def test_invalid_zero_principal(self):
        """Test 5: Invalid zero principal."""
        with self.assertRaises(ValueError):
            calculate_emi(principal=0.0, annual_rate=8.0, tenure_years=5.0)

        with self.assertRaises(ValueError):
            validate_emi_inputs("0", "8.0", "5")

    def test_invalid_negative_principal(self):
        """Test 6: Invalid negative principal."""
        with self.assertRaises(ValueError):
            calculate_emi(principal=-50000.0, annual_rate=8.0, tenure_years=5.0)

        with self.assertRaises(ValueError):
            validate_emi_inputs("-50000", "8.0", "5")

    def test_invalid_duration(self):
        """Test 7: Invalid duration (zero, negative, or exceeding 50 years)."""
        with self.assertRaises(ValueError):
            calculate_emi(principal=100000.0, annual_rate=8.0, tenure_years=0.0)

        with self.assertRaises(ValueError):
            calculate_emi(principal=100000.0, annual_rate=8.0, tenure_years=-2.0)

        with self.assertRaises(ValueError):
            calculate_emi(principal=100000.0, annual_rate=8.0, tenure_years=55.0)

        with self.assertRaises(ValueError):
            validate_emi_inputs("100000", "8.0", "0")

        with self.assertRaises(ValueError):
            validate_emi_inputs("100000", "8.0", "-5")

        with self.assertRaises(ValueError):
            validate_emi_inputs("100000", "8.0", "60")

    def test_input_validation_empty_and_alphabetic(self):
        """Additional validation checks for empty inputs and non-numeric strings."""
        with self.assertRaises(ValueError):
            validate_emi_inputs("", "8.0", "5")

        with self.assertRaises(ValueError):
            validate_emi_inputs("100000", "abc", "5")

        with self.assertRaises(ValueError):
            validate_emi_inputs("100000", "-5", "5")


if __name__ == "__main__":
    unittest.main()

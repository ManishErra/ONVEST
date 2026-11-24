"""
Unit tests for Loan EMI calculation logic and input validation.
Includes tests for NaN, Infinity, rounding edge cases, small principals,
low interest rates, long tenures, unrepresentable rounded EMIs, ratio bounds,
effective duration normalization, and explicit final-installment adjustment.
"""

import math
import unittest
from calculations.emi import calculate_emi, validate_emi_inputs, EMICalculationResult


class TestEMICalculator(unittest.TestCase):
    """Test suite covering all required EMI calculation and edge-case scenarios."""

    def test_normal_loan_calculation(self):
        """Test 1: Normal loan calculation."""
        result = calculate_emi(principal=1000000.0, annual_rate=10.0, tenure_years=5.0)
        self.assertIsInstance(result, EMICalculationResult)
        self.assertEqual(result.principal, 1000000.0)
        self.assertEqual(result.annual_rate, 10.0)
        self.assertEqual(result.tenure_years, 5.0)
        self.assertEqual(result.tenure_months, 60)
        self.assertAlmostEqual(result.monthly_emi, 21247.04, places=1)
        self.assertGreater(result.final_installment, 0.0)
        # Total repayment must equal sum of all actual installments
        expected_total = round(result.monthly_emi * 59 + result.final_installment, 2)
        self.assertEqual(result.total_repayment, expected_total)
        self.assertEqual(result.total_interest, round(result.total_repayment - result.principal, 2))
        self.assertGreater(result.principal_ratio, 0.0)
        self.assertGreater(result.interest_ratio, 0.0)
        self.assertAlmostEqual(result.principal_ratio + result.interest_ratio, 1.0, places=4)

    def test_final_installment_normal_loan_paise_difference(self):
        """
        Final Installment Test 1: Normal loan with paise-level difference.
        P = 100,000, R = 12%, n = 12 months.
        monthly_emi = 8,884.88
        final_installment = 8,884.87 (adjusted by -1 paisa)
        Total repayment = 11 * 8,884.88 + 8,884.87 = 106,618.55
        Total interest = 106,618.55 - 100,000 = 6,618.55
        """
        res = calculate_emi(principal=100000.0, annual_rate=12.0, tenure_years=1.0)
        self.assertEqual(res.tenure_months, 12)
        self.assertEqual(res.monthly_emi, 8884.88)
        self.assertEqual(res.final_installment, 8884.87)
        self.assertGreater(res.final_installment, 0.0)
        # Sum of all installments must equal total repayment identically
        self.assertEqual(res.total_repayment, round((res.monthly_emi * 11) + res.final_installment, 2))
        self.assertEqual(res.total_repayment, 106618.55)
        # Total interest equals total repayment minus principal
        self.assertEqual(res.total_interest, round(res.total_repayment - res.principal, 2))
        self.assertEqual(res.total_interest, 6618.55)

    def test_final_installment_very_low_interest_rate(self):
        """
        Final Installment Test 2: Very low interest rate with long tenure.
        P = 1,234.56, R = 0.01%, n = 600 months (50 years).
        monthly_emi = 2.06
        final_installment = 3.71
        Total repayment = 599 * 2.06 + 3.71 = 1,237.65
        Total interest = 1,237.65 - 1,234.56 = 3.09
        """
        res = calculate_emi(principal=1234.56, annual_rate=0.01, tenure_years=50.0)
        self.assertEqual(res.tenure_months, 600)
        self.assertEqual(res.monthly_emi, 2.06)
        self.assertEqual(res.final_installment, 3.71)
        self.assertGreater(res.final_installment, 0.0)
        # Sum of all installments must equal total repayment identically
        self.assertEqual(res.total_repayment, round((res.monthly_emi * 599) + res.final_installment, 2))
        self.assertEqual(res.total_repayment, 1237.65)
        self.assertEqual(res.total_interest, round(res.total_repayment - res.principal, 2))
        self.assertEqual(res.total_interest, 3.09)

    def test_final_installment_very_long_tenure(self):
        """Final Installment Test 3: Long tenure (30 years)."""
        res = calculate_emi(principal=5000000.0, annual_rate=8.5, tenure_years=30.0)
        self.assertEqual(res.tenure_months, 360)
        self.assertGreater(res.final_installment, 0.0)
        # Total repayment equals sum of all 360 installments
        expected_total = round((res.monthly_emi * 359) + res.final_installment, 2)
        self.assertEqual(res.total_repayment, expected_total)
        self.assertEqual(res.total_interest, round(res.total_repayment - res.principal, 2))

    def test_zero_interest_loan(self):
        """Final Installment Test 4: Zero-interest loan."""
        result = calculate_emi(principal=120000.0, annual_rate=0.0, tenure_years=1.0)
        self.assertEqual(result.monthly_emi, 10000.0)
        self.assertEqual(result.final_installment, 10000.0)
        self.assertGreater(result.final_installment, 0.0)
        self.assertEqual(result.total_interest, 0.0)
        self.assertEqual(result.total_repayment, 120000.0)
        # Sum of installments equals total repayment
        self.assertEqual(result.total_repayment, round((result.monthly_emi * 11) + result.final_installment, 2))
        self.assertEqual(result.principal_ratio, 1.0)
        self.assertEqual(result.interest_ratio, 0.0)
        self.assertEqual(result.principal_ratio + result.interest_ratio, 1.0)

    def test_very_small_valid_principal(self):
        """Final Installment Test 5: Very small valid principal (₹10 loan)."""
        result = calculate_emi(principal=10.0, annual_rate=8.0, tenure_years=0.5)
        self.assertGreaterEqual(result.monthly_emi, 0.01)
        self.assertGreater(result.final_installment, 0.0)
        self.assertGreaterEqual(result.total_interest, 0.0)
        self.assertGreaterEqual(result.total_repayment, result.principal)
        # Sum of installments equals total repayment
        self.assertEqual(result.total_repayment, round((result.monthly_emi * 5) + result.final_installment, 2))
        self.assertEqual(result.total_interest, round(result.total_repayment - result.principal, 2))
        self.assertGreaterEqual(result.principal_ratio, 0.0)
        self.assertLessEqual(result.principal_ratio, 1.0)
        self.assertGreaterEqual(result.interest_ratio, 0.0)
        self.assertLessEqual(result.interest_ratio, 1.0)
        self.assertAlmostEqual(result.principal_ratio + result.interest_ratio, 1.0, places=4)

    def test_final_installment_single_installment_loan(self):
        """Final Installment Test 6: Single-month tenure (n = 1)."""
        res = calculate_emi(principal=10000.0, annual_rate=12.0, tenure_years=1.0/12.0)
        self.assertEqual(res.tenure_months, 1)
        self.assertEqual(res.monthly_emi, 10100.0)
        self.assertEqual(res.final_installment, 10100.0)
        self.assertEqual(res.total_repayment, 10100.0)
        self.assertEqual(res.total_interest, 100.0)

    def test_small_loan_amount(self):
        """Test: Small loan amount (₹5,000 for 6 months)."""
        result = calculate_emi(principal=5000.0, annual_rate=12.0, tenure_years=0.5)
        self.assertEqual(result.tenure_months, 6)
        self.assertGreater(result.monthly_emi, 800.0)
        self.assertLess(result.monthly_emi, 900.0)
        self.assertGreater(result.final_installment, 0.0)
        self.assertGreaterEqual(result.total_interest, 0.0)
        self.assertEqual(result.total_repayment, round((result.monthly_emi * 5) + result.final_installment, 2))
        self.assertEqual(result.total_interest, round(result.total_repayment - result.principal, 2))
        self.assertEqual(result.principal_ratio + result.interest_ratio, 1.0)

    def test_very_low_interest_rate(self):
        """Test: Very low interest rate (0.01% p.a.)."""
        result = calculate_emi(principal=100000.0, annual_rate=0.01, tenure_years=1.0)
        self.assertGreater(result.monthly_emi, 8300.0)
        self.assertGreater(result.final_installment, 0.0)
        self.assertGreaterEqual(result.total_interest, 0.0)
        self.assertGreaterEqual(result.total_repayment, result.principal)
        self.assertEqual(result.total_repayment, round((result.monthly_emi * 11) + result.final_installment, 2))
        self.assertEqual(result.total_interest, round(result.total_repayment - result.principal, 2))
        self.assertEqual(result.principal_ratio + result.interest_ratio, 1.0)

    def test_total_repayment_and_interest_consistency(self):
        """Regression: Total Repayment = Sum of actual installments across various loan scenarios."""
        test_cases = [
            (100000.0, 8.5, 5.0),
            (500000.0, 11.25, 3.0),
            (1500000.0, 7.8, 15.0),
            (25000.0, 0.0, 2.0),
            (750.0, 14.0, 1.0),
        ]
        for p, r, t in test_cases:
            res = calculate_emi(p, r, t)
            # 1. Total repayment is never less than principal
            self.assertGreaterEqual(res.total_repayment, res.principal)
            # 2. Total interest is never negative
            self.assertGreaterEqual(res.total_interest, 0.0)
            # 3. Final installment is strictly positive
            self.assertGreater(res.final_installment, 0.0)
            # 4. Total repayment equals the sum of all actual installments
            expected_sum = round((res.monthly_emi * (res.tenure_months - 1)) + res.final_installment, 2)
            self.assertEqual(res.total_repayment, expected_sum)
            # 5. Total interest equals total repayment minus principal
            self.assertEqual(res.total_interest, round(res.total_repayment - res.principal, 2))
            # 6. Proportions sum to 1.0 exactly
            self.assertAlmostEqual(res.principal_ratio + res.interest_ratio, 1.0, places=4)

    def test_paise_rounding_boundaries(self):
        """Regression: Paise rounding boundaries with awkward decimal principals and rates."""
        awkward_cases = [
            (999.99, 9.99, 1.0),
            (1234.56, 12.34, 2.5),
            (100.01, 5.55, 0.5),
        ]
        for p, r, t in awkward_cases:
            res = calculate_emi(p, r, t)
            self.assertGreaterEqual(res.total_repayment, res.principal)
            self.assertGreaterEqual(res.total_interest, 0.0)
            self.assertGreater(res.final_installment, 0.0)
            expected_sum = round((res.monthly_emi * (res.tenure_months - 1)) + res.final_installment, 2)
            self.assertEqual(res.total_repayment, expected_sum)
            self.assertEqual(res.total_interest, round(res.total_repayment - res.principal, 2))
            self.assertAlmostEqual(res.principal_ratio + res.interest_ratio, 1.0, places=4)

    def test_effective_duration_normalization(self):
        """
        Fractional year normalization.
        Tests 1.04 years, 1.5 years, and 2.25 years.
        1.04 yrs * 12 = 12.48 -> 12 months -> effective 1.0 yr.
        1.5 yrs * 12 = 18 months -> effective 1.5 yrs.
        2.25 yrs * 12 = 27 months -> effective 2.25 yrs.
        """
        res_104 = calculate_emi(principal=100000.0, annual_rate=10.0, tenure_years=1.04)
        self.assertEqual(res_104.tenure_months, 12)
        self.assertEqual(res_104.tenure_years, 1.0)

        res_15 = calculate_emi(principal=100000.0, annual_rate=10.0, tenure_years=1.5)
        self.assertEqual(res_15.tenure_months, 18)
        self.assertEqual(res_15.tenure_years, 1.5)

        res_225 = calculate_emi(principal=100000.0, annual_rate=10.0, tenure_years=2.25)
        self.assertEqual(res_225.tenure_months, 27)
        self.assertEqual(res_225.tenure_years, 2.25)

    def test_long_loan_tenure(self):
        """Test: Long loan tenure up to max 50 years."""
        result = calculate_emi(principal=5000000.0, annual_rate=8.5, tenure_years=30.0)
        self.assertEqual(result.tenure_months, 360)
        self.assertAlmostEqual(result.monthly_emi, 38446.0, delta=10.0)
        self.assertGreater(result.total_interest, result.principal)
        self.assertEqual(result.total_repayment, round((result.monthly_emi * 359) + result.final_installment, 2))
        self.assertEqual(result.total_interest, round(result.total_repayment - result.principal, 2))
        self.assertEqual(result.principal_ratio + result.interest_ratio, 1.0)

    def test_max_tenure_50_years(self):
        """Test: Exactly 50 years tenure (600 months)."""
        result = calculate_emi(principal=1000000.0, annual_rate=9.0, tenure_years=50.0)
        self.assertEqual(result.tenure_months, 600)
        self.assertEqual(result.tenure_years, 50.0)
        self.assertGreater(result.monthly_emi, 0.01)
        self.assertGreater(result.final_installment, 0.0)
        self.assertGreater(result.total_interest, result.principal)
        self.assertEqual(result.total_repayment, round((result.monthly_emi * 599) + result.final_installment, 2))
        self.assertEqual(result.total_interest, round(result.total_repayment - result.principal, 2))
        self.assertEqual(result.principal_ratio + result.interest_ratio, 1.0)

    def test_unrepresentable_sub_paisa_emi(self):
        """Test: Extremely small principal with long tenure where monthly EMI < 1 paisa."""
        with self.assertRaises(ValueError) as ctx:
            calculate_emi(principal=0.50, annual_rate=0.0, tenure_years=50.0)
        self.assertIn("1 paisa", str(ctx.exception))

    def test_invalid_zero_principal(self):
        """Test: Invalid zero principal."""
        with self.assertRaises(ValueError):
            calculate_emi(principal=0.0, annual_rate=8.0, tenure_years=5.0)

        with self.assertRaises(ValueError):
            validate_emi_inputs("0", "8.0", "5")

    def test_invalid_negative_principal(self):
        """Test: Invalid negative principal."""
        with self.assertRaises(ValueError):
            calculate_emi(principal=-50000.0, annual_rate=8.0, tenure_years=5.0)

        with self.assertRaises(ValueError):
            validate_emi_inputs("-50000", "8.0", "5")

    def test_invalid_duration(self):
        """Test: Invalid duration (zero, negative, or exceeding 50 years)."""
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

    def test_nan_inputs_rejection(self):
        """Test: Reject NaN string and numeric inputs."""
        with self.assertRaises(ValueError):
            validate_emi_inputs("nan", "8.0", "5")
        with self.assertRaises(ValueError):
            validate_emi_inputs("100000", "NaN", "5")
        with self.assertRaises(ValueError):
            validate_emi_inputs("100000", "8.0", "nan")

        with self.assertRaises(ValueError):
            calculate_emi(float("nan"), 8.0, 5.0)
        with self.assertRaises(ValueError):
            calculate_emi(100000.0, float("nan"), 5.0)
        with self.assertRaises(ValueError):
            calculate_emi(100000.0, 8.0, float("nan"))

    def test_infinity_inputs_rejection(self):
        """Test: Reject Positive and Negative Infinity string and numeric inputs."""
        with self.assertRaises(ValueError):
            validate_emi_inputs("inf", "8.0", "5")
        with self.assertRaises(ValueError):
            validate_emi_inputs("-inf", "8.0", "5")
        with self.assertRaises(ValueError):
            validate_emi_inputs("100000", "Infinity", "5")
        with self.assertRaises(ValueError):
            validate_emi_inputs("100000", "-infinity", "5")
        with self.assertRaises(ValueError):
            validate_emi_inputs("100000", "8.0", "inf")

        with self.assertRaises(ValueError):
            calculate_emi(float("inf"), 8.0, 5.0)
        with self.assertRaises(ValueError):
            calculate_emi(float("-inf"), 8.0, 5.0)
        with self.assertRaises(ValueError):
            calculate_emi(100000.0, float("inf"), 5.0)
        with self.assertRaises(ValueError):
            calculate_emi(100000.0, float("-inf"), 5.0)
        with self.assertRaises(ValueError):
            calculate_emi(100000.0, 8.0, float("inf"))
        with self.assertRaises(ValueError):
            calculate_emi(100000.0, 8.0, float("-inf"))

    def test_input_validation_empty_and_alphabetic(self):
        """Additional validation checks for empty inputs and non-numeric strings."""
        with self.assertRaises(ValueError):
            validate_emi_inputs("", "8.0", "5")

        with self.assertRaises(ValueError):
            validate_emi_inputs("100000", "abc", "5")

        with self.assertRaises(ValueError):
            validate_emi_inputs("100000", "-5", "5")

    def test_final_installment_financial_transparency_regression(self):
        """
        Regression Test (Final Financial Transparency & Verification):
        1. Regular monthly installment * (n - 1) + final_installment == total_repayment (to 2 decimal places).
        2. Total interest == total_repayment - principal (to 2 decimal places).
        3. Final installment is strictly positive and finite.
        4. Zero-interest loans remain correct and exact.
        """
        test_scenarios = [
            # Standard retail loans
            {"name": "Standard Home Loan", "p": 5000000.0, "r": 8.5, "t": 20.0},
            {"name": "Personal Loan with paise adjustment", "p": 100000.0, "r": 12.0, "t": 1.0},
            {"name": "Auto Loan", "p": 850000.0, "r": 9.25, "t": 5.0},
            # Edge-case loans
            {"name": "Low rate long duration", "p": 1234.56, "r": 0.01, "t": 50.0},
            {"name": "Awkward decimals", "p": 98765.43, "r": 11.37, "t": 3.25},
            {"name": "Very small principal", "p": 10.0, "r": 8.0, "t": 0.5},
            {"name": "Single installment (n = 1)", "p": 25000.0, "r": 10.0, "t": 1.0 / 12.0},
            # Zero-interest loans
            {"name": "Zero-interest 1-year loan", "p": 120000.0, "r": 0.0, "t": 1.0},
            {"name": "Zero-interest 5-year loan", "p": 600000.0, "r": 0.0, "t": 5.0},
            {"name": "Zero-interest fractional year loan", "p": 35000.0, "r": 0.0, "t": 0.5833333333333334},
        ]

        for sc in test_scenarios:
            with self.subTest(scenario=sc["name"]):
                res = calculate_emi(principal=sc["p"], annual_rate=sc["r"], tenure_years=sc["t"])

                # Condition 3: Final installment is positive and finite
                self.assertTrue(math.isfinite(res.final_installment), f"Final installment not finite for {sc['name']}")
                self.assertGreater(res.final_installment, 0.0, f"Final installment not positive for {sc['name']}")
                self.assertTrue(math.isfinite(res.monthly_emi), f"Monthly EMI not finite for {sc['name']}")
                self.assertGreater(res.monthly_emi, 0.0, f"Monthly EMI not positive for {sc['name']}")

                # Condition 1: regular monthly installment * (n - 1) + final_installment == total_repayment
                n = res.tenure_months
                expected_repayment = round((res.monthly_emi * (n - 1)) + res.final_installment, 2)
                self.assertEqual(res.total_repayment, expected_repayment, f"Repayment mismatch for {sc['name']}")

                # Condition 2: total interest == total_repayment - principal
                expected_interest = round(res.total_repayment - res.principal, 2)
                self.assertEqual(res.total_interest, expected_interest, f"Interest mismatch for {sc['name']}")

                # Condition 4: Zero-interest loans remain correct
                if sc["r"] == 0.0:
                    self.assertEqual(res.total_interest, 0.0, f"Zero-interest loan has interest: {sc['name']}")
                    self.assertEqual(res.total_repayment, round(sc["p"], 2), f"Total repayment != principal: {sc['name']}")
                    self.assertEqual(res.principal_ratio, 1.0)
                    self.assertEqual(res.interest_ratio, 0.0)

    def test_option_a_theoretical_total_convention_example(self):
        """
        Regression Test for Option A (Theoretical-Total Convention):
        Principal: ₹5,00,000 | Annual Rate: 10.5% | Tenure: 3 years (36 months).
        
        Assumptions of Option A (formula estimate with final-installment adjustment):
        - Theoretical reducing-balance monthly EMI raw = 16251.22177... -> rounded to ₹16,251.22
        - Theoretical unrounded total repayment = exact_emi * 36 = 585043.9839... -> ₹5,85,043.98
        - Regular installments sum (35 * 16251.22) = ₹5,68,792.70
        - Final installment = 585043.98 - 568792.70 = ₹16,251.28
        - Total repayment = ₹5,85,043.98
        - Total interest = 585043.98 - 500000.00 = ₹85,043.98
        """
        res = calculate_emi(principal=500000.0, annual_rate=10.5, tenure_years=3.0)
        self.assertEqual(res.principal, 500000.0)
        self.assertEqual(res.annual_rate, 10.5)
        self.assertEqual(res.tenure_months, 36)
        self.assertEqual(res.tenure_years, 3.0)
        self.assertEqual(res.monthly_emi, 16251.22)
        self.assertEqual(res.final_installment, 16251.28)
        self.assertEqual(res.total_repayment, 585043.98)
        self.assertEqual(res.total_interest, 85043.98)
        # Sum of 35 regular installments + final installment equals total repayment
        self.assertEqual(round((res.monthly_emi * 35) + res.final_installment, 2), 585043.98)
        self.assertEqual(round(res.total_repayment - res.principal, 2), 85043.98)


if __name__ == "__main__":
    unittest.main()

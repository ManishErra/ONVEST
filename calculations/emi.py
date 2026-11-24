"""
Loan EMI Calculator Logic for ONVEST.

Formulas:
- Monthly interest rate: r = Annual Interest Rate / (12 * 100)
- Number of monthly payments: n = Loan Tenure in Years * 12
- If r > 0:
    EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
- If r == 0:
    EMI = P / n
- Total Repayment = EMI * n
- Total Interest Payable = Total Repayment - P
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class EMICalculationResult:
    principal: float
    annual_rate: float
    tenure_years: float
    tenure_months: int
    monthly_emi: float
    total_interest: float
    total_repayment: float
    principal_ratio: float  # Proportional ratio 0.0 - 1.0
    interest_ratio: float   # Proportional ratio 0.0 - 1.0


def validate_emi_inputs(principal_str: str, rate_str: str, tenure_str: str) -> Tuple[float, float, float]:
    """
    Validates EMI input strings and converts them to floats.
    Raises ValueError with a user-friendly message if validation fails.
    """
    if principal_str is None or rate_str is None or tenure_str is None:
        raise ValueError("All fields are required. Please fill in all inputs.")

    p_str = principal_str.strip()
    r_str = rate_str.strip()
    t_str = tenure_str.strip()

    if not p_str or not r_str or not t_str:
        raise ValueError("All fields are required. Please enter values for Principal, Rate, and Tenure.")

    # Parse principal
    try:
        principal = float(p_str)
    except ValueError:
        raise ValueError("Principal amount must be a valid number.")

    if principal <= 0:
        raise ValueError("Principal amount must be greater than zero.")

    # Parse annual interest rate
    try:
        annual_rate = float(r_str)
    except ValueError:
        raise ValueError("Annual interest rate must be a valid number.")

    if annual_rate < 0:
        raise ValueError("Annual interest rate cannot be negative.")

    if annual_rate > 100:
        raise ValueError("Annual interest rate cannot exceed 100%.")

    # Parse tenure
    try:
        tenure_years = float(t_str)
    except ValueError:
        raise ValueError("Loan tenure must be a valid number.")

    if tenure_years <= 0:
        raise ValueError("Loan tenure must be greater than zero.")

    if tenure_years > 50:
        raise ValueError("Loan tenure cannot exceed 50 years.")

    return principal, annual_rate, tenure_years


def calculate_emi(principal: float, annual_rate: float, tenure_years: float) -> EMICalculationResult:
    """
    Calculates monthly EMI, total interest, and total repayment amount.
    """
    if principal <= 0:
        raise ValueError("Principal amount must be greater than zero.")
    if annual_rate < 0 or annual_rate > 100:
        raise ValueError("Annual interest rate must be between 0% and 100%.")
    if tenure_years <= 0 or tenure_years > 50:
        raise ValueError("Loan tenure must be between > 0 and <= 50 years.")

    tenure_months = int(round(tenure_years * 12))
    if tenure_months <= 0:
        raise ValueError("Tenure in months must be at least 1 month.")

    # Monthly interest rate
    r = annual_rate / (12.0 * 100.0)
    n = tenure_months

    if r == 0:
        monthly_emi = round(principal / n, 2)
        total_repayment = round(monthly_emi * n, 2)
        total_interest = 0.0
    else:
        # Standard EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)
        power_factor = (1.0 + r) ** n
        exact_emi = principal * r * power_factor / (power_factor - 1.0)
        monthly_emi = round(exact_emi, 2)
        total_repayment = round(monthly_emi * n, 2)
        total_interest = round(total_repayment - principal, 2)

    # Ratios for visual breakdown
    if total_repayment > 0:
        principal_ratio = principal / total_repayment
        interest_ratio = total_interest / total_repayment
    else:
        principal_ratio = 1.0
        interest_ratio = 0.0

    return EMICalculationResult(
        principal=round(principal, 2),
        annual_rate=round(annual_rate, 4),
        tenure_years=round(tenure_years, 2),
        tenure_months=tenure_months,
        monthly_emi=round(monthly_emi, 2),
        total_interest=round(total_interest, 2),
        total_repayment=round(total_repayment, 2),
        principal_ratio=round(principal_ratio, 4),
        interest_ratio=round(interest_ratio, 4),
    )

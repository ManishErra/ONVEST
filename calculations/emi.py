"""
Loan EMI Calculator Logic for ONVEST.

Formulas:
- Monthly interest rate: r = Annual Interest Rate / (12 * 100)
- Number of monthly payments: n = round(Loan Tenure in Years * 12)
- Effective tenure in years: effective_years = n / 12
- If r > 0:
    exact_emi = P * r * (1 + r)^n / ((1 + r)^n - 1)
- If r == 0:
    exact_emi = P / n
- exact_total_repayment = exact_emi * n
- Standard monthly EMI = round(exact_emi, 2)
- Final installment = round(exact_total_repayment - (monthly_emi * (n - 1)), 2)
- Total Repayment = (monthly_emi * (n - 1)) + final_installment (sum of all actual installments)
- Total Interest Payable = Total Repayment - P
"""

import math
from dataclasses import dataclass
from typing import Tuple


@dataclass
class EMICalculationResult:
    principal: float
    annual_rate: float
    tenure_years: float      # Effective duration in years derived from whole months (n / 12)
    tenure_months: int       # Effective duration in months
    monthly_emi: float       # Standard rounded monthly installment for installments 1 to n-1
    final_installment: float # Explicit final installment amount (adjusted for paise rounding)
    total_interest: float    # Total cumulative interest payable
    total_repayment: float   # Total repayment equal to the sum of all actual installments
    principal_ratio: float   # Proportional ratio 0.0 - 1.0
    interest_ratio: float    # Proportional ratio 0.0 - 1.0


def validate_emi_inputs(principal_str: str, rate_str: str, tenure_str: str) -> Tuple[float, float, float]:
    """
    Validates EMI input strings and converts them to floats.
    Rejects empty, non-numeric, non-finite (NaN, Infinity), and out-of-bounds inputs.
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

    if not math.isfinite(principal):
        raise ValueError("Principal amount must be a finite number (NaN and Infinity are not allowed).")

    if principal <= 0:
        raise ValueError("Principal amount must be greater than zero.")

    # Parse annual interest rate
    try:
        annual_rate = float(r_str)
    except ValueError:
        raise ValueError("Annual interest rate must be a valid number.")

    if not math.isfinite(annual_rate):
        raise ValueError("Annual interest rate must be a finite number (NaN and Infinity are not allowed).")

    if annual_rate < 0:
        raise ValueError("Annual interest rate cannot be negative.")

    if annual_rate > 100:
        raise ValueError("Annual interest rate cannot exceed 100%.")

    # Parse tenure
    try:
        tenure_years = float(t_str)
    except ValueError:
        raise ValueError("Loan tenure must be a valid number.")

    if not math.isfinite(tenure_years):
        raise ValueError("Loan tenure must be a finite number (NaN and Infinity are not allowed).")

    if tenure_years <= 0:
        raise ValueError("Loan tenure must be greater than zero.")

    if tenure_years > 50:
        raise ValueError("Loan tenure cannot exceed 50 years.")

    return principal, annual_rate, tenure_years


def calculate_emi(principal: float, annual_rate: float, tenure_years: float) -> EMICalculationResult:
    """
    Calculates monthly EMI, explicit final installment, total interest, and total repayment amount.
    Validates direct numeric arguments.
    
    Nearest-month rounding convention:
    Fractional years are converted to nearest whole integer months (n = round(tenure_years * 12)).
    Effective duration in years is derived directly from the whole month count (effective_years = n / 12),
    ensuring that duration in months and years is completely normalized and consistent.
    
    Theoretical-Total Convention with Final-Installment Rounding Adjustment:
    Calculates the standard theoretical reducing-balance EMI and total repayment estimate:
        exact_emi = P * r * (1+r)^n / ((1+r)^n - 1)
        exact_total_repayment = exact_emi * n
    Regular monthly EMI is rounded to two decimal places (paise).
    Because monthly EMI is rounded, multiplying it by n would produce an accumulated rounding divergence
    from the theoretical formula total. An explicit final-installment rounding adjustment is derived:
        final_installment = round(exact_total_repayment - (monthly_emi * (n - 1)), 2)
        total_repayment = round((monthly_emi * (n - 1)) + final_installment, 2)
        total_interest = round(total_repayment - principal, 2)
    This represents a theoretical formula estimate with a final-installment rounding adjustment,
    not a month-by-month lender amortization schedule with daily interest or lender-specific rounding.
    """
    # Type and finiteness validation for direct numeric calls
    if not (isinstance(principal, (int, float)) and isinstance(annual_rate, (int, float)) and isinstance(tenure_years, (int, float))):
        raise ValueError("All inputs must be numeric (int or float).")

    if not (math.isfinite(principal) and math.isfinite(annual_rate) and math.isfinite(tenure_years)):
        raise ValueError("All inputs must be finite numbers (NaN and Infinity are not allowed).")

    if principal <= 0:
        raise ValueError("Principal amount must be greater than zero.")
    if annual_rate < 0 or annual_rate > 100:
        raise ValueError("Annual interest rate must be between 0% and 100%.")
    if tenure_years <= 0 or tenure_years > 50:
        raise ValueError("Loan tenure must be between > 0 and <= 50 years.")

    # Convert requested duration to nearest whole month count
    tenure_months = int(round(tenure_years * 12))
    if tenure_months <= 0:
        raise ValueError("Tenure in months must be at least 1 month.")

    # Derive effective duration in years from normalized whole month count
    effective_years = round(tenure_months / 12.0, 4)

    # Monthly interest rate
    r = annual_rate / (12.0 * 100.0)
    n = tenure_months

    try:
        if r == 0:
            exact_emi = principal / n
            exact_total_repayment = float(principal)
        else:
            # Standard reducing balance EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)
            power_factor = (1.0 + r) ** n
            if not math.isfinite(power_factor) or power_factor <= 1.0:
                raise ValueError("Calculation resulted in an invalid power factor.")
            exact_emi = principal * r * power_factor / (power_factor - 1.0)
            exact_total_repayment = exact_emi * n
    except OverflowError:
        raise ValueError("Calculation resulted in an overflow. Values exceed computational limits.")

    if not math.isfinite(exact_emi):
        raise ValueError("Calculated EMI is not a finite number.")

    monthly_emi = round(exact_emi, 2)

    # Check unrepresentable rounded EMI (< ₹0.01 / 1 paisa)
    if monthly_emi < 0.01:
        raise ValueError("Calculated monthly EMI is less than ₹0.01 (1 paisa). Please increase the principal or decrease tenure.")

    # Explicit final-installment calculation
    if n == 1:
        final_installment = round(exact_total_repayment, 2)
    else:
        raw_final = exact_total_repayment - (monthly_emi * (n - 1))
        final_installment = round(raw_final, 2)

    # Validate final installment positivity
    if not math.isfinite(final_installment) or final_installment <= 0:
        raise ValueError("Calculated final installment is non-positive or invalid. Please check loan parameters.")

    # Total repayment is exactly the sum of all actual installments
    if n == 1:
        total_repayment = final_installment
    else:
        total_repayment = round((monthly_emi * (n - 1)) + final_installment, 2)

    principal_rounded = round(principal, 2)
    total_interest = round(total_repayment - principal_rounded, 2)

    # Calculate proportional ratios strictly bounded in [0.0, 1.0] and summing to 1.0
    if total_repayment > 0:
        principal_ratio = min(1.0, max(0.0, principal_rounded / total_repayment))
        principal_ratio = round(principal_ratio, 4)
        interest_ratio = round(1.0 - principal_ratio, 4)
    else:
        principal_ratio = 1.0
        interest_ratio = 0.0

    return EMICalculationResult(
        principal=principal_rounded,
        annual_rate=round(annual_rate, 4),
        tenure_years=effective_years,
        tenure_months=tenure_months,
        monthly_emi=monthly_emi,
        final_installment=final_installment,
        total_interest=total_interest,
        total_repayment=total_repayment,
        principal_ratio=principal_ratio,
        interest_ratio=interest_ratio,
    )

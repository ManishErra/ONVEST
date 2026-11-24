"""
SIP (Systematic Investment Plan) Calculator Logic for ONVEST.

Formulas:
- Monthly expected return: i = Annual Return Rate / (12 * 100)
- Number of investment periods: n = round(Investment Duration in Years * 12)
- Effective duration in years: effective_years = n / 12
- Future value for end-of-month contributions (ordinary annuity):
    FV = M * (((1 + i)^n - 1) / i)
- If i == 0:
    FV = M * n
- Total Invested Amount = M * n
- Estimated Returns = FV - Total Invested Amount
"""

import math
from dataclasses import dataclass
from typing import Tuple


@dataclass
class SIPCalculationResult:
    monthly_investment: float
    annual_return_rate: float
    duration_years: float    # Effective duration in years derived from whole months (n / 12)
    duration_months: int     # Effective duration in months
    total_invested: float    # Total principal invested
    estimated_returns: float # Estimated capital gains
    future_value: float      # Projected maturity corpus
    invested_ratio: float    # Proportional ratio 0.0 - 1.0
    returns_ratio: float     # Proportional ratio 0.0 - 1.0


def validate_sip_inputs(monthly_str: str, rate_str: str, duration_str: str) -> Tuple[float, float, float]:
    """
    Validates SIP input strings and converts them to floats.
    Rejects empty, non-numeric, non-finite (NaN, Infinity), and out-of-bounds inputs.
    Raises ValueError with a user-friendly message if validation fails.
    """
    if monthly_str is None or rate_str is None or duration_str is None:
        raise ValueError("All fields are required. Please fill in all inputs.")

    m_str = monthly_str.strip()
    r_str = rate_str.strip()
    d_str = duration_str.strip()

    if not m_str or not r_str or not d_str:
        raise ValueError("All fields are required. Please enter values for Monthly Investment, Return Rate, and Duration.")

    # Parse monthly investment
    try:
        monthly_investment = float(m_str)
    except ValueError:
        raise ValueError("Monthly investment amount must be a valid number.")

    if not math.isfinite(monthly_investment):
        raise ValueError("Monthly investment amount must be a finite number (NaN and Infinity are not allowed).")

    if monthly_investment <= 0:
        raise ValueError("Monthly investment amount must be greater than zero.")

    # Parse annual return rate
    try:
        annual_rate = float(r_str)
    except ValueError:
        raise ValueError("Expected annual return rate must be a valid number.")

    if not math.isfinite(annual_rate):
        raise ValueError("Expected annual return rate must be a finite number (NaN and Infinity are not allowed).")

    if annual_rate < 0:
        raise ValueError("Expected annual return rate cannot be negative.")

    if annual_rate > 100:
        raise ValueError("Expected annual return rate cannot exceed 100%.")

    # Parse duration
    try:
        duration_years = float(d_str)
    except ValueError:
        raise ValueError("Investment duration must be a valid number.")

    if not math.isfinite(duration_years):
        raise ValueError("Investment duration must be a finite number (NaN and Infinity are not allowed).")

    if duration_years <= 0:
        raise ValueError("Investment duration must be greater than zero.")

    if duration_years > 50:
        raise ValueError("Investment duration cannot exceed 50 years.")

    return monthly_investment, annual_rate, duration_years


def calculate_sip(monthly_investment: float, annual_return_rate: float, duration_years: float) -> SIPCalculationResult:
    """
    Calculates total invested amount, estimated returns, and future value.
    Validates direct numeric calls and rejects non-finite numbers and mathematical overflows.
    
    Nearest-month rounding convention:
    Fractional years are converted to nearest whole integer months (n = round(duration_years * 12)).
    Effective duration in years is derived directly from the whole month count (effective_years = n / 12),
    ensuring consistent duration reporting across all views and database records.
    
    Uses standard ordinary annuity formula:
    FV = M * (((1 + i)^n - 1) / i) where i = rate / (12 * 100) and n = duration_months.
    """
    if not (isinstance(monthly_investment, (int, float)) and isinstance(annual_return_rate, (int, float)) and isinstance(duration_years, (int, float))):
        raise ValueError("All inputs must be numeric (int or float).")

    if not (math.isfinite(monthly_investment) and math.isfinite(annual_return_rate) and math.isfinite(duration_years)):
        raise ValueError("All inputs must be finite numbers (NaN and Infinity are not allowed).")

    if monthly_investment <= 0:
        raise ValueError("Monthly investment must be greater than zero.")
    if annual_return_rate < 0 or annual_return_rate > 100:
        raise ValueError("Expected annual return rate must be between 0% and 100%.")
    if duration_years <= 0 or duration_years > 50:
        raise ValueError("Investment duration must be between > 0 and <= 50 years.")

    # Convert requested duration to nearest whole month count
    duration_months = int(round(duration_years * 12))
    if duration_months <= 0:
        raise ValueError("Duration in months must be at least 1 month.")

    # Derive effective duration in years from normalized whole month count
    effective_years = round(duration_months / 12.0, 4)

    n = duration_months
    total_invested = round(monthly_investment * n, 2)

    i = annual_return_rate / (12.0 * 100.0)

    try:
        if i == 0:
            future_value = total_invested
            estimated_returns = 0.0
        else:
            # Specified formula: FV = M * (((1 + i)^n - 1) / i)
            power_factor = (1.0 + i) ** n
            if not math.isfinite(power_factor):
                raise ValueError("Calculation resulted in an invalid growth factor.")
            calc_fv = monthly_investment * ((power_factor - 1.0) / i)
            if not math.isfinite(calc_fv):
                raise ValueError("Calculated Future Value is not a finite number.")
            future_value = round(calc_fv, 2)
            # Future value is at least total invested
            future_value = max(total_invested, future_value)
            estimated_returns = round(future_value - total_invested, 2)
    except OverflowError:
        raise ValueError("Calculation resulted in an overflow. Values exceed computational limits.")

    if future_value > 0:
        invested_ratio = min(1.0, max(0.0, total_invested / future_value))
        invested_ratio = round(invested_ratio, 4)
        returns_ratio = round(1.0 - invested_ratio, 4)
    else:
        invested_ratio = 1.0
        returns_ratio = 0.0

    return SIPCalculationResult(
        monthly_investment=round(monthly_investment, 2),
        annual_return_rate=round(annual_return_rate, 4),
        duration_years=effective_years,
        duration_months=duration_months,
        total_invested=total_invested,
        estimated_returns=estimated_returns,
        future_value=future_value,
        invested_ratio=invested_ratio,
        returns_ratio=returns_ratio,
    )

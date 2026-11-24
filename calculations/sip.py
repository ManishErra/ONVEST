"""
SIP (Systematic Investment Plan) Calculator Logic for ONVEST.

Formulas:
- Monthly expected return: i = Annual Return Rate / (12 * 100)
- Total investment periods: n = Investment Duration in Years * 12
- Future value for end-of-month contributions (ordinary annuity):
    FV = M * (((1 + i)^n - 1) / i)
- If i == 0:
    FV = M * n
- Total Invested Amount = M * n
- Estimated Returns = FV - Total Invested Amount
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class SIPCalculationResult:
    monthly_investment: float
    annual_return_rate: float
    duration_years: float
    duration_months: int
    total_invested: float
    estimated_returns: float
    future_value: float
    invested_ratio: float   # Proportional ratio 0.0 - 1.0
    returns_ratio: float    # Proportional ratio 0.0 - 1.0


def validate_sip_inputs(monthly_str: str, rate_str: str, duration_str: str) -> Tuple[float, float, float]:
    """
    Validates SIP input strings and converts them to floats.
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

    if monthly_investment <= 0:
        raise ValueError("Monthly investment amount must be greater than zero.")

    # Parse annual return rate
    try:
        annual_rate = float(r_str)
    except ValueError:
        raise ValueError("Expected annual return rate must be a valid number.")

    if annual_rate < 0:
        raise ValueError("Expected annual return rate cannot be negative.")

    if annual_rate > 100:
        raise ValueError("Expected annual return rate cannot exceed 100%.")

    # Parse duration
    try:
        duration_years = float(d_str)
    except ValueError:
        raise ValueError("Investment duration must be a valid number.")

    if duration_years <= 0:
        raise ValueError("Investment duration must be greater than zero.")

    if duration_years > 50:
        raise ValueError("Investment duration cannot exceed 50 years.")

    return monthly_investment, annual_rate, duration_years


def calculate_sip(monthly_investment: float, annual_return_rate: float, duration_years: float) -> SIPCalculationResult:
    """
    Calculates total invested amount, estimated returns, and future value.
    Uses the prompt's specified formula:
    FV = M * (((1 + i)^n - 1) / i) where i = rate / (12 * 100) and n = duration * 12.
    """
    if monthly_investment <= 0:
        raise ValueError("Monthly investment must be greater than zero.")
    if annual_return_rate < 0 or annual_return_rate > 100:
        raise ValueError("Expected annual return rate must be between 0% and 100%.")
    if duration_years <= 0 or duration_years > 50:
        raise ValueError("Investment duration must be between > 0 and <= 50 years.")

    duration_months = int(round(duration_years * 12))
    if duration_months <= 0:
        raise ValueError("Duration in months must be at least 1 month.")

    n = duration_months
    total_invested = monthly_investment * n

    i = annual_return_rate / (12.0 * 100.0)

    if i == 0:
        future_value = total_invested
        estimated_returns = 0.0
    else:
        # Specified formula: FV = M * (((1 + i)^n - 1) / i)
        future_value = monthly_investment * (((1.0 + i) ** n - 1.0) / i)
        estimated_returns = future_value - total_invested

    if future_value > 0:
        invested_ratio = total_invested / future_value
        returns_ratio = estimated_returns / future_value
    else:
        invested_ratio = 1.0
        returns_ratio = 0.0

    return SIPCalculationResult(
        monthly_investment=round(monthly_investment, 2),
        annual_return_rate=round(annual_return_rate, 4),
        duration_years=round(duration_years, 2),
        duration_months=duration_months,
        total_invested=round(total_invested, 2),
        estimated_returns=round(estimated_returns, 2),
        future_value=round(future_value, 2),
        invested_ratio=round(invested_ratio, 4),
        returns_ratio=round(returns_ratio, 4),
    )

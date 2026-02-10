def calculate(
    initial_principal,
    annual_rate_percent,
    years,
    annual_contribution=0,
    compounding_per_year=12,
):
    """Compute compound interest with optional annual contributions.

    Parameters
    ----------
    initial_principal : float
        Initial amount invested, in currency units.
    annual_rate_percent : float
        Annual interest rate, as a percent (e.g., 5 for 5%).
    years : int
        Investment duration, in years.
    annual_contribution : float, optional
        Extra contribution added at the end of each year, in currency units.
        Default is 0.
    compounding_per_year : int, optional
        Number of compounding periods per year (e.g., 12 for monthly).
        Default is 12.

    Returns
    -------
    dict
        Dictionary with:
        - "final_amount": ending balance after interest and contributions.
        - "interest_earned": total interest earned over the full period.
        - "total_contributions": sum of principal and all additional deposits.
    """
    balance = initial_principal
    rate_per_period = annual_rate_percent / 100 / compounding_per_year
    total_periods = years * compounding_per_year

    for period in range(1, total_periods + 1):
        period_interest = balance * rate_per_period
        balance += period_interest
        if period % compounding_per_year == 0 and period < total_periods:
            balance += annual_contribution

    return {
        "final_amount": round(balance, 2),
        "interest_earned": round(
            balance - initial_principal - (annual_contribution * (years - 1)), 2
        ),
        "total_contributions": initial_principal
        + (annual_contribution * (years - 1)),
    }
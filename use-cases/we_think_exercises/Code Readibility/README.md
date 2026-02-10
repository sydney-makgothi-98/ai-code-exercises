# Compound Interest Calculator

This folder contains a small compound interest calculator and unit tests that validate its behavior.

## What the code does

The function in `exercise_2.py` computes a final account balance based on:
- An initial principal
- A yearly interest rate (percent)
- A number of years
- Optional annual contributions
- A compounding frequency (periods per year)

It returns a dictionary with the final balance, total interest earned, and total contributions.

## Why the tests matter

The unit tests in `unit test.py`:
- Check basic compounding without extra contributions
- Verify the effect of annual contributions
- Compare different compounding frequencies
- Confirm correct behavior with zero interest

These tests protect against logic regressions and confirm that changes to the function keep the same financial behavior.

## How the code works

At a high level:
1. Convert the annual rate into a per-period rate using the compounding frequency.
2. Loop over each compounding period and apply interest.
3. At the end of each year (except the final year), add the annual contribution.
4. Return the rounded results.

The calculations are done in currency units, with interest rate inputs in percent.

## How to use the function

Example usage:

```python
from exercise_2 import calculate

result = calculate(
    initial_principal=1000,
    annual_rate_percent=5,
    years=3,
    annual_contribution=500,
    compounding_per_year=12,
)

print(result)
```

Expected output format:

```python
{
    "final_amount": 2239.52,
    "interest_earned": 239.52,
    "total_contributions": 2000
}
```

## How to run the tests

From this folder:

```bash
python "unit test.py"
```

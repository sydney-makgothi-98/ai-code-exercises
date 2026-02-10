# Improved (idiomatic Python)
TEN = 10

def square(value: float) -> float:
    """Return the square of `value`."""
    return value ** 2

def raise_to_tenth(power: float) -> float:
    """Raise 10 to the given `power`."""
    return TEN ** power

def reynolds_number(
    density: float,
    velocity: float,
    characteristic_length: float,
    viscosity: float,
) -> float:
    """Compute the Reynolds number (dimensionless)."""
    return (density * velocity * characteristic_length) / viscosity
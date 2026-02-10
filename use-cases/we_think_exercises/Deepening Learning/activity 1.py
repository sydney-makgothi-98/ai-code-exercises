from math import log

# Global methods
def sqr_func(inp):
    return inp ** 2

def tenth_power_raiser(power_val):  # Raises things to the tenth power
    return 10 ** power_val

# Reynolds number calculation
def re_num(density, velocity, omega, viscosity):
    """
    Calculates the Reynolds number.

    Parameters:
    - density: The fluid density (kg/m^3)
    - velocity: The fluid velocity (m/s)
    - omega: The characteristic length (e.g., pipe diameter in meters)
    - viscosity: The fluid's dynamic viscosity (Pa.s or N·s/m^2)

    Returns:
    - Reynolds number (dimensionless)
    """
    return (density * velocity * omega) / viscosity

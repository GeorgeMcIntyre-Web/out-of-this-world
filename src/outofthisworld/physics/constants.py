"""Physical constants in SI units."""

from typing import Final

# Gravitational constant
G: Final[float] = 6.67430e-11  # m^3 / (kg s^2)

# Speed of light
C: Final[float] = 2.99792458e8  # m/s

# Earth parameters
M_EARTH: Final[float] = 5.9722e24  # kg
R_EARTH: Final[float] = 6.371e6  # m

# Solar system (approximate)
M_SUN: Final[float] = 1.989e30  # kg
AU: Final[float] = 1.496e11  # m (astronomical unit)

# Earth gravitational harmonics
J2_EARTH: Final[float] = 1.08263e-3  # J2 coefficient (dimensionless)

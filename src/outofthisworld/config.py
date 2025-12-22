"""Configuration constants and default parameters."""

from typing import Final

# Physical constants (SI units)
G: Final[float] = 6.67430e-11  # Gravitational constant, m^3 / (kg s^2)
C: Final[float] = 2.99792458e8  # Speed of light, m/s
M_EARTH: Final[float] = 5.9722e24  # Earth mass, kg
R_EARTH: Final[float] = 6.371e6  # Earth radius, m

# Default sensor parameters
DEFAULT_IMU_BIAS: Final[float] = 1e-5  # m/s^2
DEFAULT_IMU_NOISE_STD: Final[float] = 1e-4  # m/s^2
DEFAULT_IMU_BIAS_STABILITY: Final[float] = 1e-6  # m/s^2 (Allan deviation minimum)

# Default simulation parameters
DEFAULT_DT: Final[float] = 1.0  # Time step, seconds
DEFAULT_TOLERANCE: Final[float] = 1e-10  # Numerical tolerance

# Interferometer parameters (simplified model)
DEFAULT_INTERFEROMETER_SENSITIVITY: Final[float] = 1e-9  # m/s^2 (acceleration sensitivity)
DEFAULT_INTERFEROMETER_NOISE_STD: Final[float] = 1e-10  # m/s^2

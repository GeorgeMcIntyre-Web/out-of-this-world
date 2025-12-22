"""Relativistic effects: post-Newtonian corrections, time dilation."""

import numpy as np

from outofthisworld.physics.constants import C


def gravitational_redshift(
    r1: float,
    r2: float,
    mu: float,
) -> float:
    """
    Compute gravitational redshift factor between two radii.

    Args:
        r1: Inner radius (meters)
        r2: Outer radius (meters)
        mu: Gravitational parameter (G * M) in m^3/s^2

    Returns:
        Frequency ratio f2/f1 (f2 is observed at r2, f1 emitted at r1)
    """
    if r1 < 1e-6 or r2 < 1e-6:
        return 1.0

    phi1 = -mu / r1
    phi2 = -mu / r2
    return np.sqrt((1 + 2 * phi2 / (C**2)) / (1 + 2 * phi1 / (C**2)))


def schwarzschild_radius(mass: float) -> float:
    """
    Compute Schwarzschild radius (event horizon) for a given mass.

    Args:
        mass: Mass in kg

    Returns:
        Schwarzschild radius in meters
    """
    from outofthisworld.physics.constants import G

    return 2 * G * mass / (C**2)

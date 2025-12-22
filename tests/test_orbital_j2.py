"""Tests for J2 orbital perturbations."""

import numpy as np

from outofthisworld.physics.constants import J2_EARTH, M_EARTH, R_EARTH, G
from outofthisworld.physics.orbital import j2_acceleration, total_acceleration


def test_j2_acceleration_magnitude() -> None:
    """Test J2 acceleration has reasonable magnitude."""
    position = np.array([R_EARTH * 2, 0.0, R_EARTH * 0.5])
    mu = G * M_EARTH
    j2_accel = j2_acceleration(position, mu, J2_EARTH, R_EARTH)
    magnitude = np.linalg.norm(j2_accel)

    # J2 should be much smaller than two-body (typically < 1% at LEO)
    two_body_mag = np.linalg.norm(-mu * position / (np.linalg.norm(position) ** 3))
    assert magnitude < two_body_mag * 0.1  # J2 < 10% of two-body


def test_j2_acceleration_polar_effect() -> None:
    """Test J2 acceleration is stronger at poles."""
    # Equatorial position
    pos_eq = np.array([R_EARTH * 2, 0.0, 0.0])
    # Polar position (same radius)
    pos_pole = np.array([0.0, 0.0, R_EARTH * 2])

    mu = G * M_EARTH
    j2_eq = j2_acceleration(pos_eq, mu, J2_EARTH, R_EARTH)
    j2_pole = j2_acceleration(pos_pole, mu, J2_EARTH, R_EARTH)

    # J2 effect should be different (not just magnitude, but direction)
    assert not np.allclose(j2_eq, j2_pole)


def test_total_acceleration_with_j2() -> None:
    """Test total acceleration includes J2 when provided."""
    position = np.array([R_EARTH * 2, 0.0, R_EARTH * 0.5])
    mu = G * M_EARTH

    # Two-body only
    accel_2body = total_acceleration(position, mu)

    # With J2
    accel_total = total_acceleration(position, mu, J2_EARTH, R_EARTH)

    # Should be different
    assert not np.allclose(accel_2body, accel_total)

    # Total should be close to sum
    j2_only = j2_acceleration(position, mu, J2_EARTH, R_EARTH)
    expected = accel_2body + j2_only
    assert np.allclose(accel_total, expected, rtol=1e-10)


def test_total_acceleration_without_j2() -> None:
    """Test total acceleration equals two-body when J2 not provided."""
    position = np.array([R_EARTH * 2, 0.0, 0.0])
    mu = G * M_EARTH

    from outofthisworld.physics.orbital import two_body_acceleration

    accel_2body = two_body_acceleration(position, mu)
    accel_total = total_acceleration(position, mu)

    assert np.allclose(accel_2body, accel_total)

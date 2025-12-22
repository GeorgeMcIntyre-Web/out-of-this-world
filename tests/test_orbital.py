"""Tests for orbital mechanics."""

import numpy as np
import pytest

from outofthisworld.physics.constants import M_EARTH, R_EARTH, G
from outofthisworld.physics.orbital import propagate_orbit, two_body_acceleration


def test_two_body_acceleration_magnitude() -> None:
    """Test acceleration magnitude matches expected value."""
    position = np.array([R_EARTH * 2, 0.0, 0.0])  # 2 Earth radii
    mu = G * M_EARTH
    accel = two_body_acceleration(position, mu)
    magnitude = np.linalg.norm(accel)

    # Expected: a = mu / r^2
    r = np.linalg.norm(position)
    expected = mu / (r**2)
    assert abs(magnitude - expected) < 1e-6


def test_two_body_acceleration_direction() -> None:
    """Test acceleration points toward origin."""
    position = np.array([1e7, 0.0, 0.0])
    mu = G * M_EARTH
    accel = two_body_acceleration(position, mu)

    # Acceleration should be opposite to position (toward origin)
    dot_product = np.dot(accel, position)
    assert dot_product < 0


def test_two_body_acceleration_zero_position() -> None:
    """Test acceleration handles zero position gracefully."""
    position = np.array([0.0, 0.0, 0.0])
    mu = G * M_EARTH
    accel = two_body_acceleration(position, mu)
    assert np.allclose(accel, 0.0)


def test_propagate_orbit_conserves_energy() -> None:
    """Test orbit propagation approximately conserves energy."""
    # Circular orbit
    r = 7e6  # 7000 km altitude
    v = np.sqrt(G * M_EARTH / r)  # Circular velocity
    position = np.array([r, 0.0, 0.0])
    velocity = np.array([0.0, v, 0.0])
    mu = G * M_EARTH

    # Initial energy
    E0 = 0.5 * np.dot(velocity, velocity) - mu / np.linalg.norm(position)

    # Propagate one orbit period
    T = 2 * np.pi * np.sqrt(r**3 / mu)
    dt = T / 100  # Small steps
    n_steps = 100

    pos = position.copy()
    vel = velocity.copy()
    for _ in range(n_steps):
        pos, vel = propagate_orbit(pos, vel, mu, dt, method="rk4")

    # Final energy
    Ef = 0.5 * np.dot(vel, vel) - mu / np.linalg.norm(pos)

    # Energy should be approximately conserved (within 1%)
    assert abs(Ef - E0) / abs(E0) < 0.01


def test_propagate_orbit_invalid_method() -> None:
    """Test propagate_orbit raises error for invalid method."""
    position = np.array([7e6, 0.0, 0.0])
    velocity = np.array([0.0, 7500.0, 0.0])
    mu = G * M_EARTH

    with pytest.raises(ValueError, match="Unknown integration method"):
        propagate_orbit(position, velocity, mu, 1.0, method="invalid")

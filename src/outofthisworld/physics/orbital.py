"""Orbital mechanics: two-body propagation, perturbations."""

import numpy as np
from numpy.typing import NDArray


def two_body_acceleration(
    position: NDArray[np.float64],
    mu: float,
) -> NDArray[np.float64]:
    """
    Compute two-body gravitational acceleration.

    Args:
        position: Position vector [x, y, z] in meters
        mu: Gravitational parameter (G * M) in m^3/s^2

    Returns:
        Acceleration vector [ax, ay, az] in m/s^2
    """
    r = np.linalg.norm(position)
    if r < 1e-6:  # Guard against division by zero
        return np.zeros(3)

    return -mu * position / (r**3)


def propagate_orbit(
    position: NDArray[np.float64],
    velocity: NDArray[np.float64],
    mu: float,
    dt: float,
    method: str = "rk4",
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Propagate orbit using numerical integration.

    Args:
        position: Initial position [x, y, z] in meters
        velocity: Initial velocity [vx, vy, vz] in m/s
        mu: Gravitational parameter (G * M) in m^3/s^2
        dt: Time step in seconds
        method: Integration method ('euler' or 'rk4')

    Returns:
        Tuple of (new_position, new_velocity)
    """
    if method == "euler":
        return _propagate_euler(position, velocity, mu, dt)
    if method == "rk4":
        return _propagate_rk4(position, velocity, mu, dt)

    raise ValueError(f"Unknown integration method: {method}")


def _propagate_euler(
    position: NDArray[np.float64],
    velocity: NDArray[np.float64],
    mu: float,
    dt: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Euler integration (first-order, simple but less accurate)."""
    acceleration = two_body_acceleration(position, mu)
    new_velocity = velocity + acceleration * dt
    new_position = position + velocity * dt
    return new_position, new_velocity


def _propagate_rk4(
    position: NDArray[np.float64],
    velocity: NDArray[np.float64],
    mu: float,
    dt: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Runge-Kutta 4th order integration."""
    # k1
    a1 = two_body_acceleration(position, mu)
    v1 = velocity
    k1_pos = v1 * dt
    k1_vel = a1 * dt

    # k2
    pos2 = position + 0.5 * k1_pos
    vel2 = velocity + 0.5 * k1_vel
    a2 = two_body_acceleration(pos2, mu)
    k2_pos = vel2 * dt
    k2_vel = a2 * dt

    # k3
    pos3 = position + 0.5 * k2_pos
    vel3 = velocity + 0.5 * k2_vel
    a3 = two_body_acceleration(pos3, mu)
    k3_pos = vel3 * dt
    k3_vel = a3 * dt

    # k4
    pos4 = position + k3_pos
    vel4 = velocity + k3_vel
    a4 = two_body_acceleration(pos4, mu)
    k4_pos = vel4 * dt
    k4_vel = a4 * dt

    # Combine
    new_position = position + (k1_pos + 2 * k2_pos + 2 * k3_pos + k4_pos) / 6.0
    new_velocity = velocity + (k1_vel + 2 * k2_vel + 2 * k3_vel + k4_vel) / 6.0

    return new_position, new_velocity

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


def j2_acceleration(
    position: NDArray[np.float64],
    mu: float,
    j2: float,
    r_eq: float,
) -> NDArray[np.float64]:
    """
    Compute J2 (oblateness) perturbation acceleration.

    Args:
        position: Position vector [x, y] or [x, y, z] in meters
        mu: Gravitational parameter (G * M) in m^3/s^2
        j2: J2 coefficient (dimensionless, ~0.00108 for Earth)
        r_eq: Equatorial radius in meters

    Returns:
        J2 perturbation acceleration vector (same dimension as position) in m/s^2
    """
    r = np.linalg.norm(position)
    if r < 1e-6:
        return np.zeros_like(position)

    n_dim = len(position)
    r_sq = r * r
    r_eq_sq = r_eq * r_eq

    # J2 perturbation formula
    factor = 1.5 * j2 * mu * r_eq_sq / (r_sq * r_sq * r)

    if n_dim == 2:
        # 2D case: assume z=0 (equatorial plane)
        x, y = position[0], position[1]
        z_over_r = 0.0
        ax = factor * x * (5 * z_over_r * z_over_r - 1)
        ay = factor * y * (5 * z_over_r * z_over_r - 1)
        return np.array([ax, ay])
    if n_dim == 3:
        x, y, z = position[0], position[1], position[2]
        z_over_r = z / r
        ax = factor * x * (5 * z_over_r * z_over_r - 1)
        ay = factor * y * (5 * z_over_r * z_over_r - 1)
        az = factor * z * (5 * z_over_r * z_over_r - 3)
        return np.array([ax, ay, az])

    raise ValueError(f"Unsupported position dimension: {n_dim}")


def total_acceleration(
    position: NDArray[np.float64],
    mu: float,
    j2: float | None = None,
    r_eq: float | None = None,
) -> NDArray[np.float64]:
    """
    Compute total acceleration including perturbations.

    Args:
        position: Position vector [x, y, z] in meters
        mu: Gravitational parameter (G * M) in m^3/s^2
        j2: J2 coefficient (optional)
        r_eq: Equatorial radius in meters (required if j2 is provided)

    Returns:
        Total acceleration vector [ax, ay, az] in m/s^2
    """
    accel = two_body_acceleration(position, mu)

    if j2 is not None and r_eq is not None:
        accel = accel + j2_acceleration(position, mu, j2, r_eq)

    return accel


def propagate_orbit(
    position: NDArray[np.float64],
    velocity: NDArray[np.float64],
    mu: float,
    dt: float,
    method: str = "rk4",
    j2: float | None = None,
    r_eq: float | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Propagate orbit using numerical integration.

    Args:
        position: Initial position [x, y, z] in meters
        velocity: Initial velocity [vx, vy, vz] in m/s
        mu: Gravitational parameter (G * M) in m^3/s^2
        dt: Time step in seconds
        method: Integration method ('euler' or 'rk4')
        j2: J2 coefficient for perturbations (optional)
        r_eq: Equatorial radius for J2 (required if j2 provided)

    Returns:
        Tuple of (new_position, new_velocity)
    """
    if method == "euler":
        return _propagate_euler(position, velocity, mu, dt, j2, r_eq)
    if method == "rk4":
        return _propagate_rk4(position, velocity, mu, dt, j2, r_eq)

    raise ValueError(f"Unknown integration method: {method}")


def _propagate_euler(
    position: NDArray[np.float64],
    velocity: NDArray[np.float64],
    mu: float,
    dt: float,
    j2: float | None = None,
    r_eq: float | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Euler integration (first-order, simple but less accurate)."""
    acceleration = total_acceleration(position, mu, j2, r_eq)
    new_velocity = velocity + acceleration * dt
    new_position = position + velocity * dt
    return new_position, new_velocity


def _propagate_rk4(
    position: NDArray[np.float64],
    velocity: NDArray[np.float64],
    mu: float,
    dt: float,
    j2: float | None = None,
    r_eq: float | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Runge-Kutta 4th order integration."""
    # k1
    a1 = total_acceleration(position, mu, j2, r_eq)
    v1 = velocity
    k1_pos = v1 * dt
    k1_vel = a1 * dt

    # k2
    pos2 = position + 0.5 * k1_pos
    vel2 = velocity + 0.5 * k1_vel
    a2 = total_acceleration(pos2, mu, j2, r_eq)
    k2_pos = vel2 * dt
    k2_vel = a2 * dt

    # k3
    pos3 = position + 0.5 * k2_pos
    vel3 = velocity + 0.5 * k2_vel
    a3 = total_acceleration(pos3, mu, j2, r_eq)
    k3_pos = vel3 * dt
    k3_vel = a3 * dt

    # k4
    pos4 = position + k3_pos
    vel4 = velocity + k3_vel
    a4 = total_acceleration(pos4, mu, j2, r_eq)
    k4_pos = vel4 * dt
    k4_vel = a4 * dt

    # Combine
    new_position = position + (k1_pos + 2 * k2_pos + 2 * k3_pos + k4_pos) / 6.0
    new_velocity = velocity + (k1_vel + 2 * k2_vel + 2 * k3_vel + k4_vel) / 6.0

    return new_position, new_velocity

"""
Generate realistic simulation data for investor demos.
This creates compelling scenarios showing gravitational signature detection.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import numpy as np
from scipy.integrate import odeint

# Physical constants
G = 6.67430e-11  # m^3 kg^-1 s^-2
C = 299792458  # m/s
M_SUN = 1.989e30  # kg


def _repo_root() -> Path:
    # demos/investor_visuals/data_generation.py -> demos -> repo root
    return Path(__file__).resolve().parents[2]


@dataclass
class NeutronStar:
    """Neutron star parameters"""

    mass: float = 1.4 * M_SUN  # kg
    radius: float = 12000  # meters
    position: np.ndarray | None = None

    def __post_init__(self) -> None:
        if self.position is None:
            # Place the compact object at the origin (km) for clean visuals.
            self.position = np.array([0.0, 0.0, 0.0], dtype=float)


@dataclass
class Spacecraft:
    """Spacecraft state and sensor parameters"""

    mass: float = 1000  # kg
    sensor_noise: float = 1e-12  # m/s^2 (atom interferometer noise floor)


def gravitational_acceleration(position: np.ndarray, neutron_star: NeutronStar) -> np.ndarray:
    """
    Calculate gravitational acceleration from neutron star.

    Args:
        position: Spacecraft position [x, y, z] in meters
        neutron_star: NeutronStar object

    Returns:
        Acceleration vector [ax, ay, az] in m/s^2
    """
    r_vec = position - neutron_star.position * 1000  # Convert km to m
    r_mag = np.linalg.norm(r_vec)
    # Avoid singularities / numerical explosions if we get extremely close.
    r_mag = max(r_mag, float(neutron_star.radius * 10))

    # Newtonian gravity (sufficient for demo)
    a_mag = G * neutron_star.mass / (r_mag**2)
    a_vec = -a_mag * (r_vec / r_mag)

    return a_vec


def orbital_dynamics(state: np.ndarray, t: float, neutron_star: NeutronStar) -> np.ndarray:
    """
    ODE system for spacecraft orbital motion.

    Args:
        state: [x, y, z, vx, vy, vz] in meters and m/s
        t: Time in seconds
        neutron_star: Perturbing body

    Returns:
        Derivative [vx, vy, vz, ax, ay, az]
    """
    pos = state[:3]
    vel = state[3:]

    acc = gravitational_acceleration(pos, neutron_star)

    return np.concatenate([vel, acc])


def generate_flyby_trajectory(duration: int = 86400, dt: int = 60) -> Dict:
    """
    Generate spacecraft flyby trajectory data.

    Args:
        duration: Mission duration in seconds (default 1 day)
        dt: Time step in seconds

    Returns:
        Dictionary with trajectory, measurements, and uncertainty data
    """
    rng = np.random.default_rng(7)  # deterministic demo

    # Initial conditions: hyperbolic flyby (kept numerically stable for a 30–60s investor demo)
    # Distances here are in km (converted to meters for dynamics).
    initial_distance = 2e7  # 20,000,000 km
    initial_velocity = 150000  # 150 km/s

    state0 = np.array(
        [
            initial_distance * 1000,
            0,
            0,  # position (m)
            0,
            initial_velocity,
            0,  # velocity (m/s)
        ],
        dtype=float,
    )

    # Time points
    t = np.arange(0, duration, dt, dtype=float)

    # Neutron star
    ns = NeutronStar()

    # Integrate trajectory
    trajectory = odeint(orbital_dynamics, state0, t, args=(ns,), mxstep=5000)

    # Extract positions and velocities
    positions = trajectory[:, :3] / 1000  # Convert to km
    velocities = trajectory[:, 3:] / 1000  # Convert to km/s

    # Simulate sensor measurements (with noise)
    spacecraft = Spacecraft()
    true_accelerations = np.array(
        [gravitational_acceleration(trajectory[i, :3], ns) for i in range(len(t))]
    )

    measured_accelerations = true_accelerations + rng.normal(
        0, spacecraft.sensor_noise, true_accelerations.shape
    )

    # Compute uncertainty reduction (simulated Kalman filter performance)
    # Start with large uncertainty, converge as measurements accumulate
    initial_uncertainty = 100  # km position uncertainty
    final_uncertainty = 0.1  # km (after gravity signature detection)

    uncertainty = initial_uncertainty * np.exp(-t / (duration / 5)) + final_uncertainty

    # Gravity field grid for visualization
    grid_size = 50
    x_range = np.linspace(-3e7, 3e7, grid_size)  # km
    y_range = np.linspace(-3e7, 3e7, grid_size)  # km
    X, Y = np.meshgrid(x_range, y_range)

    gravity_magnitude = np.zeros_like(X)
    for i in range(grid_size):
        for j in range(grid_size):
            pos = np.array([X[i, j] * 1000, Y[i, j] * 1000, 0], dtype=float)
            g = gravitational_acceleration(pos, ns)
            gravity_magnitude[i, j] = np.log10(np.linalg.norm(g) + 1e-15)

    return {
        "time": t,
        "positions": positions,
        "velocities": velocities,
        "true_accelerations": true_accelerations,
        "measured_accelerations": measured_accelerations,
        "uncertainty": uncertainty,
        "gravity_field": {"X": X, "Y": Y, "magnitude": gravity_magnitude},
        "neutron_star_position": ns.position,
        "metadata": {
            "duration_hours": duration / 3600,
            "closest_approach_km": float(np.min(np.linalg.norm(positions - ns.position, axis=1))),
            "initial_uncertainty_km": float(initial_uncertainty),
            "final_uncertainty_km": float(final_uncertainty),
        },
    }


def save_demo_data(output_path: str | None = None):
    """Generate and save demo data to JSON"""
    if output_path is None:
        output_path = str(_repo_root() / "demos" / "outputs" / "demo_data.json")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print("Generating flyby trajectory data...")
    data = generate_flyby_trajectory()

    # Convert numpy arrays to lists for JSON serialization
    serializable_data = {
        "time": data["time"].tolist(),
        "positions": data["positions"].tolist(),
        "velocities": data["velocities"].tolist(),
        "true_accelerations": data["true_accelerations"].tolist(),
        "measured_accelerations": data["measured_accelerations"].tolist(),
        "uncertainty": data["uncertainty"].tolist(),
        "gravity_field": {
            "X": data["gravity_field"]["X"].tolist(),
            "Y": data["gravity_field"]["Y"].tolist(),
            "magnitude": data["gravity_field"]["magnitude"].tolist(),
        },
        "neutron_star_position": data["neutron_star_position"].tolist(),
        "metadata": data["metadata"],
    }

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(serializable_data, f, indent=2)

    print(f"Data saved to {output_file}")
    print(f"Closest approach: {data['metadata']['closest_approach_km']:.1f} km")
    print(
        "Uncertainty reduction: "
        f"{data['metadata']['initial_uncertainty_km']:.1f} → {data['metadata']['final_uncertainty_km']:.2f} km"
    )

    return data


if __name__ == "__main__":
    save_demo_data()


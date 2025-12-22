"""Demo script: run a simple simulation scenario with visualization."""

import numpy as np

try:
    import matplotlib

    # Use non-interactive backend if available (for CI/headless)
    if "MPLBACKEND" not in __import__("os").environ:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available. Install with: pip install matplotlib")
    print("Continuing without visualization...\n")

from outofthisworld.config import DEFAULT_IMU_NOISE_STD
from outofthisworld.estimation.gravity_measurements import GravityMeasurementModel
from outofthisworld.estimation.kalman import ExtendedKalmanFilter
from outofthisworld.estimation.measurement_types import MeasurementType
from outofthisworld.physics.constants import J2_EARTH, M_EARTH, R_EARTH, G
from outofthisworld.sim.runner import SimulationRunner
from outofthisworld.sim.scenario import Scenario


def m_to_km(value: float | np.ndarray) -> float | np.ndarray:
    """Convert meters to kilometers."""
    return value / 1000.0


def main() -> None:
    """Run demo simulation."""
    print("OutOfThisWorld Demo")
    print("=" * 50)

    # Setup: circular orbit at 700 km altitude
    altitude = 700e3  # 700 km
    r = R_EARTH + altitude
    v_circular = np.sqrt(G * M_EARTH / r)

    initial_position = np.array([r, 0.0, 0.0])
    initial_velocity = np.array([0.0, v_circular, 0.0])
    mu = G * M_EARTH

    # Create scenario (1 orbit period)
    period = 2 * np.pi * np.sqrt(r**3 / mu)
    scenario = Scenario(
        initial_position=initial_position,
        initial_velocity=initial_velocity,
        mu=mu,
        duration=period,
        dt=10.0,  # 10 second steps
        name="circular_orbit_700km",
    )

    print(f"Scenario: {scenario.name}")
    print(f"Initial altitude: {m_to_km(altitude):.1f} km")
    print(f"Orbital period: {period / 60:.1f} minutes")
    print(f"Time steps: {scenario.get_n_steps()}")
    print()

    # Create measurement model (gravity vector in inertial frame)
    # This is a simplified "gravimeter" measurement for demo purposes
    measurement_noise_std = DEFAULT_IMU_NOISE_STD  # m/s^2 per component
    measurement_model = GravityMeasurementModel(
        measurement_type=MeasurementType.GRAVITY_VECTOR_INERTIAL,
        mu=mu,
        noise_std=measurement_noise_std,
        j2=J2_EARTH,
        r_eq=R_EARTH,
    )

    print("Measurement: Gravity vector (inertial frame)")
    print(f"Measurement noise std: {measurement_noise_std:.2e} m/s² per component")
    print(f"J2 perturbations: Enabled (J2 = {J2_EARTH:.6f})")
    print()

    # Create EKF (2D state: position, velocity)
    initial_state = np.concatenate([initial_position[:2], initial_velocity[:2]])
    initial_covariance = np.diag([1e6, 1e6, 100.0, 100.0])  # Large initial uncertainty
    process_noise = np.diag([10.0, 10.0, 1.0, 1.0])
    measurement_noise_cov = measurement_model.measurement_noise_cov(len(initial_state))

    estimator = ExtendedKalmanFilter(
        initial_state=initial_state,
        initial_covariance=initial_covariance,
        process_noise=process_noise,
        measurement_noise=measurement_noise_cov,
    )

    # Create runner
    runner = SimulationRunner(
        scenario=scenario,
        estimator=estimator,
        measurement_model=measurement_model,
    )

    # Run simulation
    print("Running simulation...")
    results = runner.run()
    print("Simulation complete.")
    print()

    # Analyze results
    true_states = results["true_states"]
    estimated_states = results.get("estimated_states")
    measurements = results.get("measurements", np.array([]))

    # Extract positions and velocities
    true_positions = true_states[:, :3]
    true_velocities = true_states[:, 3:6]

    # Final state error
    final_true = true_states[-1]
    if estimated_states is not None:
        final_estimated = estimated_states[-1]

        # Position error (first 2 components)
        pos_error = np.linalg.norm(final_true[:2] - final_estimated[:2])
        print(f"Final position error: {m_to_km(pos_error):.2f} km")

        # Velocity error (components 3-4)
        vel_error = np.linalg.norm(final_true[2:4] - final_estimated[2:4])
        print(f"Final velocity error: {vel_error:.2f} m/s")
        print()

    # Orbital energy conservation check
    final_pos = true_states[-1, :3]
    final_vel = true_states[-1, 3:6]
    final_energy = 0.5 * np.dot(final_vel, final_vel) - mu / np.linalg.norm(final_pos)

    initial_energy = 0.5 * np.dot(initial_velocity, initial_velocity) - mu / np.linalg.norm(
        initial_position
    )
    energy_error = abs(final_energy - initial_energy) / abs(initial_energy)
    print(f"Energy conservation error: {energy_error * 100:.4f}%")
    print()

    # Visualization
    if HAS_MATPLOTLIB and estimated_states is not None:
        _plot_results(
            true_positions,
            true_velocities,
            estimated_states,
            measurements,
            scenario,
        )

    print("Demo complete.")
    print("\nNote: This demo uses simplified 'gravimeter' measurements")
    print("      (gravity vector in inertial frame) to keep the estimation")
    print("      problem observable in a toy setup.")


def _plot_results(
    true_positions: np.ndarray,
    true_velocities: np.ndarray,
    estimated_states: np.ndarray,
    measurements: np.ndarray,
    scenario: Scenario,
) -> None:
    """Create visualization plots."""
    print("Generating plots...")

    # Extract estimated positions and velocities
    est_positions = estimated_states[:, :2]  # 2D only
    est_velocities = estimated_states[:, 2:4]

    # Time array
    n_steps = len(true_positions)
    time = np.arange(n_steps) * scenario.dt / 60.0  # Convert to minutes

    # Create figure with subplots
    plt.figure(figsize=(14, 10))

    # 1. Orbit trajectory (2D projection)
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(
        m_to_km(true_positions[:, 0]),
        m_to_km(true_positions[:, 1]),
        "b-",
        label="True orbit",
        linewidth=2,
    )
    if len(est_positions) > 0:
        ax1.plot(
            m_to_km(est_positions[:, 0]),
            m_to_km(est_positions[:, 1]),
            "r--",
            label="Estimated orbit",
            linewidth=1.5,
            alpha=0.7,
        )
    # Earth
    circle = plt.Circle((0, 0), m_to_km(R_EARTH), color="green", alpha=0.3, label="Earth")
    ax1.add_patch(circle)
    ax1.set_xlabel("X position (km)")
    ax1.set_ylabel("Y position (km)")
    ax1.set_title("Orbit Trajectory (2D Projection)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect("equal")

    # 2. Position error over time
    ax2 = plt.subplot(2, 3, 2)
    if len(est_positions) > 0:
        pos_error = np.linalg.norm(true_positions[:, :2] - est_positions, axis=1)  # meters
        ax2.plot(time, m_to_km(pos_error), "r-", linewidth=1.5)
        ax2.set_xlabel("Time (minutes)")
        ax2.set_ylabel("Position error (km)")
        ax2.set_title("Position Estimation Error")
        ax2.grid(True, alpha=0.3)
        ax2.set_yscale("log")

    # 3. Velocity error over time
    ax3 = plt.subplot(2, 3, 3)
    if len(est_velocities) > 0:
        vel_error = np.linalg.norm(true_velocities[:, :2] - est_velocities, axis=1)  # m/s
        ax3.plot(time, vel_error, "b-", linewidth=1.5)
        ax3.set_xlabel("Time (minutes)")
        ax3.set_ylabel("Velocity error (m/s)")
        ax3.set_title("Velocity Estimation Error")
        ax3.grid(True, alpha=0.3)
        ax3.set_yscale("log")

    # 4. True vs measured acceleration (vector magnitude)
    ax4 = plt.subplot(2, 3, 4)
    if len(measurements) > 0:
        from outofthisworld.physics.orbital import total_acceleration

        true_accels = np.array(
            [
                np.linalg.norm(total_acceleration(pos, scenario.mu, J2_EARTH, R_EARTH))
                for pos in true_positions
            ]
        )
        time_meas = time[1:]  # Measurements start after first state
        if measurements.ndim == 2:
            # Vector measurements
            meas_mags = np.linalg.norm(measurements, axis=1)
        else:
            # Scalar measurements
            meas_mags = measurements

        ax4.plot(time_meas, true_accels[1:], "b-", label="True", linewidth=2)
        ax4.plot(
            time_meas,
            meas_mags,
            "r.",
            label="Measured",
            markersize=2,
            alpha=0.6,
        )
        ax4.set_xlabel("Time (minutes)")
        ax4.set_ylabel("Acceleration magnitude (m/s²)")
        ax4.set_title("Gravimeter Measurements vs Truth")
        ax4.legend()
        ax4.grid(True, alpha=0.3)

    # 5. Altitude over time
    ax5 = plt.subplot(2, 3, 5)
    altitudes = m_to_km(np.linalg.norm(true_positions, axis=1) - R_EARTH)  # km
    ax5.plot(time, altitudes, "g-", linewidth=2)
    ax5.set_xlabel("Time (minutes)")
    ax5.set_ylabel("Altitude (km)")
    ax5.set_title("Orbital Altitude")
    ax5.grid(True, alpha=0.3)

    # 6. Speed over time
    ax6 = plt.subplot(2, 3, 6)
    speeds = m_to_km(np.linalg.norm(true_velocities, axis=1))  # km/s
    ax6.plot(time, speeds, "m-", linewidth=2)
    ax6.set_xlabel("Time (minutes)")
    ax6.set_ylabel("Speed (km/s)")
    ax6.set_title("Orbital Speed")
    ax6.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("demo_results.png", dpi=150, bbox_inches="tight")
    print("Plots saved to demo_results.png")

    # Only show interactive plot if not using Agg backend
    if matplotlib.get_backend() != "Agg":
        print("Close the plot window to continue...")
        plt.show()
    else:
        plt.close()


if __name__ == "__main__":
    main()

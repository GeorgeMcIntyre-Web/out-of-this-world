"""Demo script: run a simple simulation scenario."""

import numpy as np

from outofthisworld.config import (
    DEFAULT_IMU_BIAS,
    DEFAULT_IMU_NOISE_STD,
)
from outofthisworld.estimation.kalman import ExtendedKalmanFilter
from outofthisworld.physics.constants import M_EARTH, R_EARTH, G
from outofthisworld.sensors.imu import IMU
from outofthisworld.sim.runner import SimulationRunner
from outofthisworld.sim.scenario import Scenario


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
    print(f"Initial altitude: {altitude / 1000:.1f} km")
    print(f"Orbital period: {period / 60:.1f} minutes")
    print(f"Time steps: {scenario.get_n_steps()}")
    print()

    # Create IMU sensor
    imu = IMU(
        bias=DEFAULT_IMU_BIAS,
        noise_std=DEFAULT_IMU_NOISE_STD,
        seed=42,
    )

    print(f"IMU bias: {DEFAULT_IMU_BIAS:.2e} m/s²")
    print(f"IMU noise std: {DEFAULT_IMU_NOISE_STD:.2e} m/s²")
    print()

    # Create EKF (simplified 2D state: position, velocity)
    # Note: This is a toy example - real implementation would be more sophisticated
    initial_state = np.concatenate([initial_position[:2], initial_velocity[:2]])
    initial_covariance = np.diag([1e6, 1e6, 100.0, 100.0])  # Large initial uncertainty
    process_noise = np.diag([1.0, 1.0, 0.1, 0.1])
    measurement_noise = np.array([[DEFAULT_IMU_NOISE_STD**2]])

    estimator = ExtendedKalmanFilter(
        initial_state=initial_state,
        initial_covariance=initial_covariance,
        process_noise=process_noise,
        measurement_noise=measurement_noise,
    )

    # Create runner
    runner = SimulationRunner(
        scenario=scenario,
        imu=imu,
        estimator=estimator,
    )

    # Run simulation
    print("Running simulation...")
    results = runner.run()
    print("Simulation complete.")
    print()

    # Analyze results
    true_states = results["true_states"]
    estimated_states = results.get("estimated_states")

    # Final state error
    final_true = true_states[-1]
    if estimated_states is not None:
        final_estimated = estimated_states[-1]

        # Position error (first 2 components)
        pos_error = np.linalg.norm(final_true[:2] - final_estimated[:2])
        print(f"Final position error: {pos_error / 1000:.2f} km")

        # Velocity error (components 3-4)
        vel_error = np.linalg.norm(final_true[2:4] - final_estimated[2:4])
        print(f"Final velocity error: {vel_error:.2f} m/s")
        print()

        # Estimated vs true bias
        true_bias = imu.get_bias()
        print(f"True IMU bias: {true_bias:.2e} m/s²")
        print(f"Initial IMU bias: {DEFAULT_IMU_BIAS:.2e} m/s²")
        print(f"Bias drift: {true_bias - DEFAULT_IMU_BIAS:.2e} m/s²")
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

    print("Demo complete.")


if __name__ == "__main__":
    main()

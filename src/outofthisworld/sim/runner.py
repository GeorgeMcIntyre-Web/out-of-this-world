"""Simulation runner: orchestrates physics, sensors, estimation."""

import numpy as np
from numpy.typing import NDArray

from outofthisworld.estimation.kalman import ExtendedKalmanFilter
from outofthisworld.physics.orbital import propagate_orbit
from outofthisworld.sensors.imu import IMU
from outofthisworld.sim.scenario import Scenario


class SimulationRunner:
    """
    Main simulation runner.

    Propagates orbit, generates sensor measurements, and runs estimation.
    """

    def __init__(
        self,
        scenario: Scenario,
        imu: IMU | None = None,
        estimator: ExtendedKalmanFilter | None = None,
    ) -> None:
        """
        Initialize simulation runner.

        Args:
            scenario: Simulation scenario
            imu: IMU sensor model (optional)
            estimator: State estimator (optional)
        """
        self.scenario = scenario
        self.imu = imu
        self.estimator = estimator

        # Storage for results
        self.true_states: list[NDArray[np.float64]] = []
        self.measurements: list[float] = []
        self.estimated_states: list[NDArray[np.float64]] = []
        self.estimated_covariances: list[NDArray[np.float64]] = []

    def run(self) -> dict[str, NDArray[np.float64]]:
        """
        Run simulation.

        Returns:
            Dictionary with results: 'true_states', 'measurements', 'estimated_states'
        """
        # Initialize
        position = self.scenario.initial_position.copy()
        velocity = self.scenario.initial_velocity.copy()
        dt = self.scenario.dt

        # Clear storage
        self.true_states.clear()
        self.measurements.clear()
        self.estimated_states.clear()
        self.estimated_covariances.clear()

        # Store initial state
        state = np.concatenate([position, velocity])
        self.true_states.append(state.copy())

        # Initialize estimator if provided
        if self.estimator is not None:
            self.estimated_states.append(self.estimator.state.copy())
            self.estimated_covariances.append(self.estimator.covariance.copy())

        # Main loop
        n_steps = self.scenario.get_n_steps()
        for step in range(n_steps):
            # Propagate orbit
            position, velocity = propagate_orbit(
                position,
                velocity,
                self.scenario.mu,
                dt,
                method="rk4",
            )

            # Compute true acceleration (for sensors)
            from outofthisworld.physics.orbital import two_body_acceleration

            true_accel = two_body_acceleration(position, self.scenario.mu)
            accel_magnitude = np.linalg.norm(true_accel)

            # Generate measurement
            if self.imu is not None:
                measurement = self.imu.measure(accel_magnitude, dt)
                self.measurements.append(float(measurement))

            # Update estimator
            if self.estimator is not None and self.imu is not None:
                self._update_estimator(measurement, dt)

            # Store state
            state = np.concatenate([position, velocity])
            self.true_states.append(state.copy())

            if self.estimator is not None:
                self.estimated_states.append(self.estimator.state.copy())
                self.estimated_covariances.append(self.estimator.covariance.copy())

        # Convert to arrays
        results: dict[str, NDArray[np.float64]] = {
            "true_states": np.array(self.true_states),
        }
        if self.measurements:
            results["measurements"] = np.array(self.measurements)
        if self.estimated_states:
            results["estimated_states"] = np.array(self.estimated_states)
        if self.estimated_covariances:
            results["estimated_covariances"] = np.array(self.estimated_covariances)

        return results

    def _update_estimator(
        self,
        measurement: float,
        dt: float,
    ) -> None:
        """Update EKF with new measurement (simplified case)."""
        if self.estimator is None:
            return

        # Get state dimension
        n = len(self.estimator.state)

        # Simplified: estimate position and velocity from acceleration measurement
        # This is a toy example - real implementation would be more sophisticated

        # Prediction: constant velocity model (works for any dimension >= 2)
        def f(x: NDArray[np.float64], _dt: float) -> NDArray[np.float64]:
            # x = [pos_x, pos_y, ..., vel_x, vel_y, ...]
            n_half = len(x) // 2
            new_pos = x[:n_half] + x[n_half:] * _dt
            new_vel = x[n_half:]
            return np.concatenate([new_pos, new_vel])

        # Jacobian: block matrix [[I, dt*I], [0, I]]
        n_half = n // 2
        I_half = np.eye(n_half)
        F = np.block([[I_half, dt * I_half], [np.zeros((n_half, n_half)), I_half]])

        self.estimator.predict(f, F, dt)

        # Update: measurement is acceleration magnitude
        # Simplified: relate to velocity magnitude (dummy model)
        def h(x: NDArray[np.float64]) -> NDArray[np.float64]:
            # This is a placeholder - in reality, we'd need to relate
            # measured acceleration to state
            n_half = len(x) // 2
            vel_mag = np.linalg.norm(x[n_half:])
            return np.array([vel_mag * 0.001])  # Dummy measurement model

        # Jacobian of h (simplified)
        n_half = n // 2
        H = np.zeros((1, n))
        if n_half > 0:
            # Approximate derivative (very simplified)
            vel_mag = np.linalg.norm(self.estimator.state[n_half:])
            if vel_mag > 1e-6:
                H[0, n_half:] = (
                    0.001 * self.estimator.state[n_half:] / vel_mag
                )  # Gradient of velocity magnitude

        z = np.array([measurement])
        self.estimator.update(z, h, H)

"""Simulation runner: orchestrates physics, sensors, estimation."""

import numpy as np
from numpy.typing import NDArray

from outofthisworld.estimation.gravity_measurements import GravityMeasurementModel
from outofthisworld.estimation.kalman import ExtendedKalmanFilter
from outofthisworld.physics.orbital import propagate_orbit, total_acceleration
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
        measurement_model: GravityMeasurementModel | None = None,
    ) -> None:
        """
        Initialize simulation runner.

        Args:
            scenario: Simulation scenario
            imu: IMU sensor model (optional, for legacy magnitude mode)
            estimator: State estimator (optional)
            measurement_model: Gravitational measurement model (optional)
        """
        self.scenario = scenario
        self.imu = imu
        self.estimator = estimator
        self.measurement_model = measurement_model

        # Storage for results
        self.true_states: list[NDArray[np.float64]] = []
        self.measurements: list[NDArray[np.float64] | float] = []
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
            # Get state dimension for measurement model
            n_half = len(self.estimator.state) // 2
        else:
            n_half = len(position)  # Full 3D if no estimator

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

            # Compute true acceleration
            true_accel = total_acceleration(position, self.scenario.mu)
            accel_magnitude = np.linalg.norm(true_accel)

            # Generate measurement
            if self.measurement_model is not None:
                # Use measurement model - use state dimension, not full 3D position
                # For 2D state, only use first 2 components of position
                state_for_measurement = np.concatenate([position[:n_half], velocity[:n_half]])
                true_measurement = self.measurement_model.predict_measurement(state_for_measurement)
                # Add noise
                noise_cov = self.measurement_model.measurement_noise_cov(len(state_for_measurement))
                noise = np.random.multivariate_normal(np.zeros(len(true_measurement)), noise_cov)
                measurement = true_measurement + noise
                self.measurements.append(measurement.copy())
            elif self.imu is not None:
                # Legacy: IMU magnitude measurement
                measurement = self.imu.measure(accel_magnitude, dt)
                self.measurements.append(float(measurement))

            # Update estimator
            if self.estimator is not None:
                if self.measurement_model is not None:
                    self._update_estimator_with_model(measurement, dt)
                elif self.imu is not None:
                    self._update_estimator_legacy(measurement, dt)

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
            # Convert measurements to array (handle mixed types)
            if isinstance(self.measurements[0], np.ndarray):
                results["measurements"] = np.array(self.measurements)
            else:
                results["measurements"] = np.array(self.measurements)
        if self.estimated_states:
            results["estimated_states"] = np.array(self.estimated_states)
        if self.estimated_covariances:
            results["estimated_covariances"] = np.array(self.estimated_covariances)

        return results

    def _update_estimator_with_model(
        self,
        measurement: NDArray[np.float64],
        dt: float,
    ) -> None:
        """Update EKF using measurement model."""
        if self.estimator is None or self.measurement_model is None:
            return

        n = len(self.estimator.state)
        n_half = n // 2

        # Prediction: constant velocity model with gravitational acceleration
        def f(x: NDArray[np.float64], _dt: float) -> NDArray[np.float64]:
            pos = x[:n_half]
            vel = x[n_half:]
            accel = total_acceleration(pos, self.scenario.mu)
            new_pos = pos + vel * _dt
            new_vel = vel + accel * _dt
            return np.concatenate([new_pos, new_vel])

        # Jacobian: F = [[I, dt*I], [d(accel)/d(pos), I]]
        I_half = np.eye(n_half)
        pos = self.estimator.state[:n_half]
        r = np.linalg.norm(pos)

        if r > 1e-6:
            mu = self.scenario.mu
            r3 = r * r * r
            r5 = r3 * r * r
            daccel_dpos = -mu / r3 * I_half + 3 * mu / r5 * np.outer(pos, pos)
        else:
            daccel_dpos = np.zeros((n_half, n_half))

        F = np.block([[I_half, dt * I_half], [dt * daccel_dpos, I_half]])
        self.estimator.predict(f, F, dt)

        # Update using measurement model
        def h(x: NDArray[np.float64]) -> NDArray[np.float64]:
            return self.measurement_model.predict_measurement(x)

        H = self.measurement_model.measurement_jacobian(self.estimator.state)

        # Ensure measurement is column vector
        if measurement.ndim == 1:
            z = measurement.reshape(-1, 1)
        else:
            z = measurement

        self.estimator.update(z, h, H)

    def _update_estimator_legacy(
        self,
        measurement: float,
        dt: float,
    ) -> None:
        """Update EKF with legacy acceleration magnitude measurement."""
        if self.estimator is None:
            return

        n = len(self.estimator.state)
        n_half = n // 2

        # Prediction: constant velocity model with gravitational acceleration
        def f(x: NDArray[np.float64], _dt: float) -> NDArray[np.float64]:
            pos = x[:n_half]
            vel = x[n_half:]
            accel = total_acceleration(pos, self.scenario.mu)
            new_pos = pos + vel * _dt
            new_vel = vel + accel * _dt
            return np.concatenate([new_pos, new_vel])

        # Jacobian: F = [[I, dt*I], [d(accel)/d(pos), I]]
        I_half = np.eye(n_half)
        pos = self.estimator.state[:n_half]
        r = np.linalg.norm(pos)

        if r > 1e-6:
            mu = self.scenario.mu
            r3 = r * r * r
            r5 = r3 * r * r
            daccel_dpos = -mu / r3 * I_half + 3 * mu / r5 * np.outer(pos, pos)
        else:
            daccel_dpos = np.zeros((n_half, n_half))

        F = np.block([[I_half, dt * I_half], [dt * daccel_dpos, I_half]])
        self.estimator.predict(f, F, dt)

        # Update: measurement is acceleration magnitude
        def h(x: NDArray[np.float64]) -> NDArray[np.float64]:
            pos = x[:n_half]
            accel = total_acceleration(pos, self.scenario.mu)
            return np.array([np.linalg.norm(accel)])

        # Jacobian of h
        pos = self.estimator.state[:n_half]
        accel = total_acceleration(pos, self.scenario.mu)
        accel_mag = np.linalg.norm(accel)

        if accel_mag > 1e-6:
            r = np.linalg.norm(pos)
            if r > 1e-6:
                mu = self.scenario.mu
                r3 = r * r * r
                r5 = r3 * r * r
                daccel_dpos = -mu / r3 * I_half + 3 * mu / r5 * np.outer(pos, pos)
            else:
                daccel_dpos = np.zeros((n_half, n_half))

            dnorm_daccel = accel / accel_mag
            dnorm_dpos = dnorm_daccel @ daccel_dpos
            H = np.concatenate([dnorm_dpos.reshape(1, -1), np.zeros((1, n_half))], axis=1)
        else:
            H = np.zeros((1, n))

        z = np.array([measurement])
        self.estimator.update(z, h, H)

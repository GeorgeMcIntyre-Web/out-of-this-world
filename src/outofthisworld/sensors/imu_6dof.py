"""6-DOF IMU sensor model with configurable noise profiles."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from outofthisworld.sensors.imu_profiles import CLASSICAL_IMU, IMUProfile


class IMU6DOF:
    """
    Six degree-of-freedom inertial measurement unit model.

    Models 3-axis accelerometer and 3-axis gyroscope with:
    - Turn-on bias (constant per run)
    - Bias instability (random walk)
    - White noise
    - Scale factor errors
    """

    def __init__(
        self,
        profile: IMUProfile = CLASSICAL_IMU,
        seed: int | None = None,
    ) -> None:
        """
        Initialize 6-DOF IMU.

        Args:
            profile: IMU noise/error profile specification
            seed: Random seed for reproducibility
        """
        self.profile = profile
        self.seed = seed
        self._rng = np.random.default_rng(seed)

        # Initialize turn-on biases (drawn from Gaussian)
        self._accel_bias = self._rng.normal(0.0, profile.accel_turn_on_bias, size=3)
        self._gyro_bias = self._rng.normal(0.0, profile.gyro_turn_on_bias, size=3)

        # Initialize scale factors (drawn from Gaussian around 1.0)
        self._accel_scale = 1.0 + self._rng.normal(0.0, profile.accel_scale_factor, size=3)
        self._gyro_scale = 1.0 + self._rng.normal(0.0, profile.gyro_scale_factor, size=3)

        # Store initial biases for reset
        self._initial_accel_bias = self._accel_bias.copy()
        self._initial_gyro_bias = self._gyro_bias.copy()

    def measure(
        self,
        true_accel: NDArray[np.float64],
        true_omega: NDArray[np.float64],
        dt: float,
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """
        Generate noisy 6-DOF measurement.

        Args:
            true_accel: True specific force [ax, ay, az] in m/s²
            true_omega: True angular velocity [ωx, ωy, ωz] in rad/s
            dt: Time step in seconds (for noise scaling)

        Returns:
            Tuple of (measured_accel, measured_omega)
        """
        # Update biases via random walk
        self._update_biases(dt)

        # Apply scale factor, bias, and white noise
        meas_accel = self._apply_errors(
            true_accel,
            self._accel_scale,
            self._accel_bias,
            self.profile.accel_white_noise,
            dt,
        )

        meas_omega = self._apply_errors(
            true_omega,
            self._gyro_scale,
            self._gyro_bias,
            self.profile.gyro_white_noise,
            dt,
        )

        return meas_accel, meas_omega

    def _update_biases(self, dt: float) -> None:
        """Update biases via random walk (bias instability)."""
        sqrt_dt = np.sqrt(dt)

        # Accelerometer bias random walk
        accel_walk = self._rng.normal(0.0, self.profile.accel_bias_instability * sqrt_dt, size=3)
        self._accel_bias = self._accel_bias + accel_walk

        # Gyroscope bias random walk
        gyro_walk = self._rng.normal(0.0, self.profile.gyro_bias_instability * sqrt_dt, size=3)
        self._gyro_bias = self._gyro_bias + gyro_walk

    def _apply_errors(
        self,
        true_value: NDArray[np.float64],
        scale: NDArray[np.float64],
        bias: NDArray[np.float64],
        white_noise_density: float,
        dt: float,
    ) -> NDArray[np.float64]:
        """Apply scale factor, bias, and white noise to measurement."""
        # Scale factor: y = (1 + s) * x ≈ scale * x
        scaled = scale * true_value

        # Add bias
        biased = scaled + bias

        # Add white noise (scaled by sqrt(1/dt) for proper spectral density)
        noise_std = white_noise_density * np.sqrt(1.0 / dt)
        noise = self._rng.normal(0.0, noise_std, size=3)

        return biased + noise

    def get_accel_bias(self) -> NDArray[np.float64]:
        """Get current accelerometer bias vector."""
        return self._accel_bias.copy()

    def get_gyro_bias(self) -> NDArray[np.float64]:
        """Get current gyroscope bias vector."""
        return self._gyro_bias.copy()

    def reset(self, seed: int | None = None) -> None:
        """
        Reset IMU to initial state.

        Args:
            seed: New random seed (optional, uses stored seed if None)
        """
        if seed is not None:
            self.seed = seed
        self._rng = np.random.default_rng(self.seed)

        # Re-draw turn-on biases
        self._accel_bias = self._rng.normal(0.0, self.profile.accel_turn_on_bias, size=3)
        self._gyro_bias = self._rng.normal(0.0, self.profile.gyro_turn_on_bias, size=3)

        # Re-draw scale factors
        self._accel_scale = 1.0 + self._rng.normal(0.0, self.profile.accel_scale_factor, size=3)
        self._gyro_scale = 1.0 + self._rng.normal(0.0, self.profile.gyro_scale_factor, size=3)

        self._initial_accel_bias = self._accel_bias.copy()
        self._initial_gyro_bias = self._gyro_bias.copy()

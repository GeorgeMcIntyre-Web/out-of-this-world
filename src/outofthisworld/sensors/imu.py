"""IMU sensor model: bias, noise, random walk."""

import numpy as np
from numpy.typing import NDArray

from outofthisworld.config import (
    DEFAULT_IMU_BIAS,
    DEFAULT_IMU_BIAS_STABILITY,
    DEFAULT_IMU_NOISE_STD,
)


class IMU:
    """
    Inertial Measurement Unit sensor model.

    Models accelerometer with bias, white noise, and bias instability (random walk).
    """

    def __init__(
        self,
        bias: float = DEFAULT_IMU_BIAS,
        noise_std: float = DEFAULT_IMU_NOISE_STD,
        bias_stability: float = DEFAULT_IMU_BIAS_STABILITY,
        seed: int | None = None,
    ) -> None:
        """
        Initialize IMU model.

        Args:
            bias: Initial bias (m/s^2)
            noise_std: White noise standard deviation (m/s^2)
            bias_stability: Bias random walk step size (m/s^2 per sqrt(second))
            seed: Random seed for reproducibility
        """
        self.bias = bias
        self.noise_std = noise_std
        self.bias_stability = bias_stability
        self.seed = seed
        self._rng = np.random.default_rng(seed)
        self._current_bias = float(bias)

    def measure(
        self,
        true_acceleration: float | NDArray[np.float64],
        dt: float = 1.0,
    ) -> float | NDArray[np.float64]:
        """
        Generate noisy acceleration measurement.

        Args:
            true_acceleration: True acceleration (m/s^2)
            dt: Time step (seconds) for bias drift

        Returns:
            Measured acceleration with bias and noise
        """
        # Update bias (random walk)
        bias_step = self._rng.normal(0.0, self.bias_stability * np.sqrt(dt))
        self._current_bias += bias_step

        # Add white noise
        if isinstance(true_acceleration, np.ndarray):
            noise = self._rng.normal(0.0, self.noise_std, size=true_acceleration.shape)
        else:
            noise = self._rng.normal(0.0, self.noise_std)

        return true_acceleration + self._current_bias + noise

    def get_bias(self) -> float:
        """Get current bias value."""
        return self._current_bias

    def reset(self, seed: int | None = None) -> None:
        """
        Reset IMU to initial state.

        Args:
            seed: New random seed (optional)
        """
        self._current_bias = float(self.bias)
        if seed is not None:
            self.seed = seed
            self._rng = np.random.default_rng(seed)

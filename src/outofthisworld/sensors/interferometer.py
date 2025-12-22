"""Atom interferometer sensor model (simplified)."""

import numpy as np
from numpy.typing import NDArray

from outofthisworld.config import (
    DEFAULT_INTERFEROMETER_NOISE_STD,
    DEFAULT_INTERFEROMETER_SENSITIVITY,
)


class Interferometer:
    """
    Simplified atom interferometer model.

    Maps acceleration to phase measurement. This is a highly simplified model
    intended for simulation only. Real atom interferometers involve complex
    physics (Raman transitions, matter-wave interference, etc.).
    """

    def __init__(
        self,
        sensitivity: float = DEFAULT_INTERFEROMETER_SENSITIVITY,
        noise_std: float = DEFAULT_INTERFEROMETER_NOISE_STD,
        seed: int | None = None,
    ) -> None:
        """
        Initialize interferometer model.

        Args:
            sensitivity: Acceleration sensitivity (m/s^2 per radian phase)
            noise_std: Phase measurement noise standard deviation (radians)
            seed: Random seed for reproducibility
        """
        self.sensitivity = sensitivity
        self.noise_std = noise_std
        self.seed = seed
        self._rng = np.random.default_rng(seed)

    def measure_phase(
        self,
        acceleration: float | NDArray[np.float64],
    ) -> float | NDArray[np.float64]:
        """
        Generate phase measurement from acceleration.

        Simplified model: phase = acceleration / sensitivity + noise

        Args:
            acceleration: True acceleration (m/s^2)

        Returns:
            Measured phase (radians)
        """
        phase_signal = acceleration / self.sensitivity

        if isinstance(acceleration, np.ndarray):
            noise = self._rng.normal(0.0, self.noise_std, size=acceleration.shape)
        else:
            noise = self._rng.normal(0.0, self.noise_std)

        return phase_signal + noise

    def phase_to_acceleration(
        self,
        phase: float | NDArray[np.float64],
    ) -> float | NDArray[np.float64]:
        """
        Convert phase measurement back to acceleration estimate.

        Args:
            phase: Measured phase (radians)

        Returns:
            Estimated acceleration (m/s^2)
        """
        return phase * self.sensitivity

    def reset(self, seed: int | None = None) -> None:
        """
        Reset interferometer (mainly for random seed).

        Args:
            seed: New random seed (optional)
        """
        if seed is not None:
            self.seed = seed
            self._rng = np.random.default_rng(seed)

"""Star tracker sensor model for attitude measurements."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np
from numpy.typing import NDArray

# Conversion constants
ARCSEC_TO_RAD: Final[float] = 4.848136811095360e-6  # arcsec to radians


@dataclass(frozen=True)
class StarTrackerConfig:
    """Star tracker configuration parameters."""

    accuracy_arcsec: float  # 1-σ attitude accuracy per axis (arcsec)
    update_rate_hz: float  # Measurement rate (Hz)
    fov_deg: float  # Field of view (degrees)
    name: str = "default"

    @property
    def accuracy_rad(self) -> float:
        """Accuracy in radians."""
        return self.accuracy_arcsec * ARCSEC_TO_RAD

    @property
    def update_period_s(self) -> float:
        """Update period in seconds."""
        return 1.0 / self.update_rate_hz


# Standard star tracker (representative of flight-proven systems)
STANDARD_STAR_TRACKER: Final[StarTrackerConfig] = StarTrackerConfig(
    accuracy_arcsec=5.0,  # 5 arcsec (typical for high-accuracy trackers)
    update_rate_hz=10.0,  # 10 Hz update rate
    fov_deg=20.0,  # 20° field of view
    name="standard",
)

# High-accuracy star tracker
HIGH_ACCURACY_STAR_TRACKER: Final[StarTrackerConfig] = StarTrackerConfig(
    accuracy_arcsec=1.0,  # 1 arcsec (high-end tracker)
    update_rate_hz=20.0,  # 20 Hz
    fov_deg=15.0,
    name="high_accuracy",
)


class StarTracker:
    """
    Star tracker attitude sensor model.

    Provides noisy attitude measurements simulating a star tracker
    that determines spacecraft orientation from star field observations.
    """

    def __init__(
        self,
        config: StarTrackerConfig = STANDARD_STAR_TRACKER,
        seed: int | None = None,
    ) -> None:
        """
        Initialize star tracker.

        Args:
            config: Star tracker configuration
            seed: Random seed for reproducibility
        """
        self.config = config
        self.seed = seed
        self._rng = np.random.default_rng(seed)
        self._last_measurement_time: float = -float("inf")

    def measure(
        self,
        true_attitude: NDArray[np.float64],
        time: float,
    ) -> NDArray[np.float64] | None:
        """
        Generate noisy attitude measurement if update is available.

        The attitude is represented as a 3-element rotation vector (Rodrigues)
        or Euler angles (roll, pitch, yaw) depending on convention used.

        Args:
            true_attitude: True attitude [θx, θy, θz] in radians
            time: Current simulation time in seconds

        Returns:
            Measured attitude with noise, or None if no update available
        """
        # Check if measurement is available based on update rate
        time_since_last = time - self._last_measurement_time
        if time_since_last < self.config.update_period_s:
            return None

        self._last_measurement_time = time

        # Add Gaussian noise to each axis
        noise = self._rng.normal(0.0, self.config.accuracy_rad, size=3)
        return true_attitude + noise

    def force_measure(
        self,
        true_attitude: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        """
        Generate measurement regardless of update rate.

        Useful for initialization or testing.

        Args:
            true_attitude: True attitude [θx, θy, θz] in radians

        Returns:
            Measured attitude with noise
        """
        noise = self._rng.normal(0.0, self.config.accuracy_rad, size=3)
        return true_attitude + noise

    def is_available(self, time: float) -> bool:
        """
        Check if a measurement is available at given time.

        Args:
            time: Current simulation time in seconds

        Returns:
            True if enough time has passed for a new measurement
        """
        return (time - self._last_measurement_time) >= self.config.update_period_s

    def get_measurement_noise_cov(self) -> NDArray[np.float64]:
        """
        Get measurement noise covariance matrix.

        Returns:
            3x3 diagonal covariance matrix (rad²)
        """
        variance = self.config.accuracy_rad**2
        return np.diag([variance, variance, variance])

    def reset(self, seed: int | None = None) -> None:
        """
        Reset star tracker state.

        Args:
            seed: New random seed (optional)
        """
        if seed is not None:
            self.seed = seed
        self._rng = np.random.default_rng(self.seed)
        self._last_measurement_time = -float("inf")


def get_star_tracker_config(name: str) -> StarTrackerConfig:
    """
    Get star tracker configuration by name.

    Args:
        name: Configuration name ('standard' or 'high_accuracy')

    Returns:
        StarTrackerConfig

    Raises:
        ValueError: If name not recognized
    """
    configs = {
        "standard": STANDARD_STAR_TRACKER,
        "high_accuracy": HIGH_ACCURACY_STAR_TRACKER,
    }
    if name not in configs:
        valid = ", ".join(configs.keys())
        raise ValueError(f"Unknown star tracker config '{name}'. Valid: {valid}")
    return configs[name]

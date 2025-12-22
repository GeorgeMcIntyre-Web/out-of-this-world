"""Scenario definition: initial conditions, parameters."""

import numpy as np
from numpy.typing import NDArray


class Scenario:
    """
    Simulation scenario definition.

    Contains initial conditions, physical parameters, and simulation settings.
    """

    def __init__(
        self,
        initial_position: NDArray[np.float64],
        initial_velocity: NDArray[np.float64],
        mu: float,
        duration: float,
        dt: float = 1.0,
        name: str = "default",
    ) -> None:
        """
        Initialize scenario.

        Args:
            initial_position: Initial position [x, y, z] in meters
            initial_velocity: Initial velocity [vx, vy, vz] in m/s
            mu: Gravitational parameter (G * M) in m^3/s^2
            duration: Simulation duration in seconds
            dt: Time step in seconds
            name: Scenario name
        """
        self.initial_position = initial_position.copy()
        self.initial_velocity = initial_velocity.copy()
        self.mu = mu
        self.duration = duration
        self.dt = dt
        self.name = name

    def get_n_steps(self) -> int:
        """Get number of time steps."""
        return int(self.duration / self.dt)

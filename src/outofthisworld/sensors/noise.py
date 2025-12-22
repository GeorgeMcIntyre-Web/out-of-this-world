"""Noise generators: white noise, random walk, colored noise."""

import numpy as np
from numpy.typing import NDArray


def generate_white_noise(
    size: int | tuple[int, ...],
    std: float,
    seed: int | None = None,
) -> NDArray[np.float64]:
    """
    Generate white (uncorrelated) Gaussian noise.

    Args:
        size: Output shape
        std: Standard deviation
        seed: Random seed (optional)

    Returns:
        Noise array
    """
    if seed is not None:
        rng = np.random.default_rng(seed)
    else:
        rng = np.random.default_rng()

    return rng.normal(0.0, std, size=size)


def generate_random_walk(
    n_steps: int,
    step_std: float,
    initial_value: float = 0.0,
    seed: int | None = None,
) -> NDArray[np.float64]:
    """
    Generate random walk (integrated white noise).

    Args:
        n_steps: Number of steps
        step_std: Standard deviation of each step
        initial_value: Starting value
        seed: Random seed (optional)

    Returns:
        Random walk array of length n_steps
    """
    if seed is not None:
        rng = np.random.default_rng(seed)
    else:
        rng = np.random.default_rng()

    steps = rng.normal(0.0, step_std, size=n_steps)
    walk = np.zeros(n_steps)
    walk[0] = initial_value
    if n_steps > 1:
        walk[1:] = initial_value + np.cumsum(steps[1:])
    return walk

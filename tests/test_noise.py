"""Tests for noise generators."""

import numpy as np

from outofthisworld.sensors.noise import generate_random_walk, generate_white_noise


def test_white_noise_shape() -> None:
    """Test white noise has correct shape."""
    noise = generate_white_noise((10,), 1.0, seed=42)
    assert noise.shape == (10,)


def test_white_noise_statistics() -> None:
    """Test white noise has approximately correct statistics."""
    noise = generate_white_noise((10000,), 2.0, seed=42)
    std = np.std(noise)
    assert abs(std - 2.0) < 0.1  # Allow some variance


def test_random_walk_length() -> None:
    """Test random walk has correct length."""
    walk = generate_random_walk(100, 0.1, seed=42)
    assert len(walk) == 100


def test_random_walk_initial_value() -> None:
    """Test random walk starts at initial value."""
    walk = generate_random_walk(10, 0.1, initial_value=5.0, seed=42)
    assert abs(walk[0] - 5.0) < 1e-10


def test_random_walk_drift() -> None:
    """Test random walk shows drift (non-zero final value likely)."""
    walk = generate_random_walk(1000, 0.1, seed=42)
    # Random walk should drift away from zero
    assert abs(walk[-1]) > 0.01  # Very likely to be non-zero

"""Tests for Kalman filter implementations."""

import numpy as np

from outofthisworld.estimation.kalman import ExtendedKalmanFilter, KalmanFilter


def test_kalman_filter_initialization() -> None:
    """Test Kalman filter initializes correctly."""
    x0 = np.array([1.0, 2.0])
    P0 = np.eye(2)
    Q = 0.1 * np.eye(2)
    R = 0.5 * np.eye(1)

    kf = KalmanFilter(x0, P0, Q, R)
    assert np.allclose(kf.state, x0)
    assert np.allclose(kf.covariance, P0)


def test_kalman_filter_predict() -> None:
    """Test Kalman filter prediction step."""
    x0 = np.array([1.0, 1.0])  # Non-zero velocity
    P0 = np.eye(2)
    Q = 0.1 * np.eye(2)
    R = 0.5 * np.eye(1)

    kf = KalmanFilter(x0, P0, Q, R)

    F = np.array([[1.0, 1.0], [0.0, 1.0]])  # Constant velocity model
    kf.predict(F)

    # State should update (position changes due to velocity)
    assert not np.allclose(kf.state, x0)
    # Covariance should increase
    assert np.trace(kf.covariance) > np.trace(P0)


def test_kalman_filter_update() -> None:
    """Test Kalman filter update step."""
    x0 = np.array([1.0, 0.0])
    P0 = np.eye(2)
    Q = 0.1 * np.eye(2)
    R = 0.5 * np.eye(1)

    kf = KalmanFilter(x0, P0, Q, R)

    H = np.array([[1.0, 0.0]])  # Measure first state
    z = np.array([2.0])  # Measurement

    kf.update(z, H)

    # State should move toward measurement
    assert kf.state[0] > x0[0]
    # Covariance should decrease
    assert kf.covariance[0, 0] < P0[0, 0]


def test_ekf_initialization() -> None:
    """Test EKF initializes correctly."""
    x0 = np.array([1.0, 2.0])
    P0 = np.eye(2)
    Q = 0.1 * np.eye(2)
    R = 0.5 * np.eye(1)

    ekf = ExtendedKalmanFilter(x0, P0, Q, R)
    assert np.allclose(ekf.state, x0)
    assert np.allclose(ekf.covariance, P0)


def test_ekf_predict() -> None:
    """Test EKF prediction with nonlinear dynamics."""
    x0 = np.array([1.0, 1.0])  # Non-zero velocity
    P0 = np.eye(2)
    Q = 0.1 * np.eye(2)
    R = 0.5 * np.eye(1)

    ekf = ExtendedKalmanFilter(x0, P0, Q, R)

    def f(x: np.ndarray, dt: float) -> np.ndarray:
        return np.array([x[0] + x[1] * dt, x[1]])

    F = np.array([[1.0, 1.0], [0.0, 1.0]])  # Jacobian
    ekf.predict(f, F, dt=1.0)

    # State should update (position changes due to velocity)
    assert not np.allclose(ekf.state, x0)

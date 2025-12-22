"""Kalman filter implementations: linear and extended."""

import numpy as np
from numpy.typing import NDArray


class KalmanFilter:
    """
    Linear Kalman filter for state estimation.

    Assumes linear dynamics and measurements.
    """

    def __init__(
        self,
        initial_state: NDArray[np.float64],
        initial_covariance: NDArray[np.float64],
        process_noise: NDArray[np.float64],
        measurement_noise: NDArray[np.float64],
    ) -> None:
        """
        Initialize Kalman filter.

        Args:
            initial_state: Initial state estimate (n x 1)
            initial_covariance: Initial covariance matrix (n x n)
            process_noise: Process noise covariance (n x n)
            measurement_noise: Measurement noise covariance (m x m)
        """
        self.state = initial_state.copy()
        self.covariance = initial_covariance.copy()
        self.Q = process_noise.copy()  # Process noise
        self.R = measurement_noise.copy()  # Measurement noise

    def predict(
        self,
        F: NDArray[np.float64],
        B: NDArray[np.float64] | None = None,
        u: NDArray[np.float64] | None = None,
    ) -> None:
        """
        Prediction step.

        Args:
            F: State transition matrix (n x n)
            B: Control input matrix (n x p), optional
            u: Control input (p x 1), optional
        """
        # State prediction
        self.state = F @ self.state
        if B is not None and u is not None:
            self.state = self.state + B @ u

        # Covariance prediction
        self.covariance = F @ self.covariance @ F.T + self.Q

    def update(
        self,
        z: NDArray[np.float64],
        H: NDArray[np.float64],
    ) -> None:
        """
        Update step.

        Args:
            z: Measurement (m x 1)
            H: Measurement matrix (m x n)
        """
        # Innovation
        y = z - H @ self.state

        # Innovation covariance
        S = H @ self.covariance @ H.T + self.R

        # Kalman gain
        K = self.covariance @ H.T @ np.linalg.inv(S)

        # State update
        self.state = self.state + K @ y

        # Covariance update (Joseph form for numerical stability)
        I = np.eye(self.covariance.shape[0])
        self.covariance = (I - K @ H) @ self.covariance


class ExtendedKalmanFilter:
    """
    Extended Kalman filter for nonlinear systems.

    Linearizes dynamics and measurements around current state estimate.
    """

    def __init__(
        self,
        initial_state: NDArray[np.float64],
        initial_covariance: NDArray[np.float64],
        process_noise: NDArray[np.float64],
        measurement_noise: NDArray[np.float64],
    ) -> None:
        """
        Initialize EKF.

        Args:
            initial_state: Initial state estimate (n x 1)
            initial_covariance: Initial covariance matrix (n x n)
            process_noise: Process noise covariance (n x n)
            measurement_noise: Measurement noise covariance (m x m)
        """
        self.state = initial_state.copy()
        self.covariance = initial_covariance.copy()
        self.Q = process_noise.copy()
        self.R = measurement_noise.copy()

    def predict(
        self,
        f: callable,
        F: NDArray[np.float64],
        dt: float,
    ) -> None:
        """
        Prediction step with nonlinear dynamics.

        Args:
            f: Nonlinear state transition function: x_new = f(x, dt)
            F: Jacobian of f with respect to state (n x n)
            dt: Time step
        """
        # State prediction (nonlinear)
        self.state = f(self.state, dt)

        # Covariance prediction (linearized)
        self.covariance = F @ self.covariance @ F.T + self.Q

    def update(
        self,
        z: NDArray[np.float64],
        h: callable,
        H: NDArray[np.float64],
    ) -> None:
        """
        Update step with nonlinear measurements.

        Args:
            z: Measurement (m x 1)
            h: Nonlinear measurement function: z_pred = h(x)
            H: Jacobian of h with respect to state (m x n)
        """
        # Predicted measurement
        z_pred = h(self.state)

        # Innovation
        # Ensure both are column vectors
        if z.ndim == 1:
            z = z.reshape(-1, 1)
        if z_pred.ndim == 1:
            z_pred = z_pred.reshape(-1, 1)
        y = z - z_pred

        # Innovation covariance
        S = H @ self.covariance @ H.T + self.R

        # Kalman gain
        K = self.covariance @ H.T @ np.linalg.inv(S)

        # State update
        self.state = self.state + (K @ y).flatten()

        # Covariance update
        I = np.eye(self.covariance.shape[0])
        self.covariance = (I - K @ H) @ self.covariance

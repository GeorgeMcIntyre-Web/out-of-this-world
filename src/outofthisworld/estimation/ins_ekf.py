"""15-state Inertial Navigation System Extended Kalman Filter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np
from numpy.typing import NDArray

from outofthisworld.sensors.imu_profiles import IMUProfile

# State indices
POS_IDX: Final[slice] = slice(0, 3)  # Position [0:3]
VEL_IDX: Final[slice] = slice(3, 6)  # Velocity [3:6]
ATT_IDX: Final[slice] = slice(6, 9)  # Attitude [6:9]
ACC_BIAS_IDX: Final[slice] = slice(9, 12)  # Accel bias [9:12]
GYR_BIAS_IDX: Final[slice] = slice(12, 15)  # Gyro bias [12:15]

STATE_DIM: Final[int] = 15


@dataclass
class INSState:
    """Navigation state container."""

    position: NDArray[np.float64]  # [x, y, z] in meters
    velocity: NDArray[np.float64]  # [vx, vy, vz] in m/s
    attitude: NDArray[np.float64]  # [θx, θy, θz] rotation vector in rad
    accel_bias: NDArray[np.float64]  # [bax, bay, baz] in m/s²
    gyro_bias: NDArray[np.float64]  # [bωx, bωy, bωz] in rad/s

    def to_vector(self) -> NDArray[np.float64]:
        """Convert to 15-element state vector."""
        return np.concatenate(
            [
                self.position,
                self.velocity,
                self.attitude,
                self.accel_bias,
                self.gyro_bias,
            ]
        )

    @classmethod
    def from_vector(cls, x: NDArray[np.float64]) -> INSState:
        """Create from 15-element state vector."""
        return cls(
            position=x[POS_IDX].copy(),
            velocity=x[VEL_IDX].copy(),
            attitude=x[ATT_IDX].copy(),
            accel_bias=x[ACC_BIAS_IDX].copy(),
            gyro_bias=x[GYR_BIAS_IDX].copy(),
        )


def skew(v: NDArray[np.float64]) -> NDArray[np.float64]:
    """Create skew-symmetric matrix from 3-vector."""
    return np.array(
        [
            [0.0, -v[2], v[1]],
            [v[2], 0.0, -v[0]],
            [-v[1], v[0], 0.0],
        ]
    )


def rotation_matrix(theta: NDArray[np.float64]) -> NDArray[np.float64]:
    """
    Compute rotation matrix from rotation vector (Rodrigues formula).

    For small angles, R ≈ I + [θ×].
    """
    angle = np.linalg.norm(theta)
    if angle < 1e-10:
        return np.eye(3)

    axis = theta / angle
    K = skew(axis)
    return np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)


class INSEKF:
    """
    Inertial Navigation System Extended Kalman Filter.

    15-state error-state EKF for integrated IMU navigation with aiding sensors.

    State vector: [position, velocity, attitude, accel_bias, gyro_bias]
    """

    def __init__(
        self,
        initial_state: INSState,
        initial_covariance: NDArray[np.float64],
        imu_profile: IMUProfile,
    ) -> None:
        """
        Initialize INS EKF.

        Args:
            initial_state: Initial navigation state
            initial_covariance: Initial 15x15 covariance matrix
            imu_profile: IMU noise profile for process noise
        """
        self.state = initial_state
        self.covariance = initial_covariance.copy()
        self.imu_profile = imu_profile

        # Build process noise from IMU profile
        self._build_process_noise()

    def _build_process_noise(self) -> None:
        """Construct process noise spectral density matrix."""
        # Continuous-time process noise spectral density
        # Q_c = diag(0, 0, 0, σ²_na, σ²_na, σ²_na, σ²_nω, σ²_nω, σ²_nω,
        #            σ²_ba, σ²_ba, σ²_ba, σ²_bω, σ²_bω, σ²_bω)
        self.Q_spectral = np.diag(
            [
                0.0,
                0.0,
                0.0,  # Position (no direct noise)
                self.imu_profile.accel_white_noise**2,  # Velocity x
                self.imu_profile.accel_white_noise**2,  # Velocity y
                self.imu_profile.accel_white_noise**2,  # Velocity z
                self.imu_profile.gyro_white_noise**2,  # Attitude x
                self.imu_profile.gyro_white_noise**2,  # Attitude y
                self.imu_profile.gyro_white_noise**2,  # Attitude z
                self.imu_profile.accel_bias_instability**2,  # Accel bias x
                self.imu_profile.accel_bias_instability**2,  # Accel bias y
                self.imu_profile.accel_bias_instability**2,  # Accel bias z
                self.imu_profile.gyro_bias_instability**2,  # Gyro bias x
                self.imu_profile.gyro_bias_instability**2,  # Gyro bias y
                self.imu_profile.gyro_bias_instability**2,  # Gyro bias z
            ]
        )

    def predict(
        self,
        accel_meas: NDArray[np.float64],
        omega_meas: NDArray[np.float64],
        dt: float,
    ) -> None:
        """
        IMU mechanization and covariance propagation.

        Args:
            accel_meas: Measured specific force [ax, ay, az] in m/s²
            omega_meas: Measured angular velocity [ωx, ωy, ωz] in rad/s
            dt: Time step in seconds
        """
        # Bias-corrected measurements
        accel_corr = accel_meas - self.state.accel_bias
        omega_corr = omega_meas - self.state.gyro_bias

        # Current rotation matrix (body to nav)
        C_bn = rotation_matrix(self.state.attitude)

        # --- State propagation (nonlinear) ---

        # Attitude update (first-order integration)
        delta_theta = omega_corr * dt
        self.state.attitude = self.state.attitude + delta_theta

        # Velocity update (nav frame acceleration)
        accel_nav = C_bn @ accel_corr
        self.state.velocity = self.state.velocity + accel_nav * dt

        # Position update
        self.state.position = self.state.position + self.state.velocity * dt

        # Biases: constant (random walk handled via process noise)
        # No explicit update needed

        # --- Covariance propagation (linearized) ---

        # State transition matrix (first-order approximation)
        F = self._compute_state_transition(accel_corr, C_bn, dt)

        # Discrete process noise
        Q_d = self.Q_spectral * dt

        # Covariance propagation
        self.covariance = F @ self.covariance @ F.T + Q_d

        # Ensure symmetry
        self.covariance = 0.5 * (self.covariance + self.covariance.T)

    def _compute_state_transition(
        self,
        accel_corr: NDArray[np.float64],
        C_bn: NDArray[np.float64],
        dt: float,
    ) -> NDArray[np.float64]:
        """Compute linearized state transition matrix."""
        F = np.eye(STATE_DIM)

        # Position from velocity
        F[POS_IDX, VEL_IDX] = np.eye(3) * dt

        # Velocity from attitude (cross product with acceleration)
        F[VEL_IDX, ATT_IDX] = -C_bn @ skew(accel_corr) * dt

        # Velocity from accel bias
        F[VEL_IDX, ACC_BIAS_IDX] = -C_bn * dt

        # Attitude from gyro bias
        F[ATT_IDX, GYR_BIAS_IDX] = -np.eye(3) * dt

        return F

    def update_attitude(
        self,
        attitude_meas: NDArray[np.float64],
        R: NDArray[np.float64],
    ) -> None:
        """
        Update filter with attitude measurement (e.g., from star tracker).

        Args:
            attitude_meas: Measured attitude [θx, θy, θz] in radians
            R: 3x3 measurement noise covariance
        """
        # Measurement matrix: H extracts attitude from state
        H = np.zeros((3, STATE_DIM))
        H[:, ATT_IDX] = np.eye(3)

        # Innovation
        z_pred = self.state.attitude
        y = attitude_meas - z_pred

        # --- Standard Kalman update ---
        self._kalman_update(y, H, R)

    def update_position(
        self,
        position_meas: NDArray[np.float64],
        R: NDArray[np.float64],
    ) -> None:
        """
        Update filter with position measurement (e.g., from GPS).

        Args:
            position_meas: Measured position [x, y, z] in meters
            R: 3x3 measurement noise covariance
        """
        H = np.zeros((3, STATE_DIM))
        H[:, POS_IDX] = np.eye(3)

        z_pred = self.state.position
        y = position_meas - z_pred

        self._kalman_update(y, H, R)

    def _kalman_update(
        self,
        innovation: NDArray[np.float64],
        H: NDArray[np.float64],
        R: NDArray[np.float64],
    ) -> None:
        """Perform standard Kalman filter measurement update."""
        # Innovation covariance
        S = H @ self.covariance @ H.T + R

        # Kalman gain
        K = self.covariance @ H.T @ np.linalg.inv(S)

        # State correction
        dx = K @ innovation
        self._apply_correction(dx)

        # Covariance update (Joseph form for numerical stability)
        I_KH = np.eye(STATE_DIM) - K @ H
        self.covariance = I_KH @ self.covariance @ I_KH.T + K @ R @ K.T

        # Ensure symmetry
        self.covariance = 0.5 * (self.covariance + self.covariance.T)

    def _apply_correction(self, dx: NDArray[np.float64]) -> None:
        """Apply error-state correction to nominal state."""
        self.state.position = self.state.position + dx[POS_IDX]
        self.state.velocity = self.state.velocity + dx[VEL_IDX]
        self.state.attitude = self.state.attitude + dx[ATT_IDX]
        self.state.accel_bias = self.state.accel_bias + dx[ACC_BIAS_IDX]
        self.state.gyro_bias = self.state.gyro_bias + dx[GYR_BIAS_IDX]

    def get_position_uncertainty(self) -> NDArray[np.float64]:
        """Get 1-σ position uncertainty per axis."""
        return np.sqrt(np.diag(self.covariance[POS_IDX, POS_IDX]))

    def get_velocity_uncertainty(self) -> NDArray[np.float64]:
        """Get 1-σ velocity uncertainty per axis."""
        return np.sqrt(np.diag(self.covariance[VEL_IDX, VEL_IDX]))

    def get_attitude_uncertainty(self) -> NDArray[np.float64]:
        """Get 1-σ attitude uncertainty per axis (radians)."""
        return np.sqrt(np.diag(self.covariance[ATT_IDX, ATT_IDX]))

    def get_state_vector(self) -> NDArray[np.float64]:
        """Get full 15-element state vector."""
        return self.state.to_vector()


def create_default_initial_covariance(
    pos_sigma: float = 10.0,
    vel_sigma: float = 0.1,
    att_sigma: float = 0.01,
    accel_bias_sigma: float = 1e-4,
    gyro_bias_sigma: float = 1e-5,
) -> NDArray[np.float64]:
    """
    Create default initial covariance matrix.

    Args:
        pos_sigma: Position uncertainty (m)
        vel_sigma: Velocity uncertainty (m/s)
        att_sigma: Attitude uncertainty (rad)
        accel_bias_sigma: Accel bias uncertainty (m/s²)
        gyro_bias_sigma: Gyro bias uncertainty (rad/s)

    Returns:
        15x15 diagonal covariance matrix
    """
    return np.diag(
        [
            pos_sigma**2,
            pos_sigma**2,
            pos_sigma**2,
            vel_sigma**2,
            vel_sigma**2,
            vel_sigma**2,
            att_sigma**2,
            att_sigma**2,
            att_sigma**2,
            accel_bias_sigma**2,
            accel_bias_sigma**2,
            accel_bias_sigma**2,
            gyro_bias_sigma**2,
            gyro_bias_sigma**2,
            gyro_bias_sigma**2,
        ]
    )

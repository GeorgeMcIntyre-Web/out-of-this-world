"""Gravitational measurement models for estimation."""

import numpy as np
from numpy.typing import NDArray

from outofthisworld.estimation.measurement_types import MeasurementType
from outofthisworld.physics.orbital import total_acceleration


class GravityMeasurementModel:
    """
    Gravitational measurement model for EKF.

    Supports multiple measurement modes: magnitude or vector.
    """

    def __init__(
        self,
        measurement_type: MeasurementType,
        mu: float,
        noise_std: float | NDArray[np.float64],
        j2: float | None = None,
        r_eq: float | None = None,
    ) -> None:
        """
        Initialize measurement model.

        Args:
            measurement_type: Type of measurement (magnitude or vector)
            mu: Gravitational parameter (G * M)
            noise_std: Measurement noise standard deviation
                - Scalar for magnitude mode
                - Vector or scalar for vector mode (if scalar, applied to each component)
            j2: J2 coefficient (optional)
            r_eq: Equatorial radius for J2 (required if j2 provided)
        """
        self.measurement_type = measurement_type
        self.mu = mu
        self.j2 = j2
        self.r_eq = r_eq

        if measurement_type == MeasurementType.GRAVITY_MAGNITUDE:
            if isinstance(noise_std, np.ndarray):
                if noise_std.size != 1:
                    raise ValueError("Magnitude mode requires scalar noise_std")
                self.noise_std = float(noise_std[0])
            else:
                self.noise_std = float(noise_std)
            self.measurement_dim = 1
        elif measurement_type == MeasurementType.GRAVITY_VECTOR_INERTIAL:
            if isinstance(noise_std, np.ndarray):
                if noise_std.ndim == 0:
                    self.noise_std = float(noise_std)
                elif noise_std.ndim == 1:
                    self.noise_std = noise_std.copy()
                else:
                    raise ValueError("Vector mode requires 1D noise_std array or scalar")
            else:
                self.noise_std = float(noise_std)
            # Measurement dimension matches position dimension (2D or 3D)
            self.measurement_dim = None  # Will be determined from state
        else:
            raise ValueError(f"Unknown measurement type: {measurement_type}")

    def predict_measurement(self, state: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        Predict measurement from state.

        Args:
            state: State vector [position, velocity]

        Returns:
            Predicted measurement
        """
        n = len(state)
        n_half = n // 2
        pos = state[:n_half]

        accel = total_acceleration(pos, self.mu, self.j2, self.r_eq)

        if self.measurement_type == MeasurementType.GRAVITY_MAGNITUDE:
            return np.array([np.linalg.norm(accel)])
        if self.measurement_type == MeasurementType.GRAVITY_VECTOR_INERTIAL:
            return accel.copy()

        raise ValueError(f"Unknown measurement type: {self.measurement_type}")

    def measurement_jacobian(self, state: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        Compute measurement Jacobian.

        Args:
            state: State vector [position, velocity]

        Returns:
            Jacobian matrix H (measurement_dim x state_dim)
        """
        n = len(state)
        n_half = n // 2
        pos = state[:n_half]
        r = np.linalg.norm(pos)

        if self.measurement_type == MeasurementType.GRAVITY_MAGNITUDE:
            # h(x) = ||a(r)||
            # H = [d(||a||)/d(pos), 0]
            accel = total_acceleration(pos, self.mu, self.j2, self.r_eq)
            accel_mag = np.linalg.norm(accel)

            if accel_mag < 1e-6:
                return np.zeros((1, n))

            # d(||a||)/d(pos) = (a^T / ||a||) * d(a)/d(pos)
            daccel_dpos = self._acceleration_jacobian(pos, r)
            dnorm_daccel = accel / accel_mag
            dnorm_dpos = dnorm_daccel @ daccel_dpos

            H = np.concatenate([dnorm_dpos.reshape(1, -1), np.zeros((1, n_half))], axis=1)
            return H

        if self.measurement_type == MeasurementType.GRAVITY_VECTOR_INERTIAL:
            # h(x) = a(r)
            # H = [d(a)/d(pos), 0]
            daccel_dpos = self._acceleration_jacobian(pos, r)
            H = np.block([[daccel_dpos, np.zeros((n_half, n_half))]])
            return H

        raise ValueError(f"Unknown measurement type: {self.measurement_type}")

    def measurement_noise_cov(self, state_dim: int | None = None) -> NDArray[np.float64]:
        """
        Get measurement noise covariance matrix.

        Args:
            state_dim: State dimension (for vector mode to determine measurement dim)

        Returns:
            Noise covariance matrix R
        """
        if self.measurement_type == MeasurementType.GRAVITY_MAGNITUDE:
            return np.array([[self.noise_std**2]])

        if self.measurement_type == MeasurementType.GRAVITY_VECTOR_INERTIAL:
            if state_dim is None:
                raise ValueError("state_dim required for vector mode")
            n_half = state_dim // 2

            if isinstance(self.noise_std, np.ndarray):
                if len(self.noise_std) == n_half:
                    return np.diag(self.noise_std**2)
                if len(self.noise_std) == 1:
                    return np.eye(n_half) * (self.noise_std[0] ** 2)
                raise ValueError(
                    f"noise_std length {len(self.noise_std)} doesn't match state dim {n_half}"
                )
            return np.eye(n_half) * (self.noise_std**2)

        raise ValueError(f"Unknown measurement type: {self.measurement_type}")

    def _acceleration_jacobian(
        self,
        pos: NDArray[np.float64],
        r: float,
    ) -> NDArray[np.float64]:
        """
        Compute Jacobian of acceleration w.r.t. position.

        Args:
            pos: Position vector
            r: Position magnitude (precomputed)

        Returns:
            Jacobian matrix (n_half x n_half)
        """
        n_half = len(pos)
        I = np.eye(n_half)

        if r < 1e-6:
            return np.zeros((n_half, n_half))

        r3 = r * r * r
        r5 = r3 * r * r

        # Two-body term: -mu/r^3 * I + 3*mu/(r^5) * pos*pos^T
        daccel_dpos = -self.mu / r3 * I + 3 * self.mu / r5 * np.outer(pos, pos)

        # J2 term (simplified - for 2D case, J2 effect is minimal in equatorial plane)
        # For full 3D J2 Jacobian, would need more complex terms
        # This approximation is reasonable for equatorial orbits
        if self.j2 is not None and self.r_eq is not None and n_half >= 3:
            # J2 adds additional terms - simplified version for 3D
            # For 2D (equatorial), J2 effect on Jacobian is small
            z_over_r = pos[2] / r if n_half >= 3 else 0.0
            j2_factor = 1.5 * self.j2 * self.mu * (self.r_eq**2) / (r5 * r)

            # Simplified J2 Jacobian terms (approximation)
            j2_terms = np.zeros((n_half, n_half))
            for i in range(n_half):
                for j in range(n_half):
                    if i == j:
                        j2_terms[i, j] = (5 * z_over_r * z_over_r - 1) * pos[i] / r
                    if i == 2 and j == 2:  # z-component
                        j2_terms[i, j] += (5 * z_over_r * z_over_r - 3) * pos[i] / r
                    j2_terms[i, j] += 5 * pos[i] * pos[j] * z_over_r / (r * r)
            daccel_dpos = daccel_dpos + j2_factor * j2_terms

        return daccel_dpos

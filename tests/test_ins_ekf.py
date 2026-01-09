"""Tests for INS EKF implementation."""

import numpy as np
import pytest

from outofthisworld.estimation.ins_ekf import (
    INSEKF,
    INSState,
    create_default_initial_covariance,
    rotation_matrix,
    skew,
)
from outofthisworld.sensors.imu_profiles import CLASSICAL_IMU, QUANTUM_IMU


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_skew_antisymmetric(self) -> None:
        """Skew matrix should be antisymmetric."""
        v = np.array([1.0, 2.0, 3.0])
        S = skew(v)

        np.testing.assert_array_almost_equal(S, -S.T)

    def test_skew_cross_product(self) -> None:
        """Skew matrix should implement cross product."""
        v1 = np.array([1.0, 2.0, 3.0])
        v2 = np.array([4.0, 5.0, 6.0])

        cross_direct = np.cross(v1, v2)
        cross_skew = skew(v1) @ v2

        np.testing.assert_array_almost_equal(cross_direct, cross_skew)

    def test_rotation_matrix_identity(self) -> None:
        """Zero rotation should give identity matrix."""
        R = rotation_matrix(np.zeros(3))
        np.testing.assert_array_almost_equal(R, np.eye(3))

    def test_rotation_matrix_orthogonal(self) -> None:
        """Rotation matrix should be orthogonal."""
        theta = np.array([0.1, 0.2, 0.3])
        R = rotation_matrix(theta)

        np.testing.assert_array_almost_equal(R @ R.T, np.eye(3))
        np.testing.assert_almost_equal(np.linalg.det(R), 1.0)


class TestINSState:
    """Tests for INS state container."""

    def test_to_vector(self) -> None:
        """State should convert to 15-element vector."""
        state = INSState(
            position=np.array([1.0, 2.0, 3.0]),
            velocity=np.array([4.0, 5.0, 6.0]),
            attitude=np.array([0.1, 0.2, 0.3]),
            accel_bias=np.array([1e-3, 2e-3, 3e-3]),
            gyro_bias=np.array([1e-4, 2e-4, 3e-4]),
        )

        vec = state.to_vector()
        assert len(vec) == 15
        np.testing.assert_array_equal(vec[:3], [1.0, 2.0, 3.0])
        np.testing.assert_array_equal(vec[3:6], [4.0, 5.0, 6.0])

    def test_from_vector(self) -> None:
        """State should be reconstructable from vector."""
        original = INSState(
            position=np.array([1.0, 2.0, 3.0]),
            velocity=np.array([4.0, 5.0, 6.0]),
            attitude=np.array([0.1, 0.2, 0.3]),
            accel_bias=np.array([1e-3, 2e-3, 3e-3]),
            gyro_bias=np.array([1e-4, 2e-4, 3e-4]),
        )

        vec = original.to_vector()
        reconstructed = INSState.from_vector(vec)

        np.testing.assert_array_equal(reconstructed.position, original.position)
        np.testing.assert_array_equal(reconstructed.velocity, original.velocity)


class TestINSEKF:
    """Tests for INS EKF."""

    def test_initialization(self) -> None:
        """EKF should initialize correctly."""
        state = INSState(
            position=np.zeros(3),
            velocity=np.zeros(3),
            attitude=np.zeros(3),
            accel_bias=np.zeros(3),
            gyro_bias=np.zeros(3),
        )
        P0 = create_default_initial_covariance()

        ekf = INSEKF(state, P0, CLASSICAL_IMU)

        assert ekf.state is not None
        assert ekf.covariance.shape == (15, 15)

    def test_predict_increases_uncertainty(self) -> None:
        """Prediction should increase covariance."""
        state = INSState(
            position=np.zeros(3),
            velocity=np.zeros(3),
            attitude=np.zeros(3),
            accel_bias=np.zeros(3),
            gyro_bias=np.zeros(3),
        )
        P0 = create_default_initial_covariance()
        ekf = INSEKF(state, P0, CLASSICAL_IMU)

        initial_trace = np.trace(ekf.covariance)

        # Predict with zero measurements
        ekf.predict(np.zeros(3), np.zeros(3), dt=1.0)

        final_trace = np.trace(ekf.covariance)

        assert final_trace >= initial_trace

    def test_update_decreases_uncertainty(self) -> None:
        """Attitude update should decrease attitude covariance."""
        state = INSState(
            position=np.zeros(3),
            velocity=np.zeros(3),
            attitude=np.zeros(3),
            accel_bias=np.zeros(3),
            gyro_bias=np.zeros(3),
        )
        P0 = create_default_initial_covariance()
        ekf = INSEKF(state, P0, CLASSICAL_IMU)

        # Propagate to increase uncertainty
        for _ in range(10):
            ekf.predict(np.zeros(3), np.zeros(3), dt=1.0)

        att_var_before = np.trace(ekf.covariance[6:9, 6:9])

        # Update with attitude measurement
        R = np.eye(3) * 1e-8  # Very accurate measurement
        ekf.update_attitude(np.zeros(3), R)

        att_var_after = np.trace(ekf.covariance[6:9, 6:9])

        assert att_var_after < att_var_before

    def test_covariance_stays_symmetric(self) -> None:
        """Covariance should remain symmetric after operations."""
        state = INSState(
            position=np.zeros(3),
            velocity=np.zeros(3),
            attitude=np.zeros(3),
            accel_bias=np.zeros(3),
            gyro_bias=np.zeros(3),
        )
        P0 = create_default_initial_covariance()
        ekf = INSEKF(state, P0, CLASSICAL_IMU)

        # Multiple predict/update cycles
        for i in range(10):
            ekf.predict(np.random.randn(3) * 1e-5, np.random.randn(3) * 1e-6, dt=1.0)
            if i % 3 == 0:
                ekf.update_attitude(np.zeros(3), np.eye(3) * 1e-6)

        # Check symmetry
        np.testing.assert_array_almost_equal(ekf.covariance, ekf.covariance.T)

    def test_velocity_integrates_acceleration(self) -> None:
        """Non-zero acceleration should change velocity."""
        state = INSState(
            position=np.zeros(3),
            velocity=np.zeros(3),
            attitude=np.zeros(3),
            accel_bias=np.zeros(3),
            gyro_bias=np.zeros(3),
        )
        P0 = create_default_initial_covariance()
        ekf = INSEKF(state, P0, CLASSICAL_IMU)

        accel = np.array([1.0, 0.0, 0.0])
        ekf.predict(accel, np.zeros(3), dt=1.0)

        assert ekf.state.velocity[0] > 0

    def test_position_integrates_velocity(self) -> None:
        """Non-zero velocity should change position."""
        state = INSState(
            position=np.zeros(3),
            velocity=np.array([10.0, 0.0, 0.0]),
            attitude=np.zeros(3),
            accel_bias=np.zeros(3),
            gyro_bias=np.zeros(3),
        )
        P0 = create_default_initial_covariance()
        ekf = INSEKF(state, P0, CLASSICAL_IMU)

        ekf.predict(np.zeros(3), np.zeros(3), dt=1.0)

        assert ekf.state.position[0] > 0


class TestDefaultCovariance:
    """Tests for default covariance creation."""

    def test_shape(self) -> None:
        """Should create 15x15 matrix."""
        P = create_default_initial_covariance()
        assert P.shape == (15, 15)

    def test_diagonal(self) -> None:
        """Should be diagonal."""
        P = create_default_initial_covariance()
        assert np.allclose(P, np.diag(np.diag(P)))

    def test_positive_definite(self) -> None:
        """Should be positive definite."""
        P = create_default_initial_covariance()
        eigenvalues = np.linalg.eigvalsh(P)
        assert np.all(eigenvalues > 0)

    def test_custom_values(self) -> None:
        """Should accept custom sigma values."""
        P = create_default_initial_covariance(
            pos_sigma=100.0,
            vel_sigma=1.0,
        )
        assert P[0, 0] == 100.0**2
        assert P[3, 3] == 1.0**2

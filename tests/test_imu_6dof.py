"""Tests for IMU profiles and 6-DOF IMU model."""

import numpy as np
import pytest

from outofthisworld.sensors.imu_6dof import IMU6DOF
from outofthisworld.sensors.imu_profiles import (
    CLASSICAL_IMU,
    QUANTUM_IMU,
    IMUProfile,
    get_profile,
)


class TestIMUProfiles:
    """Tests for IMU profile definitions."""

    def test_classical_profile_exists(self) -> None:
        """Classical profile should be defined."""
        assert CLASSICAL_IMU is not None
        assert CLASSICAL_IMU.name == "classical"

    def test_quantum_profile_exists(self) -> None:
        """Quantum profile should be defined."""
        assert QUANTUM_IMU is not None
        assert QUANTUM_IMU.name == "quantum"

    def test_quantum_better_than_classical(self) -> None:
        """Quantum profile should have lower noise than classical."""
        # Accelerometer white noise
        assert QUANTUM_IMU.accel_white_noise < CLASSICAL_IMU.accel_white_noise
        # Gyroscope white noise
        assert QUANTUM_IMU.gyro_white_noise < CLASSICAL_IMU.gyro_white_noise
        # Bias instability
        assert QUANTUM_IMU.accel_bias_instability < CLASSICAL_IMU.accel_bias_instability
        assert QUANTUM_IMU.gyro_bias_instability < CLASSICAL_IMU.gyro_bias_instability

    def test_get_profile_classical(self) -> None:
        """get_profile should return classical profile by name."""
        profile = get_profile("classical")
        assert profile is CLASSICAL_IMU

    def test_get_profile_quantum(self) -> None:
        """get_profile should return quantum profile by name."""
        profile = get_profile("quantum")
        assert profile is QUANTUM_IMU

    def test_get_profile_invalid(self) -> None:
        """get_profile should raise for invalid name."""
        with pytest.raises(ValueError, match="Unknown IMU profile"):
            get_profile("nonexistent")

    def test_profile_from_specs(self) -> None:
        """Should create profile from engineering units."""
        profile = IMUProfile.from_specs(
            name="test",
            accel_white_noise_ug_sqrt_hz=100.0,
            accel_bias_instability_ug=10.0,
            accel_turn_on_bias_ug=50.0,
            accel_scale_factor_ppm=100.0,
            gyro_white_noise_deg_sqrt_h=0.01,
            gyro_bias_instability_deg_h=0.01,
            gyro_turn_on_bias_deg_h=0.1,
            gyro_scale_factor_ppm=100.0,
        )
        assert profile.name == "test"
        # Verify conversion happened (values should be small in SI)
        assert profile.accel_white_noise < 0.001  # Well below 1 m/s²


class TestIMU6DOF:
    """Tests for 6-DOF IMU sensor model."""

    def test_initialization(self) -> None:
        """IMU should initialize with profile."""
        imu = IMU6DOF(profile=CLASSICAL_IMU, seed=42)
        assert imu.profile is CLASSICAL_IMU

    def test_deterministic_with_seed(self) -> None:
        """Same seed should produce same measurements."""
        imu1 = IMU6DOF(profile=CLASSICAL_IMU, seed=42)
        imu2 = IMU6DOF(profile=CLASSICAL_IMU, seed=42)

        true_accel = np.array([0.0, 0.0, 0.0])
        true_omega = np.array([0.0, 0.0, 0.0])

        meas1_a, meas1_w = imu1.measure(true_accel, true_omega, 1.0)
        meas2_a, meas2_w = imu2.measure(true_accel, true_omega, 1.0)

        np.testing.assert_array_equal(meas1_a, meas2_a)
        np.testing.assert_array_equal(meas1_w, meas2_w)

    def test_different_seeds_differ(self) -> None:
        """Different seeds should produce different measurements."""
        imu1 = IMU6DOF(profile=CLASSICAL_IMU, seed=42)
        imu2 = IMU6DOF(profile=CLASSICAL_IMU, seed=123)

        true_accel = np.array([0.0, 0.0, 0.0])
        true_omega = np.array([0.0, 0.0, 0.0])

        meas1_a, _ = imu1.measure(true_accel, true_omega, 1.0)
        meas2_a, _ = imu2.measure(true_accel, true_omega, 1.0)

        assert not np.allclose(meas1_a, meas2_a)

    def test_measurement_adds_noise(self) -> None:
        """Measurement should differ from true value due to noise."""
        imu = IMU6DOF(profile=CLASSICAL_IMU, seed=42)

        true_accel = np.array([1.0, 0.0, 0.0])
        true_omega = np.array([0.0, 0.1, 0.0])

        meas_a, meas_w = imu.measure(true_accel, true_omega, 1.0)

        # Measurements should be close but not exact
        assert not np.allclose(meas_a, true_accel)
        assert not np.allclose(meas_w, true_omega)

    def test_bias_drift(self) -> None:
        """Bias should change over time (random walk)."""
        imu = IMU6DOF(profile=CLASSICAL_IMU, seed=42)

        initial_accel_bias = imu.get_accel_bias().copy()

        # Make several measurements
        for _ in range(100):
            imu.measure(np.zeros(3), np.zeros(3), 1.0)

        final_accel_bias = imu.get_accel_bias()

        # Bias should have drifted
        assert not np.allclose(initial_accel_bias, final_accel_bias)

    def test_reset(self) -> None:
        """Reset should reinitialize IMU state."""
        imu = IMU6DOF(profile=CLASSICAL_IMU, seed=42)

        # Make some measurements to change state
        for _ in range(10):
            imu.measure(np.zeros(3), np.zeros(3), 1.0)

        bias_after_use = imu.get_accel_bias().copy()

        # Reset with same seed
        imu.reset(seed=42)
        bias_after_reset = imu.get_accel_bias()

        # Bias should be re-initialized (same seed = same initial bias)
        imu2 = IMU6DOF(profile=CLASSICAL_IMU, seed=42)
        np.testing.assert_array_almost_equal(bias_after_reset, imu2.get_accel_bias())

    def test_quantum_lower_noise(self) -> None:
        """Quantum IMU should have lower noise spread than classical."""
        n_samples = 1000
        dt = 1.0

        classical_imu = IMU6DOF(profile=CLASSICAL_IMU, seed=42)
        quantum_imu = IMU6DOF(profile=QUANTUM_IMU, seed=42)

        classical_measurements = []
        quantum_measurements = []

        for _ in range(n_samples):
            m, _ = classical_imu.measure(np.zeros(3), np.zeros(3), dt)
            classical_measurements.append(m)

        for _ in range(n_samples):
            m, _ = quantum_imu.measure(np.zeros(3), np.zeros(3), dt)
            quantum_measurements.append(m)

        classical_std = np.std(classical_measurements)
        quantum_std = np.std(quantum_measurements)

        # Quantum should have lower std (less noise)
        assert quantum_std < classical_std

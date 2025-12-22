"""Tests for gravitational measurement models."""

import numpy as np

from outofthisworld.estimation.gravity_measurements import GravityMeasurementModel
from outofthisworld.estimation.measurement_types import MeasurementType
from outofthisworld.physics.constants import J2_EARTH, M_EARTH, R_EARTH, G


def test_gravity_magnitude_prediction() -> None:
    """Test gravity magnitude measurement prediction."""
    mu = G * M_EARTH
    model = GravityMeasurementModel(
        measurement_type=MeasurementType.GRAVITY_MAGNITUDE,
        mu=mu,
        noise_std=1e-4,
    )

    # Test at known position
    position = np.array([R_EARTH * 2, 0.0])
    velocity = np.array([0.0, 7500.0])
    state = np.concatenate([position, velocity])

    measurement = model.predict_measurement(state)
    assert measurement.shape == (1,)
    assert measurement[0] > 0

    # Should match total_acceleration magnitude
    from outofthisworld.physics.orbital import total_acceleration

    true_accel = total_acceleration(position, mu)
    expected = np.linalg.norm(true_accel)
    assert abs(measurement[0] - expected) < 1e-10


def test_gravity_vector_prediction() -> None:
    """Test gravity vector measurement prediction."""
    mu = G * M_EARTH
    model = GravityMeasurementModel(
        measurement_type=MeasurementType.GRAVITY_VECTOR_INERTIAL,
        mu=mu,
        noise_std=1e-4,
    )

    position = np.array([R_EARTH * 2, 0.0])
    velocity = np.array([0.0, 7500.0])
    state = np.concatenate([position, velocity])

    measurement = model.predict_measurement(state)
    assert measurement.shape == (2,)

    # Should match total_acceleration
    from outofthisworld.physics.orbital import total_acceleration

    expected = total_acceleration(position, mu)
    assert np.allclose(measurement, expected, rtol=1e-10)


def test_gravity_vector_with_j2() -> None:
    """Test gravity vector with J2 perturbations."""
    mu = G * M_EARTH
    model = GravityMeasurementModel(
        measurement_type=MeasurementType.GRAVITY_VECTOR_INERTIAL,
        mu=mu,
        noise_std=1e-4,
        j2=J2_EARTH,
        r_eq=R_EARTH,
    )

    position = np.array([R_EARTH * 2, 0.0])
    velocity = np.array([0.0, 7500.0])
    state = np.concatenate([position, velocity])

    measurement = model.predict_measurement(state)

    # Should match total_acceleration with J2
    from outofthisworld.physics.orbital import total_acceleration

    expected = total_acceleration(position, mu, J2_EARTH, R_EARTH)
    assert np.allclose(measurement, expected, rtol=1e-10)


def test_measurement_jacobian_finite_difference() -> None:
    """Test measurement Jacobian using finite differences."""
    mu = G * M_EARTH
    model = GravityMeasurementModel(
        measurement_type=MeasurementType.GRAVITY_VECTOR_INERTIAL,
        mu=mu,
        noise_std=1e-4,
    )

    position = np.array([R_EARTH * 2, 0.0])
    velocity = np.array([0.0, 7500.0])
    state = np.concatenate([position, velocity])

    # Analytic Jacobian
    H_analytic = model.measurement_jacobian(state)

    # Finite difference approximation
    eps = 1e-6
    n = len(state)
    H_fd = np.zeros((2, n))

    for i in range(n):
        state_pert = state.copy()
        state_pert[i] += eps
        h_plus = model.predict_measurement(state_pert)

        state_pert[i] -= 2 * eps
        h_minus = model.predict_measurement(state_pert)

        H_fd[:, i] = (h_plus - h_minus) / (2 * eps)

    # Compare (allow some numerical error)
    assert np.allclose(H_analytic, H_fd, rtol=1e-4, atol=1e-6)


def test_measurement_jacobian_magnitude_finite_difference() -> None:
    """Test magnitude measurement Jacobian using finite differences."""
    mu = G * M_EARTH
    model = GravityMeasurementModel(
        measurement_type=MeasurementType.GRAVITY_MAGNITUDE,
        mu=mu,
        noise_std=1e-4,
    )

    position = np.array([R_EARTH * 2, 0.0])
    velocity = np.array([0.0, 7500.0])
    state = np.concatenate([position, velocity])

    # Analytic Jacobian
    H_analytic = model.measurement_jacobian(state)

    # Finite difference approximation
    eps = 1e-6
    n = len(state)
    H_fd = np.zeros((1, n))

    for i in range(n):
        state_pert = state.copy()
        state_pert[i] += eps
        h_plus = model.predict_measurement(state_pert)

        state_pert[i] -= 2 * eps
        h_minus = model.predict_measurement(state_pert)

        H_fd[0, i] = (h_plus[0] - h_minus[0]) / (2 * eps)

    # Compare (allow some numerical error)
    assert np.allclose(H_analytic, H_fd, rtol=1e-4, atol=1e-6)


def test_measurement_noise_cov_magnitude() -> None:
    """Test measurement noise covariance for magnitude mode."""
    model = GravityMeasurementModel(
        measurement_type=MeasurementType.GRAVITY_MAGNITUDE,
        mu=G * M_EARTH,
        noise_std=0.1,
    )

    R = model.measurement_noise_cov()
    assert R.shape == (1, 1)
    assert abs(R[0, 0] - 0.01) < 1e-10


def test_measurement_noise_cov_vector() -> None:
    """Test measurement noise covariance for vector mode."""
    model = GravityMeasurementModel(
        measurement_type=MeasurementType.GRAVITY_VECTOR_INERTIAL,
        mu=G * M_EARTH,
        noise_std=0.1,
    )

    R = model.measurement_noise_cov(state_dim=4)  # 2D position + 2D velocity
    assert R.shape == (2, 2)
    assert np.allclose(R, np.eye(2) * 0.01)


def test_j2_regression() -> None:
    """Test that J2 disabled matches two-body acceleration."""
    mu = G * M_EARTH
    position = np.array([R_EARTH * 2, 0.0])

    # Without J2
    model_no_j2 = GravityMeasurementModel(
        measurement_type=MeasurementType.GRAVITY_VECTOR_INERTIAL,
        mu=mu,
        noise_std=1e-4,
    )

    # With J2
    model_j2 = GravityMeasurementModel(
        measurement_type=MeasurementType.GRAVITY_VECTOR_INERTIAL,
        mu=mu,
        noise_std=1e-4,
        j2=J2_EARTH,
        r_eq=R_EARTH,
    )

    state = np.concatenate([position, np.array([0.0, 7500.0])])

    meas_no_j2 = model_no_j2.predict_measurement(state)
    meas_j2 = model_j2.predict_measurement(state)

    # Should be different (J2 adds perturbation)
    assert not np.allclose(meas_no_j2, meas_j2, rtol=1e-6)

    # Without J2 should match two-body
    from outofthisworld.physics.orbital import two_body_acceleration

    two_body = two_body_acceleration(position, mu)
    assert np.allclose(meas_no_j2, two_body, rtol=1e-10)

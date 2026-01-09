"""Tests for star tracker sensor model."""

import numpy as np
import pytest

from outofthisworld.sensors.star_tracker import (
    HIGH_ACCURACY_STAR_TRACKER,
    STANDARD_STAR_TRACKER,
    StarTracker,
    StarTrackerConfig,
    get_star_tracker_config,
)


class TestStarTrackerConfig:
    """Tests for star tracker configuration."""

    def test_standard_config_exists(self) -> None:
        """Standard config should be defined."""
        assert STANDARD_STAR_TRACKER is not None
        assert STANDARD_STAR_TRACKER.name == "standard"

    def test_high_accuracy_config_exists(self) -> None:
        """High accuracy config should be defined."""
        assert HIGH_ACCURACY_STAR_TRACKER is not None
        assert HIGH_ACCURACY_STAR_TRACKER.name == "high_accuracy"

    def test_high_accuracy_better_than_standard(self) -> None:
        """High accuracy should have smaller accuracy value."""
        assert HIGH_ACCURACY_STAR_TRACKER.accuracy_arcsec < STANDARD_STAR_TRACKER.accuracy_arcsec

    def test_accuracy_rad_conversion(self) -> None:
        """accuracy_rad property should convert correctly."""
        config = StarTrackerConfig(
            accuracy_arcsec=1.0,
            update_rate_hz=10.0,
            fov_deg=20.0,
        )
        # 1 arcsec ≈ 4.848e-6 rad
        assert abs(config.accuracy_rad - 4.848136811095360e-6) < 1e-12

    def test_get_config_standard(self) -> None:
        """get_star_tracker_config should return standard config."""
        config = get_star_tracker_config("standard")
        assert config is STANDARD_STAR_TRACKER

    def test_get_config_invalid(self) -> None:
        """get_star_tracker_config should raise for invalid name."""
        with pytest.raises(ValueError, match="Unknown star tracker"):
            get_star_tracker_config("nonexistent")


class TestStarTracker:
    """Tests for star tracker sensor model."""

    def test_initialization(self) -> None:
        """Star tracker should initialize correctly."""
        st = StarTracker(config=STANDARD_STAR_TRACKER, seed=42)
        assert st.config is STANDARD_STAR_TRACKER

    def test_deterministic_with_seed(self) -> None:
        """Same seed should produce same measurements."""
        st1 = StarTracker(seed=42)
        st2 = StarTracker(seed=42)

        true_att = np.array([0.1, 0.2, 0.3])

        meas1 = st1.force_measure(true_att)
        meas2 = st2.force_measure(true_att)

        np.testing.assert_array_equal(meas1, meas2)

    def test_measurement_adds_noise(self) -> None:
        """Measurement should differ from true attitude."""
        st = StarTracker(seed=42)
        true_att = np.array([0.1, 0.2, 0.3])

        meas = st.force_measure(true_att)

        assert not np.allclose(meas, true_att)

    def test_noise_is_reasonable(self) -> None:
        """Measurement noise should be on order of configured accuracy."""
        st = StarTracker(config=STANDARD_STAR_TRACKER, seed=42)

        n_samples = 1000
        errors = []

        for _ in range(n_samples):
            st.reset(seed=None)  # New seed each time
            true_att = np.zeros(3)
            meas = st.force_measure(true_att)
            errors.append(np.linalg.norm(meas))

        std_error = np.std(errors)

        # Error std should be on order of configured accuracy
        expected_std = st.config.accuracy_rad * np.sqrt(3)  # Approximate for 3 axes
        assert std_error < expected_std * 3  # Within 3x

    def test_measure_respects_update_rate(self) -> None:
        """measure() should return None if called too soon."""
        st = StarTracker(seed=42)
        true_att = np.zeros(3)

        # First measurement should work
        meas1 = st.measure(true_att, time=0.0)
        assert meas1 is not None

        # Immediate second call should return None
        meas2 = st.measure(true_att, time=0.01)
        assert meas2 is None

        # After update period, should work again
        period = st.config.update_period_s
        meas3 = st.measure(true_att, time=period + 0.01)
        assert meas3 is not None

    def test_is_available(self) -> None:
        """is_available should correctly report update availability."""
        st = StarTracker(seed=42)

        assert st.is_available(0.0)

        st.measure(np.zeros(3), time=0.0)

        assert not st.is_available(0.01)
        assert st.is_available(st.config.update_period_s + 0.01)

    def test_get_measurement_noise_cov(self) -> None:
        """Should return proper covariance matrix."""
        st = StarTracker(config=STANDARD_STAR_TRACKER)
        R = st.get_measurement_noise_cov()

        assert R.shape == (3, 3)
        assert np.allclose(R, R.T)  # Symmetric
        assert np.all(np.diag(R) > 0)  # Positive diagonal

        expected_var = st.config.accuracy_rad ** 2
        np.testing.assert_array_almost_equal(np.diag(R), [expected_var] * 3)

    def test_reset(self) -> None:
        """Reset should reinitialize state."""
        st = StarTracker(seed=42)

        # Make a measurement
        st.measure(np.zeros(3), time=0.0)

        # Reset
        st.reset()

        # Should be available immediately again
        assert st.is_available(0.0)

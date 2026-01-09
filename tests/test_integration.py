"""Integration tests for navigation experiments."""

import numpy as np
import pytest

from outofthisworld.sensors.imu_profiles import CLASSICAL_IMU, QUANTUM_IMU
from outofthisworld.sim.experiments import (
    run_cadence_sweep,
    run_coast_scenario,
    run_updates_scenario,
)


class TestCoastScenario:
    """Integration tests for coast (inertial-only) scenario."""

    def test_coast_runs_without_error(self) -> None:
        """Coast scenario should complete without error."""
        results = run_coast_scenario(
            imu_profile=CLASSICAL_IMU,
            duration_s=60.0,
            dt=1.0,
            seed=42,
        )

        assert results is not None
        assert len(results.time) > 0

    def test_coast_error_grows(self) -> None:
        """Position error should grow over time in coast mode."""
        results = run_coast_scenario(
            imu_profile=CLASSICAL_IMU,
            duration_s=60.0,
            dt=1.0,
            seed=42,
        )

        initial_error = np.linalg.norm(results.pos_error[0])
        final_error = results.get_final_pos_error_rms()

        assert final_error > initial_error

    def test_quantum_lower_error_than_classical(self) -> None:
        """Quantum IMU should have lower error than classical."""
        classical = run_coast_scenario(
            imu_profile=CLASSICAL_IMU,
            duration_s=300.0,  # 5 minutes
            dt=1.0,
            seed=42,
        )

        quantum = run_coast_scenario(
            imu_profile=QUANTUM_IMU,
            duration_s=300.0,
            dt=1.0,
            seed=42,
        )

        assert quantum.get_final_pos_error_rms() < classical.get_final_pos_error_rms()

    def test_deterministic_with_seed(self) -> None:
        """Same seed should produce same results."""
        results1 = run_coast_scenario(
            imu_profile=CLASSICAL_IMU,
            duration_s=60.0,
            seed=42,
        )

        results2 = run_coast_scenario(
            imu_profile=CLASSICAL_IMU,
            duration_s=60.0,
            seed=42,
        )

        np.testing.assert_array_almost_equal(
            results1.pos_error,
            results2.pos_error,
        )


class TestUpdatesScenario:
    """Integration tests for scenario with star tracker updates."""

    def test_updates_runs_without_error(self) -> None:
        """Updates scenario should complete without error."""
        results = run_updates_scenario(
            imu_profile=CLASSICAL_IMU,
            update_interval=10.0,
            duration_s=60.0,
            dt=1.0,
            seed=42,
        )

        assert results is not None
        assert results.n_updates > 0

    def test_updates_bounds_error(self) -> None:
        """Updates should prevent unbounded position error growth."""
        coast = run_coast_scenario(
            imu_profile=CLASSICAL_IMU,
            duration_s=300.0,
            seed=42,
        )

        updates = run_updates_scenario(
            imu_profile=CLASSICAL_IMU,
            update_interval=10.0,
            duration_s=300.0,
            seed=42,
        )

        # With star tracker attitude updates, position error should be lower
        # because attitude errors are corrected, preventing misrotated acceleration
        assert updates.get_final_pos_error_rms() < coast.get_final_pos_error_rms()

    def test_faster_cadence_more_updates(self) -> None:
        """Faster update cadence should result in more update events."""
        slow = run_updates_scenario(
            imu_profile=CLASSICAL_IMU,
            update_interval=60.0,
            duration_s=300.0,
            seed=42,
        )

        fast = run_updates_scenario(
            imu_profile=CLASSICAL_IMU,
            update_interval=10.0,
            duration_s=300.0,
            seed=42,
        )

        # Faster cadence should result in more updates
        assert fast.n_updates > slow.n_updates


class TestCadenceSweep:
    """Integration tests for cadence sweep."""

    def test_sweep_runs_without_error(self) -> None:
        """Cadence sweep should complete without error."""
        results = run_cadence_sweep(
            imu_profile=CLASSICAL_IMU,
            intervals=[10.0, 60.0],
            duration_s=120.0,
            seed=42,
        )

        assert len(results) == 2

    def test_sweep_error_increases_with_interval(self) -> None:
        """Longer intervals should generally result in higher error."""
        results = run_cadence_sweep(
            imu_profile=CLASSICAL_IMU,
            intervals=[10.0, 60.0, 120.0],
            duration_s=300.0,
            seed=42,
        )

        errors = [r.get_final_pos_error_rms() for r in results]

        # Error should generally increase (allow some tolerance for stochastic effects)
        assert errors[-1] > errors[0]


class TestErrorBounds:
    """Tests to verify error stays within reasonable bounds."""

    def test_classical_coast_error_bounded(self) -> None:
        """Classical coast error should be within expected range."""
        results = run_coast_scenario(
            imu_profile=CLASSICAL_IMU,
            duration_s=3600.0,  # 1 hour
            dt=1.0,
            seed=42,
        )

        final_error = results.get_final_pos_error_rms()

        # Classical IMU over 1 hour should have km-scale errors
        # but shouldn't be astronomically large
        assert final_error > 100  # At least 100 m error expected
        assert final_error < 1e8  # Sanity check: less than 100,000 km

    def test_quantum_coast_error_bounded(self) -> None:
        """Quantum coast error should be much smaller than classical."""
        classical = run_coast_scenario(
            imu_profile=CLASSICAL_IMU,
            duration_s=3600.0,
            seed=42,
        )

        quantum = run_coast_scenario(
            imu_profile=QUANTUM_IMU,
            duration_s=3600.0,
            seed=42,
        )

        # Quantum should be significantly better (at least 10x)
        ratio = classical.get_final_pos_error_rms() / quantum.get_final_pos_error_rms()
        assert ratio > 10

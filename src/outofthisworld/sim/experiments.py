"""Experiment framework: scenarios, runners, and analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from outofthisworld.estimation.ins_ekf import (
    INSEKF,
    INSState,
    create_default_initial_covariance,
)
from outofthisworld.sensors.imu_6dof import IMU6DOF
from outofthisworld.sensors.imu_profiles import IMUProfile, get_profile
from outofthisworld.sensors.star_tracker import (
    StarTracker,
    StarTrackerConfig,
    get_star_tracker_config,
)


@dataclass
class ExperimentConfig:
    """Configuration for a navigation experiment."""

    name: str
    duration_s: float
    dt: float
    seed: int
    imu_profile: IMUProfile
    star_tracker_config: StarTrackerConfig | None
    star_tracker_interval: float  # Measurement interval in seconds
    initial_position: NDArray[np.float64]
    initial_velocity: NDArray[np.float64]
    initial_attitude: NDArray[np.float64]
    initial_covariance: NDArray[np.float64]
    output_dir: Path = field(default_factory=lambda: Path("results"))
    output_prefix: str = "experiment"


@dataclass
class ExperimentResults:
    """Results from a navigation experiment."""

    config: ExperimentConfig
    time: NDArray[np.float64]
    true_position: NDArray[np.float64]
    true_velocity: NDArray[np.float64]
    true_attitude: NDArray[np.float64]
    est_position: NDArray[np.float64]
    est_velocity: NDArray[np.float64]
    est_attitude: NDArray[np.float64]
    pos_error: NDArray[np.float64]
    vel_error: NDArray[np.float64]
    att_error: NDArray[np.float64]
    pos_sigma: NDArray[np.float64]
    vel_sigma: NDArray[np.float64]
    att_sigma: NDArray[np.float64]
    n_updates: int = 0

    def get_final_pos_error_rms(self) -> float:
        """Get final position error RMS."""
        return float(np.linalg.norm(self.pos_error[-1]))

    def get_final_vel_error_rms(self) -> float:
        """Get final velocity error RMS."""
        return float(np.linalg.norm(self.vel_error[-1]))

    def get_max_pos_error(self) -> float:
        """Get maximum position error magnitude."""
        return float(np.max(np.linalg.norm(self.pos_error, axis=1)))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "config": {
                "name": self.config.name,
                "duration_s": self.config.duration_s,
                "dt": self.config.dt,
                "seed": self.config.seed,
                "imu_profile": self.config.imu_profile.name,
                "star_tracker_interval": self.config.star_tracker_interval,
            },
            "summary": {
                "final_pos_error_m": self.get_final_pos_error_rms(),
                "final_vel_error_m_s": self.get_final_vel_error_rms(),
                "max_pos_error_m": self.get_max_pos_error(),
                "n_updates": self.n_updates,
            },
            "time_s": self.time.tolist(),
            "pos_error_norm_m": np.linalg.norm(self.pos_error, axis=1).tolist(),
            "vel_error_norm_m_s": np.linalg.norm(self.vel_error, axis=1).tolist(),
            "pos_sigma_norm_m": np.linalg.norm(self.pos_sigma, axis=1).tolist(),
        }


def run_coast_scenario(
    imu_profile: IMUProfile,
    duration_s: float = 3600.0,
    dt: float = 1.0,
    seed: int = 42,
) -> ExperimentResults:
    """
    Run coast (inertial-only) scenario with no measurement updates.

    Args:
        imu_profile: IMU noise profile to use
        duration_s: Simulation duration in seconds
        dt: Time step in seconds
        seed: Random seed for reproducibility

    Returns:
        ExperimentResults with error time histories
    """
    config = ExperimentConfig(
        name=f"coast_{imu_profile.name}",
        duration_s=duration_s,
        dt=dt,
        seed=seed,
        imu_profile=imu_profile,
        star_tracker_config=None,
        star_tracker_interval=float("inf"),
        initial_position=np.zeros(3),
        initial_velocity=np.array([1000.0, 0.0, 0.0]),
        initial_attitude=np.zeros(3),
        initial_covariance=create_default_initial_covariance(),
    )

    return _run_experiment(config)


def run_updates_scenario(
    imu_profile: IMUProfile,
    update_interval: float = 60.0,
    duration_s: float = 3600.0,
    dt: float = 1.0,
    seed: int = 42,
) -> ExperimentResults:
    """
    Run scenario with periodic star tracker updates.

    Args:
        imu_profile: IMU noise profile to use
        update_interval: Star tracker update interval in seconds
        duration_s: Simulation duration in seconds
        dt: Time step in seconds
        seed: Random seed for reproducibility

    Returns:
        ExperimentResults with error time histories
    """
    st_config = get_star_tracker_config("standard")

    config = ExperimentConfig(
        name=f"updates_{imu_profile.name}_{update_interval:.0f}s",
        duration_s=duration_s,
        dt=dt,
        seed=seed,
        imu_profile=imu_profile,
        star_tracker_config=st_config,
        star_tracker_interval=update_interval,
        initial_position=np.zeros(3),
        initial_velocity=np.array([1000.0, 0.0, 0.0]),
        initial_attitude=np.zeros(3),
        initial_covariance=create_default_initial_covariance(),
    )

    return _run_experiment(config)


def run_cadence_sweep(
    imu_profile: IMUProfile,
    intervals: list[float] | None = None,
    duration_s: float = 3600.0,
    dt: float = 1.0,
    seed: int = 42,
) -> list[ExperimentResults]:
    """
    Sweep star tracker update cadence and collect final errors.

    Args:
        imu_profile: IMU noise profile to use
        intervals: List of update intervals to test (seconds)
        duration_s: Simulation duration
        dt: Time step
        seed: Random seed

    Returns:
        List of ExperimentResults, one per interval
    """
    if intervals is None:
        intervals = [10.0, 30.0, 60.0, 120.0, 300.0, 600.0, 1800.0, 3600.0]

    results = []
    for interval in intervals:
        result = run_updates_scenario(
            imu_profile=imu_profile,
            update_interval=interval,
            duration_s=duration_s,
            dt=dt,
            seed=seed,
        )
        results.append(result)

    return results


def _run_experiment(config: ExperimentConfig) -> ExperimentResults:
    """
    Core experiment runner.

    Propagates true state, generates IMU measurements, runs EKF,
    and collects error statistics.

    Key physics: In INS, attitude errors cause accelerometer readings to be
    rotated incorrectly into the navigation frame, leading to velocity and
    position errors even with perfect accelerometer measurements.
    """
    from outofthisworld.estimation.ins_ekf import rotation_matrix

    n_steps = int(config.duration_s / config.dt)

    # Initialize sensors
    imu = IMU6DOF(profile=config.imu_profile, seed=config.seed)

    star_tracker = None
    if config.star_tracker_config is not None:
        star_tracker = StarTracker(config=config.star_tracker_config, seed=config.seed + 1)

    # Initialize true state
    true_pos = config.initial_position.copy()
    true_vel = config.initial_velocity.copy()
    true_att = config.initial_attitude.copy()

    # Constant thrust in body frame (simulates deep-space maneuvering)
    # This makes attitude errors matter - they cause wrong nav-frame acceleration
    BODY_FRAME_THRUST = np.array([0.1, 0.0, 0.0])  # 0.1 m/s² along body x-axis

    # Initialize EKF
    initial_state = INSState(
        position=config.initial_position.copy(),
        velocity=config.initial_velocity.copy(),
        attitude=config.initial_attitude.copy(),
        accel_bias=np.zeros(3),
        gyro_bias=np.zeros(3),
    )
    ekf = INSEKF(
        initial_state=initial_state,
        initial_covariance=config.initial_covariance,
        imu_profile=config.imu_profile,
    )

    # Storage
    time_hist = np.zeros(n_steps + 1)
    true_pos_hist = np.zeros((n_steps + 1, 3))
    true_vel_hist = np.zeros((n_steps + 1, 3))
    true_att_hist = np.zeros((n_steps + 1, 3))
    est_pos_hist = np.zeros((n_steps + 1, 3))
    est_vel_hist = np.zeros((n_steps + 1, 3))
    est_att_hist = np.zeros((n_steps + 1, 3))
    pos_sigma_hist = np.zeros((n_steps + 1, 3))
    vel_sigma_hist = np.zeros((n_steps + 1, 3))
    att_sigma_hist = np.zeros((n_steps + 1, 3))

    # Store initial
    time_hist[0] = 0.0
    true_pos_hist[0] = true_pos
    true_vel_hist[0] = true_vel
    true_att_hist[0] = true_att
    est_pos_hist[0] = ekf.state.position
    est_vel_hist[0] = ekf.state.velocity
    est_att_hist[0] = ekf.state.attitude
    pos_sigma_hist[0] = ekf.get_position_uncertainty()
    vel_sigma_hist[0] = ekf.get_velocity_uncertainty()
    att_sigma_hist[0] = ekf.get_attitude_uncertainty()

    n_updates = 0
    last_update_time = 0.0

    for step in range(n_steps):
        t = (step + 1) * config.dt

        # --- True state propagation ---
        # True rotation matrix (body to nav)
        C_true = rotation_matrix(true_att)

        # True nav-frame acceleration from body-frame thrust
        true_accel_nav = C_true @ BODY_FRAME_THRUST

        # Integrate true state
        true_vel = true_vel + true_accel_nav * config.dt
        true_pos = true_pos + true_vel * config.dt
        # Attitude constant (no rotation in this scenario)

        # --- Generate IMU measurements ---
        # IMU measures the thrust in body frame (specific force)
        true_accel_body = BODY_FRAME_THRUST
        true_omega = np.zeros(3)

        accel_meas, omega_meas = imu.measure(true_accel_body, true_omega, config.dt)

        # --- EKF prediction ---
        # The EKF uses its ESTIMATED attitude to rotate accel to nav frame
        # If attitude has error, the nav-frame acceleration is wrong,
        # causing velocity and position errors
        ekf.predict(accel_meas, omega_meas, config.dt)

        # --- Star tracker update ---
        if star_tracker is not None:
            if (t - last_update_time) >= config.star_tracker_interval:
                att_meas = star_tracker.force_measure(true_att)
                R = star_tracker.get_measurement_noise_cov()
                ekf.update_attitude(att_meas, R)
                last_update_time = t
                n_updates += 1

        # --- Store ---
        time_hist[step + 1] = t
        true_pos_hist[step + 1] = true_pos
        true_vel_hist[step + 1] = true_vel
        true_att_hist[step + 1] = true_att
        est_pos_hist[step + 1] = ekf.state.position
        est_vel_hist[step + 1] = ekf.state.velocity
        est_att_hist[step + 1] = ekf.state.attitude
        pos_sigma_hist[step + 1] = ekf.get_position_uncertainty()
        vel_sigma_hist[step + 1] = ekf.get_velocity_uncertainty()
        att_sigma_hist[step + 1] = ekf.get_attitude_uncertainty()

    # Compute errors
    pos_error = est_pos_hist - true_pos_hist
    vel_error = est_vel_hist - true_vel_hist
    att_error = est_att_hist - true_att_hist

    return ExperimentResults(
        config=config,
        time=time_hist,
        true_position=true_pos_hist,
        true_velocity=true_vel_hist,
        true_attitude=true_att_hist,
        est_position=est_pos_hist,
        est_velocity=est_vel_hist,
        est_attitude=est_att_hist,
        pos_error=pos_error,
        vel_error=vel_error,
        att_error=att_error,
        pos_sigma=pos_sigma_hist,
        vel_sigma=vel_sigma_hist,
        att_sigma=att_sigma_hist,
        n_updates=n_updates,
    )


def load_config_from_yaml(path: Path) -> ExperimentConfig:
    """
    Load experiment configuration from YAML file.

    Args:
        path: Path to YAML config file

    Returns:
        ExperimentConfig
    """
    import yaml

    with open(path) as f:
        data = yaml.safe_load(f)

    sim = data.get("simulation", {})
    imu_data = data.get("imu", {})
    st_data = data.get("star_tracker", {})
    ic = data.get("initial_conditions", {})
    unc = data.get("initial_uncertainty", {})
    out = data.get("output", {})

    # IMU profile
    imu_profile = get_profile(imu_data.get("profile", "classical"))

    # Star tracker
    st_config = None
    st_interval = float("inf")
    if st_data.get("enabled", False):
        st_config = get_star_tracker_config(st_data.get("config", "standard"))
        st_interval = st_data.get("update_interval_seconds", 60.0)

    # Initial conditions
    initial_pos = np.array(ic.get("position_m", [0.0, 0.0, 0.0]))
    initial_vel = np.array(ic.get("velocity_m_s", [1000.0, 0.0, 0.0]))
    initial_att = np.array(ic.get("attitude_rad", [0.0, 0.0, 0.0]))

    # Initial covariance
    initial_cov = create_default_initial_covariance(
        pos_sigma=unc.get("position_m", 10.0),
        vel_sigma=unc.get("velocity_m_s", 0.1),
        att_sigma=unc.get("attitude_rad", 0.001),
        accel_bias_sigma=unc.get("accel_bias_m_s2", 1e-4),
        gyro_bias_sigma=unc.get("gyro_bias_rad_s", 1e-5),
    )

    return ExperimentConfig(
        name=sim.get("name", "experiment"),
        duration_s=sim.get("duration_hours", 1.0) * 3600.0,
        dt=sim.get("dt_seconds", 1.0),
        seed=sim.get("seed", 42),
        imu_profile=imu_profile,
        star_tracker_config=st_config,
        star_tracker_interval=st_interval,
        initial_position=initial_pos,
        initial_velocity=initial_vel,
        initial_attitude=initial_att,
        initial_covariance=initial_cov,
        output_dir=Path(out.get("directory", "results")),
        output_prefix=out.get("prefix", "experiment"),
    )

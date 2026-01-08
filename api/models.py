"""Pydantic models for API requests/responses."""

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    """Request to run a simulation."""

    imu_profile: str = Field(default="quantum", description="IMU profile: 'classical' or 'quantum'")
    scenario: str = Field(default="compare", description="Scenario: 'coast', 'updates', 'compare'")
    duration_hours: float = Field(default=1.0, ge=0.1, le=24.0)
    update_interval: float = Field(default=60.0, ge=1.0, le=3600.0)
    seed: int = Field(default=42)


class TrajectoryPoint(BaseModel):
    """3D position point."""

    x: float
    y: float
    z: float


class ExperimentResult(BaseModel):
    """Result from a single experiment."""

    name: str
    imu_profile: str
    final_pos_error_m: float
    final_vel_error_m_s: float
    max_pos_error_m: float
    n_updates: int
    time_s: list[float]
    pos_error_m: list[float]
    vel_error_m_s: list[float]
    pos_sigma_m: list[float]
    true_position: list[TrajectoryPoint]
    est_position: list[TrajectoryPoint]


class RunResponse(BaseModel):
    """Response from running simulation."""

    id: str
    experiments: list[ExperimentResult]
    improvement_factor: float | None = None


class ProfileInfo(BaseModel):
    """IMU profile information."""

    name: str
    description: str
    accel_bias_instability_ug: float
    gyro_bias_instability_deg_h: float


class ScenarioInfo(BaseModel):
    """Scenario information."""

    name: str
    description: str

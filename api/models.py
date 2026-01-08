"""Pydantic models for the FastAPI layer."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ScenarioSummary(BaseModel):
    id: str
    name: str
    description: str
    defaultConfig: str | None = None
    tags: list[str] = Field(default_factory=list)


class RunRequest(BaseModel):
    scenario_id: str
    config_path: str | None = None
    t_end_s: float | None = Field(default=None, gt=0)
    dt_s: float | None = Field(default=None, gt=0)


class ProfileInfo(BaseModel):
    name: str
    description: str
    accel_bias_instability_ug: float
    gyro_bias_instability_deg_h: float


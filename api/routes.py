"""API routes for simulation endpoints."""

from __future__ import annotations

from dataclasses import replace
from fastapi import APIRouter, HTTPException

from api.frame_adapter import (
    experiment_to_frames,
    frames_to_dicts,
    load_experiment_config,
    merge_frame_sets,
    with_overrides,
)
from api.models import ProfileInfo, RunRequest, ScenarioSummary
from outofthisworld.sim.experiments import _run_experiment

router = APIRouter()


@router.get("/profiles", response_model=list[ProfileInfo])
async def get_profiles():
    """Get available IMU profiles."""
    return [
        ProfileInfo(
            name="classical",
            description="Navigation-grade IMU (FOG/RLG class)",
            accel_bias_instability_ug=10.0,
            gyro_bias_instability_deg_h=0.01,
        ),
        ProfileInfo(
            name="quantum",
            description="Quantum-class IMU (atom interferometry)",
            accel_bias_instability_ug=0.1,
            gyro_bias_instability_deg_h=0.0001,
        ),
    ]


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/scenarios", response_model=list[ScenarioSummary])
async def get_scenarios():
    """Get available scenarios for the dashboard."""
    return [
        ScenarioSummary(
            id="coast",
            name="Coast (inertial-only)",
            description="Inertial-only propagation (no star tracker updates).",
            defaultConfig="configs/quantum.yaml",
            tags=["deep-space", "inertial", "ins-ekf"],
        ),
        ScenarioSummary(
            id="updates",
            name="Updates (star tracker)",
            description="Periodic star tracker attitude updates.",
            defaultConfig="configs/quantum.yaml",
            tags=["deep-space", "star-tracker", "ins-ekf"],
        ),
        ScenarioSummary(
            id="compare",
            name="Compare (classical vs quantum)",
            description="Compare classical vs quantum IMU baselines (coast + updates).",
            defaultConfig=None,
            tags=["classical-imu", "quantum-imu", "compare"],
        ),
    ]


@router.post("/run")
async def run_simulation(request: RunRequest):
    """Run a scenario and return a time-ordered list of frames."""
    scenario_id = request.scenario_id
    valid = {"coast", "updates", "compare"}
    if scenario_id in valid is False:
        raise HTTPException(status_code=400, detail=f"Unknown scenario: {scenario_id}")

    config_path = request.config_path
    if config_path is None:
        if scenario_id != "compare":
            config_path = "configs/quantum.yaml"

    if scenario_id != "compare":
        if config_path is None:
            raise HTTPException(status_code=400, detail="No default config for this scenario")

        try:
            base = load_experiment_config(config_path)
        except FileNotFoundError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        base = with_overrides(base, duration_s=request.t_end_s, dt_s=request.dt_s)

        config = base
        if scenario_id == "coast":
            config = replace(config, star_tracker_config=None, star_tracker_interval=float("inf"))

        result = _run_experiment(config)
        frames = experiment_to_frames(
            result,
            craft_id=f"{scenario_id}.{config.imu_profile.name}",
            craft_name=f"{scenario_id} / {config.imu_profile.name}",
            include_estimate=True,
        )
        if frames == []:
            raise HTTPException(status_code=500, detail="Simulation produced no frames")

        return frames_to_dicts(frames)

    classical_path = "configs/classical.yaml"
    quantum_path = "configs/quantum.yaml"

    try:
        classical = load_experiment_config(classical_path)
        quantum = load_experiment_config(quantum_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    classical = with_overrides(classical, duration_s=request.t_end_s, dt_s=request.dt_s)
    quantum = with_overrides(quantum, duration_s=request.t_end_s, dt_s=request.dt_s)

    classical_coast = replace(classical, star_tracker_config=None, star_tracker_interval=float("inf"))
    quantum_coast = replace(quantum, star_tracker_config=None, star_tracker_interval=float("inf"))

    results = [
        (_run_experiment(classical_coast), "coast.classical", "Coast / classical"),
        (_run_experiment(quantum_coast), "coast.quantum", "Coast / quantum"),
        (_run_experiment(classical), "updates.classical", "Updates / classical"),
        (_run_experiment(quantum), "updates.quantum", "Updates / quantum"),
    ]

    frame_sets = [
        experiment_to_frames(r, craft_id=cid, craft_name=name, include_estimate=True)
        for (r, cid, name) in results
    ]
    merged = merge_frame_sets(frame_sets)
    if merged == []:
        raise HTTPException(status_code=500, detail="Simulation produced no frames")

    return frames_to_dicts(merged)

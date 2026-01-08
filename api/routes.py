"""API routes for simulation endpoints."""

import uuid
from typing import Any

import numpy as np
from fastapi import APIRouter, HTTPException

from api.models import (
    ExperimentResult,
    ProfileInfo,
    RunRequest,
    RunResponse,
    ScenarioInfo,
    TrajectoryPoint,
)
from outofthisworld.sensors.imu_profiles import CLASSICAL_IMU, QUANTUM_IMU, get_profile
from outofthisworld.sim.experiments import (
    run_coast_scenario,
    run_updates_scenario,
)

router = APIRouter()


def _convert_result(result: Any) -> ExperimentResult:
    """Convert experiment result to API response format."""
    # Subsample for network efficiency (max 200 points)
    n = len(result.time)
    step = max(1, n // 200)
    indices = list(range(0, n, step))

    time_s = [float(result.time[i]) for i in indices]
    pos_error_m = [float(np.linalg.norm(result.pos_error[i])) for i in indices]
    vel_error_m_s = [float(np.linalg.norm(result.vel_error[i])) for i in indices]
    pos_sigma_m = [float(np.linalg.norm(result.pos_sigma[i]) * 3) for i in indices]

    true_pos = [
        TrajectoryPoint(
            x=float(result.true_position[i, 0]),
            y=float(result.true_position[i, 1]),
            z=float(result.true_position[i, 2]),
        )
        for i in indices
    ]

    est_pos = [
        TrajectoryPoint(
            x=float(result.est_position[i, 0]),
            y=float(result.est_position[i, 1]),
            z=float(result.est_position[i, 2]),
        )
        for i in indices
    ]

    return ExperimentResult(
        name=result.config.name,
        imu_profile=result.config.imu_profile.name,
        final_pos_error_m=result.get_final_pos_error_rms(),
        final_vel_error_m_s=result.get_final_vel_error_rms(),
        max_pos_error_m=result.get_max_pos_error(),
        n_updates=result.n_updates,
        time_s=time_s,
        pos_error_m=pos_error_m,
        vel_error_m_s=vel_error_m_s,
        pos_sigma_m=pos_sigma_m,
        true_position=true_pos,
        est_position=est_pos,
    )


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


@router.get("/scenarios", response_model=list[ScenarioInfo])
async def get_scenarios():
    """Get available scenarios."""
    return [
        ScenarioInfo(name="coast", description="Inertial-only propagation (no updates)"),
        ScenarioInfo(name="updates", description="Periodic star tracker attitude updates"),
        ScenarioInfo(name="compare", description="Compare classical vs quantum IMU"),
    ]


@router.post("/run", response_model=RunResponse)
async def run_simulation(request: RunRequest):
    """Run navigation simulation."""
    duration_s = request.duration_hours * 3600.0
    run_id = f"run_{uuid.uuid4().hex[:8]}"

    experiments: list[ExperimentResult] = []
    improvement_factor = None

    try:
        if request.scenario == "coast":
            profile = get_profile(request.imu_profile)
            result = run_coast_scenario(profile, duration_s, seed=request.seed)
            experiments.append(_convert_result(result))

        elif request.scenario == "updates":
            profile = get_profile(request.imu_profile)
            result = run_updates_scenario(
                profile, request.update_interval, duration_s, seed=request.seed
            )
            experiments.append(_convert_result(result))

        elif request.scenario == "compare":
            # Run all 4 combinations
            classical_coast = run_coast_scenario(CLASSICAL_IMU, duration_s, seed=request.seed)
            quantum_coast = run_coast_scenario(QUANTUM_IMU, duration_s, seed=request.seed)
            classical_updates = run_updates_scenario(
                CLASSICAL_IMU, request.update_interval, duration_s, seed=request.seed
            )
            quantum_updates = run_updates_scenario(
                QUANTUM_IMU, request.update_interval, duration_s, seed=request.seed
            )

            experiments = [
                _convert_result(classical_coast),
                _convert_result(quantum_coast),
                _convert_result(classical_updates),
                _convert_result(quantum_updates),
            ]

            # Compute improvement factor
            c_err = classical_coast.get_final_pos_error_rms()
            q_err = quantum_coast.get_final_pos_error_rms()
            improvement_factor = c_err / q_err if q_err > 0 else None

        else:
            raise HTTPException(status_code=400, detail=f"Unknown scenario: {request.scenario}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return RunResponse(
        id=run_id,
        experiments=experiments,
        improvement_factor=improvement_factor,
    )

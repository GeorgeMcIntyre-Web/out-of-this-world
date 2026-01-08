"""Convert simulation results into frame snapshots for the web UI."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np

from outofthisworld.api_models import (
    BodySnapshot,
    CraftSnapshot,
    Frame,
    SensorReading,
    euler_rpy_to_quat,
    frame_to_dict,
    vec3_from_np,
)
from outofthisworld.sim.experiments import ExperimentConfig, ExperimentResults, load_config_from_yaml


def load_experiment_config(path: str) -> ExperimentConfig:
    config_path = Path(path)
    if config_path.exists() is False:
        raise FileNotFoundError(f"Config file not found: {path}")

    return load_config_from_yaml(config_path)


def _default_bodies() -> list[BodySnapshot]:
    # This project’s current scenarios are “deep space” with no gravity model.
    # Provide a minimal reference frame marker to orient the user.
    return [
        BodySnapshot(
            id="origin",
            name="System origin",
            kind="star",
            position_m=(0.0, 0.0, 0.0),
            radius_m=1_000_000.0,
            color="#ffcc66",
        )
    ]


def _star_tracker_events(config: ExperimentConfig) -> list[dict[str, object]]:
    if config.star_tracker_config is None:
        return []

    if np.isfinite(config.star_tracker_interval) is False:
        return []

    if config.star_tracker_interval <= 0:
        return []

    n_updates = int(config.duration_s // config.star_tracker_interval)
    if n_updates <= 0:
        return []

    events: list[dict[str, object]] = []
    for i in range(1, n_updates + 1):
        t_s = float(i * config.star_tracker_interval)
        events.append({"kind": "star_tracker_update", "t_s": t_s})
    return events


def _events_for_time(all_events: list[dict[str, object]], t_s: float) -> list[dict[str, object]]:
    if all_events:
        # Only keep events that happen exactly at this time step (within float tolerance).
        return [e for e in all_events if abs(float(e.get("t_s", -1.0)) - t_s) < 1e-9]
    return []


def experiment_to_frames(
    results: ExperimentResults,
    *,
    craft_id: str,
    craft_name: str,
    include_estimate: bool,
) -> list[Frame]:
    time = results.time
    if len(time) == 0:
        return []

    bodies = _default_bodies()
    events = _star_tracker_events(results.config)

    frames: list[Frame] = []
    for i, t in enumerate(time):
        t_s = float(t)

        craft: list[CraftSnapshot] = []

        true_pos = results.true_position[i]
        true_vel = results.true_velocity[i]
        true_att = results.true_attitude[i]

        craft.append(
            CraftSnapshot(
                id=f"{craft_id}.true",
                name=f"{craft_name} (true)",
                position_m=vec3_from_np(true_pos),
                velocity_mps=vec3_from_np(true_vel),
                attitude_quat=euler_rpy_to_quat(true_att),
                sensors=[
                    SensorReading(
                        id=f"{craft_id}.truth",
                        kind="truth",
                        value={},
                    )
                ],
            )
        )

        if include_estimate:
            est_pos = results.est_position[i]
            est_vel = results.est_velocity[i]
            est_att = results.est_attitude[i]

            pos_err = results.pos_error[i]
            vel_err = results.vel_error[i]
            att_err = results.att_error[i]
            pos_sigma = results.pos_sigma[i]
            vel_sigma = results.vel_sigma[i]
            att_sigma = results.att_sigma[i]

            craft.append(
                CraftSnapshot(
                    id=f"{craft_id}.est",
                    name=f"{craft_name} (estimated)",
                    position_m=vec3_from_np(est_pos),
                    velocity_mps=vec3_from_np(est_vel),
                    attitude_quat=euler_rpy_to_quat(est_att),
                    sensors=[
                        SensorReading(
                            id=f"{craft_id}.ins_ekf",
                            kind="ins_ekf",
                            value={
                                "pos_error_norm_m": float(np.linalg.norm(pos_err)),
                                "vel_error_norm_mps": float(np.linalg.norm(vel_err)),
                                "att_error_norm_rad": float(np.linalg.norm(att_err)),
                                "pos_sigma_3_norm_m": float(np.linalg.norm(pos_sigma) * 3.0),
                                "vel_sigma_3_norm_mps": float(np.linalg.norm(vel_sigma) * 3.0),
                                "att_sigma_3_norm_rad": float(np.linalg.norm(att_sigma) * 3.0),
                            },
                        )
                    ],
                )
            )

        frames.append(
            Frame(
                t_s=t_s,
                bodies=bodies,
                craft=craft,
                events=_events_for_time(events, t_s),
            )
        )

    return frames


def merge_frame_sets(frame_sets: list[list[Frame]]) -> list[Frame]:
    """Merge multiple frame lists (same timebase) into unified frames."""
    non_empty = [fs for fs in frame_sets if fs]
    if non_empty == []:
        return []

    base = non_empty[0]
    for frames in non_empty[1:]:
        if len(frames) != len(base):
            raise ValueError("Frame lists have different lengths")

    merged: list[Frame] = []
    for i in range(len(base)):
        t_s = base[i].t_s
        bodies = base[i].bodies

        craft: list[CraftSnapshot] = []
        events: list[dict[str, object]] = []

        for frames in non_empty:
            craft.extend(frames[i].craft)
            events.extend(frames[i].events)

        merged.append(Frame(t_s=t_s, bodies=bodies, craft=craft, events=events))

    return merged


def frames_to_dicts(frames: list[Frame]) -> list[dict[str, Any]]:
    return [frame_to_dict(f) for f in frames]


def with_overrides(
    config: ExperimentConfig,
    *,
    duration_s: float | None,
    dt_s: float | None,
) -> ExperimentConfig:
    updated = config
    if duration_s is not None:
        updated = replace(updated, duration_s=float(duration_s))

    if dt_s is not None:
        updated = replace(updated, dt=float(dt_s))

    return updated


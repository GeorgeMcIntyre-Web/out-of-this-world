"""View-layer API models for 3D simulation playback.

These models are intentionally thin and decoupled from the core physics / estimation
logic. They exist to provide a stable contract between the simulation backend and
the web dashboard.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Literal, TypeAlias

import numpy as np

Vec3: TypeAlias = tuple[float, float, float]
Quat: TypeAlias = tuple[float, float, float, float]  # (x, y, z, w)


@dataclass(frozen=True, slots=True)
class BodySnapshot:
    id: str
    name: str
    kind: Literal["star", "planet", "moon", "bh", "probe"]
    position_m: Vec3
    radius_m: float
    color: str | None = None


@dataclass(frozen=True, slots=True)
class SensorReading:
    id: str
    kind: str
    value: dict[str, float]


@dataclass(frozen=True, slots=True)
class CraftSnapshot:
    id: str
    name: str
    position_m: Vec3
    velocity_mps: Vec3
    attitude_quat: Quat
    sensors: list[SensorReading]


@dataclass(frozen=True, slots=True)
class Frame:
    t_s: float
    bodies: list[BodySnapshot]
    craft: list[CraftSnapshot]
    events: list[dict[str, object]]


def _as_jsonable(value: Any) -> Any:
    """Convert dataclasses/tuples/numpy to JSON-friendly primitives."""
    if is_dataclass(value):
        return _as_jsonable(asdict(value))

    if isinstance(value, dict):
        return {str(k): _as_jsonable(v) for k, v in value.items()}

    if isinstance(value, (list, tuple)):
        return [_as_jsonable(v) for v in value]

    if isinstance(value, np.ndarray):
        return _as_jsonable(value.tolist())

    if isinstance(value, (np.floating, np.integer)):
        return value.item()

    return value


def frame_to_dict(frame: Frame) -> dict[str, Any]:
    """Serialize a Frame to a JSON-friendly dict (no dataclass leakage)."""
    return _as_jsonable(frame)


def euler_rpy_to_quat(attitude_rpy_rad: np.ndarray) -> Quat:
    """Convert roll/pitch/yaw (rad) to quaternion (x,y,z,w).

    Convention: intrinsic rotations about x (roll), y (pitch), z (yaw).
    """
    roll = float(attitude_rpy_rad[0])
    pitch = float(attitude_rpy_rad[1])
    yaw = float(attitude_rpy_rad[2])

    cr = float(np.cos(roll * 0.5))
    sr = float(np.sin(roll * 0.5))
    cp = float(np.cos(pitch * 0.5))
    sp = float(np.sin(pitch * 0.5))
    cy = float(np.cos(yaw * 0.5))
    sy = float(np.sin(yaw * 0.5))

    # x,y,z,w
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy
    w = cr * cp * cy + sr * sp * sy

    return (x, y, z, w)


def vec3_from_np(v: np.ndarray) -> Vec3:
    return (float(v[0]), float(v[1]), float(v[2]))


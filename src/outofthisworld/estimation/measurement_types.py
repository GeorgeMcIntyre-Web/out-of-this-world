"""Measurement type definitions for estimation."""

from enum import Enum


class MeasurementType(Enum):
    """Types of gravitational measurements."""

    GRAVITY_MAGNITUDE = "gravity_magnitude"
    GRAVITY_VECTOR_INERTIAL = "gravity_vector_inertial"

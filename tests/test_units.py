"""Tests for unit conversion utilities."""

import pytest

from outofthisworld.physics.units import convert_units


def test_convert_km_to_m() -> None:
    """Test kilometer to meter conversion."""
    result = convert_units(1.0, "km", "m")
    assert result == 1000.0


def test_convert_m_to_km() -> None:
    """Test meter to kilometer conversion."""
    result = convert_units(1000.0, "m", "km")
    assert result == 1.0


def test_convert_deg_to_rad() -> None:
    """Test degree to radian conversion."""
    result = convert_units(180.0, "deg", "rad")
    assert abs(result - 3.141592653589793) < 1e-6


def test_convert_same_unit() -> None:
    """Test conversion with same unit returns unchanged."""
    result = convert_units(5.0, "m", "m")
    assert result == 5.0


def test_convert_unsupported() -> None:
    """Test unsupported conversion raises error."""
    with pytest.raises(ValueError, match="Unsupported unit conversion"):
        convert_units(1.0, "invalid", "m")

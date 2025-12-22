"""Unit conversions and dimensional analysis."""

# Unit conversion factors (to SI)
KM_TO_M: float = 1000.0
AU_TO_M: float = 1.496e11  # Astronomical unit
DEG_TO_RAD: float = 0.017453292519943295
HOUR_TO_SEC: float = 3600.0
DAY_TO_SEC: float = 86400.0


def convert_units(
    value: float,
    from_unit: str,
    to_unit: str,
) -> float:
    """
    Convert between common units.

    Args:
        value: Value to convert
        from_unit: Source unit (e.g., 'km', 'deg', 'hour')
        to_unit: Target unit (e.g., 'm', 'rad', 's')

    Returns:
        Converted value

    Raises:
        ValueError: If unit conversion not supported
    """
    if from_unit == to_unit:
        return value

    # Length conversions
    if from_unit == "km" and to_unit == "m":
        return value * KM_TO_M
    if from_unit == "m" and to_unit == "km":
        return value / KM_TO_M
    if from_unit == "au" and to_unit == "m":
        return value * AU_TO_M
    if from_unit == "m" and to_unit == "au":
        return value / AU_TO_M

    # Angle conversions
    if from_unit == "deg" and to_unit == "rad":
        return value * DEG_TO_RAD
    if from_unit == "rad" and to_unit == "deg":
        return value / DEG_TO_RAD

    # Time conversions
    if from_unit == "hour" and to_unit == "s":
        return value * HOUR_TO_SEC
    if from_unit == "s" and to_unit == "hour":
        return value / HOUR_TO_SEC
    if from_unit == "day" and to_unit == "s":
        return value * DAY_TO_SEC
    if from_unit == "s" and to_unit == "day":
        return value / DAY_TO_SEC

    raise ValueError(f"Unsupported unit conversion: {from_unit} -> {to_unit}")

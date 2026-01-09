"""IMU sensor profiles: classical vs quantum-class configurations."""

from dataclasses import dataclass
from typing import Final

# Unit conversion constants
UG_TO_M_S2: Final[float] = 9.80665e-6  # μg to m/s²
DEG_PER_HOUR_TO_RAD_S: Final[float] = 4.848136811095360e-6  # °/h to rad/s
PPM: Final[float] = 1e-6  # parts per million


@dataclass(frozen=True)
class IMUProfile:
    """
    IMU noise and error profile specification.

    All values stored in SI units internally.
    Factory methods provide convenient unit conversions.
    """

    # Accelerometer parameters
    accel_white_noise: float  # m/s² / √Hz (velocity random walk)
    accel_bias_instability: float  # m/s² (Allan deviation minimum)
    accel_turn_on_bias: float  # m/s² (1-σ initial bias)
    accel_scale_factor: float  # dimensionless (1-σ)

    # Gyroscope parameters
    gyro_white_noise: float  # rad/s / √Hz (angle random walk)
    gyro_bias_instability: float  # rad/s (Allan deviation minimum)
    gyro_turn_on_bias: float  # rad/s (1-σ initial bias)
    gyro_scale_factor: float  # dimensionless (1-σ)

    # Optional name for identification
    name: str = "custom"

    @classmethod
    def from_specs(
        cls,
        name: str,
        accel_white_noise_ug_sqrt_hz: float,
        accel_bias_instability_ug: float,
        accel_turn_on_bias_ug: float,
        accel_scale_factor_ppm: float,
        gyro_white_noise_deg_sqrt_h: float,
        gyro_bias_instability_deg_h: float,
        gyro_turn_on_bias_deg_h: float,
        gyro_scale_factor_ppm: float,
    ) -> "IMUProfile":
        """
        Create profile from common engineering units.

        Args:
            name: Profile identifier
            accel_white_noise_ug_sqrt_hz: Accelerometer white noise (μg/√Hz)
            accel_bias_instability_ug: Accelerometer bias instability (μg)
            accel_turn_on_bias_ug: Accelerometer turn-on bias 1-σ (μg)
            accel_scale_factor_ppm: Accelerometer scale factor error 1-σ (ppm)
            gyro_white_noise_deg_sqrt_h: Gyroscope white noise (°/√h)
            gyro_bias_instability_deg_h: Gyroscope bias instability (°/h)
            gyro_turn_on_bias_deg_h: Gyroscope turn-on bias 1-σ (°/h)
            gyro_scale_factor_ppm: Gyroscope scale factor error 1-σ (ppm)

        Returns:
            IMUProfile with values converted to SI units
        """
        # Convert accelerometer values: μg → m/s²
        accel_white = accel_white_noise_ug_sqrt_hz * UG_TO_M_S2
        accel_bi = accel_bias_instability_ug * UG_TO_M_S2
        accel_bias = accel_turn_on_bias_ug * UG_TO_M_S2
        accel_sf = accel_scale_factor_ppm * PPM

        # Convert gyroscope values: °/h → rad/s, °/√h → rad/s/√Hz
        # Note: °/√h needs sqrt(3600) factor for Hz conversion
        gyro_white = gyro_white_noise_deg_sqrt_h * DEG_PER_HOUR_TO_RAD_S / 60.0
        gyro_bi = gyro_bias_instability_deg_h * DEG_PER_HOUR_TO_RAD_S
        gyro_bias = gyro_turn_on_bias_deg_h * DEG_PER_HOUR_TO_RAD_S
        gyro_sf = gyro_scale_factor_ppm * PPM

        return cls(
            accel_white_noise=accel_white,
            accel_bias_instability=accel_bi,
            accel_turn_on_bias=accel_bias,
            accel_scale_factor=accel_sf,
            gyro_white_noise=gyro_white,
            gyro_bias_instability=gyro_bi,
            gyro_turn_on_bias=gyro_bias,
            gyro_scale_factor=gyro_sf,
            name=name,
        )


# Classical navigation-grade IMU (representative of high-quality FOG/RLG systems)
CLASSICAL_IMU: Final[IMUProfile] = IMUProfile.from_specs(
    name="classical",
    accel_white_noise_ug_sqrt_hz=100.0,  # 100 μg/√Hz
    accel_bias_instability_ug=10.0,  # 10 μg
    accel_turn_on_bias_ug=100.0,  # 100 μg (1-σ)
    accel_scale_factor_ppm=100.0,  # 100 ppm
    gyro_white_noise_deg_sqrt_h=0.01,  # 0.01 °/√h
    gyro_bias_instability_deg_h=0.01,  # 0.01 °/h
    gyro_turn_on_bias_deg_h=0.1,  # 0.1 °/h (1-σ)
    gyro_scale_factor_ppm=100.0,  # 100 ppm
)

# Quantum-class IMU (hypothetical, based on atom interferometry projections)
QUANTUM_IMU: Final[IMUProfile] = IMUProfile.from_specs(
    name="quantum",
    accel_white_noise_ug_sqrt_hz=1.0,  # 1 μg/√Hz (~100× better)
    accel_bias_instability_ug=0.1,  # 0.1 μg (~100× better)
    accel_turn_on_bias_ug=1.0,  # 1 μg (1-σ)
    accel_scale_factor_ppm=1.0,  # 1 ppm
    gyro_white_noise_deg_sqrt_h=0.0001,  # 0.0001 °/√h (~100× better)
    gyro_bias_instability_deg_h=0.0001,  # 0.0001 °/h (~100× better)
    gyro_turn_on_bias_deg_h=0.001,  # 0.001 °/h (1-σ)
    gyro_scale_factor_ppm=1.0,  # 1 ppm
)


def get_profile(name: str) -> IMUProfile:
    """
    Get IMU profile by name.

    Args:
        name: Profile name ('classical' or 'quantum')

    Returns:
        Corresponding IMUProfile

    Raises:
        ValueError: If profile name not recognized
    """
    profiles = {
        "classical": CLASSICAL_IMU,
        "quantum": QUANTUM_IMU,
    }
    if name not in profiles:
        valid = ", ".join(profiles.keys())
        raise ValueError(f"Unknown IMU profile '{name}'. Valid profiles: {valid}")
    return profiles[name]

# Quantum IMU Noise Model Specification

This document defines the inertial measurement unit (IMU) noise models used in this simulation framework, distinguishing between **classical navigation-grade** and **quantum-class** sensor characteristics.

## Overview

An IMU consists of two sensor triads:
- **Accelerometer**: Measures specific force (acceleration minus gravity)
- **Gyroscope**: Measures angular velocity

Each sensor axis experiences multiple noise and error sources that accumulate over time during inertial navigation.

## Noise Model Components

### 1. White Noise (Velocity/Angle Random Walk)

High-frequency noise that integrates into position/angle errors.

**Accelerometer** (Velocity Random Walk - VRW):
```
σ_a = N_a · √(Δt)
```
Where `N_a` is the noise density in m/s²/√Hz.

**Gyroscope** (Angle Random Walk - ARW):
```
σ_ω = N_ω · √(Δt)
```
Where `N_ω` is the noise density in rad/s/√Hz.

### 2. Bias Instability

Low-frequency bias fluctuations characterized by Allen variance minimum. Modeled as a first-order Gauss-Markov process:

```
ḃ = -b/τ + w_b
```

Where:
- `b` is the bias state
- `τ` is the correlation time (typically hours)
- `w_b` is driving white noise with PSD = 2σ²/τ

For simplicity, we approximate this as a random walk over simulation timescales:
```
b(t + Δt) = b(t) + σ_bi · √(Δt) · n
```
Where `n ~ N(0,1)` and `σ_bi` is the bias instability.

### 3. Turn-On Bias (Initial Bias)

Fixed bias present at sensor initialization, drawn from a normal distribution:
```
b_0 ~ N(0, σ_b0²)
```

### 4. Scale Factor Error

Multiplicative error in the sensor gain:
```
y_measured = (1 + s) · y_true + bias + noise
```
Where `s` is the scale factor error (dimensionless, typically ppm).

## Parameter Definitions

| Parameter | Symbol | Units | Description |
|-----------|--------|-------|-------------|
| Accel White Noise | `N_a` | μg/√Hz | Accelerometer noise density |
| Gyro White Noise | `N_ω` | °/h/√Hz | Gyroscope noise density |
| Accel Bias Instability | `σ_bi_a` | μg | Allan deviation minimum |
| Gyro Bias Instability | `σ_bi_ω` | °/h | Allan deviation minimum |
| Accel Turn-On Bias | `b_0_a` | μg | 1-σ initial bias uncertainty |
| Gyro Turn-On Bias | `b_0_ω` | °/h | 1-σ initial bias uncertainty |
| Scale Factor Error | `s` | ppm | 1-σ scale factor uncertainty |

## Sensor Profiles

### Classical Navigation-Grade IMU

Representative of high-quality MEMS or fiber-optic gyroscope (FOG) based systems.

| Parameter | Accelerometer | Gyroscope |
|-----------|--------------|-----------|
| White Noise | 100 μg/√Hz | 0.01 °/√h |
| Bias Instability | 10 μg | 0.01 °/h |
| Turn-On Bias (1σ) | 100 μg | 0.1 °/h |
| Scale Factor (1σ) | 100 ppm | 100 ppm |

### Quantum-Class IMU (Hypothetical)

Representative of atom interferometry or other quantum sensing technologies. These values are **hypothetical projections** based on laboratory demonstrations and theoretical limits.

| Parameter | Accelerometer | Gyroscope |
|-----------|--------------|-----------|
| White Noise | 1 μg/√Hz | 0.0001 °/√h |
| Bias Instability | 0.1 μg | 0.0001 °/h |
| Turn-On Bias (1σ) | 1 μg | 0.001 °/h |
| Scale Factor (1σ) | 1 ppm | 1 ppm |

> [!IMPORTANT]
> The quantum-class parameters represent ~100× improvement over classical sensors. These are projections for simulation purposes, not validated hardware specifications.

## Assumptions

1. **Sensor axes are orthogonal**: No misalignment errors modeled
2. **Temperature stable**: No thermal drift modeled
3. **No g-sensitivity**: Gyro output not affected by acceleration
4. **White noise is uncorrelated**: No colored noise shaping
5. **Bias instability approximated as random walk**: Valid for simulation timescales << correlation time
6. **Linear scale factor**: No higher-order nonlinearities

## Non-Assumptions (What We Don't Claim)

1. **Not claiming real quantum sensor performance**: Parameters are hypothetical
2. **Not modeling atom interferometer physics**: This is a noise-equivalent model
3. **Not accounting for SWaP constraints**: Size, weight, power not considered
4. **Not modeling environmental effects**: Vibration, temperature, magnetic fields ignored
5. **Not validated against flight data**: Simulation-only framework

## Implementation Notes

The IMU model in this framework:
- Generates 6-DOF measurements (3 accel + 3 gyro) at each timestep
- Applies turn-on bias at initialization
- Accumulates bias instability via random walk
- Adds white noise scaled by √Δt
- Applies scale factor error to true values
- Supports deterministic seeding for reproducibility

## References

1. IEEE Std 647-2006, "Standard Specification Format Guide and Test Procedure for Single-Axis Laser Gyros"
2. Titterton, D. and Weston, J., "Strapdown Inertial Navigation Technology," 2nd Ed., IET, 2004
3. Kitching, J., "Chip-scale atomic devices," Applied Physics Reviews, 2018 (for quantum sensor projections)

## Conversion Factors

For implementation, convert to SI base units:
- 1 μg = 9.80665 × 10⁻⁶ m/s²
- 1 °/h = 4.848 × 10⁻⁶ rad/s
- 1 ppm = 10⁻⁶

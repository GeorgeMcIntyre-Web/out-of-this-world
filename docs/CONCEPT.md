# Cosmic Compass Concept

## Overview

The "cosmic compass" concept explores how advanced sensing and inference techniques could constrain spacecraft location, orientation, and trajectory in extreme environments. The goal is to develop methods for navigation and state estimation that rely on gravitational and inertial measurements, particularly in regions where traditional navigation (GPS, star trackers) may be unavailable or degraded.

## Core Idea

By fusing multiple measurement modalities—orbital dynamics, gravitational lensing, precision timing, inertial drift, and interferometric phase measurements—we can infer spacecraft state (position, velocity, attitude) and potentially detect subtle gravitational signatures around compact objects.

## What Can Be Measured from Far Away vs Close

### Far-Field Measurements (> 1000 km)

- **Orbital dynamics**: Period, semi-major axis, eccentricity from long-term tracking
- **Gravitational lensing**: Light deflection, time delays (requires background sources)
- **Gravitational waves**: Strain measurements (requires dedicated detectors)
- **Timing anomalies**: Clock drift due to gravitational redshift
- **Frame-dragging effects**: Precession of orbital planes (very weak, requires long baselines)

### Near-Field Measurements (< 1000 km)

- **Inertial acceleration**: Direct measurement via accelerometers or atom interferometers
- **Gravitational gradients**: Tidal forces from nearby masses
- **Rotation sensing**: Gyroscope measurements, Sagnac effects
- **Precision timing**: Local clock comparisons, frequency shifts
- **Orbital perturbations**: Deviations from two-body motion

## Signals We'd Look For

### 1. Gravitational Waves

- **Strain amplitude**: ~10^-21 for LIGO-class events, much weaker for continuous sources
- **Frequency range**: 10^-4 to 10^4 Hz depending on source
- **Challenges**: Requires long baselines, extreme isolation from noise

### 2. Timing

- **Clock drift**: Gravitational redshift causes frequency shifts
- **Time delays**: Shapiro delay, lensing delays
- **Pulsar timing**: Use millisecond pulsars as natural clocks
- **Precision**: Nanosecond-level timing enables meter-level position accuracy

### 3. Lensing

- **Light deflection**: Angular deflection of background stars/sources
- **Time delays**: Multiple images arrive at different times
- **Magnification**: Brightness changes
- **Requirements**: Need background sources, precise astrometry

### 4. Orbital Dynamics Constraints

- **Two-body motion**: Classical Keplerian orbits
- **Perturbations**: Third-body effects, non-spherical gravity, drag
- **Relativistic corrections**: Perihelion precession, frame-dragging
- **Inference**: Fit orbital parameters to observed trajectory

### 5. Inertial Drift

- **Bias instability**: Long-term drift in accelerometers/gyros
- **Allan deviation**: Characterizes noise processes
- **Integration errors**: Position/velocity errors accumulate over time
- **Mitigation**: Requires external references or sensor fusion

### 6. Interferometric Phase

- **Atom interferometry**: Phase shift proportional to acceleration/rotation
- **Laser interferometry**: Path length changes, gravitational wave detection
- **Sensitivity**: Can reach 10^-9 g levels for acceleration
- **Challenges**: Vacuum, thermal stability, vibration isolation

## Hypotheses (Not Claims)

This repository explores the following hypotheses:

1. **Multi-modal fusion** can improve state estimation accuracy beyond single-sensor limits
2. **Gravitational signatures** around compact objects may be detectable through indirect measurements
3. **Constellation architectures** can provide distributed sensing and redundancy
4. **Atom interferometry** can provide high-precision inertial measurements in space
5. **Timing networks** can enable precise relative positioning

All models are grounded in classical mechanics and perturbative general relativity. We explicitly avoid claims about:
- Proving other universes or exotic physics
- Detecting signals that violate known physics
- Flight-ready performance without validation

## Scope Limitations

For v0.1, we focus on:

- Classical orbital mechanics (two-body, perturbations)
- Simplified sensor models (IMU bias/noise, interferometer phase)
- Linear and extended Kalman filtering
- Simulation frameworks

We explicitly exclude:

- Full general relativistic simulations (black hole interiors, event horizons)
- Complete atom interferometer physics (simplified models only)
- Flight qualification or hardware validation
- Real mission data (synthetic data only)

## Where Infinities Appear and How Engineers Avoid Them

### Problem: Singularities in GR

General relativity predicts singularities at event horizons and centers of black holes. These are mathematical infinities that break numerical simulations.

### Engineering Solutions

1. **Effective models**: Use post-Newtonian approximations far from horizons
2. **Coordinate choices**: Use regular coordinates (e.g., Kerr-Schild) that avoid coordinate singularities
3. **Numerical regularization**: Add small cutoffs or smoothing terms
4. **Perturbative approach**: Treat GR effects as small corrections to Newtonian gravity
5. **Event horizon avoidance**: Stay outside Schwarzschild radius in simulations

### Practical Approach in This Repo

- We model orbits outside event horizons (r > 2GM/c²)
- Use classical mechanics with perturbative GR corrections
- Avoid coordinate systems that become singular
- Use numerical integrators with adaptive step sizes
- Clearly label where models break down


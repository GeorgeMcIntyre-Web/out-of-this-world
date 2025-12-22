# Roadmap

## Version 0.1 — Scaffold and Core

**Status**: ✅ Complete

**Deliverables**:
- ✅ Repository structure and documentation
- ✅ Basic orbit propagation (two-body)
- ✅ IMU sensor model (bias + noise)
- ✅ Simplified interferometer model
- ✅ Extended Kalman filter implementation
- ✅ Runnable demo script
- ✅ CI/CD pipeline
- ✅ Test suite

## Version 0.2 (Current) — Extended Simulation

**Status**: ✅ Complete

**Deliverables**:
- ✅ J2 orbital perturbations (Earth oblateness)
- ✅ Improved EKF with gravitational measurement models
  - ✅ Gravity vector in inertial frame (default)
  - ✅ Gravity magnitude mode (legacy)
- ✅ Visualization utilities (6-plot demo output)
- ✅ Measurement model refactoring (clean, testable API)
- ✅ Finite-difference Jacobian validation tests
- ✅ Documentation updates

**Deferred to v0.3**:
- Particle filter implementation
- Sensor model expansions (gyroscope, magnetometer stubs)
- Performance benchmarks

## Version 0.3 — Sensor Model Refinements

**Target**: Q3 2025

**Deliverables**:
- Refined interferometer model (phase noise, systematic errors)
- Timing models (clock drift, synchronization)
- Lensing effects (simplified, far-field)
- Gravitational wave detection framework (stub)
- Allan deviation analysis tools
- Sensor calibration models

## Version 0.4 — Constellation Studies

**Target**: Q4 2025

**Deliverables**:
- Multi-spacecraft simulation framework
- Distributed estimation (consensus filters)
- Inter-spacecraft ranging models
- Communication link modeling
- Constellation optimization tools
- Case studies (example missions)

## Version 1.0 — Reference Design

**Target**: 2026

**Deliverables**:
- Complete reference design document
- Validated sensor models (against literature/benchmarks)
- Mission architecture studies
- Risk analysis updates
- Performance trade-off analysis
- Open-source release preparation

## Beyond 1.0

Potential directions (not committed):

- Hardware-in-the-loop testing
- Real mission data integration
- Advanced GR models (Kerr metric, frame-dragging)
- Machine learning for anomaly detection
- Collaborative filtering across constellations

## Milestone Criteria

Each version milestone requires:

- All tests passing
- Documentation complete
- Code review ready
- Demo scenarios working
- No critical bugs

## Contributing to Roadmap

See [CONTRIBUTING.md](../CONTRIBUTING.md) for how to propose new features or milestones.


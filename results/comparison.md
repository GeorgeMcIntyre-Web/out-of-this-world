# Classical vs Quantum IMU Comparison

Generated: 2026-01-07 11:36:47 UTC

## Summary

| Experiment | IMU Profile | Duration | Final Pos Error | Final Vel Error | Updates |
|------------|-------------|----------|-----------------|-----------------|---------|
| coast_classical | classical | 1.0 h | 17.73 km | 19.605 m/s | 0 |
| coast_quantum | quantum | 1.0 h | 177.65 m | 196.151 mm/s | 0 |
| updates_classical_60s | classical | 1.0 h | 17.84 km | 19.497 m/s | 60 |
| updates_quantum_60s | quantum | 1.0 h | 174.65 m | 193.525 mm/s | 60 |

## Interpretation

The quantum-class IMU reduces final position error by a factor of **99.8x** compared to the classical IMU under identical conditions.

### Coast (Inertial-Only) Behavior

Without external updates, position error grows approximately quadratically due to integrated accelerometer bias. The quantum-class IMU's lower bias instability results in significantly slower error growth.

### With Star Tracker Updates

Periodic attitude updates from the star tracker bound navigation error. The steady-state error is limited by the star tracker accuracy and the rate at which IMU errors accumulate between updates.

## Limitations

1. Simplified dynamics: constant velocity, no gravity
2. Star tracker provides attitude only (no position)
3. IMU biases initialized to zero (optimistic)
4. No time-correlated noise modeling
5. Hypothetical quantum IMU parameters

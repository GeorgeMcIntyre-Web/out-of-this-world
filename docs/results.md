# Default Run Results

This document presents results from the default 1-hour comparison run.

## Summary

| Scenario | IMU Profile | Final Position Error | Final Velocity Error | Updates |
|----------|-------------|---------------------|---------------------|---------|
| coast_classical | classical | ~17.7 km | ~10 m/s | 0 |
| coast_quantum | quantum | ~177 m | ~0.1 m/s | 0 |
| updates_classical_60s | classical | ~17.9 km | ~10 m/s | 60 |
| updates_quantum_60s | quantum | ~175 m | ~0.1 m/s | 60 |

## Key Findings

### 1. Quantum IMU Improvement Factor: ~100×

Under default conditions, the quantum-class IMU reduces position error by approximately **100×** compared to the classical navigation-grade IMU. This matches the ~100× improvement in noise parameters defined in the sensor profiles.

### 2. Attitude Updates Have Limited Direct Impact on Position

Star tracker updates primarily correct **attitude** errors. In our simulation with constant thrust, attitude errors cause the accelerometer to be misrotated when transforming to the navigation frame. Correcting attitude thus prevents the accumulation of velocity/position errors from misrotated acceleration.

However, the dominant error source for position is **accelerometer bias**, which star tracker updates do not directly observe. Position error reduction from updates is therefore modest compared to the benefit of a better IMU.

### 3. Error Growth is Approximately Quadratic

In coast mode, position error grows approximately as t² due to the double-integration of accelerometer bias:
- Bias → velocity error (∝ t)
- Velocity error → position error (∝ t²)

## Interpretation

### Under These Assumptions, Results Show:

1. **A 100× improvement in IMU noise parameters yields ~100× improvement in navigation accuracy** for inertial-only coasting over 1 hour.

2. **Star tracker aiding bounds attitude error** but has limited impact on position error dominated by accelerometer bias.

3. **For deep-space missions with hour-scale autonomous navigation**, quantum-class IMUs could reduce position uncertainty from tens of kilometers to hundreds of meters.

### Caveats

- These are simulation results with hypothetical quantum IMU parameters
- Real navigation systems would include additional sensors (GPS, ground-based ranging)
- The simplified dynamics (constant thrust, no gravity) affect error growth rates
- Initial bias calibration significantly impacts results

## Plots

After running `uv run ootw --scenario compare`, the following plots are generated:

### Position Error Comparison

`results/comparison.png` - Shows position error vs time for classical and quantum IMUs in coast mode.

### Cadence Sweep

`results/cadence_sweep_quantum.png` - Shows how final error varies with star tracker update interval.

## Reproducing These Results

```bash
# Generate all results
uv run ootw --scenario compare --duration 1.0 --seed 42

# View outputs
cat results/comparison.md
```

## Limitations

1. **No gravity modeling**: Deep space only, no orbital mechanics effects
2. **Constant thrust**: Real missions have varying acceleration profiles
3. **No position aiding**: Only attitude updates, no range/position measurements
4. **Simplified error model**: Markov processes approximated as random walk
5. **No initial calibration**: Biases start at zero knowledge
6. **Hypothetical parameters**: Quantum IMU specs are projections, not hardware measurements

# Experiment Descriptions

This document describes the simulation scenarios and how to reproduce them.

## Scenarios

### 1. COAST (Inertial-Only)

**Description**: Spacecraft navigates using only IMU measurements, with no external updates.

**Dynamics**: 
- Constant thrust of 0.1 m/s² along body x-axis
- Initial velocity: 1000 m/s
- Duration: 1 hour

**Sensors**:
- IMU: Classical or Quantum-class profile
- No star tracker updates

**Purpose**: Quantify how navigation error grows without external aiding, comparing classical vs quantum-class IMU performance.

**Expected behavior**: Position error grows approximately as t² due to integrated accelerometer bias and attitude-dependent acceleration misrotation.

### 2. UPDATES (Star Tracker Aided)

**Description**: Spacecraft navigates with periodic star tracker attitude updates.

**Dynamics**: Same as COAST

**Sensors**:
- IMU: Classical or Quantum-class profile
- Star tracker: 5 arcsec accuracy at configurable update interval

**Purpose**: Quantify how attitude updates bound navigation error by correcting the rotation used to transform accelerometer measurements.

**Expected behavior**: Error grows between updates but is partially reset at each update. Steady-state error depends on update cadence.

### 3. CADENCE SWEEP

**Description**: Sweep star tracker update interval from 10s to 3600s to characterize error vs cadence relationship.

**Intervals tested**: 10, 30, 60, 120, 300, 600, 1800, 3600 seconds

**Purpose**: Generate error-vs-cadence curve for mission trade studies.

### 4. COMPARE

**Description**: Run all four combinations (Classical/Quantum × Coast/Updates) and generate comparison plots/reports.

**Purpose**: Demonstrate the full research question: quantify quantum IMU benefit for both aided and unaided navigation.

## How to Reproduce

### Prerequisites

```bash
# Clone and install
git clone https://github.com/your-org/out-of-this-world.git
cd out-of-this-world
uv sync --extra dev
```

### Run Default Comparison

```bash
# Generate comparison of all scenarios (1 hour simulation)
uv run ootw --scenario compare --duration 1.0

# Outputs saved to results/
# - comparison.png: Position error comparison plot
# - comparison.md: Markdown summary report
```

### Run Individual Scenarios

```bash
# Coast with classical IMU
uv run ootw --scenario coast --imu classical --duration 1.0 --seed 42

# Coast with quantum IMU
uv run ootw --scenario coast --imu quantum --duration 1.0 --seed 42

# Updates with 60-second star tracker interval
uv run ootw --scenario updates --imu quantum --duration 1.0

# Cadence sweep
uv run ootw --scenario sweep --imu quantum --duration 1.0
```

### Run from Config File

```bash
# Use custom configuration
uv run ootw --config configs/classical.yaml
uv run ootw --config configs/quantum.yaml
```

### Output Files

Each run produces:
- `{prefix}_error.png`: Position/velocity error vs time plot
- `{prefix}_results.json`: Machine-readable results
- `{prefix}_timeseries.csv`: Time-series data for external analysis
- `{prefix}_report.md`: Human-readable summary

## Metrics

| Metric | Description | Units |
|--------|-------------|-------|
| Final Position Error | RMS position error at end of simulation | meters |
| Final Velocity Error | RMS velocity error at end of simulation | m/s |
| Maximum Position Error | Peak position error during simulation | meters |
| Improvement Factor | Ratio of classical to quantum error | dimensionless |

## Reproducibility

All experiments are deterministic when using the same:
- Random seed (`--seed`)
- IMU profile
- Star tracker configuration
- Duration and time step

The default seed is 42. Different seeds will produce different realizations of sensor noise but should yield statistically similar results.

## Monte Carlo Analysis

For statistical analysis, run multiple seeds:

```python
from outofthisworld.sim.experiments import run_coast_scenario
from outofthisworld.sensors.imu_profiles import CLASSICAL_IMU

errors = []
for seed in range(100):
    result = run_coast_scenario(CLASSICAL_IMU, duration_s=3600.0, seed=seed)
    errors.append(result.get_final_pos_error_rms())

print(f"Mean error: {np.mean(errors):.1f} m")
print(f"Std error: {np.std(errors):.1f} m")
```

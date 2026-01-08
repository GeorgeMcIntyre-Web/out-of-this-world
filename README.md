# OutOfThisWorld

A research-grade simulation framework for deep-space navigation using quantum-class inertial sensors.

## Thesis

> **Research Question**: Given a quantum-class IMU noise model (characterized by ~100× lower bias instability and white noise compared to classical navigation-grade IMUs), how does navigation error grow over time under inertial-only propagation, and to what extent do periodic external updates (star tracker) reduce accumulated error compared to a classical IMU baseline?

### Measurable Metrics

| Metric | Description |
|--------|-------------|
| **Position RMS Error** | Root-mean-square position error vs time (m) |
| **Velocity RMS Error** | Root-mean-square velocity error vs time (m/s) |
| **Attitude Error** | 3-sigma attitude error vs time (deg) |
| **Cadence Sensitivity** | Final error vs update interval sweep |

### Key Findings (Default Run)

Under the default 1-hour deep-space maneuvering scenario:
- **Classical IMU**: Position error grows to ~17.7 km (inertial-only)
- **Quantum IMU**: Position error grows to ~177 m (inertial-only) — **100× improvement**
- **With Updates**: Star tracker at 60s cadence shows similar improvement ratio

*Run `uv run ootw --scenario compare` to reproduce.*

## Overview

OutOfThisWorld investigates how advanced sensing and inference techniques could constrain spacecraft location, orientation, and trajectory in extreme environments. This repository provides simulation frameworks, sensor models, estimation algorithms, and architectural studies for next-generation inertial and gravity sensing payloads.

## What Problem Are We Exploring?

- **Detecting subtle gravitational signatures** around compact objects (neutron stars, black holes) through indirect measurements
- **Next-generation inertial sensing** using atom interferometry and precision timing
- **Fusion of multi-modal measurements** (orbital dynamics, lensing, timing, inertial drift) to infer spacecraft state
- **Constellation architectures** for distributed sensing and navigation

## What This Repo Is

- **Simulation framework** for orbital dynamics, sensor models, and estimation
- **Architecture studies** for modular payload design
- **Algorithm implementations** for Kalman filtering, particle filtering, and sensor fusion
- **Placeholder BOM** and risk analysis for space-hardenable payloads
- **Research sandbox** for testing hypotheses about measurable signals

## What This Repo Is Not

- **Not a claim** of proving other universes or exotic physics
- **Not pseudoscience** — all models are grounded in classical and perturbative GR
- **Not flight-ready code** — this is research-grade simulation and analysis
- **Not a complete mission design** — components are modular and experimental

## Quickstart

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/out-of-this-world.git
cd out-of-this-world

# Install with uv
uv sync

# Or with pip
python -m pip install -e .
```

### Run Tests

```bash
# With uv
uv run pytest

# Or with pip
pytest
```

### Run Experiments

```bash
# Run COAST scenario (inertial-only, classical IMU)
uv run ootw --scenario coast --config configs/classical.yaml

# Run COAST scenario (quantum-class IMU)
uv run ootw --scenario coast --config configs/quantum.yaml

# Run UPDATES scenario (with star tracker)
uv run ootw --scenario updates --config configs/quantum.yaml

# Run cadence sweep (vary update interval)
uv run ootw --scenario sweep --config configs/quantum.yaml

# Compare classical vs quantum
uv run ootw --scenario compare

# All results saved to results/ directory
```

### Web Visualization

The project includes a full-stack visualization dashboard.

1. **Start the Backend API**:
   ```bash
   uv run uvicorn api.main:app --reload
   # Runs on http://localhost:8000
   ```

2. **Start the Frontend Dashboard**:
   ```bash
   cd web
   npm install  # First time only
   npm run dev
   # Runs on http://localhost:5173
   ```

### Run Legacy Demo

```bash
# With uv
uv run python scripts/demo_run.py

# Or with pip
python scripts/demo_run.py
```

### Linting and Formatting

```bash
# Check linting
uv run ruff check .

# Format code
uv run ruff format .

# Type checking
uv run mypy src
```

## Project Structure

```
out-of-this-world/
├── src/outofthisworld/    # Main package
│   ├── physics/           # Orbital mechanics, relativity, units
│   ├── sensors/           # IMU, interferometer, noise models
│   ├── estimation/        # Kalman filters, particle filters
│   └── sim/               # Scenario runner, simulation framework
├── tests/                 # Unit tests
├── scripts/               # Demo and utility scripts
└── docs/                  # Documentation
```

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for detailed milestones.

- **v0.1** (current): Repository scaffold, basic orbit propagation, sensor models, EKF
- **v0.2**: Extended simulation scenarios, particle filtering, sensor model expansions
- **v0.3**: Interferometer model refinements, timing models, lensing effects
- **v0.4**: Constellation studies, distributed estimation
- **v1.0**: Reference design document, validated sensor models

## Documentation

- [Concept Overview](docs/CONCEPT.md) — Cosmic compass concept and measurable signals
- [Architecture](docs/ARCHITECTURE.md) — Modular design and system components
- [Roadmap](docs/ROADMAP.md) — Development milestones
- [BOM](docs/BOM.md) — Placeholder bill of materials for payload concept
- [Risk Register](docs/RISK_REGISTER.md) — Technical and programmatic risks
- [Glossary](docs/GLOSSARY.md) — Terminology and definitions

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License — see [LICENSE](LICENSE) for details.

## Disclaimer

This is research software. Models are simplified and intended for exploration, not flight qualification. All BOM entries and performance estimates are placeholders and assumptions.

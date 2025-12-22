# OutOfThisWorld

A research and engineering sandbox for exploring "cosmic compass" concepts: space navigation and sensing through gravitational and inertial measurements.

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

## What's Implemented (v0.2)

- **J2 orbital perturbations**: Earth oblateness effects in orbit propagation
- **Extended Kalman filter**: With gravitational measurement models (vector and magnitude modes)
- **Gravitational measurement models**: Gravity vector in inertial frame (default) and magnitude modes
- **Visualization**: Demo script generates orbit plots, error analysis, and measurement comparisons
- **Comprehensive tests**: 32 tests including finite-difference Jacobian validation

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

### Run Demo

```bash
# With uv
uv run python scripts/demo_run.py

# Or with pip
python scripts/demo_run.py
```

The demo script runs a circular orbit simulation with:
- J2 perturbations enabled
- Gravity vector measurements (inertial frame)
- Extended Kalman filter state estimation
- Visualization plots saved to `demo_results.png`

**Note**: This demo uses simplified "gravimeter" measurements (gravity vector in inertial frame) to keep the estimation problem observable in a toy setup. Real accelerometers in free-fall would measure zero acceleration, not gravitational acceleration.

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

- **v0.1**: Repository scaffold, basic orbit propagation, sensor models, EKF
- **v0.2** (current): J2 perturbations, improved EKF with gravimeter modes, visualization
- **v0.3**: Particle filter, sensor model expansions (gyroscope, magnetometer), timing models
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

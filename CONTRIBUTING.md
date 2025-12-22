# Contributing to OutOfThisWorld

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/out-of-this-world.git`
3. Install dependencies: `uv sync` (or `pip install -e .`)
4. Create a branch: `git checkout -b feature/your-feature-name`

## Code Standards

### Style

- Use **guard clauses** — avoid `else` and `elseif` where possible
- Keep nesting ≤ 2 levels
- Use `is` / `is not` instead of `!` for comparisons
- Prefer compact, readable code
- Type hints everywhere practical
- Docstrings: short, engineering style

### Formatting and Linting

```bash
# Format code
ruff format .

# Check linting
ruff check .

# Type checking
mypy src
```

All checks must pass before submitting a PR.

### Testing

- Write tests for new features
- Ensure all tests pass: `pytest`
- Aim for reasonable coverage (not 100%, but meaningful)

## Pull Request Process

1. Ensure your code follows the style guidelines
2. Run tests and linting
3. Update documentation if needed
4. Create a pull request with a clear description
5. Reference any related issues

## Commit Messages

Use clear, descriptive commit messages:

```
Add EKF implementation for sensor fusion
Fix IMU bias model initialization
Update BOM with thermal estimates
```

## Documentation

- Update relevant docs in `docs/` for significant changes
- Add docstrings to new functions and classes
- Update README if adding new features or changing setup

## Questions?

Open an issue for discussion or questions about the project direction.


# Talos

![Talos hero](docs/images/talos-final.jpg)

> Deterministic WIP enforcement that turns workload pressure into guardrails against overload and thrash.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](pyproject.toml)
[![CI](https://github.com/Spitfire-Cowboy/talos/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/Spitfire-Cowboy/talos/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Spitfire-Cowboy/talos/graph/badge.svg)](https://codecov.io/gh/Spitfire-Cowboy/talos)

Named after Talos, the bronze guardian of Crete, this project is built around protection through deterministic guardrails.

## What Talos is

Talos is a deterministic enforcement engine for work-in-progress pressure.

The public code in this repository currently includes a small Python scoring core that:

- computes enforcement levels from workload and backlog signals
- persists cycle counters across runs
- stays dependency-light and deterministic

## Platform support

The current Talos Python core has been verified in local development on macOS and in a Linux container.

### Verified Linux scope

Linux verification currently means:

- the package installs from source in `python:3.12-slim`
- the current test suite passes in that container
- the public Python core behaves the same there as it does on macOS

This does **not** currently claim:

- a Linux service wrapper
- a Linux-specific daemon setup
- an MLX deployment on Linux
- broader distribution testing beyond the containerized Python environment above

The currently observed MLX-oriented service deployment is separate from the core package and is still documented as a macOS-specific setup.

## What ships today

This repository currently ships:

- the Python scoring core in `talos/`
- automated tests for scoring and persistence behavior
- GitHub Actions CI for test and coverage runs
- Codecov and CodeRabbit configuration files
- repository documentation
- verified notes about the current MLX-oriented deployment shape

It does **not** currently ship:

- packaged binaries
- a public MLX monitor implementation
- end-to-end production deployment automation

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .[dev]
pytest --cov=talos --cov-report=term-missing --cov-report=xml
```

## CLI

```bash
talos score --wip-total 10 --global-max 10 --at-cap alpha --backlog-delta 0 --cycles-at-current-level 2
```

## MLX deployment notes

A Talos process observed on the maintainer's machine is running as a Python service that watches MLX-related logs and writes JSONL summaries.

See [Running with MLX](RUNNING_WITH_MLX.md).

## Documentation

- [Documentation overview](docs/OVERVIEW.md)
- [Running with MLX](RUNNING_WITH_MLX.md)
- [Testing](TESTING.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## License

[Apache License 2.0](LICENSE)

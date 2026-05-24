# Testing

## Local

Run the Talos test suite locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .[dev]
pytest --cov=talos --cov-report=term-missing --cov-report=xml
```

## Linux verification

The current Talos Python core has also been verified in a fresh `python:3.12-slim` Linux container.

The verification flow used:

```bash
docker run --rm \
  -v "$PWD":/src \
  -w /src \
  python:3.12-slim \
  bash -lc '
    python -m venv .venv-linux-test
    . .venv-linux-test/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -e .[dev]
    pytest --cov=talos --cov-report=term-missing --cov-report=xml
  '
```

What this verifies today:

- package install from source on Linux
- test execution on Linux
- parity for the current public Python core

What this does not verify yet:

- a Linux daemon/service wrapper
- Linux packaging or distribution artifacts
- an MLX deployment on Linux

## Continuous integration

GitHub Actions runs:

- a Python version matrix on pushes and pull requests
- coverage upload from the Python 3.12 test run
- a packaging job that builds distribution artifacts and smoke-tests the installed wheel

## Codecov

This repository includes `codecov.yml` plus a GitHub Actions upload step using `codecov/codecov-action@v5`.

Recommended setup for this public repository:

1. Install the Codecov GitHub app for `Spitfire-Cowboy/talos`.
2. In Codecov settings, allow tokenless uploads for public repositories **or** add `CODECOV_TOKEN` if you prefer token-based uploads.
3. Open a pull request and confirm that `coverage.xml` is processed.

## CodeRabbit

This repository includes a root `.coderabbit.yaml` file so review behavior is version controlled.

To finish setup:

1. Install the CodeRabbit GitHub app for `Spitfire-Cowboy/talos`.
2. Open a pull request to let CodeRabbit read the repository config from the feature branch under review.

# Testing

## Local

Run the Talos test suite locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .[dev]
pytest --cov=talos --cov-report=term-missing --cov-report=xml
```

## Continuous integration

GitHub Actions runs the test suite on pushes to `main`, `develop`, and `feature/**`, and on pull requests.

## Codecov

The workflow uploads `coverage.xml` to Codecov when the repository is configured for uploads.

To finish Codecov setup:

1. Install the Codecov GitHub app for this repository.
2. If Codecov requires upload tokens for this repository, add `CODECOV_TOKEN` as a repository secret.
3. Open a pull request to confirm coverage reports appear.

## CodeRabbit

This repository includes a root `.coderabbit.yaml` file so repository-level review behavior is version controlled once the CodeRabbit GitHub app is installed.

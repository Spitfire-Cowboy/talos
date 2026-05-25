# Talos Documentation Overview

## Available documents

- `README.md` — top-level project overview, platform note, quick start, runtime CLI usage, and API example
- `RUNNING_WITH_MLX.md` — verified notes about the observed MLX-oriented deployment shape
- `TESTING.md` — local test, CI, Codecov, and CodeRabbit setup notes
- `CONTRIBUTING.md` — contribution guidance for the current repository contents
- `SECURITY.md` — security reporting guidance

## Current scope

This repository currently publishes the Talos Python scoring core, snapshot/runtime helpers, a small CLI, tests, and repository documentation.

## Platform note

The public Python core has been verified on macOS and in a Linux container.

Current Linux verification is limited to source install plus test execution in `python:3.12-slim`.

The documented MLX-oriented service deployment remains a macOS-specific setup.

## Not currently published

This repository does not currently publish:

- a public service launcher
- a public MLX monitor implementation
- end-to-end setup instructions for general deployment

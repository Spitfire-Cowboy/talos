# Talos

> Deterministic WIP enforcement that turns workload pressure into guardrails against overload and thrash.

![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
![Status: Docs only](https://img.shields.io/badge/status-docs--only-lightgrey.svg)
![Core: Python](https://img.shields.io/badge/core-Python-3776AB.svg)

Named after Talos, the bronze guardian of Crete, this project is built around protection through deterministic guardrails.

---

Talos is a deterministic enforcement engine for work-in-progress pressure.

From the code and running deployment reviewed so far, Talos computes enforcement levels from workload and backlog signals, then raises guardrails as limits are exceeded.

## What ships today

This public repository currently ships documentation and repository scaffolding only:

- project and policy documents
- GitHub issue and pull request templates
- public-safety checks for publication
- verified notes about the current MLX-oriented deployment shape

It does **not** currently publish:

- application source code
- packaged binaries
- end-to-end setup for production use
- a public MLX monitor implementation

## MLX deployment notes

A Talos process observed on the maintainer's machine is running as a Python service that watches MLX-related logs and writes JSONL summaries.

See [Running with MLX](RUNNING_WITH_MLX.md).

## Repository checks

```bash
bash scripts/check-public-safety.sh
bash scripts/check-public-safety.sh --strict-public
```

## Documentation

- [Documentation overview](docs/OVERVIEW.md)
- [Running with MLX](RUNNING_WITH_MLX.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Public repo checklist](PUBLIC_REPO_CHECKLIST.md)

## License

[Apache License 2.0](LICENSE)

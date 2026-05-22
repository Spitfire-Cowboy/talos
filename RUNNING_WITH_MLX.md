# Running Talos with MLX

This repository does not currently include the MLX monitor implementation or service wrapper.

What can be verified from the maintainer's machine is the deployment pattern:

- Talos runs as a Python process.
- It watches MLX-related log files.
- It writes summary output to a JSONL file.
- On macOS, it can be launched as a background service.

## Observed deployment shape

The running Talos process observed on this machine follows this shape:

```bash
python path/to/log-watcher.py \
  --sources path/to/mlx-server.log,path/to/mlx-embeddings.log,path/to/mlx-router.log,path/to/mlx-inference.log \
  --window 3600 \
  --output path/to/talos-mlx-monitor-summary.jsonl \
  --daemon \
  --interval 30
```

## What the arguments do

- `--sources`: comma-separated log files to monitor
- `--window`: analysis window, in seconds
- `--output`: output JSONL summary file
- `--daemon`: keep running in the background
- `--interval`: polling interval, in seconds

## Output expectation

The observed deployment writes rolling summaries to a JSONL file. This repository does not currently define a public schema for those records.

## macOS note

The observed machine runs Talos under `launchctl`, which is macOS-specific. That service setup is separate from the core Talos scoring code.

## Related docs

- [Documentation overview](docs/OVERVIEW.md)
- [Repository README](README.md)

## Scope note

This document describes the verified shape of the current MLX-oriented deployment. It does not claim that this repository contains the full MLX runtime, launcher, or service configuration.

"""Command-line interface for Talos."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

from .runtime import (
    TALOS_STATUS_FILE,
    append_history,
    evaluate_snapshot,
    load_policy,
    load_state,
    next_state_from_evaluation,
    read_snapshot,
    save_state,
    save_status,
)
from .scorer import compute_talos_level

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="talos")
    subparsers = parser.add_subparsers(dest="command", required=True)

    score_parser = subparsers.add_parser("score", help="compute a Talos enforcement level")
    score_parser.add_argument("--wip-total", type=int, required=True)
    score_parser.add_argument("--global-max", type=int, required=True)
    score_parser.add_argument("--at-cap", action="append", default=[])
    score_parser.add_argument("--backlog-delta", type=int, required=True)
    score_parser.add_argument("--cycles-at-current-level", type=int, required=True)

    evaluate_parser = subparsers.add_parser("evaluate", help="evaluate a Talos snapshot and persist state")
    evaluate_parser.add_argument("--snapshot", type=Path, required=True)

    status_parser = subparsers.add_parser("status", help="show the last persisted Talos status")
    status_parser.add_argument("--status-file", type=Path, default=TALOS_STATUS_FILE)

    explain_parser = subparsers.add_parser("explain", help="show human-readable reasons and guardrails for a snapshot")
    explain_parser.add_argument("--snapshot", type=Path, required=True)

    return parser


def _print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "score":
        level = compute_talos_level(
            wip_total=args.wip_total,
            global_max=args.global_max,
            at_cap_projects=args.at_cap,
            backlog_delta=args.backlog_delta,
            cycles_at_current_level=args.cycles_at_current_level,
        )
        _print_json({"talos_level": level})
        return 0

    if args.command == "evaluate":
        try:
            snapshot = read_snapshot(args.snapshot)
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            parser.error(f"snapshot is not valid Talos input: {exc}")
        evaluation = evaluate_snapshot(snapshot, prior_state=load_state(), policy=load_policy())
        next_state = next_state_from_evaluation(evaluation)
        persistence_results = (
            save_state(
                level=next_state.level,
                count=next_state.count,
                last_backlog=next_state.last_backlog,
                global_pressure_count=next_state.global_pressure_count,
            ),
            save_status(evaluation),
            append_history(evaluation),
        )
        _print_json(evaluation.to_dict())
        if not all(persistence_results):
            logger.error("Talos evaluation completed but one or more persistence writes failed")
            return 1
        return 0

    if args.command == "status":
        try:
            _print_json(json.loads(args.status_file.read_text()))
        except FileNotFoundError:
            parser.error(f"status file not found: {args.status_file}")
        except json.JSONDecodeError:
            parser.error(f"status file is not valid JSON: {args.status_file}")
        return 0

    if args.command == "explain":
        try:
            snapshot = read_snapshot(args.snapshot)
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            parser.error(f"snapshot is not valid Talos input: {exc}")
        evaluation = evaluate_snapshot(snapshot, prior_state=load_state(), policy=load_policy())
        for reason in evaluation.reasons:
            print(f"- {reason}")
        return 0

    parser.error(f"unknown command: {args.command}")  # pragma: no cover
    return 2  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

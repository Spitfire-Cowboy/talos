"""Command-line interface for Talos."""

from __future__ import annotations

import argparse
import json

from .scorer import compute_talos_level


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="talos")
    subparsers = parser.add_subparsers(dest="command", required=True)

    score_parser = subparsers.add_parser("score", help="compute a Talos enforcement level")
    score_parser.add_argument("--wip-total", type=int, required=True)
    score_parser.add_argument("--global-max", type=int, required=True)
    score_parser.add_argument("--at-cap", action="append", default=[])
    score_parser.add_argument("--backlog-delta", type=int, required=True)
    score_parser.add_argument("--cycles-at-current-level", type=int, required=True)

    return parser


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
        print(json.dumps({"talos_level": level}))
        return 0

    parser.error(f"unknown command: {args.command}")  # pragma: no cover
    return 2  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

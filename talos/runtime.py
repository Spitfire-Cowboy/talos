"""State, history, and evaluation helpers for Talos."""

from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import List, Optional

from .models import TalosEvaluation, TalosPolicy, TalosSnapshot, TalosState
from .scorer import compute_talos_level

logger = logging.getLogger(__name__)


def _default_data_dir() -> Path:
    return Path.home() / ".config" / "talos"


def _path_from_env(name: str, default_name: str) -> Path:
    configured = os.environ.get(name)
    if configured:
        return Path(configured).expanduser()
    return _default_data_dir() / default_name


TALOS_CYCLES_FILE = _path_from_env("TALOS_CYCLES_FILE", "cycles.json")
TALOS_STATUS_FILE = _path_from_env("TALOS_STATUS_FILE", "status.json")
TALOS_HISTORY_FILE = _path_from_env("TALOS_HISTORY_FILE", "history.jsonl")
TALOS_POLICY_FILE = _path_from_env("TALOS_POLICY_FILE", "policy.json")


def _atomic_write_text(target: Path, payload: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=target.parent,
        prefix=f".{target.name}.",
        suffix=".tmp",
        delete=False,
    )
    tmp_path = Path(temporary.name)
    try:
        with temporary:
            temporary.write(payload)
        tmp_path.replace(target)
    finally:
        tmp_path.unlink(missing_ok=True)


def load_state(path: Optional[Path] = None) -> TalosState:
    target = path or TALOS_CYCLES_FILE
    try:
        return TalosState.from_dict(json.loads(target.read_text()))
    except Exception:
        return TalosState()


def save_state(
    level: int,
    count: int,
    last_backlog: int,
    path: Optional[Path] = None,
    global_pressure_count: int = 0,
) -> None:
    target = path or TALOS_CYCLES_FILE
    try:
        _atomic_write_text(
            target,
            json.dumps(
                TalosState(
                    level=level,
                    count=count,
                    last_backlog=last_backlog,
                    global_pressure_count=global_pressure_count,
                ).to_dict(),
                sort_keys=True,
            ),
        )
    except Exception:
        logger.warning("Failed to persist Talos state to %s", target, exc_info=True)


def load_policy(path: Optional[Path] = None) -> TalosPolicy:
    target = path or TALOS_POLICY_FILE
    try:
        return TalosPolicy.from_dict(json.loads(target.read_text()))
    except Exception:
        return TalosPolicy()


def save_status(evaluation: TalosEvaluation, path: Optional[Path] = None) -> None:
    target = path or TALOS_STATUS_FILE
    try:
        _atomic_write_text(target, json.dumps(evaluation.to_dict(), indent=2, sort_keys=True))
    except Exception:
        logger.warning("Failed to persist Talos status to %s", target, exc_info=True)


def append_history(evaluation: TalosEvaluation, path: Optional[Path] = None) -> None:
    target = path or TALOS_HISTORY_FILE
    try:
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(evaluation.to_dict(), sort_keys=True) + "\n")
    except Exception:
        logger.warning("Failed to append Talos history to %s", target, exc_info=True)


def read_snapshot(path: Path) -> TalosSnapshot:
    return TalosSnapshot.from_dict(json.loads(path.read_text()))


def explain_level(snapshot: TalosSnapshot, level: int, policy: Optional[TalosPolicy] = None) -> List[str]:
    active_policy = policy or TalosPolicy()
    reasons: List[str] = []
    ratio_threshold = int(snapshot.global_max * active_policy.friction_ratio) if snapshot.global_max > 0 else 0
    if snapshot.global_max <= 0:
        return ["global_max<=0 so Talos stayed at clean level 0"]
    if snapshot.wip_total >= snapshot.global_max:
        reasons.append("wip_total reached or exceeded global_max")
    if snapshot.at_cap_projects:
        reasons.append("one or more projects are already at cap")
    if snapshot.wip_total >= ratio_threshold and snapshot.wip_total < snapshot.global_max:
        reasons.append("wip_total crossed the friction threshold")
    if snapshot.backlog_delta > 0:
        reasons.append("backlog is growing")
    if level == 0 and not reasons:
        reasons.append("wip and backlog are within policy thresholds")
    if level == 3:
        reasons.append("global cap pressure persisted long enough to block writes")
    return reasons


def evaluate_snapshot(
    snapshot: TalosSnapshot,
    prior_state: Optional[TalosState] = None,
    policy: Optional[TalosPolicy] = None,
) -> TalosEvaluation:
    active_state = prior_state or TalosState()
    active_policy = policy or TalosPolicy()
    global_pressure = snapshot.global_max > 0 and snapshot.wip_total >= snapshot.global_max
    persisted_pressure_cycles = active_state.global_pressure_count if global_pressure else 0
    if global_pressure and active_state.level == 3:
        persisted_pressure_cycles = max(persisted_pressure_cycles, active_policy.write_block_cycles)
    level = compute_talos_level(
        wip_total=snapshot.wip_total,
        global_max=snapshot.global_max,
        at_cap_projects=snapshot.at_cap_projects,
        backlog_delta=snapshot.backlog_delta,
        cycles_at_current_level=persisted_pressure_cycles,
        policy=active_policy,
    )
    pressure_streak_continues = active_state.level >= 2 and level >= 2 and global_pressure
    cycles_at_level = active_state.count + 1 if level == active_state.level or pressure_streak_continues else 1
    global_pressure_count = active_state.global_pressure_count + 1 if global_pressure else 0
    return TalosEvaluation(
        level=level,
        previous_level=active_state.level,
        cycles_at_level=cycles_at_level,
        wip_total=snapshot.wip_total,
        global_max=snapshot.global_max,
        backlog_total=snapshot.backlog_total,
        backlog_delta=snapshot.backlog_delta,
        at_cap_projects=list(snapshot.at_cap_projects),
        reasons=explain_level(snapshot=snapshot, level=level, policy=active_policy),
        source=snapshot.source,
        timestamp=snapshot.timestamp,
        global_pressure_count=global_pressure_count,
    )


def next_state_from_evaluation(evaluation: TalosEvaluation) -> TalosState:
    return TalosState(
        level=evaluation.level,
        count=evaluation.cycles_at_level,
        last_backlog=evaluation.backlog_total,
        global_pressure_count=evaluation.global_pressure_count,
    )


def load_cycles() -> dict:
    """Backward-compatible wrapper for loading persisted Talos cycle state."""
    return load_state().to_dict()


def save_cycles(level: int, count: int, last_backlog: int, global_pressure_count: int = 0) -> None:
    """Backward-compatible wrapper for saving persisted Talos cycle state."""
    save_state(
        level=level,
        count=count,
        last_backlog=last_backlog,
        global_pressure_count=global_pressure_count,
    )

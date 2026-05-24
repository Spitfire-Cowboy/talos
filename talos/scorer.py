"""Pure arithmetic scoring and persistence helpers for Talos."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def _default_cycles_file() -> Path:
    configured = os.environ.get("TALOS_CYCLES_FILE")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".config" / "talos" / "cycles.json"


TALOS_CYCLES_FILE = _default_cycles_file()


def compute_talos_level(
    wip_total: int,
    global_max: int,
    at_cap_projects: list,
    backlog_delta: int,
    cycles_at_current_level: int,
) -> int:
    """Return Talos enforcement level from deterministic pipeline inputs."""
    if global_max <= 0:
        return 0
    if wip_total >= global_max and cycles_at_current_level >= 2:
        return 3
    if wip_total >= global_max or len(at_cap_projects) > 0:
        return 2
    if wip_total >= global_max * 0.8 or backlog_delta > 0:
        return 1
    return 0


def load_cycles() -> dict:
    """Load persisted cycle counter, returning defaults if missing or corrupt."""
    try:
        data = json.loads(TALOS_CYCLES_FILE.read_text())
        return {
            "level": int(data.get("level", 0)),
            "count": int(data.get("count", 0)),
            "last_backlog": int(data.get("last_backlog", 0)),
        }
    except Exception:
        return {"level": 0, "count": 0, "last_backlog": 0}


def save_cycles(level: int, count: int, last_backlog: int) -> None:
    """Persist cycle counter across restarts and log failures."""
    try:
        TALOS_CYCLES_FILE.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        payload = json.dumps({"level": level, "count": count, "last_backlog": last_backlog})
        tmp_file = TALOS_CYCLES_FILE.with_suffix(f"{TALOS_CYCLES_FILE.suffix}.tmp")
        tmp_file.write_text(payload, encoding="utf-8")
        tmp_file.replace(TALOS_CYCLES_FILE)
    except Exception:
        logger.warning("Failed to persist cycles to %s", TALOS_CYCLES_FILE, exc_info=True)

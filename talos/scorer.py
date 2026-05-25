"""Pure arithmetic scoring helpers for Talos."""

from __future__ import annotations

from typing import List, Optional

from .models import TalosPolicy

DEFAULT_POLICY = TalosPolicy()


def compute_talos_level(
    wip_total: int,
    global_max: int,
    at_cap_projects: List[str],
    backlog_delta: int,
    cycles_at_current_level: int,
    policy: Optional[TalosPolicy] = None,
) -> int:
    """Return Talos enforcement level from deterministic inputs."""
    active_policy = policy or DEFAULT_POLICY
    if global_max <= 0:
        return 0
    if wip_total >= global_max and cycles_at_current_level >= active_policy.write_block_cycles:
        return 3
    if wip_total >= global_max or len(at_cap_projects) > 0:
        return 2
    if wip_total >= global_max * active_policy.friction_ratio or backlog_delta > 0:
        return 1
    return 0

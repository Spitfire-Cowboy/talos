"""Data models for Talos policy, snapshots, state, and evaluation results."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class TalosPolicy:
    """Configurable policy knobs for deterministic Talos scoring."""

    friction_ratio: float = 0.8
    write_block_cycles: int = 2

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "TalosPolicy":
        return cls(
            friction_ratio=float(payload.get("friction_ratio", 0.8)),
            write_block_cycles=int(payload.get("write_block_cycles", 2)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TalosSnapshot:
    """Input contract for a single Talos evaluation cycle."""

    wip_total: int
    global_max: int
    at_cap_projects: List[str] = field(default_factory=list)
    backlog_total: int = 0
    backlog_delta: int = 0
    projects: List[Dict[str, Any]] = field(default_factory=list)
    source: str = "manual"
    timestamp: str = ""

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "TalosSnapshot":
        at_cap_projects = payload.get("at_cap_projects", [])
        if not isinstance(at_cap_projects, list):
            raise TypeError(f"at_cap_projects must be a list, got {type(at_cap_projects)}")
        projects = payload.get("projects", [])
        if not isinstance(projects, list):
            raise TypeError(f"projects must be a list, got {type(projects)}")
        return cls(
            wip_total=int(payload["wip_total"]),
            global_max=int(payload["global_max"]),
            at_cap_projects=at_cap_projects.copy(),
            backlog_total=int(payload.get("backlog_total", 0)),
            backlog_delta=int(payload.get("backlog_delta", 0)),
            projects=projects.copy(),
            source=str(payload.get("source", "manual")),
            timestamp=str(payload.get("timestamp", "")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TalosState:
    """Persisted cross-cycle state for Talos."""

    level: int = 0
    count: int = 0
    last_backlog: int = 0

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "TalosState":
        return cls(
            level=int(payload.get("level", 0)),
            count=int(payload.get("count", 0)),
            last_backlog=int(payload.get("last_backlog", 0)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TalosEvaluation:
    """Structured output contract for a Talos evaluation cycle."""

    level: int
    previous_level: int
    cycles_at_level: int
    wip_total: int
    global_max: int
    backlog_total: int
    backlog_delta: int
    at_cap_projects: List[str]
    reasons: List[str]
    source: str = "manual"
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

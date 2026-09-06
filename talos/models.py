"""Data models for Talos policy, snapshots, state, and evaluation results."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


_DEPRECATED_ENFORCEMENT_TERMS = (
    "weekend-mode",
    "weekend mode",
    "weekendmode",
    "redis queue-v2",
    "redis queue v2",
    "redis-queue-v2",
    "redisqueuev2",
    "queue-v2",
    "queue v2",
    "queuev2",
    "perpetua",
    "campion",
)
_PROJECT_IDENTITY_FIELDS = ("name", "source", "service", "component", "mode", "queue", "agent", "bootstrap")
_PROJECT_LANE_FIELDS = ("lane", "category", "domain", "kind", "type", "workstream")
_BLD_ALLOWED_LANES = {"operations", "ops", "inference"}
_BLD_STALE_LANES = {"behavior", "behavioral", "agent", "bootstrap"}


def _normalized_label(value: Any) -> str:
    return str(value).strip().lower().replace("_", "-")


def _deprecated_term(value: Any) -> str:
    label = _normalized_label(value)
    for term in _DEPRECATED_ENFORCEMENT_TERMS:
        if term in label:
            return term
    return ""


def _reject_deprecated_term(value: Any, field_name: str) -> None:
    term = _deprecated_term(value)
    if term:
        raise ValueError(f"{field_name} references deprecated enforcement surface: {term}")


def _validate_project_contract(project: Dict[str, Any], index: int) -> None:
    for field_name in _PROJECT_IDENTITY_FIELDS:
        if field_name in project:
            _reject_deprecated_term(project[field_name], f"projects[{index}].{field_name}")

    bld_identity = any(
        _normalized_label(project[field_name]) == "bld"
        for field_name in _PROJECT_IDENTITY_FIELDS
        if field_name in project
    )
    if not bld_identity:
        return

    has_lane = False
    for field_name in _PROJECT_LANE_FIELDS:
        if field_name not in project:
            continue
        has_lane = True
        lane = _normalized_label(project[field_name])
        if lane in _BLD_STALE_LANES or lane not in _BLD_ALLOWED_LANES:
            raise ValueError(f"projects[{index}].{field_name} must classify BLD as operations or inference")
    if has_lane:
        return
    raise ValueError(f"projects[{index}] must classify BLD as operations or inference")


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
        source = str(payload.get("source", "manual"))
        _reject_deprecated_term(source, "source")
        for index, project_name in enumerate(at_cap_projects):
            _reject_deprecated_term(project_name, f"at_cap_projects[{index}]")
        for index, project in enumerate(projects):
            if not isinstance(project, dict):
                raise TypeError(f"projects[{index}] must be a dict, got {type(project)}")
            _validate_project_contract(project, index)
        return cls(
            wip_total=int(payload["wip_total"]),
            global_max=int(payload["global_max"]),
            at_cap_projects=at_cap_projects.copy(),
            backlog_total=int(payload.get("backlog_total", 0)),
            backlog_delta=int(payload.get("backlog_delta", 0)),
            projects=projects.copy(),
            source=source,
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
    global_pressure_count: int = 0

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "TalosState":
        return cls(
            level=int(payload.get("level", 0)),
            count=int(payload.get("count", 0)),
            last_backlog=int(payload.get("last_backlog", 0)),
            global_pressure_count=int(payload.get("global_pressure_count", 0)),
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
    global_pressure_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

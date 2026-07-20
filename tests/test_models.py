import pytest

from talos.models import TalosEvaluation, TalosPolicy, TalosSnapshot, TalosState


def test_policy_round_trip() -> None:
    policy = TalosPolicy.from_dict({"friction_ratio": 0.9, "write_block_cycles": 3})
    assert policy.to_dict() == {"friction_ratio": 0.9, "write_block_cycles": 3}


def test_snapshot_round_trip() -> None:
    payload = {
        "wip_total": 8,
        "global_max": 10,
        "at_cap_projects": ["alpha"],
        "backlog_total": 5,
        "backlog_delta": 1,
        "projects": [{"name": "alpha", "wip": 4}],
        "source": "rowan",
        "timestamp": "2026-05-25T12:00:00Z",
    }
    snapshot = TalosSnapshot.from_dict(payload)
    assert snapshot.to_dict() == payload


def test_snapshot_rejects_non_list_fields() -> None:
    with pytest.raises(TypeError, match="at_cap_projects must be a list"):
        TalosSnapshot.from_dict({"wip_total": 8, "global_max": 10, "at_cap_projects": "alpha"})

    with pytest.raises(TypeError, match="projects must be a list"):
        TalosSnapshot.from_dict({"wip_total": 8, "global_max": 10, "projects": "alpha"})

    with pytest.raises(TypeError, match=r"projects\[0\] must be a dict"):
        TalosSnapshot.from_dict({"wip_total": 8, "global_max": 10, "projects": ["alpha"]})


@pytest.mark.parametrize("source", ["Weekend Mode", "WeekendMode", "redis queue-v2", "redis_queue_v2", "Perpetua", "Campion"])
def test_snapshot_rejects_deprecated_enforcement_sources(source: str) -> None:
    with pytest.raises(ValueError, match="deprecated enforcement surface"):
        TalosSnapshot.from_dict({"wip_total": 8, "global_max": 10, "source": source})


def test_snapshot_rejects_deprecated_project_references() -> None:
    with pytest.raises(ValueError, match=r"at_cap_projects\[0\] references deprecated enforcement surface"):
        TalosSnapshot.from_dict({"wip_total": 8, "global_max": 10, "at_cap_projects": ["campion"]})

    with pytest.raises(ValueError, match=r"projects\[0\].queue references deprecated enforcement surface"):
        TalosSnapshot.from_dict(
            {"wip_total": 8, "global_max": 10, "projects": [{"name": "worker", "queue": "queue-v2"}]}
        )


def test_snapshot_classifies_bld_as_operations_or_inference() -> None:
    operations_payload = {
        "wip_total": 8,
        "global_max": 10,
        "projects": [{"name": "BLD", "lane": "operations"}, {"name": "BLD", "lane": "inference"}],
    }
    assert TalosSnapshot.from_dict(operations_payload).projects == operations_payload["projects"]

    with pytest.raises(ValueError, match="must classify BLD as operations or inference"):
        TalosSnapshot.from_dict({"wip_total": 8, "global_max": 10, "projects": [{"name": "BLD", "lane": "behavior"}]})

    with pytest.raises(ValueError, match="must classify BLD as operations or inference"):
        TalosSnapshot.from_dict(
            {"wip_total": 8, "global_max": 10, "projects": [{"name": "BLD", "lane": "ops", "category": "behavior"}]}
        )

    with pytest.raises(ValueError, match="must classify BLD as operations or inference"):
        TalosSnapshot.from_dict({"wip_total": 8, "global_max": 10, "projects": [{"name": "BLD"}]})


def test_state_round_trip() -> None:
    state = TalosState.from_dict({"level": 2, "count": 3, "last_backlog": 7})
    assert state.to_dict() == {"level": 2, "count": 3, "last_backlog": 7}


def test_evaluation_to_dict() -> None:
    evaluation = TalosEvaluation(
        level=1,
        previous_level=0,
        cycles_at_level=1,
        wip_total=8,
        global_max=10,
        backlog_total=4,
        backlog_delta=1,
        at_cap_projects=[],
        reasons=["backlog is growing"],
    )
    assert evaluation.to_dict() == {
        "level": 1,
        "previous_level": 0,
        "cycles_at_level": 1,
        "wip_total": 8,
        "global_max": 10,
        "backlog_total": 4,
        "backlog_delta": 1,
        "at_cap_projects": [],
        "reasons": ["backlog is growing"],
        "source": "manual",
        "timestamp": "",
    }

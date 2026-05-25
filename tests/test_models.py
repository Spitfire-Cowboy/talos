from talos.models import TalosEvaluation, TalosPolicy, TalosSnapshot, TalosState


def test_policy_round_trip() -> None:
    policy = TalosPolicy.from_dict({"friction_ratio": 0.9, "write_block_cycles": 3})
    assert policy.to_dict() == {"friction_ratio": 0.9, "write_block_cycles": 3}


def test_snapshot_round_trip() -> None:
    snapshot = TalosSnapshot.from_dict(
        {
            "wip_total": 8,
            "global_max": 10,
            "at_cap_projects": ["alpha"],
            "backlog_total": 5,
            "backlog_delta": 1,
            "projects": [{"name": "alpha", "wip": 4}],
            "source": "rowan",
            "timestamp": "2026-05-25T12:00:00Z",
        }
    )
    assert snapshot.to_dict()["source"] == "rowan"


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
    assert evaluation.to_dict()["reasons"] == ["backlog is growing"]

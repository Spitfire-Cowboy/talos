import json
from pathlib import Path

import pytest

from talos.models import TalosPolicy, TalosSnapshot, TalosState
from talos.runtime import (
    append_history,
    evaluate_snapshot,
    load_policy,
    load_state,
    next_state_from_evaluation,
    save_state,
    save_status,
)


def test_evaluate_snapshot_builds_structured_output() -> None:
    snapshot = TalosSnapshot(
        wip_total=10,
        global_max=10,
        at_cap_projects=["alpha"],
        backlog_total=12,
        backlog_delta=2,
        source="test",
        timestamp="2026-05-25T12:00:00Z",
    )
    evaluation = evaluate_snapshot(snapshot, prior_state=TalosState(level=2, count=2), policy=TalosPolicy())
    assert evaluation.level == 3
    assert evaluation.cycles_at_level == 3
    assert evaluation.source == "test"
    assert "global cap pressure persisted long enough to block writes" in evaluation.reasons


def test_state_round_trip(tmp_path: Path) -> None:
    target = tmp_path / "cycles.json"
    save_state(level=2, count=4, last_backlog=11, path=target)
    assert load_state(path=target).to_dict() == {"level": 2, "count": 4, "last_backlog": 11}


def test_history_appends_json_lines(tmp_path: Path) -> None:
    target = tmp_path / "history.jsonl"
    snapshot = TalosSnapshot(wip_total=4, global_max=10, backlog_total=2, backlog_delta=0)
    evaluation = evaluate_snapshot(snapshot, prior_state=TalosState())
    append_history(evaluation, path=target)
    lines = target.read_text().strip().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["level"] == 0


def test_next_state_matches_evaluation() -> None:
    snapshot = TalosSnapshot(wip_total=8, global_max=10, backlog_total=5, backlog_delta=1)
    evaluation = evaluate_snapshot(snapshot, prior_state=TalosState(level=1, count=2))
    state = next_state_from_evaluation(evaluation)
    assert state.level == evaluation.level
    assert state.count == evaluation.cycles_at_level


def test_load_policy_reads_json(tmp_path: Path) -> None:
    target = tmp_path / "policy.json"
    target.write_text('{"friction_ratio": 0.9, "write_block_cycles": 4}')
    policy = __import__("talos.runtime", fromlist=["load_policy"]).load_policy(path=target)
    assert policy.to_dict() == {"friction_ratio": 0.9, "write_block_cycles": 4}


def test_load_policy_returns_default_when_file_is_invalid(tmp_path: Path) -> None:
    target = tmp_path / "policy.json"
    target.write_text("not-json")
    assert load_policy(path=target).to_dict() == {"friction_ratio": 0.8, "write_block_cycles": 2}


def test_save_status_writes_structured_json(tmp_path: Path) -> None:
    runtime = __import__("talos.runtime", fromlist=["save_status", "TalosSnapshot", "TalosState", "evaluate_snapshot"])
    target = tmp_path / "status.json"
    evaluation = evaluate_snapshot(TalosSnapshot(wip_total=4, global_max=10), prior_state=TalosState())
    runtime.save_status(evaluation, path=target)
    assert json.loads(target.read_text())["level"] == 0


def test_save_status_logs_failures(monkeypatch, caplog, tmp_path: Path) -> None:
    evaluation = evaluate_snapshot(TalosSnapshot(wip_total=4, global_max=10), prior_state=TalosState())

    def boom(_target: Path, _payload: str) -> None:
        raise OSError("boom")

    monkeypatch.setattr("talos.runtime._atomic_write_text", boom)
    with caplog.at_level("WARNING"):
        save_status(evaluation, path=tmp_path / "status.json")
    assert "Failed to persist Talos status" in caplog.text


def test_read_snapshot_loads_json_file(tmp_path: Path) -> None:
    runtime = __import__("talos.runtime", fromlist=["read_snapshot"])
    target = tmp_path / "snapshot.json"
    target.write_text('{"wip_total": 5, "global_max": 10, "backlog_delta": 1}')
    snapshot = runtime.read_snapshot(target)
    assert snapshot.wip_total == 5


def test_explain_level_handles_zero_cap() -> None:
    runtime = __import__("talos.runtime", fromlist=["explain_level"])
    reasons = runtime.explain_level(TalosSnapshot(wip_total=1, global_max=0), level=0)
    assert reasons == ["global_max<=0 so Talos stayed at clean level 0"]


def test_append_history_logs_failures(caplog, tmp_path: Path) -> None:
    target = tmp_path / "history.jsonl"
    target.write_text("")
    evaluation = evaluate_snapshot(TalosSnapshot(wip_total=4, global_max=10), prior_state=TalosState())

    original_open = Path.open

    def broken_open(self: Path, *args, **kwargs):
        if self == target:
            raise OSError("boom")
        return original_open(self, *args, **kwargs)

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(Path, "open", broken_open)
        with caplog.at_level("WARNING"):
            append_history(evaluation, path=target)
    assert "Failed to append Talos history" in caplog.text

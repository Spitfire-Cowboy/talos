import json
from pathlib import Path

import pytest

from talos import cli


def test_talos_score_command_outputs_level(capsys, monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "talos",
            "score",
            "--wip-total",
            "10",
            "--global-max",
            "10",
            "--at-cap",
            "alpha",
            "--backlog-delta",
            "0",
            "--cycles-at-current-level",
            "2",
        ],
    )
    assert cli.main() == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out) == {"talos_level": 3}


def test_evaluate_and_status_commands(tmp_path: Path, capsys, monkeypatch) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text(json.dumps({"wip_total": 8, "global_max": 10, "backlog_total": 3, "backlog_delta": 1}))
    state_path = tmp_path / "cycles.json"
    status_path = tmp_path / "status.json"
    history_path = tmp_path / "history.jsonl"
    monkeypatch.setattr(cli, "TALOS_STATUS_FILE", status_path)
    monkeypatch.setattr("talos.runtime.TALOS_CYCLES_FILE", state_path)
    monkeypatch.setattr("talos.runtime.TALOS_STATUS_FILE", status_path)
    monkeypatch.setattr("talos.runtime.TALOS_HISTORY_FILE", history_path)
    monkeypatch.setattr("sys.argv", ["talos", "evaluate", "--snapshot", str(snapshot_path)])
    assert cli.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["level"] == 1
    assert status_path.exists()
    assert history_path.exists()

    monkeypatch.setattr("sys.argv", ["talos", "status", "--status-file", str(status_path)])
    assert cli.main() == 0
    status_payload = json.loads(capsys.readouterr().out)
    assert status_payload["level"] == 1


def test_evaluate_returns_nonzero_when_writes_fail_despite_stale_outputs(
    tmp_path: Path, capsys, monkeypatch, caplog
) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text(json.dumps({"wip_total": 8, "global_max": 10, "backlog_total": 3, "backlog_delta": 1}))
    state_path = tmp_path / "cycles.json"
    status_path = tmp_path / "status.json"
    history_path = tmp_path / "history.jsonl"
    for output_path in (state_path, status_path, history_path):
        output_path.write_text("stale")
    monkeypatch.setattr(cli, "save_state", lambda **kwargs: False)
    monkeypatch.setattr(cli, "save_status", lambda _evaluation: False)
    monkeypatch.setattr(cli, "append_history", lambda _evaluation: False)
    monkeypatch.setattr("sys.argv", ["talos", "evaluate", "--snapshot", str(snapshot_path)])
    with caplog.at_level("ERROR"):
        assert cli.main() == 1
    assert json.loads(capsys.readouterr().out)["level"] == 1
    assert "persistence writes failed" in caplog.text


@pytest.mark.parametrize("command", ["evaluate", "explain"])
def test_snapshot_commands_report_missing_files_as_usage_errors(tmp_path: Path, capsys, monkeypatch, command: str) -> None:
    missing_path = tmp_path / "missing.json"
    monkeypatch.setattr("sys.argv", ["talos", command, "--snapshot", str(missing_path)])

    with pytest.raises(SystemExit):
        cli.main()

    assert "snapshot is not valid Talos input" in capsys.readouterr().err


def test_evaluate_command_errors_when_snapshot_uses_deprecated_source(
    tmp_path: Path, capsys, monkeypatch
) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text(json.dumps({"wip_total": 8, "global_max": 10, "source": "WeekendMode"}))
    monkeypatch.setattr("sys.argv", ["talos", "evaluate", "--snapshot", str(snapshot_path)])
    with pytest.raises(SystemExit):
        cli.main()
    assert "snapshot is not valid Talos input" in capsys.readouterr().err


def test_explain_command_outputs_reasons(tmp_path: Path, capsys, monkeypatch) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text(json.dumps({"wip_total": 10, "global_max": 10, "backlog_total": 5, "backlog_delta": 0}))
    monkeypatch.setattr("sys.argv", ["talos", "explain", "--snapshot", str(snapshot_path)])
    assert cli.main() == 0
    assert "wip_total reached or exceeded global_max" in capsys.readouterr().out


def test_explain_command_errors_when_snapshot_uses_deprecated_source(tmp_path: Path, capsys, monkeypatch) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text(json.dumps({"wip_total": 8, "global_max": 10, "source": "WeekendMode"}))
    monkeypatch.setattr("sys.argv", ["talos", "explain", "--snapshot", str(snapshot_path)])
    with pytest.raises(SystemExit):
        cli.main()
    assert "snapshot is not valid Talos input" in capsys.readouterr().err


def test_explain_command_outputs_orchestration_guardrail(tmp_path: Path, capsys, monkeypatch) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text(
        json.dumps(
            {
                "wip_total": 4,
                "global_max": 10,
                "backlog_total": 1,
                "backlog_delta": 0,
                "orchestration": {
                    "subagents_requested": True,
                    "main_thread_role": "orchestrator",
                    "coordination_actions": 1,
                    "implementation_actions": 3,
                },
            }
        )
    )
    monkeypatch.setattr("sys.argv", ["talos", "explain", "--snapshot", str(snapshot_path)])
    assert cli.main() == 0
    assert "orchestration drift detected" in capsys.readouterr().out


def test_status_command_errors_when_file_is_missing(tmp_path: Path, monkeypatch) -> None:
    missing_path = tmp_path / "missing.json"
    monkeypatch.setattr("sys.argv", ["talos", "status", "--status-file", str(missing_path)])
    with pytest.raises(SystemExit):
        cli.main()


def test_status_command_errors_when_file_is_invalid_json(tmp_path: Path, monkeypatch) -> None:
    status_path = tmp_path / "status.json"
    status_path.write_text("not-json")
    monkeypatch.setattr("sys.argv", ["talos", "status", "--status-file", str(status_path)])
    with pytest.raises(SystemExit):
        cli.main()


def test_parser_requires_a_subcommand() -> None:
    parser = cli.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])

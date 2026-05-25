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


def test_explain_command_outputs_reasons(tmp_path: Path, capsys, monkeypatch) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text(json.dumps({"wip_total": 10, "global_max": 10, "backlog_total": 5, "backlog_delta": 0}))
    monkeypatch.setattr("sys.argv", ["talos", "explain", "--snapshot", str(snapshot_path)])
    assert cli.main() == 0
    assert "wip_total reached or exceeded global_max" in capsys.readouterr().out


def test_parser_requires_a_subcommand() -> None:
    parser = cli.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])

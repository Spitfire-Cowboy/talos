import json

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


def test_parser_requires_a_subcommand() -> None:
    parser = cli.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])

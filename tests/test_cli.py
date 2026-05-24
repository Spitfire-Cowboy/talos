import json
import subprocess
import sys


def test_talos_score_command_outputs_level() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "talos.cli",
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
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(result.stdout) == {"talos_level": 3}

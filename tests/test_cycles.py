from pathlib import Path

import talos.scorer as scorer


def test_default_cycles_file_uses_secure_home_config_location(monkeypatch) -> None:
    monkeypatch.delenv("TALOS_CYCLES_FILE", raising=False)
    monkeypatch.setattr(scorer.Path, "home", lambda: Path("/tmp/fake-home"))
    assert scorer._default_cycles_file() == Path("/tmp/fake-home/.config/talos/cycles.json")


def test_default_cycles_file_honors_environment_override(monkeypatch) -> None:
    monkeypatch.setenv("TALOS_CYCLES_FILE", "/tmp/custom/talos-cycles.json")
    assert scorer._default_cycles_file() == Path("/tmp/custom/talos-cycles.json")


def test_load_cycles_returns_defaults_when_file_is_missing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(scorer, "TALOS_CYCLES_FILE", tmp_path / "missing.json")
    assert scorer.load_cycles() == {"level": 0, "count": 0, "last_backlog": 0}


def test_load_cycles_returns_defaults_when_file_is_corrupt(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "cycles.json"
    target.write_text("not-json")
    monkeypatch.setattr(scorer, "TALOS_CYCLES_FILE", target)
    assert scorer.load_cycles() == {"level": 0, "count": 0, "last_backlog": 0}


def test_save_cycles_and_load_cycles_round_trip(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "cycles.json"
    monkeypatch.setattr(scorer, "TALOS_CYCLES_FILE", target)
    scorer.save_cycles(level=2, count=4, last_backlog=11)
    assert scorer.load_cycles() == {"level": 2, "count": 4, "last_backlog": 11}


def test_save_cycles_logs_failures(monkeypatch, caplog) -> None:
    class BrokenPath:
        parent = Path("/tmp")

        def write_text(self, _payload: str) -> None:
            raise OSError("boom")

    monkeypatch.setattr(scorer, "TALOS_CYCLES_FILE", BrokenPath())
    with caplog.at_level("WARNING"):
        scorer.save_cycles(level=1, count=2, last_backlog=3)
    assert "Failed to persist cycles" in caplog.text


def test_save_cycles_writes_atomically(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "cycles.json"
    monkeypatch.setattr(scorer, "TALOS_CYCLES_FILE", target)
    scorer.save_cycles(level=7, count=8, last_backlog=9)
    assert target.exists()
    assert not target.with_suffix(".json.tmp").exists()
    assert scorer.load_cycles() == {"level": 7, "count": 8, "last_backlog": 9}

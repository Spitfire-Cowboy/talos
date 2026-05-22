from pathlib import Path

import talos.scorer as scorer


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

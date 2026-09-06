from pathlib import Path

import talos.runtime as runtime


def test_default_cycles_file_uses_secure_home_config_location(monkeypatch) -> None:
    monkeypatch.delenv("TALOS_CYCLES_FILE", raising=False)
    monkeypatch.setattr(runtime.Path, "home", lambda: Path("/tmp/fake-home"))
    assert runtime._path_from_env("TALOS_CYCLES_FILE", "cycles.json") == Path("/tmp/fake-home/.config/talos/cycles.json")


def test_default_cycles_file_honors_environment_override(monkeypatch) -> None:
    monkeypatch.setenv("TALOS_CYCLES_FILE", "/tmp/custom/talos-cycles.json")
    assert runtime._path_from_env("TALOS_CYCLES_FILE", "cycles.json") == Path("/tmp/custom/talos-cycles.json")


def test_load_cycles_returns_defaults_when_file_is_missing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(runtime, "TALOS_CYCLES_FILE", tmp_path / "missing.json")
    assert runtime.load_cycles() == {"level": 0, "count": 0, "last_backlog": 0}


def test_load_cycles_returns_defaults_when_file_is_corrupt(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "cycles.json"
    target.write_text("not-json")
    monkeypatch.setattr(runtime, "TALOS_CYCLES_FILE", target)
    assert runtime.load_cycles() == {"level": 0, "count": 0, "last_backlog": 0}


def test_save_cycles_and_load_cycles_round_trip(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "cycles.json"
    monkeypatch.setattr(runtime, "TALOS_CYCLES_FILE", target)
    runtime.save_cycles(level=2, count=4, last_backlog=11)
    assert runtime.load_cycles() == {"level": 2, "count": 4, "last_backlog": 11}


def test_save_cycles_logs_failures(monkeypatch, caplog) -> None:
    class BrokenPath:
        parent = Path("/tmp")
        suffix = ".json"

        def write_text(self, _payload: str, encoding: str = "utf-8") -> None:
            raise OSError("boom")

        def with_suffix(self, suffix: str):
            return self

        def replace(self, target):
            return target

    monkeypatch.setattr(runtime, "TALOS_CYCLES_FILE", BrokenPath())
    with caplog.at_level("WARNING"):
        runtime.save_cycles(level=1, count=2, last_backlog=3)
    assert "Failed to persist Talos state" in caplog.text


def test_save_cycles_writes_atomically(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "cycles.json"
    monkeypatch.setattr(runtime, "TALOS_CYCLES_FILE", target)
    runtime.save_cycles(level=7, count=8, last_backlog=9)
    assert target.exists()
    assert sorted(tmp_path.iterdir()) == [target]
    assert runtime.load_cycles() == {"level": 7, "count": 8, "last_backlog": 9}

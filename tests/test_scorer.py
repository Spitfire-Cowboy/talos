from talos import compute_talos_level


def test_returns_clean_when_global_cap_is_invalid() -> None:
    assert compute_talos_level(10, 0, [], 3, 5) == 0


def test_returns_clean_when_below_thresholds() -> None:
    assert compute_talos_level(3, 10, [], 0, 0) == 0


def test_returns_friction_when_backlog_grows() -> None:
    assert compute_talos_level(3, 10, [], 1, 0) == 1


def test_returns_friction_at_eighty_percent_of_cap() -> None:
    assert compute_talos_level(8, 10, [], 0, 0) == 1


def test_returns_selective_when_any_project_is_at_cap() -> None:
    assert compute_talos_level(4, 10, ["alpha"], 0, 0) == 2


def test_returns_selective_when_global_cap_is_reached_for_first_cycle() -> None:
    assert compute_talos_level(10, 10, [], 0, 1) == 2


def test_returns_write_when_global_cap_is_reached_for_multiple_cycles() -> None:
    assert compute_talos_level(10, 10, [], 0, 2) == 3

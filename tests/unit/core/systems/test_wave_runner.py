"""Tests of a level's wave script (P06-R07, GD-40), `core/systems/wave_runner.py`."""

import pytest

from core.entities.enemy import EnemyEntry
from core.systems.wave_runner import Wave, WaveRunner, validate_wave_script

TOP = EnemyEntry("top", 0.5)
KINDS = ["scout", "drone"]


def _runner(script: list[Wave]) -> tuple[WaveRunner, list[tuple[str, EnemyEntry]]]:
    spawned: list[tuple[str, EnemyEntry]] = []
    runner = WaveRunner(script, lambda kind, entry: spawned.append((kind, entry)))
    return runner, spawned


def test_p06_r07_a_valid_script_passes_validation() -> None:
    validate_wave_script([Wave(0, "scout", 2, 0.5, TOP), Wave(10, "drone", 1.0, 0, TOP)], KINDS)


def test_p06_r07_a_wave_of_an_unknown_kind_is_rejected() -> None:
    with pytest.raises(ValueError, match="unknown enemy kind"):
        validate_wave_script([Wave(0, "boss", 1, 0, TOP)], KINDS)


@pytest.mark.parametrize("count", [0, -1, 1.5])
def test_p06_r07_a_wave_needs_a_whole_positive_count(count: float) -> None:
    with pytest.raises(ValueError, match="bad count"):
        validate_wave_script([Wave(0, "scout", count, 0, TOP)], KINDS)


def test_p06_r07_a_wave_with_a_negative_distance_or_interval_is_rejected() -> None:
    with pytest.raises(ValueError, match="bad timing"):
        validate_wave_script([Wave(-1, "scout", 1, 0, TOP)], KINDS)
    with pytest.raises(ValueError, match="bad timing"):
        validate_wave_script([Wave(0, "scout", 1, -0.5, TOP)], KINDS)


@pytest.mark.parametrize("position", [-0.1, 1.5])
def test_p06_r07_a_wave_entry_must_lie_on_its_edge(position: float) -> None:
    with pytest.raises(ValueError, match="bad entry position"):
        validate_wave_script([Wave(0, "scout", 1, 0, EnemyEntry("top", position))], KINDS)


def test_p06_r07_an_infinite_count_is_a_descriptive_bad_count() -> None:
    with pytest.raises(ValueError, match="bad count"):
        validate_wave_script([Wave(0, "scout", float("inf"), 0, TOP)], KINDS)


def test_p06_r07_a_group_comes_in_when_its_wave_is_passed() -> None:
    runner, spawned = _runner([Wave(10, "scout", 1, 0, TOP)])
    runner.step(1, 5)
    assert spawned == []
    assert runner.triggered == 0
    runner.step(1, 10)
    assert [(k, e.side, e.position) for k, e in spawned] == [("scout", "top", 0.5)]
    assert runner.triggered == 1
    assert runner.finished is True


def test_p06_r07_the_groups_of_a_wave_come_in_one_interval_apart() -> None:
    runner, spawned = _runner([Wave(0, "scout", 3, 1, TOP)])
    runner.step(1, 0)
    assert len(spawned) == 1
    assert runner.finished is False
    runner.step(1, 0)
    runner.step(1, 0)
    assert len(spawned) == 3
    assert runner.finished is True


def test_p06_r07_waves_are_triggered_in_distance_order_whatever_the_script_order() -> None:
    runner, spawned = _runner([Wave(50, "drone", 1, 0, TOP), Wave(10, "scout", 1, 0, TOP)])
    runner.step(0.1, 10)
    assert [k for k, _ in spawned] == ["scout"]
    runner.step(0.1, 60)
    assert [k for k, _ in spawned] == ["scout", "drone"]


def test_p06_r07_groups_due_at_the_same_time_keep_their_order() -> None:
    runner, spawned = _runner(
        [
            Wave(0, "scout", 2, 5, TOP),
            Wave(0, "drone", 1, 0, TOP),
        ]
    )
    runner.step(1, 0)
    # The scout's second group is due in 5 seconds; the drone's group is due now, after it.
    assert [k for k, _ in spawned] == ["scout", "drone"]
    runner.step(5, 0)
    assert [k for k, _ in spawned] == ["scout", "drone", "scout"]


def test_p06_r07_a_wave_spreads_its_groups_along_the_entry_edge() -> None:
    runner, spawned = _runner([Wave(0, "scout", 3, 0, EnemyEntry("top", 0.1), 0.3)])
    runner.step(1, 0)
    assert [e.position for _, e in spawned] == pytest.approx([0.1, 0.4, 0.7])
    assert all(e.side == "top" for _, e in spawned)


def test_p06_r07_a_spread_wraps_back_into_the_edge() -> None:
    runner, spawned = _runner([Wave(0, "scout", 2, 0, EnemyEntry("left", 0.9), 0.5)])
    runner.step(1, 0)
    assert [e.position for _, e in spawned] == pytest.approx([0.9, 0.4])


def test_p06_r07_a_wave_without_a_spread_enters_at_one_point() -> None:
    runner, spawned = _runner([Wave(0, "scout", 2, 0, TOP)])
    runner.step(1, 0)
    assert [e.position for _, e in spawned] == [0.5, 0.5]


def test_p06_r03_stopping_drops_the_groups_waiting_and_the_rest_of_the_script() -> None:
    runner, spawned = _runner([Wave(0, "scout", 3, 1, TOP), Wave(5, "drone", 1, 0, TOP)])
    runner.step(1, 0)
    runner.stop()
    assert runner.finished is True
    runner.step(10, 100)
    assert len(spawned) == 1
    assert runner.triggered == 1


def test_p06_r09_skipping_ahead_drops_the_waves_before_and_keeps_the_later_ones() -> None:
    runner, spawned = _runner(
        [Wave(0, "scout", 3, 1, TOP), Wave(50, "drone", 1, 0, TOP), Wave(100, "scout", 1, 0, TOP)]
    )
    runner.step(1, 0)
    runner.skip_to(60)
    assert runner.triggered == 2
    runner.step(1, 60)
    assert [k for k, _ in spawned] == ["scout"]
    runner.step(1, 100)
    assert [k for k, _ in spawned] == ["scout", "scout"]
    assert runner.finished is True


def test_p06_r09_skipping_past_every_wave_leaves_nothing_to_come() -> None:
    runner, _ = _runner([Wave(0, "scout", 1, 0, TOP)])
    runner.skip_to(1000)
    assert runner.triggered == 1
    assert runner.finished is True


def test_p06_r09_skipping_after_a_stop_starts_the_script_again() -> None:
    runner, spawned = _runner([Wave(20, "scout", 1, 0, TOP)])
    runner.stop()
    runner.skip_to(0)
    runner.step(1, 25)
    assert len(spawned) == 1

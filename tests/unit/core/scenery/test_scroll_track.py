# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/core/scenery/scroll_track.py`."""

import pytest

from core.scenery.scroll_track import ScrollTrack


def test_game_level_02_the_ground_scrolls_at_the_speed_until_the_level_ends() -> None:
    """Also GAME-SCREEN-03."""
    track = ScrollTrack(10.0, 100.0)
    assert track.duration == pytest.approx(10.0)
    track.step(1.0)
    assert track.progress == pytest.approx(10.0)
    assert track.distance == pytest.approx(10.0)
    assert track.time == pytest.approx(1.0)
    for _ in range(20):
        track.step(1.0)
    assert track.ended
    assert track.progress == pytest.approx(100.0)
    # The ground keeps moving past the level's end (GAME-LEVEL-07).
    assert track.distance == pytest.approx(210.0)


def test_game_screen_03_negative_time_does_not_move_the_track() -> None:
    track = ScrollTrack(10.0, 100.0)
    track.step(-5.0)
    assert track.progress == 0.0
    assert track.distance == 0.0


def test_game_screen_03_time_scale_speeds_up_or_pauses_the_track() -> None:
    track = ScrollTrack(10.0, 100.0)
    track.time_scale = 4.0
    track.step(1.0)
    assert track.progress == pytest.approx(40.0)
    track.time_scale = 0.0
    track.step(1.0)
    assert track.progress == pytest.approx(40.0)


def test_game_level_06_a_held_track_scrolls_the_ground_but_not_the_level() -> None:
    """Also GAME-LEVEL-07: the ground and the level's progress are kept apart."""
    track = ScrollTrack(10.0, 100.0)
    track.held = True
    track.step(2.0)
    assert track.progress == 0.0
    assert track.distance == pytest.approx(20.0)
    track.held = False
    track.step(1.0)
    assert track.progress == pytest.approx(10.0)


def test_game_level_08_the_ground_keeps_its_lead_when_the_level_is_sought() -> None:
    track = ScrollTrack(10.0, 100.0)
    track.held = True
    track.step(2.0)
    track.held = False
    track.seek(5.0)
    assert track.progress == pytest.approx(50.0)
    assert track.distance == pytest.approx(70.0)
    track.seek(-3.0)
    assert track.progress == 0.0
    track.seek(1000.0)
    assert track.progress == pytest.approx(100.0)


def test_speed_factor_changes_at_once_without_seconds() -> None:
    track = ScrollTrack(10.0, 100.0)
    track.set_speed_factor(2.0, 0.0)
    assert track.speed_factor == 2.0
    track.step(1.0)
    assert track.distance == pytest.approx(20.0)


def test_game_level_07_speed_factor_eases_over_its_seconds() -> None:
    track = ScrollTrack(10.0, 1000.0)
    track.set_speed_factor(0.0, 2.0)
    track.step(1.0)
    assert track.speed_factor == pytest.approx(0.5)
    track.step(1.0)
    assert track.speed_factor == pytest.approx(0.0)
    track.step(1.0)
    assert track.speed_factor == pytest.approx(0.0)


def test_game_level_07_the_ground_eases_back_after_the_final_boss_at_the_level_end() -> None:
    """The final boss sits at the end: the progress is at the end and not held.

    Yet the ground still eases from the boss's speed back to the level's speed over 2 s, and keeps
    moving.
    """
    track = ScrollTrack(60.0, 100.0)
    track.step(10.0)  # the level reaches its end
    assert track.ended
    track.held = True
    track.set_speed_factor(1.5, 0.0)
    track.step(1.0)
    track.held = False
    track.set_speed_factor(1.0, 2.0)  # the boss is gone: ease back over 2 s
    before = track.distance
    track.step(1.0)  # half way: factor 1.25 (smooth ease)
    assert track.distance - before == pytest.approx(60.0 * 1.25)
    before = track.distance
    track.step(1.0)  # eased: factor 1
    assert track.speed_factor == pytest.approx(1.0)
    assert track.distance - before == pytest.approx(60.0)
    assert track.progress == pytest.approx(100.0)


def test_speed_factor_and_speed_must_not_be_negative() -> None:
    with pytest.raises(ValueError, match="scroll speed must be positive"):
        ScrollTrack(0.0, 10.0)
    with pytest.raises(ValueError, match="length cannot be negative"):
        ScrollTrack(10.0, -1.0)
    track = ScrollTrack(10.0, 10.0)
    with pytest.raises(ValueError, match="speed factor cannot be negative"):
        track.set_speed_factor(-1.0, 1.0)


def test_restart_puts_the_track_back_at_the_start() -> None:
    track = ScrollTrack(10.0, 100.0)
    track.set_speed_factor(3.0, 1.0)
    track.held = True
    track.step(2.0)
    track.restart()
    assert (track.progress, track.distance, track.speed_factor, track.held) == (
        0.0,
        0.0,
        1.0,
        False,
    )

"""Unit tests of `src/core/scenery/scroll_track.py`."""

import pytest

from core.scenery.scroll_track import ScrollTrack


def test_p04_r06_the_ground_scrolls_at_the_speed_until_the_level_ends() -> None:
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
    assert track.distance == pytest.approx(100.0)


def test_p04_r06_negative_time_does_not_move_the_track() -> None:
    track = ScrollTrack(10.0, 100.0)
    track.step(-5.0)
    assert track.progress == 0.0 and track.distance == 0.0


def test_p04_r06_time_scale_speeds_up_or_pauses_the_track() -> None:
    track = ScrollTrack(10.0, 100.0)
    track.time_scale = 4.0
    track.step(1.0)
    assert track.progress == pytest.approx(40.0)
    track.time_scale = 0.0
    track.step(1.0)
    assert track.progress == pytest.approx(40.0)


def test_p07_r03_a_held_track_scrolls_the_ground_but_not_the_level() -> None:
    track = ScrollTrack(10.0, 100.0)
    track.held = True
    track.step(2.0)
    assert track.progress == 0.0
    assert track.distance == pytest.approx(20.0)
    track.held = False
    track.step(1.0)
    assert track.progress == pytest.approx(10.0)


def test_p07_r03_the_ground_keeps_its_lead_when_the_level_is_sought() -> None:
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


def test_p04_r06_speed_factor_eases_over_its_seconds() -> None:
    track = ScrollTrack(10.0, 1000.0)
    track.set_speed_factor(0.0, 2.0)
    track.step(1.0)
    assert track.speed_factor == pytest.approx(0.5)
    track.step(1.0)
    assert track.speed_factor == pytest.approx(0.0)
    track.step(1.0)
    assert track.speed_factor == pytest.approx(0.0)


def test_speed_factor_and_speed_must_not_be_negative() -> None:
    with pytest.raises(ValueError):
        ScrollTrack(0.0, 10.0)
    with pytest.raises(ValueError):
        ScrollTrack(10.0, -1.0)
    track = ScrollTrack(10.0, 10.0)
    with pytest.raises(ValueError):
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

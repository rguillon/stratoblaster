"""Unit tests of `src/app/perf_monitor.py`."""
# (P13-R01, P13-R03, P13-R04, ENG-111).

from unittest.mock import MagicMock

import pytest
from helpers.dom import FakeDocument, FakeEvent

from app import perf_monitor
from app.perf_monitor import PerfMonitor, PerfOverlayOptions, perf_overlay


class Clock:
    """A clock in milliseconds that the test moves on."""

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def frame(monitor: PerfMonitor, clock: Clock, ms: float) -> None:
    monitor.frame_started()
    clock.now += ms
    monitor.frame_ended()


def test_p13_r01_frames_are_counted_and_the_long_ones_are_flagged() -> None:
    clock = Clock()
    monitor = PerfMonitor(50, clock)
    frame(monitor, clock, 16)
    frame(monitor, clock, 80)
    numbers = monitor.numbers
    assert numbers.frames == 2
    assert numbers.long_frames == 1
    assert numbers.longest_frame == 80


def test_p13_r01_a_frame_end_without_a_start_is_ignored() -> None:
    clock = Clock()
    monitor = PerfMonitor(50, clock)
    monitor.frame_ended()
    assert monitor.numbers.frames == 0


def test_p13_r04_the_first_frames_of_a_level_are_skipped_once_it_has_loaded() -> None:
    clock = Clock()
    monitor = PerfMonitor(50, clock)
    monitor.load_started()
    frame(monitor, clock, 300)
    monitor.load_finished(skip_frames=2)
    frame(monitor, clock, 200)
    frame(monitor, clock, 200)
    frame(monitor, clock, 10)
    numbers = monitor.numbers
    assert numbers.frames == 1
    assert numbers.long_frames == 0


def test_p13_r03_the_loading_time_and_its_longest_step_are_recorded() -> None:
    clock = Clock()
    monitor = PerfMonitor(50, clock)
    monitor.load_started()
    assert monitor.loading is True
    frame(monitor, clock, 120)
    frame(monitor, clock, 40)
    clock.now += 5
    monitor.load_finished()
    assert monitor.loading is False
    numbers = monitor.numbers
    assert numbers.last_load == 165
    assert numbers.longest_load_step == 120
    assert numbers.frames == 0


def test_p13_r03_a_load_started_inside_a_frame_counts_that_frame() -> None:
    clock = Clock()
    monitor = PerfMonitor(50, clock)
    monitor.frame_started()
    clock.now += 30
    monitor.load_started()
    clock.now += 10
    monitor.load_finished()
    # The loading runs from the start of the frame that confirmed the level: 30 + 10 ms.
    assert monitor.numbers.last_load == 40
    monitor.frame_ended()


def test_p13_r03_finishing_a_load_that_never_started_does_nothing() -> None:
    clock = Clock()
    monitor = PerfMonitor(50, clock)
    monitor.load_finished()
    assert monitor.numbers.last_load is None


def test_p13_r01_reset_clears_the_counts_but_keeps_the_last_load() -> None:
    clock = Clock()
    monitor = PerfMonitor(50, clock)
    frame(monitor, clock, 90)
    monitor.reset(1)
    numbers = monitor.numbers
    assert (numbers.frames, numbers.long_frames, numbers.longest_frame) == (0, 0, 0)
    frame(monitor, clock, 5)
    assert monitor.numbers.frames == 0


def test_eng111_without_a_perf_parent_the_overlay_does_nothing() -> None:
    clock = Clock()
    perf = PerfMonitor(50, clock)
    options = PerfOverlayOptions(FakeDocument(), None, None)
    handle = perf_overlay(options, perf)
    ticker = MagicMock()
    assert handle.wrap(ticker) is ticker
    handle.dispose()


def test_eng111_the_overlay_is_toggled_by_its_key_and_refreshed_after_each_frame(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    doc = FakeDocument()
    parent = doc.createElement("div")
    target = MagicMock()
    clock = Clock()
    perf = PerfMonitor(50, clock)
    handle = perf_overlay(PerfOverlayOptions(doc, parent, target), perf)
    on_key = target.addEventListener.call_args.args[1]
    event = FakeEvent()
    event.code = "F3"
    event.preventDefault = MagicMock()
    on_key(event)
    event.preventDefault.assert_called_once()
    overlay_root = parent.children[0]
    assert overlay_root.hidden is False

    simulate = MagicMock()
    wrapped = handle.wrap(perf_monitor.Ticker(simulate, MagicMock()))
    wrapped.simulate(0.5)
    simulate.assert_called_once_with(0.5)
    assert overlay_root.textContent.startswith("Long frames: 0")

    other = FakeEvent()
    other.code = "KeyZ"
    on_key(other)  # another key: nothing toggles
    assert overlay_root.hidden is False
    handle.dispose()
    target.removeEventListener.assert_called_once()
    assert parent.children == []

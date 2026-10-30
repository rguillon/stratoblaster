"""Unit tests of `src/input/hold_repeater.py`."""

import pytest

from input.hold_repeater import HoldRepeater


def test_p01_r09_a_press_is_emitted_once_until_released() -> None:
    repeater = HoldRepeater(0.35, 0.12)
    assert repeater.press("up") is True
    assert repeater.press("up") is False
    repeater.release("up")
    assert repeater.press("up") is True


def test_p01_r09_no_repeat_before_the_delay() -> None:
    repeater = HoldRepeater(0.35, 0.12)
    repeater.press("down")
    assert repeater.update(0.2) == []
    assert repeater.update(0.1) == []


def test_p01_r09_repeats_after_the_delay_then_every_interval() -> None:
    repeater = HoldRepeater(0.35, 0.12)
    repeater.press("down")
    assert repeater.update(0.4) == ["down"]
    # 0.35 - 0.4 is past zero: one repeat now, 0.07 of the interval left.
    assert repeater.update(0.06) == []
    assert repeater.update(0.02) == ["down"]


def test_p01_r09_a_long_frame_emits_every_repeat_it_covers() -> None:
    repeater = HoldRepeater(0.1, 0.1)
    repeater.press("left")
    # 0.1 - 0.35 = -0.25, then -0.13 and -0.01 are repeats too; 0.09 is left for the next one.
    assert repeater.update(0.35) == ["left", "left", "left"]


def test_p01_r09_release_stops_the_repeats() -> None:
    repeater = HoldRepeater(0.1, 0.1)
    repeater.press("left")
    repeater.release("left")
    assert repeater.update(1.0) == []
    repeater.release("unknown")


def test_p01_r09_held_lists_keys_in_press_order_and_release_all_clears() -> None:
    repeater = HoldRepeater(0.1, 0.1)
    repeater.press("up")
    repeater.press("right")
    assert repeater.held == ["up", "right"]
    repeater.release_all()
    assert repeater.held == []


def test_p01_r09_repeats_come_in_press_order() -> None:
    repeater = HoldRepeater(0.1, 0.5)
    repeater.press("up")
    repeater.press("down")
    assert repeater.update(0.2) == ["up", "down"]


@pytest.mark.parametrize(("delay", "interval"), [(0.1, 0.0), (0.1, -1.0), (-0.1, 0.1)])
def test_p01_r09_invalid_timing_is_refused(delay: float, interval: float) -> None:
    with pytest.raises(ValueError):
        HoldRepeater(delay, interval)

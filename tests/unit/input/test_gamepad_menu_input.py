"""Unit tests of `src/input/gamepad_menu_input.py`."""

import pytest
from helpers.gamepads import FakeGamepad

from config.menu_input import MENU_INPUT_CONFIG
from input.gamepad_menu_input import (
    GamepadMenuInput,
    axis_value,
    browser_gamepads,
    stick_direction,
)


def make_input(pads: list) -> GamepadMenuInput:
    return GamepadMenuInput(lambda: pads, MENU_INPUT_CONFIG)


def test_p01_r10_axis_value_reads_inside_the_list_and_defaults_to_zero() -> None:
    assert axis_value([0.5, -0.25], 1) == -0.25
    assert axis_value([0.5], 3) == 0
    assert axis_value([0.5], -1) == 0


@pytest.mark.parametrize(
    ("x", "y", "expected"),
    [
        (0.0, 0.0, None),
        (0.1, 0.1, None),
        (1.0, 0.0, "right"),
        (-1.0, 0.0, "left"),
        (0.0, 1.0, "down"),
        (0.0, -1.0, "up"),
        (0.6, 0.6, "right"),
        (-0.4, 0.9, "down"),
    ],
)
def test_p01_r10_stick_direction_picks_the_dominant_axis(
    x: float, y: float, expected: str | None
) -> None:
    assert stick_direction(x, y, 0.35) == expected


def test_p01_r10_buttons_fire_once_on_press() -> None:
    pad = FakeGamepad().press(0)
    menu = make_input([pad])
    assert menu.update(0.016) == ["confirm"]
    assert menu.update(0.016) == []
    pad.release(0)
    assert menu.update(0.016) == []
    pad.press(0)
    assert menu.update(0.016) == ["confirm"]


def test_p01_r10_dpad_direction_repeats_while_held() -> None:
    pad = FakeGamepad().press(12)
    menu = make_input([pad])
    assert menu.update(0) == ["up"]
    assert menu.update(0.2) == []
    assert menu.update(0.2) == ["up"]


def test_p01_r10_left_stick_repeats_while_tilted_inside_the_dead_zone_is_ignored() -> None:
    pad = FakeGamepad().tilt(0, 0.2)
    menu = make_input([pad])
    assert menu.update(0) == []
    pad.tilt(0, 0.9)
    assert menu.update(0) == ["down"]


def test_p01_r10_releasing_the_stick_stops_its_repeat() -> None:
    pad = FakeGamepad().tilt(1, 0)
    menu = make_input([pad])
    menu.update(0)
    pad.tilt(0, 0)
    assert menu.update(5.0) == []


def test_p01_r10_all_connected_gamepads_are_merged_and_empty_slots_skipped() -> None:
    first = FakeGamepad().press(0)
    second = FakeGamepad().press(1)
    menu = GamepadMenuInput(lambda: [None, first, second], MENU_INPUT_CONFIG)
    assert menu.update(0) == ["confirm", "back"]


def test_p01_r10_a_direction_held_on_the_dpad_and_the_stick_is_emitted_once() -> None:
    pad = FakeGamepad().press(13).tilt(0, 1)
    menu = make_input([pad])
    assert menu.update(0) == ["down"]


def test_p01_r10_start_button_pauses() -> None:
    menu = make_input([FakeGamepad().press(9)])
    assert menu.update(0) == ["pause"]


def test_p01_r10_browser_gamepads_reads_navigator_or_gives_nothing() -> None:
    pad = FakeGamepad()

    class Nav:
        def getGamepads(self) -> list:  # noqa: N802 (DOM name)
            return [None, pad]

    assert browser_gamepads(Nav())() == [None, pad]
    assert browser_gamepads(object())() == []

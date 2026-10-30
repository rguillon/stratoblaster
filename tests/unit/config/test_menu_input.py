"""Unit tests of `src/config/menu_input.py`."""

from config.menu_input import MENU_INPUT_CONFIG
from input.menu_action import MENU_ACTIONS


def test_p01_r09_every_keyboard_binding_is_a_known_menu_action() -> None:
    assert set(MENU_INPUT_CONFIG.keyboard.values()) <= set(MENU_ACTIONS)


def test_p01_r10_every_gamepad_binding_is_a_known_menu_action() -> None:
    assert set(MENU_INPUT_CONFIG.gamepad_buttons.values()) <= set(MENU_ACTIONS)


def test_p12_r01_escape_is_back_on_menus_and_pause_in_a_level() -> None:
    assert MENU_INPUT_CONFIG.keyboard["Escape"] == "cancel"
    assert MENU_INPUT_CONFIG.keyboard["Backspace"] == "back"


def test_p01_r10_the_standard_gamepad_buttons_are_mapped() -> None:
    buttons = MENU_INPUT_CONFIG.gamepad_buttons
    assert buttons[0] == "confirm"
    assert buttons[1] == "back"
    assert buttons[9] == "pause"
    assert [buttons[i] for i in (12, 13, 14, 15)] == ["up", "down", "left", "right"]


def test_p01_r10_the_left_stick_reads_y_as_down_positive() -> None:
    stick = MENU_INPUT_CONFIG.gamepad_stick
    assert (stick.x_axis, stick.y_axis) == (0, 1)
    assert 0 < MENU_INPUT_CONFIG.gamepad_dead_zone < 1


def test_p01_r09_key_repeat_delay_is_longer_than_its_interval() -> None:
    assert MENU_INPUT_CONFIG.repeat_delay_seconds > MENU_INPUT_CONFIG.repeat_interval_seconds > 0

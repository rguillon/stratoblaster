# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/config/menu_input.py` (bindings in config, UI-INPUT-03)."""

from config.menu_input import MENU_INPUT_CONFIG
from input.menu_action import MENU_ACTIONS


def test_ui_input_04_every_keyboard_binding_is_a_known_menu_action() -> None:
    assert set(MENU_INPUT_CONFIG.keyboard.values()) <= set(MENU_ACTIONS)


def test_ui_input_07_every_gamepad_binding_is_a_known_menu_action() -> None:
    assert set(MENU_INPUT_CONFIG.gamepad_buttons.values()) <= set(MENU_ACTIONS)


def test_ui_pause_01_escape_is_back_on_menus_and_pause_in_a_level() -> None:
    """Also UI-INPUT-02 (what cancel and back mean) and UI-INPUT-04 (the bindings)."""
    assert MENU_INPUT_CONFIG.keyboard["Escape"] == "cancel"
    assert MENU_INPUT_CONFIG.keyboard["Backspace"] == "back"


def test_ui_input_07_the_standard_gamepad_buttons_are_mapped() -> None:
    buttons = MENU_INPUT_CONFIG.gamepad_buttons
    assert buttons[0] == "confirm"
    assert buttons[1] == "back"
    assert buttons[9] == "pause"
    assert [buttons[i] for i in (12, 13, 14, 15)] == ["up", "down", "left", "right"]


def test_ui_input_08_the_left_stick_reads_y_as_down_positive() -> None:
    stick = MENU_INPUT_CONFIG.gamepad_stick
    assert (stick.x_axis, stick.y_axis) == (0, 1)
    assert 0 < MENU_INPUT_CONFIG.gamepad_dead_zone < 1


def test_ui_input_06_key_repeat_delay_is_longer_than_its_interval() -> None:
    assert MENU_INPUT_CONFIG.repeat_delay_seconds > MENU_INPUT_CONFIG.repeat_interval_seconds > 0


def test_ui_input_04_wasd_positions_map_to_the_same_actions_as_arrows() -> None:
    keys = MENU_INPUT_CONFIG.keyboard
    assert keys["KeyW"] == keys["ArrowUp"] == "up"
    assert keys["KeyS"] == keys["ArrowDown"] == "down"
    assert keys["KeyA"] == keys["ArrowLeft"] == "left"
    assert keys["KeyD"] == keys["ArrowRight"] == "right"

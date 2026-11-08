# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/input/pointer_menu_input.py`."""

from input.menu_action import MenuSelect
from input.pointer_menu_input import pointer_command, pointer_commands


def test_ui_input_09_tapping_the_selected_entry_confirms_it() -> None:
    assert pointer_command(2, 2) == "confirm"


def test_ui_input_09_tapping_another_entry_selects_it() -> None:
    command = pointer_command(0, 3)
    assert isinstance(command, MenuSelect)
    assert command.select == 0


def test_ui_input_09_one_tap_selects_then_confirms() -> None:
    """D-287: one click is enough."""
    first, second = pointer_commands(0, 3, two_step=False)
    assert isinstance(first, MenuSelect)
    assert first.select == 0
    assert second == "confirm"
    assert pointer_commands(2, 2, two_step=False) == ["confirm"]


def test_ui_input_09_a_two_step_screen_keeps_select_then_confirm() -> None:
    only = pointer_commands(0, 3, two_step=True)
    assert len(only) == 1
    assert isinstance(only[0], MenuSelect)
    assert pointer_commands(2, 2, two_step=True) == ["confirm"]

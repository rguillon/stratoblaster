# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/input/pointer_menu_input.py`."""

from input.menu_action import MenuSelect
from input.pointer_menu_input import pointer_command


def test_ui_input_09_tapping_the_selected_entry_confirms_it() -> None:
    assert pointer_command(2, 2) == "confirm"


def test_ui_input_09_tapping_another_entry_selects_it() -> None:
    command = pointer_command(0, 3)
    assert isinstance(command, MenuSelect)
    assert command.select == 0

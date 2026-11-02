# Copyright (c) 2026 Renaud Guillon
"""Tap / click on a menu entry (UI-INPUT-09, UI-INPUT-01).

Tapping the selected entry confirms it, tapping another entry selects it.
"""

from input.menu_action import MenuSelect

# isort: split
# __pragma__ ("skip")
from input.menu_action import MenuCommand

# __pragma__ ("noskip")


def pointer_command(tapped: int, selected: int) -> MenuCommand:
    """Return the command for tapping entry `tapped` while entry `selected` is selected."""
    return "confirm" if tapped == selected else MenuSelect(tapped)

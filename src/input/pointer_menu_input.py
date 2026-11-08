# Copyright (c) 2026 Renaud Guillon
"""Tap / click on a menu entry (UI-INPUT-09, UI-INPUT-01).

One tap selects the entry and confirms it (D-287). On the dev viewers, where picking an item shows
it, tapping the selected entry confirms it and tapping another only selects it.
"""

from input.menu_action import MenuSelect

# isort: split
# __pragma__ ("skip")
from input.menu_action import MenuCommand

# __pragma__ ("noskip")


def pointer_command(tapped: int, selected: int) -> MenuCommand:
    """Return the command for tapping entry `tapped` while entry `selected` is selected.

    The two-step tap of the dev viewers: confirm the selected entry, select another.
    """
    return "confirm" if tapped == selected else MenuSelect(tapped)


def pointer_commands(tapped: int, selected: int, two_step: bool) -> list[MenuCommand]:
    """Return the commands, in order, for tapping entry `tapped` while `selected` is selected.

    One tap goes: select the entry if it is not, then confirm it (D-287). `two_step` (the dev
    viewers): see `pointer_command`.
    """
    if two_step:
        return [pointer_command(tapped, selected)]
    if tapped == selected:
        return ["confirm"]
    return [MenuSelect(tapped), "confirm"]

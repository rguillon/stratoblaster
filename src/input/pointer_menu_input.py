"""Tap / click on a menu entry (P01-R11, P01-R12):
tapping the selected entry confirms it, tapping another entry selects it."""

from org.transcrypt.stubs.browser import __pragma__

from input.menu_action import MenuSelect

__pragma__("skip")
from input.menu_action import MenuCommand  # noqa: E402

__pragma__("noskip")


def pointer_command(tapped: int, selected: int) -> MenuCommand:
    """The command for tapping entry `tapped` while entry `selected` is selected."""
    return "confirm" if tapped == selected else MenuSelect(tapped)

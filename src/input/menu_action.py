"""Abstract menu actions every input device is translated into (P01-R12), ported from
`input/menu-action.ts`:
- `back`: Back on the menu screens (Backspace, gamepad B); nothing in a level (P12-R01);
- `cancel`: the Escape key: Back on the menu screens (P01-R09), pause in a level (P12-R01);
- `pause`: pauses a level, or resumes it from the pause menu (P, gamepad Start / Select, the
  on-screen pause button);
- `resume`: resumes a paused level (test API, P12-R12).

An action is a plain string (the TypeScript union of literals); `MENU_ACTIONS` lists them all.
"""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import TypeGuard  # noqa: E402

MenuAction = str
MenuDirection = str
__pragma__("noskip")

# Every menu action, e.g. to validate actions coming from outside (test API).
MENU_ACTIONS = ["up", "down", "left", "right", "confirm", "back", "cancel", "pause", "resume"]

# Selection moves, which repeat while held.
DIRECTIONS = ["up", "down", "left", "right"]


class MenuSelect:
    """Selects entry `select` of the current screen directly (tap or click on another entry)."""

    def __init__(self, select: int) -> None:
        self.select = select


class MenuSet:
    """Sets slider `set` of the settings screen to `value` (tap or drag on it, P12-R04)."""

    def __init__(self, set_index: int, value: float) -> None:
        self.set = set_index
        self.value = value


__pragma__("skip")
# What menu screens react to: an abstract action, a direct selection or a slider value.
MenuCommand = MenuAction | MenuSelect | MenuSet
__pragma__("noskip")


def is_menu_direction(action: MenuAction) -> TypeGuard[MenuDirection]:
    """True for the four selection moves."""
    return action in DIRECTIONS


def is_menu_action(value: object) -> TypeGuard[MenuAction]:
    """True when `value` is one of `MENU_ACTIONS`."""
    return isinstance(value, str) and value in MENU_ACTIONS

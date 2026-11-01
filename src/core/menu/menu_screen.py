"""The screens of the menu flow (UI-FLOW-01), a pure state machine (UI-FLOW-04)

`pause` is the menu over a paused level, `settings` the settings screen, from the title or the
pause menu (UI-PAUSE-07, UI-SET-01). `dev` is the dev menu (from the title, with `?dev`), and
`dev-viewer` one of its viewers (D-199).
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Literal  # noqa: E402 (after the Transcrypt skip block, ENG-153)

MenuScreen = Literal[
    "loading",
    "title",
    "ship-select",
    "level-select",
    "game",
    "pause",
    "settings",
    "dev",
    "dev-viewer",
]

__pragma__("noskip")

# Allowed screen changes (UI-FLOW-02): forward through the flow, Back on each menu screen
# (UI-FLOW-05), from a completed level back to the level select screen (UI-FLOW-07), and the pause
# menu and the settings screen. The level is left through the pause menu (UI-FLOW-06).
# (No annotation: Transcrypt would not export an annotated module-level assignment.)
MENU_TRANSITIONS = {
    "loading": ["title"],
    "title": ["ship-select", "settings", "dev"],
    "ship-select": ["level-select", "title"],
    "level-select": ["game", "ship-select"],
    "game": ["pause", "level-select"],
    "pause": ["game", "settings", "title"],
    "settings": ["title", "pause"],
    "dev": ["title", "dev-viewer"],
    "dev-viewer": ["dev"],
}


def can_transition(source: MenuScreen, target: MenuScreen) -> bool:
    """True when the flow may go from `source` to `target`; it refuses the others (UI-FLOW-03)."""
    return target in MENU_TRANSITIONS[source]

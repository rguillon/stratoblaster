"""The screens of the menu flow (`02-game-design.md` section 7, P01-R01)

`pause` is the menu over a paused level, `settings` the settings screen, from the title or the
pause menu (P12-R02, P12-R04). `dev` is the dev menu (from the title, with `?dev`), and
`dev-viewer` one of its viewers (D-199).
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Literal  # noqa: E402

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

# Allowed screen changes: forward through the flow, Back on each menu screen, from a completed
# level back to the level select screen (P06-R03), and the pause menu and the settings screen
# (P12-R02, P12-R04). The level is left through the pause menu.
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
    """True when the flow may go from `source` to `target`."""
    return target in MENU_TRANSITIONS[source]

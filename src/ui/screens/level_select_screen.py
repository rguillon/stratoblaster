"""Level select screen (P01-R07), ported from `ui/screens/level-select-screen.ts`: a grid of
levels, locked ones greyed out with a padlock."""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

from ui.menu_view import LevelSelectView  # noqa: E402
from ui.screens.screen_handlers import ScreenHandlers  # noqa: E402

__pragma__("noskip")

from ui.screens.elements import back_button, element, entry, padlock  # noqa: E402


def render_level_select_screen(doc: Any, view: LevelSelectView, handlers: ScreenHandlers) -> Any:
    """Renders the level select screen (P01-R07)."""
    root = element(doc, "div", "menu-screen level-select-screen")
    grid = element(doc, "div", "level-grid")
    grid.style.gridTemplateColumns = "repeat(" + str(view.columns) + ", 1fr)"
    for i, level in enumerate(view.levels):
        cell = entry(doc, "level-cell", i, i == view.selected, handlers.on_tap)
        cell.append(element(doc, "span", "level-label", level.label))
        if level.locked:
            # Still selectable (not aria-disabled): confirming it gives the "locked" feedback.
            cell.classList.add("locked")
            cell.append(padlock(doc))
        grid.append(cell)
    root.append(
        back_button(doc, view.back, handlers.on_back),
        element(doc, "h2", "menu-heading", view.heading),
        grid,
        element(doc, "div", "menu-status"),
        element(doc, "div", "menu-hint", view.hint),
    )
    return root

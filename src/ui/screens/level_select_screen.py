# Copyright (c) 2026 Renaud Guillon
"""Level select screen (UI-LEVEL-01): a grid of levels, locked ones greyed out.

A padlock (UI-LEVEL-04).
"""

from ui.screens.elements import back_button, element, entry, padlock

# isort: split
# __pragma__ ("skip")
from typing import Any

from ui.menu_view import LevelSelectView
from ui.screens.screen_handlers import ScreenHandlers

# __pragma__ ("noskip")


def render_level_select_screen(doc: Any, view: LevelSelectView, handlers: ScreenHandlers) -> Any:
    """Render the level select screen (UI-LEVEL-09)."""
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

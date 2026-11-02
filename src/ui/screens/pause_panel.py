# Copyright (c) 2026 Renaud Guillon
"""The pause menu (UI-PAUSE-07): over the playfield, dimmed by a layer behind it (UI-PAUSE-03).

Resume, Settings and Main menu, or the question before leaving the level.
"""

from ui.screens.elements import element, entry

# isort: split
# __pragma__ ("skip")
from typing import Any

from ui.menu_view import PauseQuestion, PauseView
from ui.screens.screen_handlers import ScreenHandlers

# __pragma__ ("noskip")


def _question(doc: Any, asked: PauseQuestion, handlers: ScreenHandlers) -> Any:
    """Return the `Leave the level?` question (UI-PAUSE-10): No and Yes.

    A tap selects, a second tap confirms.
    """
    box = element(doc, "div", "pause-question")
    row = element(doc, "div", "pause-choices")
    for i, label in enumerate(asked.choices):
        choice = entry(doc, "pause-choice", i, i == asked.selected, handlers.on_tap)
        choice.textContent = label
        row.append(choice)
    box.append(element(doc, "div", "pause-question-text", asked.text), row)
    return box


def pause_panel(doc: Any, view: PauseView, selected: int, handlers: ScreenHandlers) -> Any:
    """Return the pause menu (UI-PAUSE-07) over the playfield."""
    dim = element(doc, "div", "pause-dim")
    panel = element(doc, "div", "pause-panel")
    panel.append(element(doc, "div", "pause-heading", view.heading))
    if view.question:
        panel.append(_question(doc, view.question, handlers))
    else:
        for i, label in enumerate(view.entries):
            item = entry(doc, "pause-entry", i, i == selected, handlers.on_tap)
            item.textContent = label
            panel.append(item)
        panel.append(element(doc, "div", "menu-hint pause-hint", view.hint))
    dim.append(panel)
    return dim

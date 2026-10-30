"""The pause menu (P12-R02): over the playfield, dimmed
by a layer behind it: Resume, Settings and Main menu, or the question before leaving the level."""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

from ui.menu_view import PauseQuestion, PauseView  # noqa: E402
from ui.screens.screen_handlers import ScreenHandlers  # noqa: E402

__pragma__("noskip")

from ui.screens.elements import element, entry  # noqa: E402


def _question(doc: Any, asked: PauseQuestion, handlers: ScreenHandlers) -> Any:
    """The `Leave the level?` question (P12-R02): No and Yes, a tap selects, a second confirms."""
    box = element(doc, "div", "pause-question")
    row = element(doc, "div", "pause-choices")
    for i, label in enumerate(asked.choices):
        choice = entry(doc, "pause-choice", i, i == asked.selected, handlers.on_tap)
        choice.textContent = label
        row.append(choice)
    box.append(element(doc, "div", "pause-question-text", asked.text), row)
    return box


def pause_panel(doc: Any, view: PauseView, selected: int, handlers: ScreenHandlers) -> Any:
    """The pause menu (P12-R02) over the playfield."""
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

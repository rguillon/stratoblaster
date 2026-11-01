# Copyright (c) 2026 Renaud Guillon
"""Ship select screen (UI-SHIP-02): a card with name and stats under each rotating ship."""

from ui.screens.elements import back_button, element, entry

# isort: split
# __pragma__ ("skip")
from typing import Any

from ui.menu_view import ShipSelectView
from ui.screens.screen_handlers import ScreenHandlers

# __pragma__ ("noskip")


def render_ship_select_screen(doc: Any, view: ShipSelectView, handlers: ScreenHandlers) -> Any:
    """Render the ship select screen (UI-SHIP-02)."""
    root = element(doc, "div", "menu-screen ship-select-screen")
    cards = element(doc, "div", "ship-cards")
    cards.style.width = str(view.cards_width_percent) + "%"
    for i, ship in enumerate(view.ships):
        card = entry(doc, "ship-card", i, i == view.selected, handlers.on_tap)
        card.append(element(doc, "div", "ship-card-name", ship.title))
        for line in ship.lines:
            card.append(element(doc, "div", "ship-card-stat", line))
        cards.append(card)
    root.append(
        back_button(doc, view.back, handlers.on_back),
        element(doc, "h2", "menu-heading", view.heading),
        cards,
        element(doc, "div", "menu-hint", view.hint),
    )
    return root

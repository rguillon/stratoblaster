"""Ship select screen (P01-R06), ported from `ui/screens/ship-select-screen.ts`: a card with name
and stats under each rotating ship."""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

from ui.menu_view import ShipSelectView  # noqa: E402
from ui.screens.screen_handlers import ScreenHandlers  # noqa: E402

__pragma__("noskip")

from ui.screens.elements import back_button, element, entry  # noqa: E402


def render_ship_select_screen(doc: Any, view: ShipSelectView, handlers: ScreenHandlers) -> Any:
    """Renders the ship select screen (P01-R06)."""
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

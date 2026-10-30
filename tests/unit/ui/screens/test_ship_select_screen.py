"""Unit tests of `src/ui/screens/ship_select_screen.py`."""

from helpers.dom import FakeDocument

from ui.caption_row import Caption
from ui.menu_view import ShipSelectView
from ui.screens.screen_handlers import ScreenHandlers
from ui.screens.ship_select_screen import render_ship_select_screen


def test_p01_r06_one_card_per_ship_with_its_name_and_stats() -> None:
    taps: list[int] = []
    ships = [Caption("Alpha", ["Speed x1", "HP 5"]), Caption("Beta", ["HP 9"])]
    view = ShipSelectView("Choose", "Hint", "Back", 1, ships, 70)
    root = render_ship_select_screen(
        FakeDocument(), view, ScreenHandlers(taps.append, lambda: None)
    )
    cards = root.querySelector(".ship-cards")
    assert cards.style.width == "70%"
    assert len(cards.children) == 2
    alpha = cards.children[0]
    assert alpha.querySelector(".ship-card-name").textContent == "Alpha"
    assert [line.textContent for line in alpha.querySelectorAll(".ship-card-stat")] == [
        "Speed x1",
        "HP 5",
    ]
    assert cards.children[1].classList.contains("selected")
    alpha.fire("click")
    assert taps == [0]


def test_p01_r11_the_ship_select_has_a_back_button_heading_and_hint() -> None:
    backs: list[bool] = []
    view = ShipSelectView("Choose", "Hint", "Back", 0, [], 50)
    root = render_ship_select_screen(
        FakeDocument(), view, ScreenHandlers(lambda i: None, lambda: backs.append(True))
    )
    assert root.querySelector(".menu-heading").textContent == "Choose"
    assert root.querySelector(".menu-hint").textContent == "Hint"
    root.querySelector(".menu-back").fire("click")
    assert backs == [True]

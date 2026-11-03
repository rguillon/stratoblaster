# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/ui/screens/dev_screen.py` (D-199)."""

from types import SimpleNamespace

from helpers.dom import FakeDocument

from ui.menu_view import DevAudioView, DevChoice, DevMenuView, DevViewerView
from ui.screens.dev_screen import (
    centre_menu,
    render_dev_audio_screen,
    render_dev_screen,
    render_dev_viewer_screen,
)
from ui.screens.screen_handlers import ScreenHandlers


def test_d199_the_dev_menu_lists_one_tappable_entry_per_viewer() -> None:
    """DEV-MENU-03: the dev menu."""
    taps: list[int] = []
    backs: list[bool] = []
    view = DevMenuView("Dev tools", "Pick", "Back", 1, ["Ships", "Enemies"])
    root = render_dev_screen(
        FakeDocument(), view, ScreenHandlers(taps.append, lambda: backs.append(True))
    )
    entries = root.querySelectorAll(".dev-entry")
    assert [e.textContent for e in entries] == ["Ships", "Enemies"]
    assert entries[1].classList.contains("selected")
    entries[0].fire("click")
    root.querySelector(".menu-back").fire("click")
    assert (taps, backs) == ([0], [True])
    assert root.querySelector(".menu-heading").textContent == "Dev tools"


def test_d199_a_viewer_shows_its_item_and_passes_the_wheel_on() -> None:
    """DEV-MENU-05: a viewer's screen."""
    wheels: list[float] = []
    view = DevViewerView("Enemies", "Wheel", "Back", 2, "Hornet", "3 / 21", scrub=False)
    handlers = ScreenHandlers(lambda _i: None, lambda: None, None, None, None, wheels.append)
    root = render_dev_viewer_screen(FakeDocument(), view, handlers)
    assert root.querySelector(".dev-item").textContent == "Hornet"
    assert root.querySelector(".dev-position").textContent == "3 / 21"
    assert root.querySelector(".dev-heading").textContent == "Enemies"
    assert root.querySelector(".dev-status") is not None
    prevented: list[bool] = []
    root.fire(
        "wheel",
        SimpleNamespace(deltaY=120, target=None, preventDefault=lambda: prevented.append(True)),
    )
    assert (wheels, prevented) == ([120], [True])


def test_d199_without_a_wheel_handler_the_wheel_is_only_kept_from_the_page() -> None:
    view = DevViewerView("Levels", "Wheel", "Back", 0, "1-1", "1 / 20", scrub=True)
    root = render_dev_viewer_screen(
        FakeDocument(), view, ScreenHandlers(lambda _i: None, lambda: None)
    )
    prevented: list[bool] = []
    root.fire(
        "wheel",
        SimpleNamespace(deltaY=5, target=None, preventDefault=lambda: prevented.append(True)),
    )
    assert prevented == [True]


class Target:
    def __init__(self, back: bool) -> None:
        self.back = back

    def closest(self, _selector: str) -> bool:
        return self.back


def pointer(x: float, y: float, back: bool = False) -> SimpleNamespace:
    return SimpleNamespace(clientX=x, clientY=y, pointerId=1, target=Target(back))


def test_d199_a_drag_on_a_viewer_turns_its_model_but_not_from_the_back_button() -> None:
    """DEV-MENU-10: dragging turns the model."""
    turns: list[tuple[float, float]] = []
    view = DevViewerView("Ships", "Drag", "Back", 0, "Alpha", "1 / 3", scrub=False)
    handlers = ScreenHandlers(
        lambda _i: None,
        lambda: None,
        None,
        None,
        None,
        None,
        lambda dx, dy: turns.append((dx, dy)),
    )
    root = render_dev_viewer_screen(FakeDocument(), view, handlers)
    root.setPointerCapture = lambda _pointer_id: None
    root.fire("pointermove", pointer(5, 5))
    root.fire("pointerdown", pointer(10, 20))
    root.fire("pointermove", pointer(15, 18))
    root.fire("pointermove", pointer(25, 18))
    root.fire("pointerup", pointer(25, 18))
    root.fire("pointermove", pointer(40, 40))
    root.fire("pointerdown", pointer(0, 0, back=True))
    root.fire("pointermove", pointer(9, 9))
    assert turns == [(5, -2), (10, 0)]


def test_d206_a_grouped_viewer_has_a_menu_of_tappable_headings_and_items() -> None:
    """DEV-MENU-07: the scrolling menu."""
    taps: list[int] = []
    menu = [
        DevChoice("Farm (2)", 0, selected=True, heading=True),
        DevChoice("hut", 0, selected=False),
        DevChoice("barn", 1, selected=True),
        DevChoice("City (1)", 2, selected=False, heading=True),
    ]
    view = DevViewerView(
        "Props", "Wheel", "Back", 1, "barn", "Farm · 2 / 2", scrub=False, menu=menu
    )
    root = render_dev_viewer_screen(FakeDocument(), view, ScreenHandlers(taps.append, lambda: None))
    panel = root.querySelector(".dev-menu")
    headings = panel.querySelectorAll(".dev-menu-group")
    items = panel.querySelectorAll(".dev-menu-item")
    assert [h.textContent for h in headings] == ["Farm (2)", "City (1)"]
    assert [i.textContent for i in items] == ["hut", "barn"]
    assert headings[0].classList.contains("selected")
    assert items[1].classList.contains("selected")
    headings[1].fire("click")
    items[0].fire("click")
    assert taps == [2, 0]


def test_d206_a_viewer_without_groups_has_no_menu() -> None:
    view = DevViewerView("Ships", "Wheel", "Back", 0, "Alpha", "1 / 2", scrub=False)
    root = render_dev_viewer_screen(
        FakeDocument(), view, ScreenHandlers(lambda _i: None, lambda: None)
    )
    assert root.querySelector(".dev-menu") is None


class Menu:
    def __init__(self, selected: object) -> None:
        self.selected = selected
        self.scrollTop = 0.0
        self.clientHeight = 300.0

    def querySelector(self, _selector: str) -> object:
        return self.selected


def test_d206_the_wheel_over_the_menu_scrolls_it() -> None:
    wheels: list[float] = []
    view = DevViewerView("Props", "Wheel", "Back", 0, "hut", "Farm · 1 / 1", scrub=False, menu=[])
    handlers = ScreenHandlers(lambda _i: None, lambda: None, None, None, None, wheels.append)
    root = render_dev_viewer_screen(FakeDocument(), view, handlers)
    menu = Menu(None)
    target = SimpleNamespace(closest=lambda _selector: menu)
    root.fire("wheel", SimpleNamespace(deltaY=40, target=target, preventDefault=lambda: None))
    assert (menu.scrollTop, wheels) == (40, [])


def test_d206_the_menu_is_scrolled_to_put_the_item_shown_in_its_middle() -> None:
    menu = Menu(SimpleNamespace(offsetTop=500.0, offsetHeight=20.0))
    centre_menu(SimpleNamespace(querySelector=lambda _selector: menu))
    assert menu.scrollTop == 360
    centre_menu(SimpleNamespace(querySelector=lambda _selector: None))


def test_d199_without_a_turn_handler_a_drag_on_a_viewer_turns_nothing() -> None:
    """DEV-MENU-10: the drag is followed, with no one to turn the model."""
    view = DevViewerView("Ships", "Drag", "Back", 0, "Alpha", "1 / 3", scrub=False)
    root = render_dev_viewer_screen(
        FakeDocument(), view, ScreenHandlers(lambda _i: None, lambda: None)
    )
    captured: list[int] = []
    root.setPointerCapture = captured.append
    root.fire("pointerdown", pointer(10, 20))
    root.fire("pointermove", pointer(15, 18))
    assert captured == [1]


def test_d206_a_menu_with_no_item_shown_is_left_where_it_is() -> None:
    menu = Menu(None)
    menu.scrollTop = 80.0
    centre_menu(SimpleNamespace(querySelector=lambda _selector: menu))
    assert menu.scrollTop == 80.0


def test_dev_menu_19_an_audio_viewer_is_a_grid_of_tappable_buttons_with_a_status_line() -> None:
    """DEV-MENU-19, DEV-MENU-20: a button per sound or track, in the dev viewers' menu."""
    taps: list[int] = []
    backs: list[bool] = []
    entries = [
        DevChoice("Levels (2)", 0, selected=True, heading=True),
        DevChoice("level-1-1", 0, selected=True),
        DevChoice("level-1-2", 1, selected=False),
    ]
    view = DevAudioView("Music", "Tap to play", "Back", 0, entries)
    root = render_dev_audio_screen(
        FakeDocument(), view, ScreenHandlers(taps.append, lambda: backs.append(True))
    )
    assert root.classList.contains("dev-audio-screen")
    assert root.querySelector(".menu-heading").textContent == "Music"
    assert root.querySelector(".dev-status").textContent == ""
    assert root.querySelector(".menu-hint").textContent == "Tap to play"
    menu = root.querySelector(".dev-audio-menu")
    assert menu.classList.contains("dev-menu")
    items = menu.querySelectorAll(".dev-menu-item")
    assert [i.textContent for i in items] == ["level-1-1", "level-1-2"]
    assert items[0].classList.contains("selected")
    assert menu.querySelector(".dev-menu-group").textContent == "Levels (2)"
    assert items[1].dataset.index == "1"
    # A button plays as soon as it is pressed, not on the release.
    items[1].fire("pointerdown")
    items[1].fire("click")
    root.querySelector(".menu-back").fire("click")
    assert (taps, backs) == ([1], [True])
    root.fire("pointerup")


def test_dev_menu_19_a_button_pressed_is_held_until_the_pointer_lets_go() -> None:
    taps: list[int] = []
    holds: list[bool] = []
    entries = [DevChoice("hit", 0, selected=True), DevChoice("bomb", 1, selected=False)]
    view = DevAudioView("Sounds", "Hold", "Back", 0, entries)
    handlers = ScreenHandlers(taps.append, lambda: None, on_hold=holds.append)
    root = render_dev_audio_screen(FakeDocument(), view, handlers)
    items = root.querySelectorAll(".dev-menu-item")
    items[1].fire("pointerdown")
    assert (taps, holds) == ([1], [True])
    root.fire("pointerup")
    items[0].fire("pointerdown")
    root.fire("pointercancel")
    items[0].fire("pointerdown")
    root.fire("pointerleave")
    assert holds == [True, False, True, False, True, False]

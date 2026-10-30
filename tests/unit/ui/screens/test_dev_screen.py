"""Unit tests of `src/ui/screens/dev_screen.py` (D-199)."""

from types import SimpleNamespace

from helpers.dom import FakeDocument

from ui.menu_view import DevMenuView, DevViewerView
from ui.screens.dev_screen import render_dev_screen, render_dev_viewer_screen
from ui.screens.screen_handlers import ScreenHandlers


def test_d199_the_dev_menu_lists_one_tappable_entry_per_viewer() -> None:
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
    wheels: list[float] = []
    view = DevViewerView("Enemies", "Wheel", "Back", 2, "Hornet", "3 / 21", False)
    handlers = ScreenHandlers(lambda i: None, lambda: None, None, None, None, None, wheels.append)
    root = render_dev_viewer_screen(FakeDocument(), view, handlers)
    assert root.querySelector(".dev-item").textContent == "Hornet"
    assert root.querySelector(".dev-position").textContent == "3 / 21"
    assert root.querySelector(".dev-heading").textContent == "Enemies"
    assert root.querySelector(".dev-status") is not None
    prevented: list[bool] = []
    root.fire("wheel", SimpleNamespace(deltaY=120, preventDefault=lambda: prevented.append(True)))
    assert (wheels, prevented) == ([120], [True])


def test_d199_without_a_wheel_handler_the_wheel_is_only_kept_from_the_page() -> None:
    view = DevViewerView("Levels", "Wheel", "Back", 0, "1-1", "1 / 20", True)
    root = render_dev_viewer_screen(
        FakeDocument(), view, ScreenHandlers(lambda i: None, lambda: None)
    )
    prevented: list[bool] = []
    root.fire("wheel", SimpleNamespace(deltaY=5, preventDefault=lambda: prevented.append(True)))
    assert prevented == [True]


class Target:
    def __init__(self, back: bool) -> None:
        self.back = back

    def closest(self, selector: str) -> bool:
        return self.back


def pointer(x: float, y: float, back: bool = False) -> SimpleNamespace:
    return SimpleNamespace(clientX=x, clientY=y, pointerId=1, target=Target(back))


def test_d199_a_drag_on_a_viewer_turns_its_model_but_not_from_the_back_button() -> None:
    turns: list[tuple[float, float]] = []
    view = DevViewerView("Ships", "Drag", "Back", 0, "Alpha", "1 / 3", False)
    handlers = ScreenHandlers(
        lambda i: None,
        lambda: None,
        None,
        None,
        None,
        None,
        None,
        lambda dx, dy: turns.append((dx, dy)),
    )
    root = render_dev_viewer_screen(FakeDocument(), view, handlers)
    root.setPointerCapture = lambda pointer_id: None
    root.fire("pointermove", pointer(5, 5))
    root.fire("pointerdown", pointer(10, 20))
    root.fire("pointermove", pointer(15, 18))
    root.fire("pointermove", pointer(25, 18))
    root.fire("pointerup", pointer(25, 18))
    root.fire("pointermove", pointer(40, 40))
    root.fire("pointerdown", pointer(0, 0, back=True))
    root.fire("pointermove", pointer(9, 9))
    assert turns == [(5, -2), (10, 0)]

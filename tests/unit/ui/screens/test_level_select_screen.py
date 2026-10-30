"""Unit tests of `src/ui/screens/level_select_screen.py`."""

from helpers.dom import FakeDocument

from ui.menu_view import LevelOption, LevelSelectView
from ui.screens.level_select_screen import render_level_select_screen
from ui.screens.screen_handlers import ScreenHandlers


def render(selected: int, taps: list[int], backs: list[bool]) -> object:
    levels = [LevelOption("1", False), LevelOption("2", True), LevelOption("3", False)]
    view = LevelSelectView("Pick a level", "Arrows", "Back", selected, 2, levels, "Locked")
    handlers = ScreenHandlers(taps.append, lambda: backs.append(True))
    return render_level_select_screen(FakeDocument(), view, handlers)


def test_p01_r07_the_levels_are_laid_out_in_the_columns_of_the_view() -> None:
    root = render(0, [], [])
    grid = root.querySelector(".level-grid")
    assert grid.style.gridTemplateColumns == "repeat(2, 1fr)"
    assert len(grid.children) == 3
    assert [cell.querySelector(".level-label").textContent for cell in grid.children] == [
        "1",
        "2",
        "3",
    ]


def test_p01_r07_a_locked_level_is_still_tappable_and_shows_a_padlock() -> None:
    taps: list[int] = []
    root = render(0, taps, [])
    locked = root.querySelector(".level-grid").children[1]
    assert locked.classList.contains("locked")
    assert locked.querySelector(".padlock") is not None
    locked.fire("click")
    assert taps == [1]
    unlocked = root.querySelector(".level-grid").children[0]
    assert unlocked.querySelector(".padlock") is None


def test_p01_r07_the_selected_level_is_highlighted() -> None:
    root = render(2, [], [])
    selected = root.querySelector(".level-grid").children[2]
    assert selected.classList.contains("selected")


def test_p01_r11_the_back_button_and_heading_and_hint_are_there() -> None:
    backs: list[bool] = []
    root = render(0, [], backs)
    assert root.querySelector(".menu-heading").textContent == "Pick a level"
    assert root.querySelector(".menu-hint").textContent == "Arrows"
    root.querySelector(".menu-back").fire("click")
    assert backs == [True]
    assert root.querySelector(".menu-status") is not None

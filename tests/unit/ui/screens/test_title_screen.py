"""Unit tests of `src/ui/screens/title_screen.py`."""

from helpers.dom import FakeDocument

from ui.menu_view import TitleView
from ui.screens.screen_handlers import ScreenHandlers
from ui.screens.title_screen import render_title_screen


def view(selected: int = 0) -> TitleView:
    return TitleView(
        "STRATOBLASTER",
        "HIGH SCORE",
        4200,
        "Start",
        "Settings",
        selected,
        "Arrows fly",
        "1.2",
        "ab12",
    )


def test_p01_r04_the_title_screen_shows_the_title_the_high_score_and_the_version() -> None:
    root = render_title_screen(FakeDocument(), view(), ScreenHandlers(lambda i: None, lambda: None))
    assert root.className == "menu-screen title-screen"
    assert root.querySelector(".title-name").textContent == "STRATOBLASTER"
    assert root.querySelector(".title-score-label").textContent == "HIGH SCORE"
    assert root.querySelector(".title-high-score").textContent == "4200"
    assert root.querySelector(".version-number").textContent == "v1.2"
    assert root.querySelector(".version-commit").textContent == "ab12"
    assert root.querySelector(".title-hint").textContent == "Arrows fly"


def test_p01_r04_start_and_settings_are_entries_that_report_their_index() -> None:
    taps: list[int] = []
    root = render_title_screen(FakeDocument(), view(1), ScreenHandlers(taps.append, lambda: None))
    start = root.querySelector(".title-start")
    settings = root.querySelector(".title-settings")
    assert start.textContent == "Start"
    assert settings.textContent == "Settings"
    assert settings.classList.contains("selected")
    assert not start.classList.contains("selected")
    start.fire("click")
    settings.fire("click")
    assert taps == [0, 1]


def test_d199_the_dev_entry_follows_settings_only_when_given() -> None:
    assert (
        render_title_screen(
            FakeDocument(), view(), ScreenHandlers(lambda i: None, lambda: None)
        ).querySelector(".title-dev")
        is None
    )
    taps: list[int] = []
    dev_view = TitleView(
        "STRATOBLASTER", "HIGH SCORE", 0, "Start", "Settings", 2, "hint", "1", "c", "Dev"
    )
    root = render_title_screen(FakeDocument(), dev_view, ScreenHandlers(taps.append, lambda: None))
    dev = root.querySelector(".title-dev")
    assert dev.textContent == "Dev"
    assert dev.classList.contains("selected")
    dev.fire("click")
    assert taps == [2]

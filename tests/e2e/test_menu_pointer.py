# Copyright (c) 2026 Renaud Guillon
"""e2e: the menus with the mouse or taps only.

UI-INPUT-09, UI-INPUT-10, UI-INPUT-12, UI-LEVEL-01, UI-PAUSE-01, UI-PAUSE-10.
"""

from collections.abc import Callable

import pytest
from e2e.menu_helpers import expect_state, open_game
from playwright.sync_api import Locator, Page, expect

TOUCH_PHONE = {"has_touch": True, "viewport": {"width": 390, "height": 844}}


def run_flow(page: Page, press: Callable[[Locator], None]) -> None:
    """Title → level select → game → pause → back to title with one kind of press.

    One press selects and confirms (UI-INPUT-09, D-287); the Back button goes back (UI-INPUT-10).
    """
    open_game(page)
    press(page.locator(".title-start"))
    expect_state(page, {"screen": "level-select", "selectedId": "1-1", "shipId": "balanced"})
    press(page.locator(".menu-back"))
    expect_state(page, {"screen": "title", "selectedId": "start"})
    press(page.locator(".title-start"))
    expect_state(page, {"screen": "level-select", "selectedId": "1-1"})
    press(page.locator(".level-cell").first)
    expect_state(page, {"screen": "game", "shipId": "balanced", "chosenLevelId": "1-1"})
    expect(page.locator(".game-level")).to_have_text("Level 1-1")
    # No Back button and no pause button over the playfield (UI-HUD-09, D-251): Escape pauses
    # (UI-PAUSE-01), then Main menu and Yes, leave, by pointer (UI-PAUSE-10).
    expect(page.locator(".menu-back")).to_have_count(0)
    expect(page.locator(".game-pause")).to_have_count(0)
    page.keyboard.press("Escape")
    expect_state(page, {"screen": "pause", "paused": True, "selectedId": "resume"})
    press(page.locator(".pause-entry").nth(2))
    expect_state(page, {"leaving": True, "choice": 0})
    press(page.locator(".pause-choice").nth(1))
    expect_state(page, {"screen": "title", "paused": False})


def test_ui_input_12_the_whole_flow_with_the_mouse_only(page: Page) -> None:
    run_flow(page, lambda target: target.click())


@pytest.mark.browser_context_args(**TOUCH_PHONE)
def test_ui_input_12_the_whole_flow_with_taps_only(page: Page) -> None:
    run_flow(page, lambda target: target.tap())


def test_ui_level_01_20_levels_all_unlocked(page: Page) -> None:
    """Also UI-LEVEL-03: no level is locked."""
    open_game(page)
    page.locator(".title-start").click()
    expect_state(page, {"screen": "level-select"})
    cells = page.locator(".level-cell")
    expect(cells).to_have_count(20)
    expect(cells.first).to_have_text("1-1")
    expect(cells.last).to_have_text("4-5")
    # Every level of Worlds 1 to 4 is built; the "locked" feedback is unit tested (menu overlay,
    # menu controller), as no level of this game is locked any more.
    expect(page.locator(".level-cell.locked")).to_have_count(0)
    # One click on a level plays it (UI-INPUT-09, D-287).
    cells.nth(16).click()
    expect_state(page, {"screen": "game", "chosenLevelId": "4-2"})

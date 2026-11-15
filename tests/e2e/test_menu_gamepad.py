# Copyright (c) 2026 Renaud Guillon
"""e2e: the menus with a gamepad only (UI-INPUT-07, UI-INPUT-12, UI-PAUSE-01)."""

from typing import Any

import pytest
from e2e.menu_helpers import expect_state, game_state, open_game, step
from playwright.sync_api import Page

A = 0
B = 1
SELECT = 8
START = 9
DPAD_DOWN = 13
DPAD_RIGHT = 15


@pytest.fixture(autouse=True)
def fake_gamepad(page: Page) -> None:
    """Replace the Gamepad API with one fake standard gamepad the test controls."""
    page.add_init_script(
        """(() => {
            // Babylon's gamepad manager reads the same API, so the fake has the standard fields.
            const pad = {
                id: 'Fake gamepad (STANDARD GAMEPAD)',
                index: 0,
                connected: true,
                mapping: 'standard',
                timestamp: 0,
                buttons: Array.from({ length: 17 }, () => ({
                    pressed: false, touched: false, value: 0,
                })),
                axes: [0, 0, 0, 0],
            };
            window.__pad = pad;
            navigator.getGamepads = () => [pad];
        })();"""
    )


def set_pad(page: Page, change: dict[str, Any]) -> None:
    page.evaluate(
        """(c) => {
            const pad = window.__pad;
            if (c.button) {
                const button = pad.buttons[c.button[0]];
                if (button) button.pressed = c.button[1];
            }
            if (c.axes) pad.axes = c.axes;
        }""",
        change,
    )


def press_button(page: Page, index: int, expected: dict[str, Any]) -> None:
    """Hold a button until the game reaches `expected`, then release it."""
    set_pad(page, {"button": [index, True]})
    expect_state(page, expected)
    set_pad(page, {"button": [index, False]})
    step(page)


def tilt_stick(page: Page, x: float, y: float, expected: dict[str, Any] | None = None) -> None:
    """Tilts the left stick until the game reaches `expected` (or for 5 frames), then centres it."""
    set_pad(page, {"axes": [x, y, 0, 0]})
    if expected:
        expect_state(page, expected)
    else:
        step(page, 5)
    set_pad(page, {"axes": [0, 0, 0, 0]})
    step(page)


def test_ui_input_12_the_whole_flow_with_the_gamepad_only(page: Page) -> None:
    """Also UI-INPUT-07 (the buttons) and UI-INPUT-08 (the stick's dead zone)."""
    open_game(page)
    press_button(page, A, {"screen": "level-select", "selectedId": "1-1"})
    tilt_stick(page, 0.2, 0)  # inside the dead zone
    assert game_state(page)["selectedId"] == "1-1"
    tilt_stick(page, 0.9, 0, {"selectedId": "1-2"})
    press_button(page, DPAD_RIGHT, {"selectedId": "1-3"})
    press_button(page, B, {"screen": "title", "selectedId": "start"})
    press_button(page, A, {"screen": "level-select", "selectedId": "1-1"})
    press_button(page, A, {"screen": "game", "chosenLevelId": "1-1"})
    # UI-PAUSE-05: B does nothing in a level; UI-PAUSE-01: Start and Select pause; B resumes
    # (UI-PAUSE-08); the level is left from the pause menu (UI-PAUSE-10).
    set_pad(page, {"button": [B, True]})
    step(page, 3)
    set_pad(page, {"button": [B, False]})
    step(page)
    assert game_state(page)["screen"] == "game"
    press_button(page, START, {"screen": "pause", "paused": True})
    press_button(page, B, {"screen": "game", "paused": False})
    press_button(page, SELECT, {"screen": "pause", "selectedId": "resume"})
    press_button(page, DPAD_DOWN, {"selectedId": "settings"})
    press_button(page, DPAD_DOWN, {"selectedId": "main-menu"})
    press_button(page, A, {"leaving": True, "choice": 0})
    press_button(page, DPAD_RIGHT, {"choice": 1})
    press_button(page, A, {"screen": "title"})

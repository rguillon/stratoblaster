# Copyright (c) 2026 Renaud Guillon
"""e2e: level loading in steps.

The perf overlay (specs/performance.md, specs/dev/perf-tools.md).
"""

import pytest
from e2e.menu_helpers import (
    expect_state,
    game_state,
    open_game,
    send_action,
    step,
    wait_for_level_time,
    wait_for_load,
)
from playwright.sync_api import Page, expect

# Tunable values of specs/performance.md: level_load_max_s, scaled by e2e_slowdown (software
# WebGL, PERF-01).
LEVEL_LOAD_MAX_S = 4
E2E_SLOWDOWN = 10


@pytest.mark.parametrize("world", [1, 2, 3, 4])
def test_dev_perf_07_a_world_s_first_level_loads_in_steps_its_loading_time_in_budget(
    page: Page, world: int
) -> None:
    """Also PERF-08 (the load time), PERF-09 (in steps), UI-LOAD-06 (behind its loading screen).

    DEV-API-06 (the perf numbers).
    """
    level_id = f"{world}-1"
    open_game(page)
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select"})
    for _ in range(1, world):
        send_action(page, "down")
    expect_state(page, {"selectedId": level_id})
    send_action(page, "confirm")
    # PERF-04, PERF-05: the press shows the game screen at once; the level loads behind its
    # loading screen, then plays.
    expect_state(page, {"screen": "game", "chosenLevelId": level_id})
    wait_for_load(page)
    wait_for_level_time(page, 0.2)
    state = game_state(page)
    perf = state["perf"]
    assert state["game"]["levelId"] == level_id
    assert perf["lastLoad"] is not None
    assert perf["lastLoad"] < LEVEL_LOAD_MAX_S * 1000 * E2E_SLOWDOWN
    assert perf["longestLoadStep"] is not None


def test_dev_perf_03_f3_shows_the_perf_overlay(page: Page) -> None:
    """Also ENG-111 (hidden unless asked for) and ENG-101 (the long frames it counts)."""
    open_game(page)
    overlay = page.locator(".perf-overlay")
    expect(overlay).to_be_hidden()
    page.keyboard.press("F3")
    step(page, 30)
    expect(overlay).to_be_visible()
    expect(overlay).to_contain_text("Long frames:")
    expect(overlay).to_contain_text("Longest frame:")
    expect(overlay).to_contain_text("Level load:")
    page.keyboard.press("F3")
    expect(overlay).to_be_hidden()

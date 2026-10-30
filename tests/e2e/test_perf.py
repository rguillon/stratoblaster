"""e2e: level loading in steps and the perf overlay (phase 13)."""

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

# Tunable values of phase 13: level_load_max_s, scaled by e2e_slowdown (software WebGL).
LEVEL_LOAD_MAX_S = 2
E2E_SLOWDOWN = 10


@pytest.mark.parametrize("world", [1, 2, 3, 4])
def test_p13_r03_a_world_s_first_level_loads_in_steps_its_loading_time_in_budget(
    page: Page, world: int
) -> None:
    level_id = f"{world}-1"
    open_game(page)
    send_action(page, "confirm")
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select"})
    for _ in range(1, world):
        send_action(page, "down")
    expect_state(page, {"selectedId": level_id})
    send_action(page, "confirm")
    # P13-R02: the press shows the game screen at once; the level loads behind its loading
    # screen, then plays.
    expect_state(page, {"screen": "game", "chosenLevelId": level_id})
    wait_for_load(page)
    wait_for_level_time(page, 0.2)
    state = game_state(page)
    perf = state["perf"]
    assert state["game"]["levelId"] == level_id
    assert perf["lastLoad"] is not None
    assert perf["lastLoad"] < LEVEL_LOAD_MAX_S * 1000 * E2E_SLOWDOWN
    assert perf["longestLoadStep"] is not None


def test_p13_r01_f3_shows_the_perf_overlay(page: Page) -> None:
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

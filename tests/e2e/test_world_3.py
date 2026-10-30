"""e2e: World 3, its weather and its final bosses (phase 9, and the way into World 4)."""

import re

import pytest
from e2e.menu_helpers import (
    destroy_boss,
    expect_state,
    game_state,
    matches,
    open_debug,
    open_game,
    send_action,
    wait_for_level_time,
)
from playwright.sync_api import Page, expect

WORLD_3 = ["3-1", "3-2", "3-3", "3-4", "3-5"]


def test_p09_r01_the_world_3_row_shows_3_1_to_3_5_all_unlocked(page: Page) -> None:
    open_game(page)
    send_action(page, "confirm")
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select"})
    cells = page.locator(".level-cell")
    for i, level_id in enumerate(WORLD_3):
        expect(cells.nth(10 + i)).to_have_text(level_id)
        expect(cells.nth(10 + i)).not_to_have_class(re.compile("locked"))


@pytest.mark.parametrize(("index", "level_id"), list(enumerate(WORLD_3)))
def test_p09_r01_a_level_can_be_confirmed_from_the_menu_and_plays(
    page: Page, index: int, level_id: str
) -> None:
    open_game(page)
    send_action(page, "confirm")
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select", "selectedId": "1-1"})
    # Down two rows to World 3, then along it.
    send_action(page, "down")
    send_action(page, "down")
    for _ in range(index):
        send_action(page, "right")
    expect_state(page, {"selectedId": level_id})
    send_action(page, "confirm")
    expect_state(page, {"screen": "game", "chosenLevelId": level_id})
    wait_for_level_time(page, 0.2)
    played = game_state(page)["game"]
    assert matches(played, {"levelId": level_id, "phase": "playing", "timeScale": 1})
    assert 290 <= played["duration"] <= 310
    expect(page.locator(".game-level")).to_have_text(f"Level {level_id}")


def test_p09_r11_level_3_3_t_120_starts_at_2_00_in_its_thunderstorm(page: Page) -> None:
    open_debug(page, "?level=3-3&t=120")
    wait_for_level_time(page, 120.1)
    played = game_state(page)["game"]
    assert played["levelId"] == "3-3"
    assert 120 <= played["time"] < 126
    # P09-R04: rain 0.8 (1 600 of the 2 000 streaks) with lightning.
    assert matches(played["sky"], {"weather": "rain", "weatherParticles": 1600, "lightning": 1})


def test_p09_r11_weather_0_shows_no_rain_and_no_lightning(page: Page) -> None:
    open_debug(page, "?level=3-3&t=120&weather=0")
    wait_for_level_time(page, 120.1)
    sky = game_state(page)["game"]["sky"]
    expected = {"weather": "none", "weatherParticles": 0, "rainRings": 0, "lightning": 0}
    assert matches(sky, {**expected, "flash": 0})


def test_p09_r04_3_5_rains_at_night_over_the_lit_villages(page: Page) -> None:
    open_debug(page, "?level=3-5&t=60")
    wait_for_level_time(page, 60.1)
    sky = game_state(page)["game"]["sky"]
    assert matches(sky, {"weather": "rain", "weatherParticles": 1000})
    assert sky["groundLights"] > 1


def test_p09_r09_k_destroys_the_river_leviathan_and_the_level_is_complete(page: Page) -> None:
    open_debug(page, "?level=3-1&boss=final")
    destroy_boss(page, "River Leviathan")
    expect(page.locator(".level-complete-level")).to_have_text("3-1")
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select", "selectedId": "3-2", "game": None})


def test_p09_r01_after_2_5_the_level_select_highlights_3_1(page: Page) -> None:
    open_debug(page, "?level=2-5&boss=final")
    destroy_boss(page, "Boreal Citadel")
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select", "selectedId": "3-1", "game": None})


def test_p10_r01_after_3_5_the_level_select_highlights_4_1(page: Page) -> None:
    open_debug(page, "?level=3-5&boss=final")
    destroy_boss(page, "Verdant Crown")
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select", "selectedId": "4-1", "game": None})

"""e2e: World 4, its ash and embers and its final bosses (phase 10)."""

import re

import pytest
from e2e.menu_helpers import (
    boss_name,
    destroy_boss,
    expect_state,
    game_state,
    matches,
    open_debug,
    open_game,
    send_action,
    step_until,
    wait_for_level_time,
)
from playwright.sync_api import Page, expect

WORLD_4 = ["4-1", "4-2", "4-3", "4-4", "4-5"]


def test_p10_r01_the_world_4_row_shows_4_1_to_4_5_all_unlocked_the_last_row(page: Page) -> None:
    open_game(page)
    send_action(page, "confirm")
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select"})
    cells = page.locator(".level-cell")
    for i, level_id in enumerate(WORLD_4):
        expect(cells.nth(15 + i)).to_have_text(level_id)
        expect(cells.nth(15 + i)).not_to_have_class(re.compile("locked"))
    expect(cells).to_have_count(20)
    expect(page.locator(".level-cell.locked")).to_have_count(0)


@pytest.mark.parametrize(("index", "level_id"), list(enumerate(WORLD_4)))
def test_p10_r01_a_level_can_be_confirmed_from_the_menu_and_plays(
    page: Page, index: int, level_id: str
) -> None:
    open_game(page)
    send_action(page, "confirm")
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select", "selectedId": "1-1"})
    # Down three rows to World 4, then along it.
    for _ in range(3):
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
    # P10-R07: the shots are drawn in the contrast style in every World 4 level.
    assert played["sky"]["shotStyle"] == "contrast"
    expect(page.locator(".game-level")).to_have_text(f"Level {level_id}")


def test_p10_r04_4_2_falls_ash_at_midday_weather_0_shows_none(page: Page) -> None:
    open_debug(page, "?level=4-2&t=60")
    wait_for_level_time(page, 60.1)
    # Falling ash 0.5: 750 of the 1 500 flakes.
    sky = game_state(page)["game"]["sky"]
    assert matches(sky, {"weather": "ash", "weatherParticles": 750, "lava": False})
    open_debug(page, "?level=4-2&t=60&weather=0")
    wait_for_level_time(page, 60.1)
    sky = game_state(page)["game"]["sky"]
    assert matches(sky, {"weather": "none", "secondWeather": "none", "weatherParticles": 0})


def test_p10_r04_4_4_a_night_over_the_lit_towers_with_ash_and_embers(page: Page) -> None:
    open_debug(page, "?level=4-4&t=60")
    wait_for_level_time(page, 60.1)
    sky = game_state(page)["game"]["sky"]
    # Ash 0.3 (450) and embers 0.3 (240). No lava since the rework (reviewer, 2026-10-27): the
    # river is water.
    expected = {"weather": "ash", "secondWeather": "embers", "weatherParticles": 690}
    assert matches(sky, {**expected, "lava": False})
    assert sky["groundLights"] > 1


def test_p10_r13_boss_final_starts_4_5_at_the_caldera_throne_in_the_eruption(page: Page) -> None:
    open_debug(page, "?level=4-5&boss=final")
    step_until(page, lambda: boss_name(page), lambda n: n == "Caldera Throne")
    sky = game_state(page)["game"]["sky"]
    # Over downtown (no lava since the rework, 2026-10-27); the embers at their strongest.
    assert matches(sky, {"lava": False, "weather": "embers", "weatherParticles": 800})
    assert sky["groundLights"] > 1


def test_p10_r11_k_destroys_the_steam_dreadnought_and_the_level_is_complete(page: Page) -> None:
    open_debug(page, "?level=4-1&boss=final")
    destroy_boss(page, "Steam Dreadnought")
    expect(page.locator(".level-complete-level")).to_have_text("4-1")
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select", "selectedId": "4-2", "game": None})


def test_p10_r01_after_4_5_the_level_select_highlights_4_5(page: Page) -> None:
    open_debug(page, "?level=4-5&boss=final")
    destroy_boss(page, "Caldera Throne")
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select", "selectedId": "4-5", "game": None})

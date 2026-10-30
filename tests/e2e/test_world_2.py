"""e2e: World 2, its times of day and its final boss (phase 8)."""

import re
from typing import Any

import pytest
from e2e.menu_helpers import (
    boss,
    destroy_boss,
    expect_state,
    game,
    game_state,
    matches,
    open_debug,
    open_game,
    send_action,
    step_until,
    wait_for_level_time,
)
from playwright.sync_api import Page, expect

WORLD_2 = ["2-1", "2-2", "2-3", "2-4", "2-5"]


def sky_at(page: Page, query: str, time: float) -> dict[str, Any]:
    """The sky of the level opened with `query`, once its clock is past `time`."""
    open_debug(page, query)
    wait_for_level_time(page, time)
    sky: dict[str, Any] = game_state(page)["game"]["sky"]
    return sky


def test_p08_r01_the_world_2_row_shows_2_1_to_2_5_all_unlocked(page: Page) -> None:
    open_game(page)
    send_action(page, "confirm")
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select"})
    cells = page.locator(".level-cell")
    for i, level_id in enumerate(WORLD_2):
        expect(cells.nth(5 + i)).to_have_text(level_id)
        expect(cells.nth(5 + i)).not_to_have_class(re.compile("locked"))


@pytest.mark.parametrize(("index", "level_id"), list(enumerate(WORLD_2)))
def test_p08_r01_a_level_can_be_confirmed_from_a_fresh_start_and_plays(
    page: Page, index: int, level_id: str
) -> None:
    open_game(page)
    send_action(page, "confirm")
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select", "selectedId": "1-1"})
    # Down a row to World 2, then along it.
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


def test_p08_r12_level_2_4_t_150_starts_2_4_at_2_30(page: Page) -> None:
    open_debug(page, "?level=2-4&t=150")
    # At 2:30, the middle of the level, its mini boss comes (and holds the level's progress).
    step_until(page, lambda: (game(page) or {}).get("time", 0), lambda t: t >= 150)
    played = game_state(page)["game"]
    assert played["levelId"] == "2-4"
    assert 150 <= played["time"] < 156


def test_p08_r06_no_weather_or_aurora_in_world_2(page: Page) -> None:
    for query, time in [("?level=2-1", 0.2), ("?level=2-5&t=120", 120.1)]:
        assert matches(sky_at(page, query, time), {"weatherParticles": 0, "aurora": 0}), query


def test_p08_r06_the_lights_come_on_at_dusk_and_night(page: Page) -> None:
    morning = sky_at(page, "?level=2-1", 0.2)
    dusk = sky_at(page, "?level=2-4&t=60", 60.1)
    night = sky_at(page, "?level=2-5&t=120", 120.1)
    assert morning["groundLights"] < 0.5
    assert dusk["groundLights"] > morning["groundLights"]
    assert night["groundLights"] > 1
    assert night["sunIntensity"] < morning["sunIntensity"]


def test_p08_r12_look_forces_a_time_of_day(page: Page) -> None:
    night = sky_at(page, "?level=2-5&t=120", 120.1)
    midday = sky_at(page, "?level=2-5&t=120&look=midday", 120.1)
    assert midday["groundLights"] < 0.5
    assert midday["sunIntensity"] > night["sunIntensity"]


def test_p08_r10_k_destroys_the_narwhal_and_the_level_is_complete(page: Page) -> None:
    open_debug(page, "?level=2-1&boss=final")
    step_until(page, lambda: (boss(page) or {}).get("parts", 0), lambda parts: parts >= 4)
    destroy_boss(page, "Narwhal")
    expect(page.locator(".level-complete-level")).to_have_text("2-1")
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select", "selectedId": "2-2", "game": None})


def test_p08_r01_after_1_5_the_level_select_highlights_2_1(page: Page) -> None:
    open_debug(page, "?level=1-5&boss=final")
    destroy_boss(page, "Overlord")
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select", "selectedId": "2-1", "game": None})

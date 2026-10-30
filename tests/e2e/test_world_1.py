"""e2e: World 1, its levels, the debug options and the end of a level (phases 6 and 7)."""

import re

import pytest
from e2e.menu_helpers import (
    advance,
    boss_name,
    destroy_boss,
    expect_state,
    game_state,
    leave_level,
    level,
    open_debug,
    open_game,
    send_action,
    step,
    step_until,
    wait_for_level_time,
)
from playwright.sync_api import Page, expect

WORLD_1 = ["1-1", "1-2", "1-3", "1-4", "1-5"]


def play_level(page: Page, index: int, ship: int = 0) -> None:
    """Through the menus to level `index` of World 1, with the ship at `ship` (0 = balanced)."""
    level_id = WORLD_1[index]
    open_game(page)
    send_action(page, "confirm")
    for _ in range(ship):
        send_action(page, "right")
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select", "selectedId": "1-1"})
    for _ in range(index):
        send_action(page, "right")
    expect_state(page, {"selectedId": level_id})
    send_action(page, "confirm")
    expect_state(page, {"screen": "game", "chosenLevelId": level_id})
    wait_for_level_time(page, 0.2)


def test_p06_r01_the_world_1_row_shows_1_1_to_1_5_all_unlocked(page: Page) -> None:
    open_game(page)
    send_action(page, "confirm")
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select"})
    cells = page.locator(".level-cell")
    for i, level_id in enumerate(WORLD_1):
        expect(cells.nth(i)).to_have_text(level_id)
        expect(cells.nth(i)).not_to_have_class(re.compile("locked"))


@pytest.mark.parametrize(("index", "level_id"), list(enumerate(WORLD_1)))
def test_p06_r01_p06_r02_a_level_can_be_confirmed_from_a_fresh_start_and_plays(
    page: Page, index: int, level_id: str
) -> None:
    play_level(page, index)
    played = game_state(page)["game"]
    assert played["levelId"] == level_id
    assert played["phase"] == "playing"
    assert played["timeScale"] == 1
    assert 230 <= played["duration"] <= 250
    expect(page.locator(".game-level")).to_have_text(f"Level {level_id}")
    # Phase 6 review: a HUD with the ship's health and the weapon level; no kills since the
    # reviewer's rework (2026-10-28).
    expect(page.locator(".hud-health-text")).to_have_text("HP 100 / 100")
    expect(page.locator(".hud-weapon")).to_have_text("Bullet · Lv 1/5")
    expect(page.locator(".hud-destroyed")).to_have_count(0)
    expect(page.locator(".menu-back")).to_have_count(0)
    leave_level(page)
    expect_state(page, {"screen": "title", "game": None})


def test_p06_r02_the_heavy_ship_flies_over_1_1_shoots_and_stays_on_screen(page: Page) -> None:
    play_level(page, 0, 1)
    assert game_state(page)["chosenShipId"] == "heavy"
    # The ship rises into the level first (reviewer, 2026-10-28).
    advance(page, 2)
    start = level(page)["player"]
    page.keyboard.down("ArrowUp")
    page.keyboard.down("Space")
    advance(page, 0.5)
    flying = level(page)
    assert flying["player"]["y"] > start["y"] + 20
    assert flying["shots"] > 0
    assert flying["firing"] is True
    # Phase 6 review: E (by position) switches to the next weapon.
    page.keyboard.press("KeyE")
    step(page)
    expect(page.locator(".hud-weapon")).to_have_text("Laser · Lv 1/5")
    page.keyboard.press("KeyE")
    step(page)
    expect(page.locator(".hud-weapon")).to_have_text("Missile · Lv 1/5")
    page.keyboard.up("Space")
    page.keyboard.up("ArrowUp")
    # Pushed against the left edge for a while, it stops there, inside the playfield.
    page.keyboard.down("ArrowLeft")
    advance(page, 4)
    first = level(page)
    advance(page, 0.5)
    second = level(page)
    page.keyboard.up("ArrowLeft")
    assert second["player"]["x"] == first["player"]["x"]
    assert second["player"]["x"] > 0
    assert second["player"]["x"] < 240 - 100


def test_p06_r09_without_debug_options_f_and_the_arrows_do_not_change_the_time(
    page: Page,
) -> None:
    play_level(page, 0)
    page.keyboard.press("KeyF")
    page.keyboard.press("ArrowRight")
    page.keyboard.press("ArrowRight")
    step(page)
    played = game_state(page)["game"]
    assert played["timeScale"] == 1
    assert played["time"] < 1
    expect(page.locator(".stats-tile")).to_have_count(0)


def test_p06_r09_level_1_3_t_120_starts_at_2_00_the_waves_before_it_skipped(page: Page) -> None:
    open_debug(page, "?level=1-3&t=120")
    state = game_state(page)
    played = state["game"]
    assert state["screen"] == "game"
    assert state["chosenShipId"] == "balanced"
    assert played["levelId"] == "1-3"
    assert 120 <= played["time"] < 121
    # The first wave after 2:00 comes at 2:10: nothing before it came in. At 2:00, the middle of
    # the level, its mini boss arrives (P07-R06), and only it.
    assert played["boss"]["name"] == "Dust Devil"
    assert played["spawned"] == 1
    # The debug tile: one simulated second of frames, then the polygons of the frame drawn.
    step(page, 60)
    expect(page.locator(".stats-fps")).to_have_text(re.compile(r"^FPS: [1-9]\d*$"))
    expect(page.locator(".stats-polygons")).to_have_text(re.compile(r"^Polygons: [1-9][\d,]*$"))
    page.keyboard.press("KeyF")
    assert level(page)["timeScale"] == 4
    before = level(page)["time"]
    page.keyboard.press("ArrowRight")
    assert level(page)["time"] >= before + 10


def test_p06_r03_p07_r06_p07_r09_1_1_ends_once_its_final_boss_is_destroyed(page: Page) -> None:
    open_debug(page, "?level=1-1&boss=final&ship=light")
    assert game_state(page)["chosenShipId"] == "light"
    step_until(page, lambda: boss_name(page), lambda n: n == "Storm Petrel")
    # P07-R02: its health bar shows.
    expect(page.locator(".boss-bar")).to_be_visible()
    expect(page.locator(".boss-name")).to_have_text("Storm Petrel")
    assert level(page)["phase"] == "playing"
    # K destroys its four parts one by one (the stage goes up), then its core.
    destroy_boss(page, "Storm Petrel")
    expect(page.locator(".level-complete-heading")).to_have_text("Level complete!")
    expect(page.locator(".level-complete-level")).to_have_text("1-1")
    expect(page.locator(".level-complete-enemies")).to_have_text(
        re.compile(r"^Enemies destroyed: \d+ / \d+$")
    )
    state = game_state(page)
    assert state["levelResult"]["levelId"] == "1-1"
    assert state["game"]["phase"] == "complete"
    assert state["game"]["bossesDefeated"] == 1
    # Confirm goes to 1-2.
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select", "selectedId": "1-2", "game": None})

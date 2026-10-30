"""e2e: the score, the high score, the lives and the bombs (phase 11)."""

import re

import pytest
from e2e.menu_helpers import (
    advance,
    boss_name,
    boss_stage,
    destroy_boss,
    expect_state,
    game,
    game_state,
    leave_level,
    matches,
    open_debug,
    open_game,
    overlap,
    send_action,
    step,
    step_until,
)
from playwright.sync_api import Page, expect

TOUCH_PHONE = {"has_touch": True, "viewport": {"width": 390, "height": 844}}


def wait_for_boss(page: Page, name: str) -> None:
    """Steps the level until the boss `name` is fought."""
    step_until(page, lambda: boss_name(page), lambda n: n == name)


def test_p11_r01_r02_r03_r08_boss_parts_score_a_new_high_score_is_saved_and_shown(
    page: Page,
) -> None:
    open_debug(page, "?level=1-1&boss=final&ship=light")
    wait_for_boss(page, "Storm Petrel")
    expect(page.locator(".hud-score-value")).to_have_text("0000000")
    expect(page.locator(".hud-high-score")).to_have_text("HI 0000000")
    assert game_state(page)["highScore"] == 0
    # K destroys its four parts (800 points each, 10 % of its 8 000), then its core.
    for stage in range(1, 5):
        page.keyboard.press("KeyK")
        step_until(page, lambda: boss_stage(page), lambda s, at=stage: s == at)
    assert (game(page) or {}).get("score", 0) >= 3200
    expect(page.locator(".hud-score-value")).to_have_text(re.compile(r"^00\d{5}$"))
    destroy_boss(page, "Storm Petrel")
    state = game_state(page)
    result = state["levelResult"]
    score = result["score"]
    assert score >= 3200 + 8000
    assert result["newHighScore"] is True
    assert state["highScore"] == score
    expect(page.locator(".level-complete-score")).to_have_text(f"Score: {score}")
    expect(page.locator(".level-complete-high-score")).to_have_text("New high score!")
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select"})
    send_action(page, "back")
    send_action(page, "back")
    expect_state(page, {"screen": "title"})
    expect(page.locator(".title-high-score")).to_have_text(str(score))
    page.reload()
    open_game(page)
    expect(page.locator(".title-high-score")).to_have_text(str(score))


def test_p11_r03_p12_r02_leaving_a_level_from_the_pause_menu_saves_its_score(page: Page) -> None:
    open_debug(page, "?level=1-1&boss=final")
    wait_for_boss(page, "Storm Petrel")
    page.keyboard.press("KeyK")
    step_until(page, lambda: (game(page) or {}).get("score", 0), lambda s: s == 800)
    leave_level(page)
    expect(page.locator(".title-high-score")).to_have_text("800")
    page.reload()
    open_game(page)
    expect(page.locator(".title-high-score")).to_have_text("800")


def test_p11_r05_r06_r08_r_sets_a_bomb_off_the_enemy_shots_go_the_boss_is_hurt(
    page: Page,
) -> None:
    open_debug(page, "?level=1-2&boss=mini")
    step_until(page, lambda: boss_name(page), lambda n: n is not None)
    expect(page.locator(".hud-bombs")).to_have_text("● 3")
    # Let the mini boss come in and fire.
    step_until(page, lambda: (game(page) or {}).get("enemyShots", 0), lambda n: n > 0, frames=30)
    before = (game(page) or {})["boss"]["health"]
    page.keyboard.press("KeyR")
    step(page)
    bombed = game(page) or {}
    assert matches(bombed, {"bombs": 2, "enemyShots": 0})
    assert bombed["boss"]["health"] < before
    expect(page.locator(".hud-bombs")).to_have_text("● 2")
    # E switches the weapon and sets no bomb off.
    advance(page, 1.1)
    page.keyboard.press("KeyE")
    step(page)
    expect(page.locator(".hud-weapon")).to_have_text("Laser · Lv 1/5")
    assert (game(page) or {})["bombs"] == 2
    # Then `bomb` from the test API.
    send_action(page, "bomb")
    step(page)
    assert (game(page) or {})["bombs"] == 1


def test_p11_r04_a_continue_after_the_mini_boss_keeps_the_score_up_to_the_checkpoint(
    page: Page,
) -> None:
    open_debug(page, "?level=1-1&boss=mini&ship=light")
    wait_for_boss(page, "Reef Warden")

    def press_k_and_count() -> int:
        page.keyboard.press("KeyK")
        defeated: int = (game(page) or {}).get("bossesDefeated", 0)
        return defeated

    step_until(page, press_k_and_count, lambda n: n == 1)
    # The ship sits still until the enemies have taken all its lives.
    step_until(
        page,
        lambda: (game_state(page)["levelResult"] or {}).get("outcome"),
        lambda outcome: outcome == "over",
        frames=20 * 60,
    )
    result = game_state(page)["levelResult"]
    saved = (result.get("checkpoint") or {}).get("score", -1)
    assert saved >= 3000
    expect(page.locator(".level-complete-choice").first).to_have_text("Continue")
    send_action(page, "confirm")
    step_until(page, lambda: game_state(page)["levelResult"], lambda r: r is None)
    step_until(page, lambda: (game(page) or {}).get("score", -1), lambda s: s == saved)
    assert (game(page) or {})["bombs"] == 3


@pytest.mark.parametrize(("width", "height"), [(800, 600), (390, 844)])
def test_p11_r02_the_score_lines_show_and_cover_no_other_hud_part(
    page: Page, width: int, height: int
) -> None:
    page.set_viewport_size({"width": width, "height": height})
    open_debug(page, "?level=1-1&boss=final")
    wait_for_boss(page, "Storm Petrel")
    score = page.locator(".hud-score")
    expect(score).to_be_visible()
    expect(page.locator(".boss-bar")).to_be_visible()
    for other in [".hud-health", ".hud-weapon", ".hud-progress", ".boss-bar"]:
        assert not overlap(score, page.locator(other)), other
    box = score.bounding_box()
    assert box
    assert box["y"] >= 0
    assert box["x"] + box["width"] <= width


@pytest.mark.browser_context_args(**TOUCH_PHONE)
def test_p11_r06_the_bomb_button_sets_a_bomb_off_the_fire_button_still_shows(
    page: Page,
) -> None:
    open_debug(page, "?level=1-1&t=10")
    button = page.locator(".hud-bomb-button")
    expect(button).to_be_visible()
    expect(button).to_have_text("Bomb 3")
    button.tap()
    step(page)
    assert (game(page) or {})["bombs"] == 2
    expect(button).to_have_text("Bomb 2")
    expect(page.locator(".game-fire")).to_be_visible()

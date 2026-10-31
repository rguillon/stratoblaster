"""e2e: the ship, the enemies and the shots stand out from the background (phase 14)."""

import json
from typing import Any

import pytest
from e2e.menu_helpers import game, open_debug, step
from playwright.sync_api import Page

from game.config.readability import READABILITY


def readability(page: Page) -> dict[str, Any] | None:
    """What `__GAME_TEST__.readability()` returns (`app/readability_probe.py`)."""
    report: dict[str, Any] | None = page.evaluate(
        "(share) => window.__GAME_TEST__.readability(share)",
        READABILITY.backgroundBrightPixelBudget,
    )
    return report


def full_frame(page: Page) -> dict[str, Any]:
    """Steps the level until the ship, an enemy, an enemy bullet and a player shot are all on
    screen. The frames are not drawn (`readability` draws the frames it measures), and the probe,
    three drawn frames and two read back, runs only once the state has enemies, enemy shots and
    player shots: under software WebGL, a probe on every check made the test last minutes."""
    last: dict[str, Any] | None = None
    for _ in range(120):
        step(page, 5, False)
        played = game(page) or {}
        if not (played.get("enemies") and played.get("enemyShots") and played.get("shots")):
            continue
        last = readability(page)
        if not last:
            continue
        if all(last[key] is not None for key in ["enemy", "enemyBullet", "playerShot"]):
            return last
    raise AssertionError(f"No full frame: {json.dumps(last)}")


# One level of each world, at a time it is busy with enemies shooting.
LEVELS = [("1-2", 40), ("2-1", 40), ("3-1", 40), ("4-1", 90)]


@pytest.mark.parametrize(("level_id", "time"), LEVELS)
def test_p14_r08_the_ship_enemies_and_shots_stand_out_from_the_background(
    page: Page, level_id: str, time: int
) -> None:
    open_debug(page, f"?level={level_id}&t={time}")
    page.keyboard.down("Space")
    report = full_frame(page)
    page.keyboard.up("Space")
    print(f"readability {level_id}: {json.dumps(report)}")
    # P14-R01: the background is dimmed, but for a few small lights.
    assert report["backgroundLuminance"] <= READABILITY.backgroundMaxLuminance
    # P14-R03, R04: the ship and the enemies stand out.
    assert report["player"] >= READABILITY.minObjectContrast
    assert report["enemy"] >= READABILITY.minObjectContrast
    # P14-R05: the enemy bullets most of all; P14-R06: the player shots, toned down, still show.
    assert report["enemyBullet"] >= READABILITY.minBulletContrast
    assert report["playerShot"] >= READABILITY.minPlayerShotContrast

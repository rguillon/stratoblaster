# Copyright (c) 2026 Renaud Guillon
"""e2e: the ship, the enemies.

The shots stand out from the background (GFX-READ-01, measured by the readability probe,
DEV-API-09).
"""

import json
from typing import Any

import pytest
from e2e.menu_helpers import game, open_debug, step
from playwright.sync_api import Page

from game.config.readability import READABILITY


def readability(page: Page) -> dict[str, Any] | None:
    """Return what `__GAME_TEST__.readability()` returns (`app/readability_probe.py`)."""
    report: dict[str, Any] | None = page.evaluate(
        "(share) => window.__GAME_TEST__.readability(share)",
        READABILITY.backgroundBrightPixelBudget,
    )
    return report


def full_frame(page: Page) -> dict[str, Any]:
    """Step the level until the ship, an enemy, an enemy bullet and a player shot are on screen.

    The frames are not drawn (`readability` draws the frames it measures), and the probe, three
    drawn frames and two read back, runs only once the state has enemies, enemy shots and player
    shots: under software WebGL, a probe on every check made the test last minutes (DEV-API-11). The
    game only moves when stepped (ENG-58).
    """
    last: dict[str, Any] | None = None
    for _ in range(120):
        step(page, 5, render=False)
        played = game(page) or {}
        if not (played.get("enemies") and played.get("enemyShots") and played.get("shots")):
            continue
        last = readability(page)
        if not last:
            continue
        if all(last[key] is not None for key in ["enemy", "enemyBullet", "playerShot"]):
            return last
    msg = f"No full frame: {json.dumps(last)}"
    raise AssertionError(msg)


# One level of each world, at a time it is busy with enemies shooting. 4-1 at 60 s (D-249: at
# 90 s and 120 s the first shot probed flies over a lit tile of the garden town and reads at
# 1.3 to 1.9, under the floor of 2; at 60 s it reads at 4.8).
LEVELS = [("1-2", 40), ("2-1", 40), ("3-1", 40), ("4-1", 60)]


@pytest.mark.parametrize(("level_id", "time"), LEVELS)
def test_dev_api_09_the_ship_enemies_and_shots_stand_out_from_the_background(
    page: Page, level_id: str, time: int
) -> None:
    open_debug(page, f"?level={level_id}&t={time}")
    page.keyboard.down("Space")
    report = full_frame(page)
    page.keyboard.up("Space")
    # GFX-READ-01: the background is dimmed, but for a few small lights; GFX-READ-03: the
    # gameplay objects are not.
    assert report["backgroundLuminance"] <= READABILITY.backgroundMaxLuminance
    # GFX-READ-07, GFX-READ-09: the ship and the enemies stand out (the enemy trim, ENM-47).
    assert report["player"] >= READABILITY.minObjectContrast
    assert report["enemy"] >= READABILITY.minObjectContrast
    # GFX-READ-10: the enemy bullets most of all; GFX-READ-14: the player shots, toned down,
    # still show.
    assert report["enemyBullet"] >= READABILITY.minBulletContrast
    assert report["playerShot"] >= READABILITY.minPlayerShotContrast

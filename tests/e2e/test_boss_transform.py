# Copyright (c) 2026 Renaud Guillon
"""e2e: bosses transform as they lose parts.

Revealing hidden weapons that fire (docs/superpowers/
specs/2026-10-31-ship-glow-and-boss-transform-design.md, Part B).
"""

import pytest
from e2e.menu_helpers import boss, boss_stage, open_debug, step_until, wait_out_transformation
from playwright.sync_api import Page

# The first level of each world: its final boss transforms twice.
LEVELS = ["1-1", "2-1", "3-1", "4-1"]


@pytest.mark.parametrize("level_id", LEVELS)
def test_a_final_boss_transforms_and_its_hidden_weapons_come_out_and_fire(
    page: Page, level_id: str
) -> None:
    """BOSS-35 (a final boss transforms) and BOSS-38 (its hidden weapons come out and fire)."""
    open_debug(page, f"?level={level_id}&boss=final")
    step_until(page, lambda: (boss(page) or {}).get("state"), lambda s: s == "fighting")
    hidden = boss(page)["hiddenParts"]
    assert hidden > 0
    # Break its parts one at a time (K, DEV-OPT-09) until it starts transforming.
    stage = boss_stage(page)
    while boss(page)["state"] != "transforming":
        page.keyboard.press("KeyK")
        stage += 1
        step_until(page, lambda: boss_stage(page), lambda s, at=stage: s >= at, frames=1)
    wait_out_transformation(page)
    fought = boss(page)
    assert fought["form"] == 1
    assert fought["hiddenParts"] < hidden
    # Its new weapons fire: it shoots again once the transformation is over.
    step_until(page, lambda: (boss(page) or {}).get("state"), lambda s: s == "fighting")
    step_until(
        page,
        lambda: page.evaluate("() => window.__GAME_TEST__.getState().game.enemyShots"),
        lambda n: n > 0,
    )

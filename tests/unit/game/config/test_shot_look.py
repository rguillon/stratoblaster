# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/shot_look.py`."""

from game.config.shot_look import SHOT_LOOK


def test_gfx_shot_01_the_shot_look_covers_bullets_lasers_missiles_and_impacts() -> None:
    """Also GFX-SHOT-03 (laser), GFX-SHOT-06 (missile), GFX-FX-02 and GFX-FX-03 (impacts)."""
    for name in ("bullet", "laser", "missile", "impact"):
        assert SHOT_LOOK[name] is not None, name

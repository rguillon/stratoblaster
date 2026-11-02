# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/shots/player_shot_renderers.py`."""

from game.config.player_weapons import BULLET, LASER, MISSILE
from game.view.shots.bullet_renderer import create_bullet_renderer
from game.view.shots.laser_renderer import create_laser_renderer
from game.view.shots.missile_renderer import create_missile_renderer
from game.view.shots.player_shot_renderers import PLAYER_SHOT_RENDERERS


def test_gfx_shot_01_each_player_weapon_has_its_own_shot_renderer() -> None:
    """Also GFX-SHOT-03 and GFX-SHOT-06: the tracer, the beam and the missile each have theirs."""
    assert {
        BULLET.id: create_bullet_renderer,
        LASER.id: create_laser_renderer,
        MISSILE.id: create_missile_renderer,
    } == PLAYER_SHOT_RENDERERS

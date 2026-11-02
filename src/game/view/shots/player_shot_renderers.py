# Copyright (c) 2026 Renaud Guillon
"""Shot renderer of each player weapon, keyed by weapon id."""

from game.config.player_weapons import BULLET, LASER, MISSILE
from game.view.shots.bullet_renderer import create_bullet_renderer
from game.view.shots.laser_renderer import create_laser_renderer
from game.view.shots.missile_renderer import create_missile_renderer

# Shot renderer of each player weapon, keyed by weapon id.
PLAYER_SHOT_RENDERERS = {
    BULLET.id: create_bullet_renderer,
    LASER.id: create_laser_renderer,
    MISSILE.id: create_missile_renderer,
}

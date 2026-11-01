# Copyright (c) 2026 Renaud Guillon
"""The Strafer (`specs/enemies/strafer.md`)."""

import math

from core.entities.enemy import Enemy
from core.systems.enemy_motion import fan_headings
from core.systems.gun_muzzles import GunMuzzles
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.enemy_helpers import DEG, DOWN, Cadence, on_playfield

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


CFG = ENEMY_CONFIG.strafer


class Strafer(Enemy):
    """ENM-STRAFER-05: crosses the top third of the screen sideways, from `side`.

    And fires a fan of 3 bullets straight down every second (ENM-STRAFER-06; preset directions -15°,
    0°, +15°, ENM-20), from the gun on its side facing down.
    """

    def __init__(self, x: float, y: float, side: str) -> None:
        super().__init__(x, y, CFG.stats)
        self._gun = Cadence(CFG.fireInterval, CFG.fireInterval / 2)
        self._muzzles = GunMuzzles(CFG.muzzles)
        self._direction = 1 if side == "left" else -1
        self.heading = (self._direction * math.pi) / 2

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        self.x += self._direction * CFG.speed * dt
        if not on_playfield(self, ctx):
            return
        _count = self._gun.tick(dt * ctx.fire_rate)
        for _i in range(_count):
            for heading in fan_headings(DOWN, CFG.fanCount, CFG.fanSpacing * DEG):
                point = self._muzzles.along(ctx, self, heading)
                ctx.fire_bullet(point.x, point.y, heading, CFG.bullet)
        self.charge = self._gun.progress

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


# Headings straight to the screen's right and left (radians from +Y, positive to the right).
RIGHT = math.pi / 2
LEFT = -math.pi / 2


class Strafer(Enemy):
    """ENM-STRAFER-05: crosses the screen, from `side`.

    From "left" or "right" it crosses the top third sideways and fires a fan of 3 bullets straight
    down every second (ENM-STRAFER-06; preset directions -15°, 0°, +15°, ENM-20). From "top" it
    flies straight down the screen and fires its fan sideways, level, towards the player's side.
    Each fan leaves from the three barrels of its flank facing that way, along the barrels (WPN-01).
    """

    def __init__(self, x: float, y: float, side: str) -> None:
        super().__init__(x, y, CFG.stats)
        self._gun = Cadence(CFG.fireInterval, CFG.fireInterval / 2)
        self._muzzles = GunMuzzles(CFG.muzzles)
        self.barrels = self._muzzles.barrels
        self._ctx: EnemyContext | None = None
        self._vertical = side == "top"
        self._direction = 1 if side == "left" else -1
        self.heading = DOWN if self._vertical else (self._direction * math.pi) / 2

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        if self._vertical:
            self.y -= CFG.speed * dt
        else:
            self.x += self._direction * CFG.speed * dt
        if not on_playfield(self, ctx):
            return
        self._ctx = ctx
        _count = self._gun.tick(dt * ctx.fire_rate)
        for _i in range(_count):
            for heading in fan_headings(self._aim(ctx), CFG.fanCount, CFG.fanSpacing * DEG):
                self._muzzles.shoot(ctx, self, heading, self._fire)
        self.charge = self._gun.progress

    def _aim(self, ctx: EnemyContext) -> float:
        """Return the middle of its fan: down the screen, or level towards the player's side."""
        if not self._vertical:
            return DOWN
        return RIGHT if ctx.player_x >= self.x else LEFT

    def _fire(self, x: float, y: float, heading: float) -> None:
        """Fire a bullet from a barrel's tip, along the barrel (WPN-01)."""
        if self._ctx is not None:
            self._ctx.fire_bullet(x, y, heading, CFG.bullet)

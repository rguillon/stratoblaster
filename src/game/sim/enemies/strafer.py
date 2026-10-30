"""The Strafer (P05-R04)"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import Enemy
from core.systems.enemy_motion import fan_headings
from core.systems.gun_muzzles import GunMuzzles
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.enemy_helpers import DEG, DOWN, Cadence, on_playfield

__pragma__("skip")
from core.entities.enemy import EnemyContext  # noqa: E402

__pragma__("noskip")

CFG = ENEMY_CONFIG.strafer


class Strafer(Enemy):
    """P05-R04: crosses the top third of the screen sideways, from `side`, and fires a fan of 3
    bullets straight down every second (preset directions -15°, 0°, +15°, GD-44), from the gun on
    its side facing down.
    """

    def __init__(self, x: float, y: float, side: str) -> None:
        super().__init__(x, y, CFG.stats)
        self._gun = Cadence(CFG.fireInterval, CFG.fireInterval / 2)
        self._muzzles = GunMuzzles(CFG.muzzles)
        self._direction = 1 if side == "left" else -1
        self.heading = (self._direction * math.pi) / 2

    def update(self, ctx: EnemyContext, dt: float) -> None:
        self.x += self._direction * CFG.speed * dt
        if not on_playfield(self, ctx):
            return
        _count = self._gun.tick(dt * ctx.fire_rate)
        for _i in range(_count):
            for heading in fan_headings(DOWN, CFG.fanCount, CFG.fanSpacing * DEG):
                point = self._muzzles.along(ctx, self, heading)
                ctx.fire_bullet(point.x, point.y, heading, CFG.bullet)
        self.charge = self._gun.progress

"""The Minelayer (`specs/enemies/minelayer.md`)"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import Enemy
from core.systems.gun_muzzles import GunMuzzles
from game.config.enemies_veteran import VETERAN_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, Cadence, on_playfield

__pragma__("skip")
from core.entities.enemy import EnemyContext  # noqa: E402 (after the Transcrypt skip block, ENG-153)

__pragma__("noskip")

CFG = VETERAN_CONFIG.minelayer


class Minelayer(Enemy):
    """ENM-MINELAYER-07: crosses the top half of the screen sideways from `side`, like a Strafer
    (ENM-STRAFER-05). Every 0.8 s it drops a mine from its belly rack (ENM-MINELAYER-08): a slow
    bullet drifting down that bursts into a ring of 6 bullets 1.5 s later (ENM-MINELAYER-09,
    `EnemyBulletSpec.burst`). Its `charge` lights its charge lights (ENM-MINELAYER-04).
    """

    def __init__(self, x: float, y: float, side: str) -> None:
        super().__init__(x, y, CFG.stats)
        self._rack = Cadence(CFG.dropInterval, CFG.firstDrop)
        self._muzzles = GunMuzzles(CFG.muzzles)
        self._direction = 1 if side == "left" else -1
        self.heading = (self._direction * math.pi) / 2

    def update(self, ctx: EnemyContext, dt: float) -> None:
        self.x += self._direction * CFG.speed * dt
        if not on_playfield(self, ctx):
            return
        _count = self._rack.tick(dt * ctx.fire_rate)
        for _i in range(_count):
            # The rack's hatches take turns.
            point = self._muzzles.along(ctx, self, DOWN)
            ctx.fire_bullet(point.x, point.y, DOWN, CFG.mine)
        self.charge = self._rack.progress

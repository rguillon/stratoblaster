"""The Hive (P05-R23)"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.jointed_enemy import JointedEnemy
from core.entities.muzzle import muzzle_point
from core.systems.gun_muzzles import GunMuzzles
from game.config.enemies_elite import ELITE_CONFIG
from game.sim.enemies.enemy_helpers import DEG, DOWN, Cadence, on_playfield
from game.sim.enemies.wasp import Wasp

__pragma__("skip")
from core.entities.enemy import EnemyContext  # noqa: E402

__pragma__("noskip")

CFG = ELITE_CONFIG.hive


class Hive(JointedEnemy):
    """P05-R23: a huge rounded hive-ship with a launch ring turning on its back (its `spin`; it has
    no destroyable parts). It flies slowly straight down the screen and leaves at the bottom. Every
    4 s a Wasp (P05-R14) comes out of the hatch on its ring and attacks; every 3 s it fires a ring
    of 12 bullets from the vents around its rim. It stops launching and firing in the lower part of
    the screen. Its `charge` is how close the next launch is.
    """

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, CFG.stats, CFG.design)
        self._launcher = Cadence(CFG.launchInterval, CFG.firstLaunch)
        self._ring = Cadence(CFG.ringInterval, CFG.firstRing)
        self._ring_muzzles = GunMuzzles(CFG.ringMuzzles)
        self.heading = DOWN

    def hatch(self, ctx: EnemyContext) -> tuple[float, float]:
        """Where the ring's hatch is now, as the camera sees it on the playfield."""
        point = ctx.seen(muzzle_point(self, CFG.port, self.spin))
        return (point.x, point.y)

    def act(self, ctx: EnemyContext, dt: float) -> None:
        self.spin += CFG.ringSpin * DEG * dt
        self.y -= CFG.speed * dt
        if not on_playfield(self, ctx) or self.y < CFG.lastFraction * ctx.height:
            self.charge = 0
            return
        _count = self._launcher.tick(dt)
        for _i in range(_count):
            x, y = self.hatch(ctx)
            ctx.spawn(Wasp(x, y, y - CFG.launchDrop))
        self.charge = self._launcher.progress
        _count = self._ring.tick(dt * ctx.fire_rate)
        for _i in range(_count):
            for k in range(CFG.ringCount):
                heading = self.heading + (2 * math.pi * k) / CFG.ringCount
                point = self._ring_muzzles.along(ctx, self, heading)
                ctx.fire_bullet(point.x, point.y, heading, CFG.ringBullet)

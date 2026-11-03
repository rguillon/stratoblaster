# Copyright (c) 2026 Renaud Guillon
"""The Hatchery (`specs/enemies/hatchery.md`)."""

from core.entities.enemy import Enemy
from game.config.enemy_hatchery import HATCHERY_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, Cadence, on_playfield
from game.sim.enemies.wasp import Wasp

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


CFG = HATCHERY_CONFIG


class Hatchery(Enemy):
    """ENM-HATCHERY-05: a big, slow egg-pod carrier.

    It descends straight down and never shoots (ENM-HATCHERY-06); every 6 s a group of 3 Wasps
    comes out of its ventral hatch (ENM-HATCHERY-07). It stops launching in the lower part of the
    screen (ENM-HATCHERY-08). Its `charge` is how close the next launch is (the hatch glows).
    """

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self._launcher = Cadence(CFG.launchInterval, CFG.firstLaunch)
        self.heading = DOWN

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        self.y -= CFG.speed * dt
        if not on_playfield(self, ctx) or self.y < CFG.lastLaunchFraction * ctx.height:
            self.charge = 0
            return
        _count = self._launcher.tick(dt)
        for _i in range(_count):
            self._launch(ctx)
        self.charge = self._launcher.progress

    def _launch(self, ctx: EnemyContext) -> None:
        hatch = ctx.seen(self.place(CFG.hatch))
        for offset in CFG.group:
            x = hatch.x + offset[0]
            y = hatch.y + offset[1]
            ctx.spawn(Wasp(x, y, y - CFG.launchDrop))

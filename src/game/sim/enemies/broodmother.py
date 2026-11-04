# Copyright (c) 2026 Renaud Guillon
"""The Broodmother (`specs/enemies/broodmother.md`)."""

from core.entities.enemy import Enemy
from game.config.enemy_broodmother import BROODMOTHER_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, Cadence, on_playfield
from game.sim.enemies.phantom import Phantom

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


CFG = BROODMOTHER_CONFIG


class Broodmother(Enemy):
    """ENM-BROODMOTHER-06: a huge, slow brood carrier.

    It descends straight down and never shoots (ENM-BROODMOTHER-06); every 7 s a Phantom comes out
    of the hatch on its belly (ENM-BROODMOTHER-07). It stops launching in the lower part of the
    screen (ENM-BROODMOTHER-09). Its `charge` is how close the next launch is (the egg sacs glow,
    ENM-BROODMOTHER-03).
    """

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self._launcher = Cadence(CFG.launchInterval, CFG.firstLaunch)
        self.heading = DOWN

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        self.y -= CFG.speed * dt
        if not on_playfield(self, ctx) or self.y < CFG.lastFraction * ctx.height:
            self.charge = 0
            return
        _count = self._launcher.tick(dt)
        for _i in range(_count):
            self._launch(ctx)
        self.charge = self._launcher.progress

    def _launch(self, ctx: EnemyContext) -> None:
        """Send a Phantom out of the hatch."""
        x = self.x + CFG.port[0]
        y = self.y + CFG.port[1]
        ctx.spawn(Phantom(x, y, y - CFG.launchDrop))

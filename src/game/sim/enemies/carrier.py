# Copyright (c) 2026 Renaud Guillon
"""The Carrier (`specs/enemies/carrier.md`)."""

from core.entities.enemy import Enemy
from core.systems.enemy_motion import Path
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, Cadence, on_playfield
from game.sim.enemies.gnat import Gnat

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


CFG = ENEMY_CONFIG.carrier
GROUP_DELAY = ENEMY_CONFIG.gnat.groupDelay


class Carrier(Enemy):
    """ENM-CARRIER-05: a fat flying carrier.

    It descends slowly and never shoots (ENM-CARRIER-06); every 3 s a Gnat comes out of each of its
    side ports (two a side, ENM-CARRIER-07), flying out sideways and then down the screen
    (ENM-CARRIER-08). It stops launching in the lower part of the screen (ENM-CARRIER-09). Its
    `charge` is how close the next launch is (the ports glow).
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
        for side in (-1, 1):
            for i, port in enumerate(CFG.ports):
                x0 = self.x + side * port[0]
                y0 = self.y + port[1]
                controls = [[x0 + side * point[0], y0 + point[1]] for point in CFG.launchPath]
                ctx.spawn(Gnat(Path(controls), i * GROUP_DELAY))

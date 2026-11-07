# Copyright (c) 2026 Renaud Guillon
"""The Carrier (`specs/enemies/carrier.md`)."""

from core.entities.barrel import Barrel
from core.entities.enemy import Enemy
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, Cadence, on_playfield
from game.sim.enemies.hornet import Hornet, hornet_options

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


CFG = ENEMY_CONFIG.carrier
QUARTER = 1.5707963267948966


def launch_order() -> list[list[int]]:
    """Return the bays in the order they launch: `[side, port]`, alternating sides, front first.

    Bay number `k` in this order is launcher `k` (`Enemy.launchers`): the model's docked Hornet in
    that bay is gone from its launch until the next one has moved up into the bay.
    """
    return [[side, port] for port in range(len(CFG.ports)) for side in (1, -1)]


class Carrier(Enemy):
    """ENM-CARRIER-05: a fat flying carrier.

    It descends slowly and never shoots (ENM-CARRIER-06). A Hornet waits in each of the landing
    bays dug into its flanks (two a side, ENM-CARRIER-07); they leave one by one, in turn, each bay
    every `launchInterval`: a Hornet flies out of its bay sideways, then pauses, turns to the
    player and dives (ENM-CARRIER-08). It stops launching in the lower part of the screen
    (ENM-CARRIER-09). Its `charge` is how close the next launch is (the bays' thresholds glow).
    """

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self._order = launch_order()
        gap = CFG.launchInterval / len(self._order)
        self._launcher = Cadence(gap, CFG.firstLaunch)
        self._next = 0
        self.launchers = [Barrel([0, 0, 0]) for _bay in self._order]
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
        """Send the Hornet in the next bay out: it starts in its bay, nose out, and flies clear."""
        k = self._next
        self._next = (k + 1) % len(self._order)
        side = self._order[k][0]
        port = CFG.ports[self._order[k][1]]
        x0 = self.x + side * port[0]
        y0 = self.y + port[1]
        options = hornet_options(ENEMY_CONFIG.hornet, y0, x0 + side * CFG.launchExit)
        hornet = Hornet(x0, y0, options)
        hornet.heading = side * QUARTER
        ctx.spawn(hornet)
        self.launchers[k].kick(self.age)

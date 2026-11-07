# Copyright (c) 2026 Renaud Guillon
"""The Broodmother (`specs/enemies/broodmother.md`)."""

from core.entities.enemy import Enemy
from game.config.enemy_broodmother import BROODMOTHER_CONFIG
from game.sim.enemies.carrier_guns import CarrierGuns
from game.sim.enemies.enemy_helpers import DOWN, Cadence, on_playfield
from game.sim.enemies.phantom import Phantom

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


CFG = BROODMOTHER_CONFIG
INFINITY = float("Infinity")


def ramp(t: float, length: float) -> float:
    """Return how far a move `length` seconds long is after `t` seconds, 0 to 1."""
    return min(1, max(0, t / length))


class Broodmother(Enemy):
    """ENM-BROODMOTHER-06: a huge, slow flying aircraft carrier.

    It descends straight down; the gun turret on its left sponson turns towards the player and
    fires an aimed bullet once it points at them, every `fireInterval` (it no longer holds its fire,
    ENM-BROODMOTHER-06). Every 7 s the Phantom waiting
    in the hangar at its stern rolls out of its mouth onto the runway and takes off, flying down
    over its deck; the next one is loaded in the hangar (ENM-BROODMOTHER-07). It stops launching in
    the lower part of the screen (ENM-BROODMOTHER-09). Its `charge` is how close the next launch is
    (the hangar's mouth glows).

    `tracks` tells the model where its moving part is: the Phantom in the hangar (0 inside, 1 out
    on the runway; below 0 while the hangar is empty).
    """

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self._launcher = Cadence(CFG.launchInterval, CFG.firstLaunch)
        self._launched_at: float | None = None
        self.tracks = [0.0]
        self._guns = CarrierGuns(CFG.turrets)
        self.turrets = self._guns.turrets
        self.barrels = self._guns.barrels
        self.heading = DOWN

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        self.y -= CFG.speed * dt
        if on_playfield(self, ctx):
            self._guns.update(self, ctx, dt)
        if not on_playfield(self, ctx) or self.y < CFG.lastFraction * ctx.height:
            self.charge = 0
            self._roll(INFINITY)
            return
        _count = self._launcher.tick(dt)
        for _i in range(_count):
            self._launch(ctx)
        self.charge = self._launcher.progress
        self._roll((1 - self._launcher.progress) * CFG.launchInterval)

    def _roll(self, next_launch: float) -> None:
        """Place the Phantom in the hangar, `next_launch` seconds before the next launch."""
        hangar = CFG.hangar
        since = INFINITY if self._launched_at is None else self.age - self._launched_at
        if since < hangar.reloadDelay:
            # It just left: the hangar is empty a moment before the next one is loaded.
            self.tracks[0] = -1.0
            return
        self.tracks[0] = ramp(hangar.rollSeconds - next_launch, hangar.rollSeconds)

    def _launch(self, ctx: EnemyContext) -> None:
        """Send the Phantom off the runway, flying down to its first place."""
        at = ctx.seen(self.place((CFG.port[0], CFG.port[1], 0)))
        ctx.spawn(Phantom(at.x, at.y, at.y - CFG.launchDrop))
        self._launched_at = self.age

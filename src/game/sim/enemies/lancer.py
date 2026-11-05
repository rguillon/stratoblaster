# Copyright (c) 2026 Renaud Guillon
"""The Lancer (`specs/enemies/lancer.md`)."""

import math

from core.entities.enemy import Enemy, EnemyLaserSpec
from core.entities.muzzle import RaisedPoint
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.enemy_helpers import DOWN

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext
from core.entities.muzzle import Muzzle

# __pragma__ ("noskip")


CFG = ENEMY_CONFIG.lancer

# Slowest speed while braking into a stop, px/s, so that it always gets there.
CREEP = 8


class LancerBeam:
    """What the Lancer's laser leaves from and follows.

    Its emitter at the nose (raised above the playfield), along the Lancer's heading. It stops with
    the Lancer.
    """

    def __init__(self, lancer: "Lancer", muzzle: Muzzle) -> None:
        self._lancer = lancer
        self._muzzle = muzzle

    @property
    def emitter(self) -> RaisedPoint:
        """Where the laser leaves from, raised above the playfield."""
        return self._lancer.place(self._muzzle)

    @property
    def heading(self) -> float:
        """The direction the laser points."""
        return self._lancer.heading

    @property
    def gone(self) -> bool:
        """Whether the laser is gone."""
        return self._lancer.gone

    @property
    def health(self) -> float:
        """The health of the laser."""
        return self._lancer.health


class Lancer(Enemy):
    """ENM-LANCER-05: moves to a fixed point in the top part of the screen and stops.

    A warning line shows straight down from its emitter for 1 s, then it fires a laser along that
    line for 1.5 s, without moving (ENM-LANCER-06, ENM-19). Then it goes on straight down the
    screen, never turning: it speeds up, brakes into its next stop a `stepFraction` of the screen
    lower and fires again, until its next stop would be under `lastStopFraction`; from there it
    speeds up down and out of the bottom of the screen (ENM-LANCER-07).
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self.stop_y: float | None = stop_y
        self.state = "move"
        self._attack_for = 0.0
        # It comes in at its entry speed, then eases into its first stop.
        self._speed = float(CFG.entrySpeed)
        self.heading = DOWN

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        if self.state == "move":
            self._move(ctx, dt)
        else:
            self._attack(ctx, dt)

    def _move(self, ctx: EnemyContext, dt: float) -> None:
        """Fly straight down: up to its cruise speed, braking into its next stop if it has one."""
        cruise = CFG.cruiseSpeed if self.stop_y is not None else CFG.exitSpeed
        # Eases towards its cruise speed: speeding up, or slowing down from a faster entry.
        if self._speed < cruise:
            speed = min(cruise, self._speed + CFG.acceleration * dt)
        else:
            speed = max(cruise, self._speed - CFG.brake * dt)
        if self.stop_y is None:
            self._speed = speed
            self.y -= speed * dt
            return
        left = self.y - self.stop_y
        # Braking at a steady rate so that it comes to rest right on its stop.
        speed = max(CREEP, min(speed, math.sqrt(2 * CFG.brake * max(0, left))))
        self._speed = speed
        if speed * dt < left:
            self.y -= speed * dt
            return
        self.y = self.stop_y
        self._speed = 0
        self._attack_for = 0
        self.state = "attack"
        ctx.fire_laser(LancerBeam(self, CFG.muzzle), _laser_spec())

    def _attack(self, ctx: EnemyContext, dt: float) -> None:
        warning_seconds = CFG.laser.warningSeconds
        firing_seconds = CFG.laser.firingSeconds
        self._attack_for += dt
        # Its emitter charges up through the warning (ENM-LANCER-03).
        self.charge = min(1, self._attack_for / warning_seconds)
        if self._attack_for < warning_seconds + firing_seconds:
            return
        self.charge = 0
        self.state = "move"
        # Its next stop further down, or none: then it leaves through the bottom of the screen.
        here = self.y if self.stop_y is None else self.stop_y
        below = here - CFG.stepFraction * ctx.height
        self.stop_y = below if below >= CFG.lastStopFraction * ctx.height else None


def _laser_spec() -> EnemyLaserSpec:
    """Return the Lancer's laser: a warning line first, then the beam (ENM-LANCER-06, ENM-19)."""
    spec = CFG.laser
    return EnemyLaserSpec(spec.warningSeconds, spec.firingSeconds, spec.width, spec.style)

# Copyright (c) 2026 Renaud Guillon
"""The Lancer (`specs/enemies/lancer.md`)."""

from core.entities.enemy import Enemy, EnemyLaserSpec
from core.entities.muzzle import RaisedPoint
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, leave_upward

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext
from core.entities.muzzle import Muzzle

# __pragma__ ("noskip")


CFG = ENEMY_CONFIG.lancer

# Slowest speed while braking to the stop point, px/s.
CREEP = 20


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
    line for 1.5 s, without moving (ENM-LANCER-06, ENM-19); then it backs away upward
    (ENM-LANCER-07).
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self.stop_y = stop_y
        self.state = "enter"
        self._attack_for = 0.0
        self.heading = DOWN

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        if self.state == "enter":
            self._enter(ctx, dt)
        elif self.state == "attack":
            self._attack(dt)
        else:
            leave_upward(self, CFG.exitSpeed, dt)

    def _enter(self, ctx: EnemyContext, dt: float) -> None:
        left = self.y - self.stop_y
        speed = max(CREEP, CFG.entrySpeed * min(1, left / CFG.brakeDistance))
        self.y = max(self.stop_y, self.y - speed * dt)
        if self.y > self.stop_y:
            return
        self.state = "attack"
        ctx.fire_laser(LancerBeam(self, CFG.muzzle), _laser_spec())

    def _attack(self, dt: float) -> None:
        warning_seconds = CFG.laser.warningSeconds
        firing_seconds = CFG.laser.firingSeconds
        self._attack_for += dt
        # Its emitter charges up through the warning (ENM-LANCER-03).
        self.charge = min(1, self._attack_for / warning_seconds)
        if self._attack_for < warning_seconds + firing_seconds:
            return
        self.state = "exit"
        self.charge = 0


def _laser_spec() -> EnemyLaserSpec:
    """Return the Lancer's laser: a warning line first, then the beam (ENM-LANCER-06, ENM-19)."""
    spec = CFG.laser
    return EnemyLaserSpec(spec.warningSeconds, spec.firingSeconds, spec.width, spec.style)

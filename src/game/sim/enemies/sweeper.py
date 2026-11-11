# Copyright (c) 2026 Renaud Guillon
"""The Sweeper (`specs/enemies/sweeper.md`)."""

from core.entities.enemy import Enemy, EnemyLaserSpec
from core.entities.muzzle import RaisedPoint
from game.config.enemy_sweeper import SWEEPER_CONFIG
from game.sim.enemies.enemy_helpers import DEG, DOWN, leave_upward

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext
from core.entities.muzzle import Muzzle

# __pragma__ ("noskip")


CFG = SWEEPER_CONFIG

# Slowest speed while braking to the stop point, px/s.
CREEP = 20


class SweeperBeam:
    """What the Sweeper's laser leaves from and follows.

    Its emitter at the end of the barrel (raised above the playfield), along the Sweeper's heading,
    which turns while the laser fires.
    """

    def __init__(self, sweeper: "Sweeper", muzzle: Muzzle) -> None:
        self._sweeper = sweeper
        self._muzzle = muzzle

    @property
    def emitter(self) -> RaisedPoint:
        """Where the laser leaves from, raised above the playfield."""
        return self._sweeper.place(self._muzzle)

    @property
    def heading(self) -> float:
        """The direction the laser points."""
        return self._sweeper.heading

    @property
    def gone(self) -> bool:
        """Whether the laser is gone."""
        return self._sweeper.gone

    @property
    def health(self) -> float:
        """The health of the laser."""
        return self._sweeper.health


class Sweeper(Enemy):
    """ENM-SWEEPER-05: a hovering laser platform that sweeps its beam across an arc.

    It moves to a fixed point in the upper part of the screen and stops, its barrel turning while
    it brakes to one edge of the arc, away from the player's side (D-322). A warning line shows
    along it for 1 s (ENM-SWEEPER-06, ENM-19), then the laser fires while the whole platform
    turns `arcDeg` degrees over 2.2 s (ENM-SWEEPER-07, ENM-32), the beam sweeping across the
    screen with it; then it backs away upward (ENM-SWEEPER-08). Its `charge` fills through the
    warning.
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self.stop_y = stop_y
        self.state = "enter"
        self.heading = DOWN
        self._attack_for = 0.0
        # The heading the sweep starts at, and the way it turns (+1 or -1); chosen as it starts
        # braking (`_aimed`), so it turns to the start while it slows down (D-322).
        self._start = DOWN
        self._way = 1
        self._aimed = False

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
        # D-322: it turns its barrel to the sweep's first edge while it brakes, eased in and out,
        # so it is there as it stops (it used to turn there at once on stopping).
        braked = min(1, max(0, 1 - (self.y - self.stop_y) / CFG.brakeDistance))
        if braked > 0 and not self._aimed:
            self._aim(ctx)
        if self._aimed:
            eased = braked * braked * (3 - 2 * braked)
            self.heading = DOWN + (self._start - DOWN) * eased
        if self.y > self.stop_y:
            return
        self.state = "attack"
        self.heading = self._start
        ctx.fire_laser(SweeperBeam(self, CFG.muzzle), _sweeping())

    def _aim(self, ctx: EnemyContext) -> None:
        """Choose the sweep's first edge: away from the player's side (ENM-SWEEPER-06).

        A heading above DOWN points to the left: it starts on the far side from the player and
        sweeps towards them and past.
        """
        self._aimed = True
        self._way = -1 if ctx.player_x >= self.x else 1
        self._start = DOWN - self._way * CFG.arcDeg * DEG / 2

    def _attack(self, dt: float) -> None:
        warning_seconds = CFG.laser.warningSeconds
        firing_seconds = CFG.laser.firingSeconds
        self._attack_for += dt
        self.charge = min(1, self._attack_for / warning_seconds)
        swept = min(1, max(0, (self._attack_for - warning_seconds) / firing_seconds))
        self.heading = self._start + self._way * CFG.arcDeg * DEG * swept
        if self._attack_for < warning_seconds + firing_seconds:
            return
        self.state = "exit"
        self.charge = 0


def _sweeping() -> EnemyLaserSpec:
    """Return the Sweeper's laser, whose beam keeps turning with it."""
    spec = CFG.laser
    return EnemyLaserSpec(
        spec.warningSeconds, spec.firingSeconds, spec.width, spec.style, True, spec.damage
    )

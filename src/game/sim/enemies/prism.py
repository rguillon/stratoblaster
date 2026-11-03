# Copyright (c) 2026 Renaud Guillon
"""The Prism (`specs/enemies/prism.md`)."""

from core.entities.enemy import Enemy, EnemyLaserSpec
from core.entities.muzzle import RaisedPoint
from game.config.enemy_prism import PRISM_CONFIG
from game.sim.enemies.enemy_helpers import DEG, DOWN

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext
from core.entities.muzzle import Muzzle

# __pragma__ ("noskip")


CFG = PRISM_CONFIG

# Slowest speed while braking to the stop point, px/s.
CREEP = 20


class PrismBeam:
    """What one of the Prism's lasers leaves from and follows.

    The emitter at the tip of its wing, and a heading set by the Prism's sweep: straight down turned
    by the sweep angle, outward for a positive angle, inward for a negative one (ENM-PRISM-07).
    """

    def __init__(self, prism: "Prism", muzzle: Muzzle) -> None:
        self._prism = prism
        self._muzzle = muzzle
        # -1 for the left emitter, 1 for the right one.
        self._side = 1 if muzzle[0] > 0 else -1

    @property
    def emitter(self) -> RaisedPoint:
        """Where the laser leaves from, raised above the playfield."""
        return self._prism.place(self._muzzle)

    @property
    def heading(self) -> float:
        """The direction the laser points now."""
        return DOWN - self._side * self._prism.sweep

    @property
    def gone(self) -> bool:
        """Whether the laser is gone."""
        return self._prism.gone

    @property
    def health(self) -> float:
        """The health of the laser."""
        return self._prism.health


def _sweeping() -> EnemyLaserSpec:
    """Return the beams' laser, which keeps turning with the Prism's sweep (ENM-32)."""
    return EnemyLaserSpec(
        CFG.laser.warningSeconds, CFG.laser.firingSeconds, CFG.laser.width, CFG.laser.style, True
    )


class Prism(Enemy):
    """ENM-PRISM-05: a crystalline laser platform with two fixed emitters on its wings.

    It moves to the upper third of the screen and stops (ENM-PRISM-05). Each emitter shows a warning
    line for 1 s (ENM-PRISM-06, ENM-19), its lights charging (ENM-PRISM-04), then fires a laser for
    2 s while both beams turn together: the first burst closes the beams from outward through
    crossing, the second opens them again (ENM-PRISM-07). Then it leaves upward (ENM-PRISM-08). Its
    `sweep` is the angle of the beams from straight down, in radians, positive outward.
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self.stop_y = stop_y
        # What it is doing: enter, attack (a burst), gap (between the bursts) or exit.
        self.state = "enter"
        self.heading = DOWN
        # The beams' angle from straight down, radians, outward positive.
        self.sweep = 0.0
        # The burst it is on, and the seconds it has lasted.
        self.burst = 0
        self._for = 0.0

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        if self.state == "enter":
            self._enter(ctx, dt)
        elif self.state == "attack":
            self._attack(dt)
        elif self.state == "gap":
            self._gap(ctx, dt)
        else:
            self.y += CFG.exitSpeed * dt

    def _enter(self, ctx: EnemyContext, dt: float) -> None:
        left = self.y - self.stop_y
        speed = max(CREEP, CFG.entrySpeed * min(1, left / CFG.brakeDistance))
        self.y = max(self.stop_y, self.y - speed * dt)
        if self.y > self.stop_y:
            return
        self._start_burst(ctx)

    def _start_burst(self, ctx: EnemyContext) -> None:
        """Show both warning lines and fire both lasers at the beams' first angle."""
        self.state = "attack"
        self._for = 0.0
        self.sweep = CFG.bursts[self.burst].start * DEG
        spec = _sweeping()
        for muzzle in CFG.emitters:
            ctx.fire_laser(PrismBeam(self, muzzle), spec)

    def _attack(self, dt: float) -> None:
        warning_seconds = CFG.laser.warningSeconds
        firing_seconds = CFG.laser.firingSeconds
        burst = CFG.bursts[self.burst]
        self._for += dt
        # Its emitters charge up through the warning (ENM-PRISM-04).
        self.charge = min(1, self._for / warning_seconds)
        if self._for < warning_seconds + firing_seconds:
            fired = min(1, max(0, (self._for - warning_seconds) / firing_seconds))
            self.sweep = (burst.start + (burst.end - burst.start) * fired) * DEG
            return
        self.sweep = burst.end * DEG
        self.charge = 0
        self.burst += 1
        self._for = 0.0
        self.state = "exit" if self.burst >= len(CFG.bursts) else "gap"

    def _gap(self, ctx: EnemyContext, dt: float) -> None:
        self._for += dt
        if self._for >= CFG.gapSeconds:
            self._start_burst(ctx)

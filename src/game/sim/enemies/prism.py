# Copyright (c) 2026 Renaud Guillon
"""The Prism (`specs/enemies/prism.md`)."""

import math

from core.entities.enemy import Enemy, EnemyLaserSpec
from core.entities.muzzle import RaisedPoint
from core.systems.projectile_motion import heading_to, turn_towards, wrap_angle
from game.config.enemy_prism import PRISM_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, leave_upward

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext
from core.entities.muzzle import Muzzle

# __pragma__ ("noskip")


CFG = PRISM_CONFIG

# Slowest speed while braking to the stop point, px/s.
CREEP = 20

# How quickly its turn to the player eases in as the nose gets there (1/s).
TURN_EASE = 14


class PrismBeam:
    """What one of the Prism's lasers leaves from and follows.

    The emitter at the tip of its wing, and the Prism's own heading: both beams fire straight
    ahead, side by side (ENM-PRISM-07).
    """

    def __init__(self, prism: "Prism", muzzle: Muzzle) -> None:
        self._prism = prism
        self._muzzle = muzzle

    @property
    def emitter(self) -> RaisedPoint:
        """Where the laser leaves from, raised above the playfield."""
        return self._prism.place(self._muzzle)

    @property
    def heading(self) -> float:
        """The direction the laser points now."""
        return self._prism.heading

    @property
    def gone(self) -> bool:
        """Whether the laser is gone."""
        return self._prism.gone

    @property
    def health(self) -> float:
        """The health of the laser."""
        return self._prism.health


def _laser() -> EnemyLaserSpec:
    """Return the beams' laser: a warning line, then the beam, along the Prism's heading."""
    return EnemyLaserSpec(
        CFG.laser.warningSeconds, CFG.laser.firingSeconds, CFG.laser.width, CFG.laser.style
    )


class Prism(Enemy):
    """ENM-PRISM-05: a crystalline laser platform with two fixed emitters on its wings.

    It moves to the upper third of the screen and stops (ENM-PRISM-05). It turns its nose to the
    player (ENM-PRISM-07), then each emitter shows a warning line for 1 s (ENM-PRISM-06, ENM-19),
    its lights charging (ENM-PRISM-04), and fires a laser for 2 s, both straight ahead; it does not
    turn any more once the warning lines show. It does that `bursts` times, then leaves upward
    (ENM-PRISM-08).
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self.stop_y = stop_y
        # What it is doing: enter, aim (turning to the player), attack (a burst) or exit.
        self.state = "enter"
        self.heading = DOWN
        # The burst it is on, and the seconds it has lasted in this state.
        self.burst = 0
        self._for = 0.0

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        if self.state == "enter":
            self._enter(dt)
        elif self.state == "aim":
            self._aim(ctx, dt)
        elif self.state == "attack":
            self._attack(dt)
        else:
            leave_upward(self, CFG.exitSpeed, dt)

    def _enter(self, dt: float) -> None:
        left = self.y - self.stop_y
        speed = max(CREEP, CFG.entrySpeed * min(1, left / CFG.brakeDistance))
        self.y = max(self.stop_y, self.y - speed * dt)
        if self.y > self.stop_y:
            return
        self._go("aim")

    def _go(self, state: str) -> None:
        self.state = state
        self._for = 0.0

    def _aim(self, ctx: EnemyContext, dt: float) -> None:
        """Turn the nose to the player, easing in as it gets there, then fire."""
        target = heading_to(self.x, self.y, ctx.player_x, ctx.player_y)
        left = abs(wrap_angle(target - self.heading))
        # Fast enough to turn all the way round during the aim, slowing down near the end.
        rate = min(math.pi / CFG.aimSeconds, TURN_EASE * left)
        self.heading = turn_towards(self.heading, target, rate * dt)
        self._for += dt
        if self._for >= CFG.aimSeconds:
            self._start_burst(ctx)

    def _start_burst(self, ctx: EnemyContext) -> None:
        """Show both warning lines and fire both lasers straight ahead; the nose stays as it is."""
        self._go("attack")
        spec = _laser()
        for muzzle in CFG.emitters:
            ctx.fire_laser(PrismBeam(self, muzzle), spec)

    def _attack(self, dt: float) -> None:
        warning_seconds = CFG.laser.warningSeconds
        self._for += dt
        # Its emitters charge up through the warning (ENM-PRISM-04).
        self.charge = min(1, self._for / warning_seconds)
        if self._for < warning_seconds + CFG.laser.firingSeconds:
            return
        self.charge = 0
        self.burst += 1
        self._go("exit" if self.burst >= CFG.bursts else "aim")

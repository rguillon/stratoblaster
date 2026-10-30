"""The Scissor (P05-R21)"""

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import EnemyLaserSpec
from core.entities.jointed_enemy import EnemyPart, JointedEnemy
from core.entities.muzzle import RaisedPoint
from game.config.enemies_elite import ELITE_CONFIG
from game.sim.enemies.enemy_helpers import DOWN

__pragma__("skip")
from typing import Any  # noqa: E402

from core.entities.enemy import EnemyContext  # noqa: E402
from core.entities.muzzle import Muzzle  # noqa: E402

__pragma__("noskip")

CFG = ELITE_CONFIG.scissor

# Slowest speed while braking to the stop point, px/s.
CREEP = 20


class ArmBeam:
    """What an arm's laser leaves from and follows: the emitter at the arm's tip, along the arm."""

    def __init__(self, arm: EnemyPart, muzzle: Muzzle) -> None:
        self._arm = arm
        self._muzzle = muzzle

    @property
    def emitter(self) -> RaisedPoint:
        return self._arm.place(self._muzzle)

    @property
    def heading(self) -> float:
        return self._arm.heading

    @property
    def gone(self) -> bool:
        return self._arm.gone

    @property
    def health(self) -> float:
        return self._arm.health


def _sweeping(spec: Any) -> EnemyLaserSpec:
    """The same laser, whose beam keeps turning with its arm."""
    return EnemyLaserSpec(spec.warningSeconds, spec.firingSeconds, spec.width, spec.style, True)


class Scissor(JointedEnemy):
    """P05-R21: a long, narrow hull with two laser arms hinged at its shoulders (moving parts,
    P05-R13), 25° out from straight down. It moves to the upper part of the screen and stops; each
    living arm shows a warning line along it for 1 s (GD-43), then fires its laser along it for 2 s
    while both arms swing 15° inward, the beams closing like scissors; then it backs away.

    The arms' joints only swing while the lasers fire, so the inward swing starts with the beams,
    which sweep with their arms (`EnemyLaserSpec.sweeps`).
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        super().__init__(x, y, CFG.stats, CFG.design)
        self.stop_y = stop_y
        self.state = "enter"
        self._attack_for = 0.0
        self.heading = DOWN
        self.swinging = False

    def act(self, ctx: EnemyContext, dt: float) -> None:
        if self.state == "enter":
            self._enter(ctx, dt)
        elif self.state == "warn":
            self._warn(dt)
        elif self.state == "fire":
            self._fire(dt)
        else:
            self.y += CFG.exitSpeed * dt

    def _enter(self, ctx: EnemyContext, dt: float) -> None:
        left = self.y - self.stop_y
        speed = max(CREEP, CFG.entrySpeed * min(1, left / CFG.brakeDistance))
        self.y = max(self.stop_y, self.y - speed * dt)
        if self.y > self.stop_y:
            return
        self.state = "warn"
        self._attack_for = 0.0
        for arm in CFG.arms:
            part = self.part(arm.id)
            if part is not None:
                ctx.fire_laser(ArmBeam(part, arm.muzzle), _sweeping(CFG.laser))

    def _warn(self, dt: float) -> None:
        self._attack_for += dt
        self.charge = min(1, self._attack_for / CFG.laser.warningSeconds)
        if self._attack_for < CFG.laser.warningSeconds:
            return
        self.state = "fire"
        # The arms close while the beams fire.
        self.swinging = True

    def _fire(self, dt: float) -> None:
        self._attack_for += dt
        if self._attack_for < CFG.laser.warningSeconds + CFG.laser.firingSeconds:
            return
        self.state = "exit"
        self.swinging = False
        self.charge = 0

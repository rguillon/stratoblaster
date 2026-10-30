"""The Lancer (P05-R07), ported from `game/sim/enemies/lancer.ts`."""

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import Enemy
from core.entities.muzzle import RaisedPoint
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.enemy_helpers import DOWN

__pragma__("skip")
from core.entities.enemy import EnemyContext  # noqa: E402
from core.entities.muzzle import Muzzle  # noqa: E402

__pragma__("noskip")

CFG = ENEMY_CONFIG.lancer

# Slowest speed while braking to the stop point, px/s.
CREEP = 20


class LancerBeam:
    """What the Lancer's laser leaves from and follows: its emitter at the nose (raised above the
    playfield), along the Lancer's heading. It stops with the Lancer.
    """

    def __init__(self, lancer: "Lancer", muzzle: Muzzle) -> None:
        self._lancer = lancer
        self._muzzle = muzzle

    @property
    def emitter(self) -> RaisedPoint:
        return self._lancer.place(self._muzzle)

    @property
    def heading(self) -> float:
        return self._lancer.heading

    @property
    def gone(self) -> bool:
        return self._lancer.gone

    @property
    def health(self) -> float:
        return self._lancer.health


class Lancer(Enemy):
    """P05-R07: moves to a fixed point in the top part of the screen and stops. A warning line shows
    straight down from its emitter for 1 s, then it fires a laser along that line for 1.5 s (GD-43),
    without moving; then it backs away upward.
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self.stop_y = stop_y
        self.state = "enter"
        self._attack_for = 0.0
        self.heading = DOWN

    def update(self, ctx: EnemyContext, dt: float) -> None:
        if self.state == "enter":
            self._enter(ctx, dt)
        elif self.state == "attack":
            self._attack(dt)
        else:
            self.y += CFG.exitSpeed * dt

    def _enter(self, ctx: EnemyContext, dt: float) -> None:
        left = self.y - self.stop_y
        speed = max(CREEP, CFG.entrySpeed * min(1, left / CFG.brakeDistance))
        self.y = max(self.stop_y, self.y - speed * dt)
        if self.y > self.stop_y:
            return
        self.state = "attack"
        ctx.fire_laser(LancerBeam(self, CFG.muzzle), CFG.laser)

    def _attack(self, dt: float) -> None:
        warning_seconds = CFG.laser.warningSeconds
        firing_seconds = CFG.laser.firingSeconds
        self._attack_for += dt
        self.charge = min(1, self._attack_for / warning_seconds)
        if self._attack_for < warning_seconds + firing_seconds:
            return
        self.state = "exit"
        self.charge = 0

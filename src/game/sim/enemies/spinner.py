"""The Spinner (P05-R06)"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import Enemy
from core.systems.gun_muzzles import GunMuzzles
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.enemy_helpers import DEG, Cadence

__pragma__("skip")
from core.entities.enemy import EnemyContext  # noqa: E402

__pragma__("noskip")

CFG = ENEMY_CONFIG.spinner


class SpinnerPod:
    """Where one of a Spinner's pods is, and the direction it fires to."""

    def __init__(self, x: float, y: float, heading: float) -> None:
        self.x = x
        self.y = y
        self.heading = heading


class Spinner(Enemy):
    """P05-R06: descends to its stop height in the upper half, stops, then spins for 3 s firing a
    spiral of bullets from its four pods (each bullet leaves outwards, so the directions turn with
    the ring), then leaves upward. Its heading is the ring's rotation.
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self.stop_y = stop_y
        self.state = "enter"
        self._guns = Cadence(CFG.fireInterval, 0)
        self._muzzles = GunMuzzles(CFG.muzzles)
        self._fired_for = 0.0

    def pods(self) -> list[SpinnerPod]:
        """Where each pod is, and the direction it fires to."""
        result: list[SpinnerPod] = []
        for i in range(CFG.pods):
            heading = self.heading + (2 * math.pi * i) / CFG.pods
            result.append(
                SpinnerPod(
                    self.x + math.sin(heading) * CFG.podRadius,
                    self.y + math.cos(heading) * CFG.podRadius,
                    heading,
                )
            )
        return result

    def update(self, ctx: EnemyContext, dt: float) -> None:
        spin = CFG.firingSpin if self.state == "fire" else CFG.idleSpin
        self.heading += spin * DEG * dt
        if self.state == "enter":
            self.y = max(self.stop_y, self.y - CFG.entrySpeed * dt)
            if self.y == self.stop_y:
                self.state = "fire"
        elif self.state == "fire":
            self._fire(ctx, dt)
        else:
            self.y += CFG.exitSpeed * dt

    def _fire(self, ctx: EnemyContext, dt: float) -> None:
        self._fired_for += dt
        self.charge = 1
        _count = self._guns.tick(dt * ctx.fire_rate)
        for _i in range(_count):
            for pod in self.pods():
                point = self._muzzles.along(ctx, self, pod.heading)
                ctx.fire_bullet(point.x, point.y, pod.heading, CFG.bullet)
        if self._fired_for >= CFG.fireDuration:
            self.state = "exit"
            self.charge = 0

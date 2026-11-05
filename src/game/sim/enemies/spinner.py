# Copyright (c) 2026 Renaud Guillon
"""The Spinner (`specs/enemies/spinner.md`)."""

import math

from core.entities.boss_turret import BossTurret, BossTurretSpec
from core.entities.enemy import Enemy
from core.systems.gun_muzzles import GunMuzzles
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.enemy_helpers import DEG, DOWN, Cadence

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


CFG = ENEMY_CONFIG.spinner


class SpinnerPod:
    """Where one of a Spinner's pods is, and the direction it fires to."""

    def __init__(self, x: float, y: float, heading: float) -> None:
        self.x = x
        self.y = y
        self.heading = heading


class Spinner(Enemy):
    """ENM-SPINNER-04: descends to its stop height in the upper half, stops.

    Then spins for 3 s firing a spiral of bullets from its four pods (ENM-SPINNER-05; each bullet
    leaves outwards, so the directions turn with the ring), then leaves upward (ENM-SPINNER-06). Its
    body keeps facing down the screen; its ring, with the pods, turns about its centre: the ring's
    rotation is its `turret`'s aim.
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self.stop_y = stop_y
        self.state = "enter"
        self._ctx: EnemyContext | None = None
        self._guns = Cadence(CFG.fireInterval, 0)
        self.heading = DOWN
        self._ring = BossTurret(BossTurretSpec(0, 0, 0))
        self.turret = self._ring
        self._muzzles = GunMuzzles(CFG.muzzles, True)
        self.barrels = self._muzzles.barrels
        self._fired_for = 0.0

    def pods(self) -> list[SpinnerPod]:
        """Where each pod is, and the direction it fires to."""
        result: list[SpinnerPod] = []
        for i in range(CFG.pods):
            heading = self.heading + self._ring.aim + (2 * math.pi * i) / CFG.pods
            result.append(
                SpinnerPod(
                    self.x + math.sin(heading) * CFG.podRadius,
                    self.y + math.cos(heading) * CFG.podRadius,
                    heading,
                )
            )
        return result

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        spin = CFG.firingSpin if self.state == "fire" else CFG.idleSpin
        self._ring.aim = (self._ring.aim + spin * DEG * dt) % (2 * math.pi)
        if self.state == "enter":
            self.y = max(self.stop_y, self.y - CFG.entrySpeed * dt)
            if self.y == self.stop_y:
                self.state = "fire"
        elif self.state == "fire":
            self._fire(ctx, dt)
        else:
            self.y += CFG.exitSpeed * dt

    def _fire_bullet(self, x: float, y: float, heading: float) -> None:
        if self._ctx is not None:
            self._ctx.fire_bullet(x, y, heading, CFG.bullet)

    def _fire(self, ctx: EnemyContext, dt: float) -> None:
        self._ctx = ctx
        self._fired_for += dt
        self.charge = 1
        _count = self._guns.tick(dt * ctx.fire_rate)
        for _i in range(_count):
            # One bullet from each pod's barrel, along it (WPN-01): the barrels turn with the ring.
            self._muzzles.fire_all(ctx, self, self._fire_bullet)
        if self._fired_for >= CFG.fireDuration:
            self.state = "exit"
            self.charge = 0

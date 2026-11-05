# Copyright (c) 2026 Renaud Guillon
"""The Harrier (`specs/enemies/harrier.md`)."""

from core.entities.enemy import Enemy
from core.systems.gun_muzzles import GunMuzzles
from game.config.enemy_harrier import HARRIER_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, Cadence, leave_upward, missile_spec

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


CFG = HARRIER_CONFIG

# Slowest speed while braking to the stop point, px/s.
CREEP = 30


class Harrier(Enemy):
    """ENM-HARRIER-05: a fast gunship that holds in the upper third and launches missiles.

    It comes in from the top, brakes and holds at its stop point, strafing slowly sideways
    (ENM-HARRIER-06) while it launches one fast homing missile at a time, from its two rails in turn
    (ENM-HARRIER-07, ENM-18), every 2.5 s; after its last missile it leaves upward
    (ENM-HARRIER-08). Its `charge` is how close the next missile is (the rails glow,
    ENM-HARRIER-03).
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self.stop_y = stop_y
        self.state = "enter"
        self.heading = DOWN
        self.missiles_left = CFG.missiles
        self._launcher = Cadence(CFG.fireInterval, CFG.firstShot)
        self._rails = [GunMuzzles([muzzle]) for muzzle in CFG.muzzles]
        # Which way it strafes: 1 to the right, -1 to the left.
        self._strafe = 1

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        if self.state == "enter":
            self._enter(ctx, dt)
        elif self.state == "hold":
            self._hold(ctx, dt)
        else:
            leave_upward(self, CFG.exitSpeed, dt)

    def _enter(self, ctx: EnemyContext, dt: float) -> None:
        left = self.y - self.stop_y
        speed = max(CREEP, CFG.entrySpeed * min(1, left / CFG.brakeDistance))
        self.y = max(self.stop_y, self.y - speed * dt)
        if self.y > self.stop_y:
            return
        self.state = "hold"
        # It strafes towards the middle of the screen first.
        self._strafe = 1 if self.x < ctx.width / 2 else -1

    def _hold(self, ctx: EnemyContext, dt: float) -> None:
        self.x += self._strafe * CFG.strafeSpeed * dt
        if self.x >= ctx.width - CFG.strafeMargin:
            self._strafe = -1
        elif self.x <= CFG.strafeMargin:
            self._strafe = 1
        _count = self._launcher.tick(dt * ctx.fire_rate)
        for _i in range(_count):
            self._launch(ctx)
        if self.state == "hold":
            self.charge = self._launcher.progress

    def _launch(self, ctx: EnemyContext) -> None:
        if self.missiles_left <= 0:
            return
        rail = self._rails[(CFG.missiles - self.missiles_left) % len(self._rails)]
        point = rail.along(ctx, self, DOWN)
        ctx.fire_missile(point.x, point.y, DOWN, missile_spec(CFG.missile))
        self.missiles_left -= 1
        if self.missiles_left <= 0:
            self.state = "exit"
            self.charge = 0

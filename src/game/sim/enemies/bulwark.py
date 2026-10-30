"""The Bulwark (P05-R09)"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import Enemy
from core.systems.enemy_motion import approach
from core.systems.gun_muzzles import GunMuzzles, fire_aimed
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, Cadence, bullet_shot, on_playfield

__pragma__("skip")
from core.entities.enemy import EnemyContext  # noqa: E402

__pragma__("noskip")

CFG = ENEMY_CONFIG.bulwark


class Bulwark(Enemy):
    """P05-R09: a heavy gunship. It comes down slowly to the upper third, drifts left and right for
    8 s, then leaves downward. Every 2 s it fires a spread of 5 bullets 10° apart, the middle one
    aimed at the player (GD-44), from the twin cannon on its tower.
    """

    def __init__(self, center_x: float, y: float, stop_y: float) -> None:
        super().__init__(center_x, y, CFG.stats)
        self.center_x = center_x
        self.stop_y = stop_y
        self.state = "enter"
        self._gun = Cadence(CFG.fireInterval, CFG.fireInterval / 2)
        self._muzzles = GunMuzzles(CFG.muzzles)
        self._drift_for = 0.0
        self.heading = DOWN

    def update(self, ctx: EnemyContext, dt: float) -> None:
        if self.state == "enter":
            self.y = approach(self.y, self.stop_y, CFG.entrySpeed * dt)
            if self.y == self.stop_y:
                self.state = "drift"
        elif self.state == "drift":
            self._drift_for += dt
            self.x = self.center_x + CFG.drift * math.sin(
                (2 * math.pi * self._drift_for) / CFG.driftPeriod
            )
            if self._drift_for >= CFG.stay:
                self.state = "exit"
        else:
            self.y -= CFG.exitSpeed * dt
        if on_playfield(self, ctx):
            self._fire(ctx, dt)

    def _fire(self, ctx: EnemyContext, dt: float) -> None:
        _count = self._gun.tick(dt * ctx.fire_rate)
        for _i in range(_count):
            fire_aimed(
                ctx,
                self._muzzles,
                self,
                (CFG.spreadCount, CFG.spreadSpacing),
                bullet_shot(ctx, CFG.bullet),
            )
        self.charge = self._gun.progress

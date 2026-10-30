"""The Juggernaut (P05-R22)"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.jointed_enemy import JointedEnemy
from core.systems.enemy_motion import approach
from core.systems.gun_muzzles import GunMuzzles, fire_aimed
from game.config.enemies_elite import ELITE_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, Cadence, bullet_shot, on_playfield
from game.sim.joints import jointed_design

__pragma__("skip")
from core.entities.enemy import EnemyContext  # noqa: E402

__pragma__("noskip")

CFG = ELITE_CONFIG.juggernaut


class Juggernaut(JointedEnemy):
    """P05-R22: an armoured brute. It comes down slowly to the upper third, drifts left and right
    for 10 s, then leaves downward. Its two shoulder cannons swing to and fro (moving parts,
    P05-R13), each firing a burst of 3 bullets along its barrel every 1.6 s; its two front plates
    are parts too, and while one stands the core cannot be hit (a shield, as a boss's, P07-R01).
    The core's turret fires a spread of 7 bullets 9° apart centred on the player every 2.5 s.
    """

    def __init__(self, center_x: float, y: float, stop_y: float) -> None:
        super().__init__(center_x, y, CFG.stats, jointed_design(CFG.design))
        self.center_x = center_x
        self.stop_y = stop_y
        self.state = "enter"
        self._gun = Cadence(CFG.fireInterval, CFG.firstShot)
        self._muzzles = GunMuzzles(CFG.muzzles)
        self._cannons = Cadence(CFG.cannonInterval, CFG.firstBurst)
        # Bullets left in the cannons' burst, and seconds until the next one.
        self._burst_left = 0
        self._burst_clock = 0.0
        self._drift_for = 0.0
        self.heading = DOWN

    def act(self, ctx: EnemyContext, dt: float) -> None:
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
            self._fire(ctx, dt * ctx.fire_rate)

    def _fire(self, ctx: EnemyContext, dt: float) -> None:
        _count = self._gun.tick(dt)
        for _i in range(_count):
            fire_aimed(
                ctx,
                self._muzzles,
                self,
                (CFG.spreadCount, CFG.spreadSpacing),
                bullet_shot(ctx, CFG.bullet),
            )
        self.charge = self._gun.progress
        if self._cannons.tick(dt) > 0:
            self._burst_left = CFG.burstCount
            self._burst_clock = 0.0
        self._burst_clock -= dt
        while self._burst_left > 0 and self._burst_clock <= 0:
            self._fire_cannons(ctx)
            self._burst_left -= 1
            self._burst_clock += CFG.burstGap

    def _fire_cannons(self, ctx: EnemyContext) -> None:
        """Each standing shoulder cannon fires a bullet along its barrel."""
        for spec in CFG.cannons:
            cannon = self.part(spec.id)
            if cannon is None:
                continue
            point = ctx.seen(cannon.place(spec.muzzle))
            # Along the barrel as its joint is turned now (the part's heading is set after `act`).
            heading = self.heading + self.joints.angle(spec.joint)
            ctx.fire_bullet(point.x, point.y, heading, CFG.cannonBullet)

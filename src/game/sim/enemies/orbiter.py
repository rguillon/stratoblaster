"""The Orbiter (P05-R20)"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.jointed_enemy import JointedEnemy
from core.systems.enemy_motion import approach
from core.systems.gun_muzzles import GunMuzzles
from core.systems.projectile_motion import heading_to
from game.config.enemies_elite import ELITE_CONFIG
from game.sim.enemies.enemy_helpers import DEG, DOWN, Cadence, on_playfield

__pragma__("skip")
from core.entities.enemy import EnemyContext  # noqa: E402

__pragma__("noskip")

CFG = ELITE_CONFIG.orbiter


class Orbiter(JointedEnemy):
    """P05-R20: a spherical core with three armoured drones orbiting it (moving parts, P05-R13),
    close enough to catch the shots aimed at the core. It comes down to the upper half, stays 8 s,
    then leaves upward. Every 3 s the core fires a ring of 12 bullets from its equator; each drone
    fires a bullet aimed at the player every 2 s, in turn.
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        super().__init__(x, y, CFG.stats, CFG.design)
        self.stop_y = stop_y
        self.state = "enter"
        self._ring = Cadence(CFG.ringInterval, CFG.firstRing)
        self._ring_muzzles = GunMuzzles(CFG.ringMuzzles)
        self._drones = [Cadence(CFG.droneFireInterval, drone.firstShot) for drone in CFG.drones]
        self._stayed = 0.0
        self.heading = DOWN

    def act(self, ctx: EnemyContext, dt: float) -> None:
        self.spin += CFG.spin * DEG * dt
        if self.state == "enter":
            self.y = approach(self.y, self.stop_y, CFG.entrySpeed * dt)
            if self.y == self.stop_y:
                self.state = "stay"
        elif self.state == "stay":
            self._stayed += dt
            if self._stayed >= CFG.stay:
                self.state = "exit"
        else:
            self.y += CFG.exitSpeed * dt
        if on_playfield(self, ctx):
            self._fire(ctx, dt * ctx.fire_rate)

    def _fire(self, ctx: EnemyContext, dt: float) -> None:
        _count = self._ring.tick(dt)
        for _i in range(_count):
            for k in range(CFG.ringCount):
                heading = self.heading + (2 * math.pi * k) / CFG.ringCount
                point = self._ring_muzzles.along(ctx, self, heading)
                ctx.fire_bullet(point.x, point.y, heading, CFG.ringBullet)
        self.charge = self._ring.progress
        for i, spec in enumerate(CFG.drones):
            times = self._drones[i].tick(dt)
            drone = self.part(spec.id)
            if drone is None:
                continue
            for _k in range(times):
                point = ctx.seen(drone.place(spec.muzzle))
                aim = heading_to(point.x, point.y, ctx.player_x, ctx.player_y)
                ctx.fire_bullet(point.x, point.y, aim, CFG.droneBullet)

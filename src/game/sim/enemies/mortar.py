# Copyright (c) 2026 Renaud Guillon
"""The Mortar (`specs/enemies/mortar.md`)."""

from core.entities.enemy import Enemy, EnemyBulletSpec, EnemyBurstSpec, EnemyMissileSpec
from core.systems.gun_muzzles import GunMuzzles
from core.systems.projectile_motion import heading_to
from game.config.enemies_veteran import VETERAN_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, Cadence, missile_flight, on_playfield

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


CFG = VETERAN_CONFIG.mortar


def mortar_missile() -> EnemyMissileSpec:
    """Return the Mortar's missile of the config, with the ring it bursts into (ENM-MORTAR-09)."""
    missile = CFG.missile
    burst = missile.burst
    ring = burst.bullet
    return EnemyMissileSpec(
        missile.speed,
        missile.turnRateDeg,
        missile.homingSeconds,
        missile.radius,
        missile.health,
        missile.style,
        EnemyBurstSpec(
            burst.after, burst.count, EnemyBulletSpec(ring.speed, ring.radius, ring.style)
        ),
        missile_flight(False),
    )


class Mortar(Enemy):
    """ENM-MORTAR-07: tier 3's missile launcher, a squat gunship descending slowly.

    Every 3.5 s it launches a slow, heavy homing missile from its launcher tube, first towards the
    player (ENM-MORTAR-08). The missile can be shot down; when its fuse is out, 2.5 s after launch,
    it bursts into a ring of 10 bullets (ENM-MORTAR-09). Its `charge` lights its charge light
    (ENM-MORTAR-04).
    """

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self._gun = Cadence(CFG.fireInterval, CFG.firstShot)
        self._muzzles = GunMuzzles(CFG.muzzles)
        self._missile = mortar_missile()
        self.heading = DOWN

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        self.y -= CFG.speed * dt
        if not on_playfield(self, ctx):
            return
        _count = self._gun.tick(dt * ctx.fire_rate)
        for _i in range(_count):
            aim = heading_to(self.x, self.y, ctx.player_x, ctx.player_y)
            point = self._muzzles.along(ctx, self, aim)
            ctx.fire_missile(
                point.x,
                point.y,
                heading_to(point.x, point.y, ctx.player_x, ctx.player_y),
                self._missile,
            )
        self.charge = self._gun.progress

# Copyright (c) 2026 Renaud Guillon
"""The Scout (`specs/enemies/scout.md`)."""

from core.entities.boss_turret import BossTurret, BossTurretSpec
from core.entities.enemy import Enemy
from core.systems.gun_muzzles import GunMuzzles
from core.systems.projectile_motion import heading_to, turn_towards
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.enemy_helpers import DEG, DOWN, Cadence, on_playfield

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


CFG = ENEMY_CONFIG.scout


class Scout(Enemy):
    """ENM-SCOUT-05: flies straight down slowly and fires aimed bullets at the player.

    One bullet every 1.5 s (ENM-SCOUT-06, ENM-20), from its nose gun while it is over the playfield.
    The gun turns on a pivot to point at the player (WPN-02) and a due shot waits until it does; the
    bullet leaves along the barrel (WPN-01).
    """

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self._gun = Cadence(CFG.fireInterval, CFG.firstShot)
        self._muzzles = GunMuzzles(CFG.muzzles, True)
        self.barrels = self._muzzles.barrels
        self.turret = BossTurret(BossTurretSpec(CFG.turret.x, CFG.turret.y, CFG.turret.turnDeg))
        # Shots due that wait for the gun to point at the player.
        self._due = 0
        self._ctx: EnemyContext | None = None
        self.heading = DOWN

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        self.y -= CFG.speed * dt
        if not on_playfield(self, ctx):
            return
        self._ctx = ctx
        self._due += self._gun.tick(dt * ctx.fire_rate)
        self._turn_gun(ctx, dt)
        if self._due > 0:
            aim = heading_to(self.x, self.y, ctx.player_x, ctx.player_y)
            if self._muzzles.shoot(ctx, self, aim, self._fire):
                self._due -= 1
        self.charge = self._gun.progress

    def _turn_gun(self, ctx: EnemyContext, dt: float) -> None:
        """Turn the gun towards the player, at its turn rate, from the nose (DOWN)."""
        turret = self.turret
        if turret is None:
            return
        aim = heading_to(self.x, self.y, ctx.player_x, ctx.player_y) - self.heading
        turret.aim = turn_towards(turret.aim, aim, turret.spec.turn_rate_deg * DEG * dt)

    def _fire(self, x: float, y: float, heading: float) -> None:
        """Fire a bullet from the barrel's tip, along the barrel (WPN-01)."""
        if self._ctx is not None:
            self._ctx.fire_bullet(x, y, heading, CFG.bullet)

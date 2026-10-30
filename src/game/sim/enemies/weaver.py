"""The Weaver (P05-R05)"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import Enemy
from core.systems.gun_muzzles import GunMuzzles, fire_aimed
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.enemy_helpers import Cadence, bullet_shot, on_playfield

__pragma__("skip")
from core.entities.enemy import EnemyContext  # noqa: E402

__pragma__("noskip")

CFG = ENEMY_CONFIG.weaver


class Weaver(Enemy):
    """P05-R05: moves down along a sine wave: its X is a sine of the distance it has come down.
    Every 2 s it fires a pair of bullets aimed at the player, one from each hull.
    """

    def __init__(self, center_x: float, y: float) -> None:
        super().__init__(center_x, y, CFG.stats)
        self.center_x = center_x
        self._gun = Cadence(CFG.fireInterval, CFG.fireInterval / 2)
        # One gun per hull, each firing its own bullet.
        self._hulls = [GunMuzzles([muzzle]) for muzzle in CFG.muzzles]
        self._start_y = y

    @staticmethod
    def sway_at(center_x: float, down: float) -> float:
        """X at a distance `down` below the start."""
        x: float = center_x + CFG.amplitude * math.sin((2 * math.pi * down) / CFG.wavelength)
        return x

    def update(self, ctx: EnemyContext, dt: float) -> None:
        before = self.x
        self.y -= CFG.speed * dt
        self.x = Weaver.sway_at(self.center_x, self._start_y - self.y)
        self.heading = math.atan2(self.x - before, -CFG.speed * dt)
        if not on_playfield(self, ctx):
            return
        _count = self._gun.tick(dt * ctx.fire_rate)
        for _i in range(_count):
            for hull in self._hulls:
                fire_aimed(ctx, hull, self, (1, 0), bullet_shot(ctx, CFG.bullet))
        self.charge = self._gun.progress

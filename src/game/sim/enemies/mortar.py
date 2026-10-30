"""The Mortar (P05-R15), ported from `game/sim/enemies/mortar.ts`."""

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import Enemy
from core.systems.gun_muzzles import GunMuzzles, fire_aimed
from game.config.enemies_veteran import VETERAN_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, Cadence, bullet_shot, on_playfield

__pragma__("skip")
from core.entities.enemy import EnemyContext  # noqa: E402

__pragma__("noskip")

CFG = VETERAN_CONFIG.mortar


class Mortar(Enemy):
    """P05-R15: a squat gunship descending slowly. Every 2.5 s it lobs a big, slow shell aimed at
    the player (GD-44) from its barrel; 1.2 s later the shell bursts into a ring of 8 bullets (a
    bursting bullet, `EnemyBulletSpec.burst`).
    """

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self._gun = Cadence(CFG.fireInterval, CFG.firstShot)
        self._muzzles = GunMuzzles(CFG.muzzles)
        self.heading = DOWN

    def update(self, ctx: EnemyContext, dt: float) -> None:
        self.y -= CFG.speed * dt
        if not on_playfield(self, ctx):
            return
        _count = self._gun.tick(dt * ctx.fire_rate)
        for _i in range(_count):
            fire_aimed(ctx, self._muzzles, self, (1, 0), bullet_shot(ctx, CFG.shell))
        self.charge = self._gun.progress

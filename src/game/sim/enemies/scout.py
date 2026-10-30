"""The Scout (P05-R03)"""

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import Enemy
from core.systems.gun_muzzles import GunMuzzles, fire_aimed
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, Cadence, bullet_shot, on_playfield

__pragma__("skip")
from core.entities.enemy import EnemyContext  # noqa: E402

__pragma__("noskip")

CFG = ENEMY_CONFIG.scout


class Scout(Enemy):
    """P05-R03: flies straight down slowly and fires one bullet aimed at the player every 1.5 s
    (GD-44) from its nose gun while it is over the playfield.
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
            fire_aimed(ctx, self._muzzles, self, (1, 0), bullet_shot(ctx, CFG.bullet))
        self.charge = self._gun.progress

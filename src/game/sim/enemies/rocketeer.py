"""The Rocketeer (P05-R08), ported from `game/sim/enemies/rocketeer.ts`."""

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import Enemy
from core.systems.gun_muzzles import GunMuzzles
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, Cadence, on_playfield

__pragma__("skip")
from core.entities.enemy import EnemyContext  # noqa: E402

__pragma__("noskip")

CFG = ENEMY_CONFIG.rocketeer


class Rocketeer(Enemy):
    """P05-R08: descends slowly and every 3 s launches one missile from each side pod. The missiles
    turn towards the player at a limited rate and can be shot down (GD-43). Its `charge` is how far
    the pods are reloaded (the tips glow when loaded).
    """

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self._launcher = Cadence(CFG.fireInterval, CFG.firstShot)
        self._pods = [GunMuzzles([muzzle]) for muzzle in CFG.muzzles]
        self.heading = DOWN
        self.charge = 1

    def update(self, ctx: EnemyContext, dt: float) -> None:
        self.y -= CFG.speed * dt
        if not on_playfield(self, ctx):
            return
        _count = self._launcher.tick(dt * ctx.fire_rate)
        for _i in range(_count):
            for pod in self._pods:
                point = pod.along(ctx, self, DOWN)
                ctx.fire_missile(point.x, point.y, DOWN, CFG.missile)
        self.charge = self._launcher.progress

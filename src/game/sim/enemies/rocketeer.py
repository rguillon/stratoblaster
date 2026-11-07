# Copyright (c) 2026 Renaud Guillon
"""The Rocketeer (`specs/enemies/rocketeer.md`)."""

from core.entities.enemy import Enemy
from core.systems.gun_muzzles import GunMuzzles
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, Cadence, missile_spec, on_playfield

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


CFG = ENEMY_CONFIG.rocketeer


class Rocketeer(Enemy):
    """ENM-ROCKETEER-05: descends slowly and launches missiles from its side pods.

    Every 3 s it launches one missile from each side pod (ENM-ROCKETEER-06). The missiles turn
    towards the player at a limited rate (ENM-ROCKETEER-07) and can be shot down (ENM-18). Its
    `charge` is how far the pods are reloaded (the tips glow when loaded, ENM-ROCKETEER-02).
    """

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self._launcher = Cadence(CFG.fireInterval, CFG.firstShot)
        self._pods = [GunMuzzles([muzzle]) for muzzle in CFG.muzzles]
        # Each pod's port, kicked as its missile leaves (WPN-07).
        self.launchers = [pod.barrels[0] for pod in self._pods]
        self.heading = DOWN
        self.charge = 1

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        self.y -= CFG.speed * dt
        if not on_playfield(self, ctx):
            return
        _count = self._launcher.tick(dt * ctx.fire_rate)
        for _i in range(_count):
            for pod in self._pods:
                point = pod.along(ctx, self, DOWN)
                ctx.fire_missile(point.x, point.y, DOWN, missile_spec(CFG.missile))
        self.charge = self._launcher.progress

# Copyright (c) 2026 Renaud Guillon
"""The Splitter (`specs/enemies/splitter.md`)."""

import math

from core.entities.enemy import Enemy
from core.systems.enemy_motion import Path
from core.systems.gun_muzzles import GunMuzzles, fire_aimed
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.enemy_helpers import Cadence, bullet_shot, on_playfield
from game.sim.enemies.hornet import Hornet, hornet_options

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


CFG = ENEMY_CONFIG.splitter
POD = ENEMY_CONFIG.splitterPod


class Splitter(Enemy):
    """ENM-SPLITTER-05: flies down a predefined curved path.

    It fires one aimed bullet every 2.5 s (ENM-SPLITTER-06). When it is destroyed its three pods
    break off (ENM-SPLITTER-07), and each dives at the player like a small Hornet (ENM-SPLITTER-08).
    """

    def __init__(self, path: Path) -> None:
        start = path.at(0)
        super().__init__(start.x, start.y, CFG.stats)
        self.path = path
        self._gun = Cadence(CFG.fireInterval, CFG.firstShot)
        self._muzzles = GunMuzzles(CFG.muzzles)
        self._travelled = 0.0
        self.heading = start.heading

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        self._travelled += CFG.speed * dt
        pose = self.path.at(self._travelled)
        self.x = pose.x
        self.y = pose.y
        self.heading = pose.heading
        if self._travelled >= self.path.length:
            self.gone = True
        if not on_playfield(self, ctx):
            return
        _count = self._gun.tick(dt * ctx.fire_rate)
        for _i in range(_count):
            fire_aimed(ctx, self._muzzles, self, (1, 0), bullet_shot(ctx, CFG.bullet))
        self.charge = self._gun.progress

    def on_destroyed(self, ctx: EnemyContext) -> None:
        """Spawn the three pods, 120° apart around the core, each facing outwards."""
        for i in range(3):
            heading = self.heading + (2 * math.pi * i) / 3
            x = self.x + math.sin(heading) * CFG.podOffset
            y = self.y + math.cos(heading) * CFG.podOffset
            pod = Hornet(x, y, hornet_options(POD, None))
            pod.heading = heading
            ctx.spawn(pod)

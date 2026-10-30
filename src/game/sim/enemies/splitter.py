"""The Splitter (P05-R10)"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import Enemy
from core.systems.enemy_motion import Path
from core.systems.gun_muzzles import GunMuzzles, fire_aimed
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.enemy_helpers import Cadence, bullet_shot, on_playfield
from game.sim.enemies.hornet import Hornet, hornet_options

__pragma__("skip")
from core.entities.enemy import EnemyContext  # noqa: E402

__pragma__("noskip")

CFG = ENEMY_CONFIG.splitter
POD = ENEMY_CONFIG.splitterPod


class Splitter(Enemy):
    """P05-R10: flies down a predefined curved path and fires one aimed bullet every 2.5 s. When it
    is destroyed its three pods break off, and each dives at the player like a small Hornet.
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
        """The three pods, 120° apart around the core, each facing outwards."""
        for i in range(3):
            heading = self.heading + (2 * math.pi * i) / 3
            x = self.x + math.sin(heading) * CFG.podOffset
            y = self.y + math.cos(heading) * CFG.podOffset
            pod = Hornet(x, y, hornet_options(POD, None))
            pod.heading = heading
            ctx.spawn(pod)

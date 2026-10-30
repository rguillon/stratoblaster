"""The Gnat (P05-R01)"""

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import Enemy
from core.systems.enemy_motion import Path
from game.config.enemies import ENEMY_CONFIG

__pragma__("skip")
from core.entities.enemy import EnemyContext  # noqa: E402

__pragma__("noskip")

CFG = ENEMY_CONFIG.gnat


class Gnat(Enemy):
    """P05-R01: a small swarm drone. It waits `delay` seconds, then follows its group's predefined
    S-shaped path at a constant speed, from the top of the screen to the bottom. It does not shoot.
    """

    def __init__(self, path: Path, delay: float) -> None:
        start = path.at(0)
        super().__init__(start.x, start.y, CFG.stats)
        self.path = path
        self.delay = delay
        self._travelled = 0.0
        self.heading = start.heading

    def update(self, _ctx: EnemyContext, dt: float) -> None:
        if self.age <= self.delay:
            return
        self._travelled += CFG.speed * dt
        pose = self.path.at(self._travelled)
        self.x = pose.x
        self.y = pose.y
        self.heading = pose.heading
        if self._travelled >= self.path.length:
            self.gone = True

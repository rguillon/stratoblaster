# Copyright (c) 2026 Renaud Guillon
"""The Splitter (`specs/enemies/splitter.md`)."""

import math

from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.hornet import Hornet, hornet_options

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


CFG = ENEMY_CONFIG.splitter
POD = ENEMY_CONFIG.splitterPod


class Splitter(Hornet):
    """ENM-SPLITTER-05: tier 4's diver, a bigger and tougher Hornet that never shoots.

    It comes in from the top, brakes in the upper half, turns its nose to the player and dives at
    where the player was (ENM-SPLITTER-06). It has the Hornet's stats of its own (ENM-SPLITTER-09).
    When it is destroyed its three pods break off (ENM-SPLITTER-07), and each dives at the player
    like a small Hornet (ENM-SPLITTER-08). The Hive launches them mid-screen (ENM-HIVE-09).
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        """Comes in from (x, y) flying down to `stop_y`; at or below it, it starts aiming."""
        super().__init__(x, y, hornet_options(CFG, min(stop_y, y)))

    def on_destroyed(self, ctx: EnemyContext) -> None:
        """Spawn the three pods, 120° apart around the core, each facing outwards."""
        for i in range(3):
            heading = self.heading + (2 * math.pi * i) / 3
            x = self.x + math.sin(heading) * CFG.podOffset
            y = self.y + math.cos(heading) * CFG.podOffset
            pod = Hornet(x, y, hornet_options(POD, None))
            pod.heading = heading
            ctx.spawn(pod)

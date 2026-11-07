# Copyright (c) 2026 Renaud Guillon
"""The Hydra (`specs/enemies/hydra.md`)."""

from core.entities.barrel import Barrel
from core.entities.jointed_enemy import JointedEnemy
from core.systems.enemy_motion import approach
from game.config.enemies_elite import ELITE_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, Cadence, on_playfield
from game.sim.joints import jointed_design

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


CFG = ELITE_CONFIG.hydra


class Hydra(JointedEnemy):
    """ENM-HYDRA-07: a broad hull with three long necks swaying out of step.

    Its necks are moving parts (ENM-HYDRA-08, ENM-27). It comes down to the upper third, stays 7 s,
    then leaves downward. As tier 4's shooter its heads fire in turn, one every 0.8 s, each a
    burst of bullets from the gun on its brow, along the head (ENM-HYDRA-09, WPN-01); with
    every head gone it no longer fires, but its hull can still be destroyed (ENM-HYDRA-10). Its
    necks and heads come from its config, as the engine's specs (ENM-HYDRA-12).
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        super().__init__(x, y, CFG.stats, jointed_design(CFG.design))
        self.stop_y = stop_y
        self.state = "enter"
        self._heads = Cadence(CFG.headFireInterval, CFG.firstShot)
        # Index of the head whose turn it is.
        self._next = 0
        # The head firing its burst, the bullets left in it, and seconds to the next.
        self._firing: int | None = None
        self._burst_left = 0
        self._burst_clock = 0.0
        # One gun per head, in the order of the heads: each recoils as it fires (WPN-03).
        self.barrels = [Barrel(list(h.muzzle)) for h in CFG.heads]
        self._stayed = 0.0
        self.heading = DOWN

    def act(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        if self.state == "enter":
            self.y = approach(self.y, self.stop_y, CFG.entrySpeed * dt)
            if self.y == self.stop_y:
                self.state = "stay"
        elif self.state == "stay":
            self._stayed += dt
            if self._stayed >= CFG.stay:
                self.state = "exit"
        else:
            self.y -= CFG.exitSpeed * dt
        if on_playfield(self, ctx):
            self._fire(ctx, dt)

    def _fire(self, ctx: EnemyContext, dt: float) -> None:
        dt *= ctx.fire_rate
        if self._heads.tick(dt) > 0 and self._firing is None:
            self._firing = self._next_head()
            self._burst_left = CFG.burstCount
            self._burst_clock = 0.0
        self._burst_clock -= dt
        while self._firing is not None and self._burst_left > 0 and self._burst_clock <= 0:
            self._fire_head(ctx, self._firing)
            self._burst_left -= 1
            self._burst_clock += CFG.burstGap
        if self._burst_left <= 0:
            self._firing = None
        self.charge = self._heads.progress

    def _next_head(self) -> int | None:
        """Return the next living head in turn (left, middle, right), None when none is left."""
        heads = CFG.heads
        for k in range(len(heads)):
            index = (self._next + k) % len(heads)
            if self.part(heads[index].id) is not None:
                self._next = index + 1
                return index
        return None

    def _fire_head(self, ctx: EnemyContext, index: int) -> None:
        """Fire a bullet from a head's gun tip, along the head as its neck is turned now."""
        spec = CFG.heads[index]
        head = self.part(spec.id)
        if head is None:
            return
        point = ctx.seen(head.place(spec.muzzle))
        heading = self.heading + spec.aim + self.joints.angle(spec.joint)
        self.barrels[index].kick(self.age)
        ctx.fire_bullet(point.x, point.y, heading, CFG.bullet)

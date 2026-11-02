# Copyright (c) 2026 Renaud Guillon
"""The Hydra (`specs/enemies/hydra.md`)."""

from core.entities.jointed_enemy import JointedEnemy
from core.systems.enemy_motion import approach
from core.systems.projectile_motion import heading_to
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
    then leaves downward. Its heads fire in turn, one every 0.5 s, each a bullet aimed at the player
    from its eye (ENM-HYDRA-09); with every head gone it no longer fires, but its hull can still be
    destroyed (ENM-HYDRA-10). Its necks and heads come from its config, as the engine's specs
    (ENM-HYDRA-12).
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        super().__init__(x, y, CFG.stats, jointed_design(CFG.design))
        self.stop_y = stop_y
        self.state = "enter"
        self._heads = Cadence(CFG.headFireInterval, CFG.firstShot)
        # Index of the head whose turn it is.
        self._next = 0
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
        _count = self._heads.tick(dt * ctx.fire_rate)
        for _i in range(_count):
            self._fire_next_head(ctx)
        self.charge = self._heads.progress

    def _fire_next_head(self, ctx: EnemyContext) -> None:
        """Fire a bullet at the player from the eye of the next living head in turn."""
        heads = CFG.heads
        for k in range(len(heads)):
            index = (self._next + k) % len(heads)
            spec = heads[index]
            head = self.part(spec.id)
            if head is None:
                continue
            self._next = index + 1
            point = ctx.seen(head.place(spec.muzzle))
            aim = heading_to(point.x, point.y, ctx.player_x, ctx.player_y)
            ctx.fire_bullet(point.x, point.y, aim, CFG.bullet)
            return

"""The Hydra (P05-R19), ported from `game/sim/enemies/hydra.ts`."""

from org.transcrypt.stubs.browser import __pragma__

from core.entities.jointed_enemy import JointedEnemy
from core.systems.enemy_motion import approach
from core.systems.projectile_motion import heading_to
from game.config.enemies_elite import ELITE_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, Cadence, on_playfield

__pragma__("skip")
from core.entities.enemy import EnemyContext  # noqa: E402

__pragma__("noskip")

CFG = ELITE_CONFIG.hydra


class Hydra(JointedEnemy):
    """P05-R19: a broad hull with three long necks swaying out of step (moving parts, P05-R13). It
    comes down to the upper third, stays 7 s, then leaves downward. Its heads fire in turn, one
    every 0.5 s, each a bullet aimed at the player from its eye; with every head gone it no longer
    fires, but its hull can still be destroyed.
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        super().__init__(x, y, CFG.stats, CFG.design)
        self.stop_y = stop_y
        self.state = "enter"
        self._heads = Cadence(CFG.headFireInterval, CFG.firstShot)
        # Index of the head whose turn it is.
        self._next = 0
        self._stayed = 0.0
        self.heading = DOWN

    def act(self, ctx: EnemyContext, dt: float) -> None:
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
        """The next living head in turn fires a bullet at the player from its eye."""
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

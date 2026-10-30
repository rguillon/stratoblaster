"""The Wasp (P05-R14), ported from `game/sim/enemies/wasp.ts`."""

from org.transcrypt.stubs.browser import __pragma__

from core.systems.gun_muzzles import GunMuzzles, fire_aimed
from game.config.enemies_veteran import VETERAN_CONFIG
from game.sim.enemies.enemy_helpers import bullet_shot, on_playfield
from game.sim.enemies.hornet import Hornet, hornet_options

__pragma__("skip")
from core.entities.enemy import EnemyContext  # noqa: E402

__pragma__("noskip")

CFG = VETERAN_CONFIG.wasp


class Wasp(Hornet):
    """P05-R14: an armed diver. It flies down to its stop height, pauses 0.4 s turning its nose to
    the player, fires a fan of 3 bullets 12° apart aimed at the player (GD-44) once, then dives at
    where the player was at that moment, like a Hornet (P05-R02). The Hive launches them too
    (P05-R23).
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        """Comes in from (x, y) flying down to `stop_y`, pauses turning to the player, fires its
        aimed fan of 3, then dives. Already at or below `stop_y`, it starts with the pause.
        """
        super().__init__(x, y, hornet_options(CFG, min(stop_y, y)))
        self._muzzles = GunMuzzles(CFG.muzzles)

    def update(self, ctx: EnemyContext, dt: float) -> None:
        aiming = self.state == "aim"
        Hornet.update(self, ctx, dt)
        # The pause just ended: the dive heading is the player's direction now.
        if aiming and self.state == "dive":
            self._fire(ctx)

    def _fire(self, ctx: EnemyContext) -> None:
        if not on_playfield(self, ctx):
            return
        fire_aimed(
            ctx,
            self._muzzles,
            self,
            (CFG.fanCount, CFG.fanSpacing),
            bullet_shot(ctx, CFG.bullet),
        )

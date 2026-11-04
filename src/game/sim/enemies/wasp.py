# Copyright (c) 2026 Renaud Guillon
"""The Wasp (`specs/enemies/wasp.md`)."""

from core.systems.gun_muzzles import GunMuzzles, fire_aimed
from game.config.enemies_veteran import VETERAN_CONFIG
from game.sim.enemies.enemy_helpers import bullet_shot, on_playfield
from game.sim.enemies.hornet import Hornet, hornet_options

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


CFG = VETERAN_CONFIG.wasp


class Wasp(Hornet):
    """ENM-WASP-08: an armed diver.

    It flies down to its stop height, pauses 0.4 s turning its nose to the player, fires a fan of 3
    bullets 12° apart aimed at the player once (ENM-WASP-09, ENM-20), then dives at where the player
    was at that moment, like a Hornet (ENM-WASP-10).
    """

    def __init__(self, x: float, y: float, stop_y: float, stop_x: float | None = None) -> None:
        """Comes in from (x, y) flying down to `stop_y`, pauses turning to the player.

        With `stop_x` it flies in a straight line to (`stop_x`, `stop_y`), as from a side.

        Fires its aimed fan of 3, then dives. Already at or below `stop_y`, it starts with the
        pause.
        """
        super().__init__(x, y, hornet_options(CFG, min(stop_y, y), stop_x))
        self._muzzles = GunMuzzles(CFG.muzzles)

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
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

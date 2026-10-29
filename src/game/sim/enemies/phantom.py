"""The Phantom (P05-R17), ported from `game/sim/enemies/phantom.ts`."""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import Enemy
from core.systems.enemy_motion import approach
from core.systems.gun_muzzles import GunMuzzles, fire_aimed
from core.systems.projectile_motion import heading_to
from game.config.enemies_veteran import VETERAN_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, bullet_shot, range_in

__pragma__("skip")
from core.entities.enemy import EnemyContext  # noqa: E402
from core.entities.shot_target import ShotTarget  # noqa: E402

__pragma__("noskip")

CFG = VETERAN_CONFIG.phantom

# Slowest speed while braking to its first place, px/s.
CREEP = 25
# Tries at finding a place far enough from the last one.
TRIES = 8


class Phantom(Enemy):
    """P05-R17: a cloaker. It comes in from the top to a place in the upper half, then three times:
    fades out over 0.4 s, stays invisible for 0.8 s, reappears at another place in the upper half
    (fading in over 0.4 s, its nose to the player) and fires a spread of 5 bullets 12° apart
    centred on the player (GD-44). Then it leaves upward. While it is faded out (less than half
    visible), shots pass through it and it cannot ram the player.
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self.stop_y = stop_y
        # What it is doing: enter, hold, fadeOut, hidden, fadeIn or exit.
        self.state = "enter"
        # How visible it is, 0 (gone) to 1, for the model.
        self.opacity = 1.0
        # Reappearances so far.
        self.jumps = 0
        self._muzzles = GunMuzzles(CFG.muzzles)
        self._timer = 0.0
        self.heading = DOWN

    @property
    def cloaked(self) -> bool:
        """Whether shots pass through it and it cannot ram the player."""
        cloaked: bool = self.opacity < CFG.solidOpacity
        return cloaked

    def _hit_targets(self) -> list[ShotTarget]:
        """Nothing to hit while it is cloaked."""
        if self.cloaked:
            return []
        return super()._hit_targets()

    def update(self, ctx: EnemyContext, dt: float) -> None:
        self._timer += dt
        if self.state == "enter":
            self._enter(dt)
        elif self.state == "hold":
            # Its attacks come faster with the level's fire rate (P06-R08).
            self._after(CFG.hold / ctx.fire_rate, "fadeOut" if self.jumps < CFG.jumps else "exit")
        elif self.state == "fadeOut":
            self.opacity = max(0, 1 - self._timer / CFG.fade)
            self._after(CFG.fade, "hidden")
        elif self.state == "hidden":
            if self._timer >= CFG.hidden:
                self._reappear(ctx)
        elif self.state == "fadeIn":
            self.opacity = min(1, self._timer / CFG.fade)
            self.charge = self.opacity
            if self._timer >= CFG.fade:
                self._fire(ctx)
        else:
            self.y += CFG.exitSpeed * dt

    def _enter(self, dt: float) -> None:
        left = self.y - self.stop_y
        speed = max(CREEP, CFG.entrySpeed * min(1, left / CFG.brakeDistance))
        self.y = approach(self.y, self.stop_y, speed * dt)
        if self.y == self.stop_y:
            self._go("hold")

    def _after(self, seconds: float, next_state: str) -> None:
        """Goes on to `next_state` once `seconds` have passed in this state."""
        if self._timer >= seconds:
            self._go(next_state)

    def _go(self, state: str) -> None:
        self.state = state
        self._timer = 0.0

    def _pick_place(self, ctx: EnemyContext) -> tuple[float, float]:
        return (
            range_in(ctx.random, CFG.placeX) * ctx.width,
            range_in(ctx.random, CFG.placeY) * ctx.height,
        )

    def _reappear(self, ctx: EnemyContext) -> None:
        """Moves, unseen, to another place in the upper half, and starts fading in there."""
        place = self._pick_place(ctx)
        tries = 1
        while tries < TRIES and self._too_near(place):
            place = self._pick_place(ctx)
            tries += 1
        self.x = place[0]
        self.y = place[1]
        self.heading = heading_to(self.x, self.y, ctx.player_x, ctx.player_y)
        self._go("fadeIn")

    def _too_near(self, place: tuple[float, float]) -> bool:
        near: bool = math.hypot(place[0] - self.x, place[1] - self.y) < CFG.jumpDistance
        return near

    def _fire(self, ctx: EnemyContext) -> None:
        self.opacity = 1
        self.charge = 0
        self.jumps += 1
        fire_aimed(
            ctx,
            self._muzzles,
            self,
            (CFG.spreadCount, CFG.spreadSpacing),
            bullet_shot(ctx, CFG.bullet),
        )
        self._go("hold")

# Copyright (c) 2026 Renaud Guillon
"""The Phantom (`specs/enemies/phantom.md`)."""

import math

from core.entities.enemy import Enemy
from core.systems.enemy_motion import approach
from core.systems.gun_muzzles import GunMuzzles, fire_aimed
from core.systems.projectile_motion import heading_to, turn_towards, wrap_angle
from game.config.enemies_veteran import VETERAN_CONFIG
from game.sim.enemies.enemy_helpers import DOWN, bullet_shot, range_in

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext
from core.entities.shot_target import ShotTarget

# __pragma__ ("noskip")


CFG = VETERAN_CONFIG.phantom

# Slowest speed while braking to its first place, px/s.
CREEP = 25
# Tries at finding a place far enough from the last one.
TRIES = 8
# How fast the nose eases in on the player: turn rate per radian left to turn, per second.
TURN_EASE = 14


class Phantom(Enemy):
    """ENM-PHANTOM-08: tier 3's diver, a cloaker.

    It comes in from where it is launched to a place in the upper half, then twice (ENM-PHANTOM-09):
    fades out over 0.4 s, stays invisible for 0.8 s and reappears at another place in the upper half
    (fading in over 0.4 s, its nose to the player). After the first jump it fires a spread of 5
    bullets 12 degrees apart centred on the player (ENM-PHANTOM-10, ENM-20). After the last it turns
    its nose to the player for 0.5 s, then dives in a straight line at where the player was,
    accelerating from rest, and leaves at the bottom of the screen (ENM-PHANTOM-11). While it is
    faded out (less than half visible), shots pass through it and it cannot ram the player
    (ENM-PHANTOM-12). A Broodmother launches it with the same constructor (ENM-PHANTOM-08).
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self.stop_y = stop_y
        # What it is doing: enter, hold, fadeOut, hidden, fadeIn, aim or dive.
        self.state = "enter"
        # How visible it is, 0 (gone) to 1, for the model, which fades with it (ENM-PHANTOM-06).
        self.opacity = 1.0
        # Reappearances so far.
        self.jumps = 0
        # Direction of the dive, fixed at the end of the aim; None before.
        self.dive_heading: float | None = None
        self._muzzles = GunMuzzles(CFG.muzzles)
        self._timer = 0.0
        self._speed = 0.0
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
        """Advance the enemy by `dt` seconds."""
        self._timer += dt
        if self.state == "enter":
            self._enter(dt)
        elif self.state == "hold":
            # Its attacks come faster with the level's fire rate (ENM-22).
            self._after(CFG.hold / ctx.fire_rate, "fadeOut")
        elif self.state == "fadeOut":
            self.opacity = max(0, 1 - self._timer / CFG.fade)
            self._after(CFG.fade, "hidden")
        elif self.state == "hidden":
            if self._timer >= CFG.hidden:
                self._reappear(ctx)
        elif self.state == "fadeIn":
            self.opacity = min(1, self._timer / CFG.fade)
            # Its charge light follows the fade-in (ENM-PHANTOM-04).
            self.charge = self.opacity
            if self._timer >= CFG.fade:
                self._faded_in(ctx)
        elif self.state == "aim":
            self._aim(ctx, dt)
        else:
            self._dive(dt)

    def _enter(self, dt: float) -> None:
        left = abs(self.y - self.stop_y)
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
        """Move, unseen, to another place in the upper half, and start fading in there."""
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

    def _faded_in(self, ctx: EnemyContext) -> None:
        """Fully visible again: the first time it fires its spread; after the last jump it dives."""
        self.opacity = 1
        self.charge = 0
        self.jumps += 1
        if self.jumps == CFG.spreadJump:
            fire_aimed(
                ctx,
                self._muzzles,
                self,
                (CFG.spreadCount, CFG.spreadSpacing),
                bullet_shot(ctx, CFG.bullet),
            )
        self._go("hold" if self.jumps < CFG.jumps else "aim")

    def _aim(self, ctx: EnemyContext, dt: float) -> None:
        """Turn the nose to the player, then lock the dive at where it is (ENM-PHANTOM-11)."""
        target = heading_to(self.x, self.y, ctx.player_x, ctx.player_y)
        left = abs(wrap_angle(target - self.heading))
        # Fast enough to turn all the way round during the pause, slowing down near the end.
        rate = min(math.pi / CFG.pause, TURN_EASE * left)
        self.heading = turn_towards(self.heading, target, rate * dt)
        self.charge = min(1, self._timer / CFG.pause)
        if self._timer >= CFG.pause:
            self.dive_heading = target
            self.heading = target
            self.charge = 0
            self._go("dive")

    def _dive(self, dt: float) -> None:
        self._speed = min(CFG.diveMaxSpeed, self._speed + CFG.diveAcceleration * dt)
        self.x += math.sin(self.heading) * self._speed * dt
        self.y += math.cos(self.heading) * self._speed * dt

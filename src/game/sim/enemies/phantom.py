# Copyright (c) 2026 Renaud Guillon
"""The Phantom (`specs/enemies/phantom.md`)."""

import math

from core.entities.enemy import Enemy
from core.systems.gun_muzzles import GunMuzzles, fire_aimed
from core.systems.projectile_motion import heading_to, turn_towards, wrap_angle
from game.config.enemies_veteran import VETERAN_CONFIG
from game.sim.enemies.enemy_helpers import DEG, DOWN, bullet_shot, range_in

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


CFG = VETERAN_CONFIG.phantom

# Slowest speed while braking into a place, px/s, so that it always gets there.
CREEP = 12
# Tries at finding a place far enough from the last one.
TRIES = 8
# How fast the nose eases in on the player: turn rate per radian left to turn, per second.
TURN_EASE = 14


class Phantom(Enemy):
    """ENM-PHANTOM-08: tier 3's diver, a flying wing that strikes from place to place.

    It flies in from where it is launched to a place in the upper half, braking into it, turns its
    nose to the player and fires a spread of 5 bullets 12 degrees apart centred on the player
    (ENM-PHANTOM-10, ENM-20); it holds a moment, then flies to another place in the upper half
    (speeding up, its nose along its way, then braking into it and turning back to the player) and
    fires again, `stops` times in all (ENM-PHANTOM-09). After its last spread it turns its nose to
    the player for 0.5 s, then dives in a straight line at where the player was, accelerating from
    rest, and leaves at the bottom of the screen (ENM-PHANTOM-11). It no longer cloaks. A
    Broodmother launches it with the same constructor (ENM-PHANTOM-08).
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        super().__init__(x, y, CFG.stats)
        # Where it flies to next.
        self.target_x = x
        self.target_y = stop_y
        # What it is doing: fly, aim, hold, lock (its last aim, before the dive) or dive.
        self.state = "fly"
        # Places it still has to fire from.
        self.stops_left = CFG.stops
        # Direction of the dive, fixed at the end of the lock; None before.
        self.dive_heading: float | None = None
        self._muzzles = GunMuzzles(CFG.muzzles)
        self.barrels = self._muzzles.barrels
        self._timer = 0.0
        self._speed = float(CFG.entrySpeed)
        self.heading = DOWN

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        self._timer += dt
        if self.state == "fly":
            self._fly(ctx, dt)
        elif self.state == "aim":
            self._aim(ctx, dt)
        elif self.state == "hold":
            # Its attacks come faster with the level's fire rate (ENM-22).
            if self._timer >= CFG.hold / ctx.fire_rate:
                self._next(ctx)
        elif self.state == "lock":
            self._lock(ctx, dt)
        else:
            self._dive(dt)

    def _go(self, state: str) -> None:
        self.state = state
        self._timer = 0.0

    def _fly(self, ctx: EnemyContext, dt: float) -> None:
        """Fly to its place: up to its cruise speed, its nose along its way, then brake into it.

        As it brakes, its nose comes round to the player.
        """
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        left = math.hypot(dx, dy)
        if self._speed < CFG.cruiseSpeed:
            speed = min(CFG.cruiseSpeed, self._speed + CFG.acceleration * dt)
        else:
            speed = max(CFG.cruiseSpeed, self._speed - CFG.brake * dt)
        braking = math.sqrt(2 * CFG.brake * left)
        if braking < speed:
            speed = max(CREEP, braking)
            self._turn_to(heading_to(self.x, self.y, ctx.player_x, ctx.player_y), dt)
        elif left > 0:
            self.heading = turn_towards(self.heading, math.atan2(dx, dy), CFG.turnDeg * DEG * dt)
        self._speed = speed
        step = speed * dt
        if step < left:
            self.x += dx / left * step
            self.y += dy / left * step
            return
        self.x = self.target_x
        self.y = self.target_y
        self._speed = 0.0
        self._go("aim")

    def _turn_to(self, target: float, dt: float) -> None:
        """Turn the nose towards `target`, easing in as it gets there."""
        left = abs(wrap_angle(target - self.heading))
        rate = min(math.pi / CFG.aimTime, TURN_EASE * left)
        self.heading = turn_towards(self.heading, target, rate * dt)

    def _aim(self, ctx: EnemyContext, dt: float) -> None:
        """Point at the player, its gun charging, then fire its spread (ENM-PHANTOM-10)."""
        self._turn_to(heading_to(self.x, self.y, ctx.player_x, ctx.player_y), dt)
        # Its charge light fills as it aims (ENM-PHANTOM-04).
        self.charge = min(1, self._timer / CFG.aimTime)
        if self._timer < CFG.aimTime:
            return
        self.charge = 0
        fire_aimed(
            ctx,
            self._muzzles,
            self,
            (CFG.spreadCount, CFG.spreadSpacing),
            bullet_shot(ctx, CFG.bullet),
        )
        self.stops_left -= 1
        self._go("hold")

    def _next(self, ctx: EnemyContext) -> None:
        """Fly on to another place, or, after its last spread, lock on and dive."""
        if self.stops_left <= 0:
            self._go("lock")
            return
        place = self._pick_place(ctx)
        tries = 1
        while tries < TRIES and self._too_near(place):
            place = self._pick_place(ctx)
            tries += 1
        self.target_x = place[0]
        self.target_y = place[1]
        self._go("fly")

    def _pick_place(self, ctx: EnemyContext) -> tuple[float, float]:
        return (
            range_in(ctx.random, CFG.placeX) * ctx.width,
            range_in(ctx.random, CFG.placeY) * ctx.height,
        )

    def _too_near(self, place: tuple[float, float]) -> bool:
        near: bool = math.hypot(place[0] - self.x, place[1] - self.y) < CFG.moveDistance
        return near

    def _lock(self, ctx: EnemyContext, dt: float) -> None:
        """Turn the nose to the player, then lock the dive at where it is (ENM-PHANTOM-11)."""
        target = heading_to(self.x, self.y, ctx.player_x, ctx.player_y)
        self._turn_to(target, dt)
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

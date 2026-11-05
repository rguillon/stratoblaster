# Copyright (c) 2026 Renaud Guillon
"""Where a gun's shots leave from (ENM-21).

A gun fires from its muzzles: the one furthest along each shot's way, the ones side by side in
turn, as the camera sees them.
"""

import math

from core.entities.barrel import Barrel
from core.entities.muzzle import PlanePoint
from core.systems.enemy_motion import fan_headings
from core.systems.projectile_motion import heading_to, wrap_angle

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable, Sequence
from typing import Protocol

from core.entities.boss_turret import BossTurret
from core.entities.enemy import EnemyContext, LaserOwner
from core.entities.muzzle import Muzzle, RaisedPoint


class MuzzleSource(LaserOwner, Protocol):
    """What a gun fires from: an enemy or a boss's piece, and where its muzzles are now."""

    @property
    def x(self) -> float:
        """X of the source's centre."""
        ...

    @property
    def y(self) -> float:
        """Y of the source's centre."""
        ...

    def place(self, muzzle: Muzzle, on_turret: bool = False) -> RaisedPoint:
        """Where `muzzle` is now (`Enemy.place`, `BossPiece.place`).

        Turned with its turret when `on_turret`; guns with muzzles need it.
        """
        ...


# __pragma__ ("noskip")


DEG = math.pi / 180

# Muzzles closer than this to the furthest one along a shot's heading take turns.
TIE = 0.5
# A gun with fewer muzzles than this has no choice to make.
MIN_MUZZLES = 2
# A fixed barrel fires a volley's shot only if it points within this of its heading (WPN-02).
BARREL_TOLERANCE = 6 * DEG


def _now(source: MuzzleSource) -> float:
    """Return the age of `source`, the clock a barrel's recoil follows (0 when it has none)."""
    return source.age if hasattr(source, "age") else 0


class _TurnedLaserOwner:
    """The laser owner a laser fired from one of a source's muzzles follows."""

    def __init__(self, source: MuzzleSource, muzzle: Muzzle, on_turret: bool) -> None:
        self._source = source
        self._muzzle = muzzle
        self._on_turret = on_turret

    @property
    def emitter(self) -> PlanePoint | RaisedPoint:
        return self._source.place(self._muzzle, self._on_turret)

    @property
    def heading(self) -> float:
        return self._source.heading

    @property
    def gone(self) -> bool:
        return self._source.gone

    @property
    def health(self) -> float:
        return self._source.health


class GunMuzzles:
    """The muzzles of a gun, and which of them fires next."""

    def __init__(
        self, muzzles: Sequence[Muzzle] | None = None, on_turret: bool | None = False
    ) -> None:
        """`on_turret`: the muzzles turn with the source's turret."""
        entries = list(muzzles) if muzzles is not None else []
        # Each muzzle is `[x, y, height]`, with the barrel's angle in degrees after them when the
        # barrel is fixed (WPN-01): see `Barrel`.
        self.barrels: list[Barrel] = [Barrel(list(m)) for m in entries]
        self._muzzles: list[Muzzle] = [barrel.muzzle for barrel in self.barrels]
        self._on_turret = bool(on_turret)
        self._next = 0

    def along(self, ctx: EnemyContext, source: MuzzleSource, heading: float) -> PlanePoint:
        """Where a shot going towards `heading` starts, on the playfield."""
        point = self._pick(source, heading)
        if point:
            return ctx.seen(point)
        return PlanePoint(source.x, source.y)

    def shoot(
        self,
        ctx: EnemyContext,
        source: MuzzleSource,
        heading: float,
        fire: Callable[[float, float, float], None],
    ) -> bool:
        """Fire one shot towards `heading` and return whether it was fired (WPN-01, WPN-02).

        A fixed barrel (one with an angle) that points that way, within the tolerance, fires it from
        its tip along the way the barrel itself points; the shot is held (False) when none does. A
        gun without fixed barrels fires from the muzzle furthest along `heading`.
        """
        swivel = self._swivel_of(source)
        if swivel is not None:
            return self._shoot_swivel(ctx, source, heading, fire, swivel)
        fixed = self._fixed_towards(source, heading)
        if fixed is None:
            if self.has_fixed():
                return False
            point = self.along(ctx, source, heading)
            fire(point.x, point.y, heading)
            return True
        barrel, own = fixed
        tip = ctx.seen(source.place(barrel.muzzle, self._on_turret))
        barrel.kick(_now(source))
        fire(tip.x, tip.y, own)
        return True

    def fire_all(
        self,
        ctx: EnemyContext,
        source: MuzzleSource,
        fire: Callable[[float, float, float], None],
    ) -> None:
        """Fire one shot from every fixed barrel, along it (a ring, a pod ring): WPN-01, WPN-02.

        Barrels on a turret point the way it has turned them.
        """
        swivel = self._swivel_of(source)
        turn = swivel.aim if swivel is not None else 0
        for barrel in self.barrels:
            if barrel.angle is None:
                continue
            tip = ctx.seen(source.place(barrel.muzzle, self._on_turret))
            barrel.kick(_now(source))
            fire(tip.x, tip.y, source.heading + turn + barrel.angle)

    def _swivel_of(self, source: MuzzleSource) -> BossTurret | None:
        """Return the turning turret these barrels are on, if the source has one (WPN-02)."""
        if not self._on_turret or not hasattr(source, "turret"):
            return None
        turret: BossTurret | None = source.turret
        return turret

    def _shoot_swivel(
        self,
        ctx: EnemyContext,
        source: MuzzleSource,
        heading: float,
        fire: Callable[[float, float, float], None],
        turret: BossTurret,
    ) -> bool:
        """Fire from the barrel of a turret, once it points towards `heading`, along it."""
        own = source.heading + turret.aim
        if abs(wrap_angle(own - heading)) > BARREL_TOLERANCE or len(self.barrels) == 0:
            return False
        barrel = self.barrels[self._next % len(self.barrels)]
        self._next += 1
        tip = ctx.seen(source.place(barrel.muzzle, True))
        barrel.kick(_now(source))
        fire(tip.x, tip.y, own)
        return True

    def has_fixed(self) -> bool:
        """Whether any of its barrels is fixed (has an angle)."""
        return any(barrel.angle is not None for barrel in self.barrels)

    def _fixed_towards(self, source: MuzzleSource, heading: float) -> tuple[Barrel, float] | None:
        """Return the fixed barrel pointing nearest `heading` and its heading, within tolerance."""
        best: tuple[Barrel, float] | None = None
        gap = BARREL_TOLERANCE
        for barrel in self.barrels:
            if barrel.angle is None:
                continue
            own = source.heading + barrel.angle
            off = abs(wrap_angle(own - heading))
            if off <= gap:
                gap = off
                best = (barrel, own)
        return best

    def laser(self, source: MuzzleSource) -> LaserOwner:
        """Return the laser owner a laser fired along `source`'s heading follows.

        Its piece, from a muzzle.
        """
        muzzle = self._choose(source, source.heading)
        if muzzle is None or not hasattr(source, "place"):
            return source
        return _TurnedLaserOwner(source, muzzle, self._on_turret)

    def _pick(self, source: MuzzleSource, heading: float) -> RaisedPoint | None:
        muzzle = self._choose(source, heading)
        if muzzle is None or not hasattr(source, "place"):
            return None
        for barrel in self.barrels:
            if barrel.muzzle == muzzle:
                barrel.kick(_now(source))
        return source.place(muzzle, self._on_turret)

    def _choose(self, source: MuzzleSource, heading: float) -> Muzzle | None:
        if not hasattr(source, "place") or len(self._muzzles) < MIN_MUZZLES:
            return self._muzzles[0] if len(self._muzzles) > 0 else None
        dx = math.sin(heading)
        dy = math.cos(heading)
        reach: list[float] = []
        for m in self._muzzles:
            p = source.place(m, self._on_turret)
            reach.append((p.x - source.x) * dx + (p.y - source.y) * dy)
        best = max(reach)
        ahead: list[Muzzle] = [m for i, m in enumerate(self._muzzles) if reach[i] >= best - TIE]
        index = self._next % len(ahead)
        self._next += 1
        return ahead[index]


def fire_aimed(
    ctx: EnemyContext,
    guns: GunMuzzles,
    source: MuzzleSource,
    count_and_spacing: tuple[int, float],
    fire: Callable[[float, float, float], None],
) -> None:
    """Fire a fan of `count` shots `spacing_deg` apart around the player's direction (ENM-20).

    Each from the muzzle facing its way and aimed from where it leaves.
    """
    count, spacing_deg = count_and_spacing
    aim = heading_to(source.x, source.y, ctx.player_x, ctx.player_y)
    if guns.has_fixed():
        # Fixed barrels: each shot leaves the barrel pointing nearest its way, along it (WPN-01).
        for turn in fan_headings(0, count, spacing_deg * DEG):
            guns.shoot(ctx, source, aim + turn, fire)
        return
    for turn in fan_headings(0, count, spacing_deg * DEG):
        point = guns.along(ctx, source, aim + turn)
        fire(point.x, point.y, heading_to(point.x, point.y, ctx.player_x, ctx.player_y) + turn)

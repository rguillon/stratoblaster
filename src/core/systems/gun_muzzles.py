"""Where a gun's shots leave from (phase 7 review), ported from `core/systems/gun-muzzles.ts`.

A gun fires from its muzzles: the one furthest along each shot's way, the ones side by side in
turn, as the camera sees them.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.muzzle import PlanePoint
from core.systems.enemy_motion import fan_headings
from core.systems.projectile_motion import heading_to

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402
from typing import Protocol  # noqa: E402

from core.entities.enemy import EnemyContext, LaserOwner  # noqa: E402
from core.entities.muzzle import Muzzle, RaisedPoint  # noqa: E402


class MuzzleSource(LaserOwner, Protocol):
    """What a gun fires from: an enemy or a boss's piece, and where its muzzles are now."""

    @property
    def x(self) -> float: ...

    @property
    def y(self) -> float: ...

    def place(self, muzzle: Muzzle, on_turret: bool = False) -> RaisedPoint:
        """Where `muzzle` is now (`Enemy.place`, `BossPiece.place`), turned with its turret when
        `on_turret`; guns with muzzles need it.
        """
        ...


__pragma__("noskip")

DEG = math.pi / 180

# Muzzles closer than this to the furthest one along a shot's heading take turns.
TIE = 0.5
# A gun with fewer muzzles than this has no choice to make.
MIN_MUZZLES = 2


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
        self._muzzles: list[Muzzle] = list(muzzles) if muzzles is not None else []
        self._on_turret = bool(on_turret)
        self._next = 0

    def along(self, ctx: EnemyContext, source: MuzzleSource, heading: float) -> PlanePoint:
        """Where a shot going towards `heading` starts, on the playfield."""
        point = self._pick(source, heading)
        if point:
            return ctx.seen(point)
        return PlanePoint(source.x, source.y)

    def laser(self, source: MuzzleSource) -> LaserOwner:
        """The laser owner a laser fired along `source`'s heading follows: its piece, from a
        muzzle.
        """
        muzzle = self._choose(source, source.heading)
        if muzzle is None or not hasattr(source, "place"):
            return source
        return _TurnedLaserOwner(source, muzzle, self._on_turret)

    def _pick(self, source: MuzzleSource, heading: float) -> RaisedPoint | None:
        muzzle = self._choose(source, heading)
        if muzzle is None or not hasattr(source, "place"):
            return None
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
        ahead: list[Muzzle] = []
        for i in range(len(self._muzzles)):
            if reach[i] >= best - TIE:
                ahead.append(self._muzzles[i])
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
    """Fires a fan of `count` shots `spacing_deg` apart around the player's direction (GD-44),
    each from the muzzle facing its way and aimed from where it leaves.
    """
    count, spacing_deg = count_and_spacing
    aim = heading_to(source.x, source.y, ctx.player_x, ctx.player_y)
    for turn in fan_headings(0, count, spacing_deg * DEG):
        point = guns.along(ctx, source, aim + turn)
        fire(point.x, point.y, heading_to(point.x, point.y, ctx.player_x, ctx.player_y) + turn)

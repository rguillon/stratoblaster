# Copyright (c) 2026 Renaud Guillon
"""A boss's gun mounts: every bullet, laser and missile leaves one of them (BOSS-23, BOSS-58).

A mount is on one of the boss's pieces (a part or the core) and goes with it. Its barrels are
fixed on it: each shot leaves a barrel's tip along that barrel, which is thrown back (WPN-03); a
mount on a turret turns its barrels with it (BOSS-29), and a rotor's barrels all round its hub
fire one bullet each of its rings. Pure and deterministic.
"""

import math

from core.entities.barrel import Barrel
from core.entities.boss_turret import BossTurret
from core.entities.muzzle import PlanePoint
from core.systems.enemy_motion import fan_headings
from core.systems.projectile_motion import heading_to

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable

from core.entities.boss_turret import BossTurretSpec
from core.entities.enemy import EnemyContext
from core.entities.muzzle import Muzzle, RaisedPoint
from core.systems.gun_muzzles import MuzzleSource

# A shot to fire: `fire(x, y, heading)` from a point of the playfield.
Fire = Callable[[float, float, float], None]
# A missile to launch: `fire(mouth, seen, heading, side)`, from its port's mouth above the plane, or
# from where the camera sees that mouth on the plane; an upward one drifts along `side` (WPN-09).
Launch = Callable[[RaisedPoint, PlanePoint, float, float], None]
# __pragma__ ("noskip")


DEG = 3.141592653589793 / 180
# A port this close to its block's middle (px) has no side to drift off to.
SIDE_GAP = 0.5


class BossMountSpec:
    """A mount of a boss's piece: what it fires, from which barrels, and its turret if any."""

    def __init__(
        self,
        id_: str,
        piece: str,
        kind: str,
        barrels: list[list[float]],
        turret: BossTurretSpec | None = None,
    ) -> None:
        """`kind` is "gun", "laser" or "missile"; `piece` the part id (or `core`) it is on.

        `barrels`: one `[x, y, height]` per barrel's tip (a laser's lens, a missile port), as the
        boss is drawn at rest, then the way it points (degrees from the piece's nose, positive to
        the right, as headings) for a gun or a laser. `turret`: its pivot and turn rates when it
        turns, None for a fixed mount.
        """
        self.id = id_
        self.piece = piece
        self.kind = kind
        self.barrels = barrels
        self.turret = turret


class BossMount:
    """A mount of a boss's piece, its barrels' recoil and its turret's aim (see `BossMountSpec`)."""

    def __init__(self, spec: BossMountSpec) -> None:
        self.spec = spec
        self.id = spec.id
        self.kind = spec.kind
        self.turret: BossTurret | None = BossTurret(spec.turret) if spec.turret else None
        self.barrels: list[Barrel] = [Barrel(list(entry)) for entry in spec.barrels]
        # The boss's age when its guns first came into use (its stage fires from it): it is not
        # there before (BOSS-58); None until then.
        self.shown_at: float | None = None
        self._next = 0

    def tip(self, source: MuzzleSource, barrel: Barrel) -> RaisedPoint:
        """Where `barrel`'s tip is now on its piece, turned with the mount's turret."""
        muzzle: Muzzle = barrel.muzzle
        if self.turret is not None:
            muzzle = self.turret.turned(muzzle)
        return source.place(muzzle)

    def heading_of(self, source: MuzzleSource, barrel: Barrel) -> float:
        """Return the way `barrel` points now: its piece's heading, turret's aim and own angle."""
        turn = self.turret.aim if self.turret is not None else 0
        angle = barrel.angle if barrel.angle is not None else 0
        return source.heading + turn + angle

    def fire(self, ctx: EnemyContext, source: MuzzleSource, count: int, fire: Fire) -> None:
        """Fire `count` of its barrels, each a bullet from its tip along it (WPN-01, WPN-03).

        Barrels side by side, all pointing the same way, take turns; of barrels pointing different
        ways, the middle ones. Never more bullets than barrels.
        """
        for barrel in self._chosen(count):
            self._shoot(ctx, source, barrel, fire)

    def fire_all(self, ctx: EnemyContext, source: MuzzleSource, fire: Fire) -> None:
        """Fire every barrel at once: a rotor's ring, one bullet a barrel."""
        for barrel in self.barrels:
            self._shoot(ctx, source, barrel, fire)

    def launch(
        self,
        ctx: EnemyContext,
        source: MuzzleSource,
        count_and_spacing: tuple[int, float],
        fire: Launch,
    ) -> None:
        """Launch `count` missiles from its ports in turn, in a fan around the player's direction.

        Each port launches (and reloads, WPN-07) as its missile leaves it: `fire(x, y, heading,
        height)` gets both the port's mouth (`x`, `y`, `height`: an upward silo's missile climbs
        from there, WPN-09) and, for one flying flat from the start, where the camera sees it on the
        plane (`seen`, see `Launch`).
        """
        count, spacing_deg = count_and_spacing
        if len(self.barrels) == 0:
            return
        middle = self._middle(source)
        for turn in fan_headings(0, count, spacing_deg * DEG):
            barrel = self.barrels[self._next % len(self.barrels)]
            self._next += 1
            mouth = self.tip(source, barrel)
            point = ctx.seen(mouth)
            barrel.kick(_now(source))
            heading = heading_to(point.x, point.y, ctx.player_x, ctx.player_y) + turn
            # Off to its side: away from the block's middle (WPN-09), or its way for a lone port.
            apart = math.hypot(mouth.x - middle.x, mouth.y - middle.y) > SIDE_GAP
            side = heading_to(middle.x, middle.y, mouth.x, mouth.y) if apart else heading
            fire(mouth, point, heading, side)

    def _middle(self, source: MuzzleSource) -> PlanePoint:
        """Return the middle of its ports, where they are now."""
        sx = 0.0
        sy = 0.0
        for barrel in self.barrels:
            tip = self.tip(source, barrel)
            sx += tip.x
            sy += tip.y
        n = len(self.barrels)
        return PlanePoint(sx / n, sy / n)

    def laser(self, source: MuzzleSource) -> "MountLaserOwner":
        """Return what a laser of this mount leaves from and follows: its lens, along its barrel."""
        return MountLaserOwner(self, source)

    def _shoot(self, ctx: EnemyContext, source: MuzzleSource, barrel: Barrel, fire: Fire) -> None:
        point = ctx.seen(self.tip(source, barrel))
        barrel.kick(_now(source))
        fire(point.x, point.y, self.heading_of(source, barrel))

    def _chosen(self, count: int) -> list[Barrel]:
        """Return the barrels `count` bullets leave from (see `fire`)."""
        n = len(self.barrels)
        k = min(count, n)
        if k <= 0:
            return []
        if self._side_by_side():
            start = self._next
            self._next += k
            return [self.barrels[(start + i) % n] for i in range(k)]
        first = (n - k) // 2
        return [self.barrels[first + i] for i in range(k)]

    def _side_by_side(self) -> bool:
        """Whether its barrels all point the same way (a twin gun's take turns)."""
        angle = self.barrels[0].angle
        return all(barrel.angle == angle for barrel in self.barrels)


class MountLaserOwner:
    """A laser fired from a mount: from its lens, the way its barrel points, as it turns."""

    def __init__(self, mount: BossMount, source: MuzzleSource) -> None:
        self._mount = mount
        self._source = source

    @property
    def emitter(self) -> PlanePoint | RaisedPoint:
        """Its mount's lens, where it is now."""
        return self._mount.tip(self._source, self._mount.barrels[0])

    @property
    def heading(self) -> float:
        """The way its mount's barrel points now."""
        return self._mount.heading_of(self._source, self._mount.barrels[0])

    @property
    def gone(self) -> bool:
        """Whether its piece is gone."""
        return self._source.gone

    @property
    def health(self) -> float:
        """Its piece's health."""
        return self._source.health


def _now(source: MuzzleSource) -> float:
    """Return the age of `source`, the clock a barrel's recoil follows (0 when it has none)."""
    return source.age if hasattr(source, "age") else 0

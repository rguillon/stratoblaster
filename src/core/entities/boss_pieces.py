# Copyright (c) 2026 Renaud Guillon
"""The pieces of a boss (BOSS-12).

Its destroyable parts and its core, as shots and weapons see them.
"""

import math

from core.entities.boss_turret import BossTurret
from core.entities.muzzle import PlanePoint, muzzle_point

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import TYPE_CHECKING, Protocol

from core.entities.muzzle import Muzzle, RaisedPoint
from core.entities.shot_target import ShotTarget

# `boss` imports this module, so the names of `boss` are imported for the annotations only.
if TYPE_CHECKING:
    from core.entities.boss import Boss, BossPartSpec


class BossPiece(ShotTarget, Protocol):
    """Something of a boss that shots hit and its weapons fire from: a part or the core."""

    # Seconds since it last took damage (for the hit flash); infinity before.
    since_hit: float

    @property
    def heading(self) -> float:
        """Direction its nose points, in radians from +Y."""
        ...

    @property
    def gone(self) -> bool:
        """Whether it is done and the world should remove it."""
        ...

    @property
    def emitter(self) -> PlanePoint:
        """Where its lasers leave from: one radius ahead of its centre, along its heading."""
        ...

    @property
    def turret(self) -> BossTurret | None:
        """The turret its guns are on, if any (BOSS-29): its weapons turn it."""
        ...

    def place(self, muzzle: Muzzle, on_turret: bool = False) -> RaisedPoint:
        """Where one of its guns' muzzles is now.

        `muzzle` given from the boss's centre (as the boss is drawn, its orbiting parts at a spin of
        0, its joints at rest).
        """
        ...


# __pragma__ ("noskip")


INFINITY = float("Infinity")


def _turret_of(boss: "Boss", item_id: str) -> BossTurret | None:
    """Return the turret of the piece `item_id` of `boss`, if it has one."""
    turrets = boss.stats.turrets
    spec = turrets.get(item_id) if turrets is not None else None
    if spec is None:
        return None
    return BossTurret(spec)


def _emitter_of(x: float, y: float, radius: float, heading: float) -> PlanePoint:
    """Laser owners fire along their heading from one radius ahead of their centre."""
    return PlanePoint(x + math.sin(heading) * radius, y + math.cos(heading) * radius)


class BossPart:
    """A destroyable part of a `Boss`, at its offset from the boss's centre (a `DropSource`)."""

    def __init__(self, spec: "BossPartSpec", index: int, boss: "Boss") -> None:
        self.spec = spec
        self.index = index
        self._boss = boss
        self.x = 0.0
        self.y = 0.0
        self.since_hit = INFINITY
        # Set once the boss has taken its destruction into account (its stage went up).
        self.broken = False
        self.radius = spec.radius
        self.max_health = spec.health
        self.drop_chance = spec.drop_chance
        self.shields_core = spec.shields_core
        self.turret = _turret_of(boss, spec.id)
        # Points scored when the player destroys it (GAME-SCORE-04).
        part_points = boss.stats.part_points
        self.points = part_points if part_points is not None else 0
        self._health = spec.health

    @property
    def id(self) -> int:
        """Unique among the boss's pieces (the core is the boss's id)."""
        return -(self._boss.id * 64 + self.index + 1)

    @property
    def heading(self) -> float:
        """The way its nose points: its boss's (down the screen, unless it has turned, D-228)."""
        return self._boss.heading

    @property
    def age(self) -> float:
        """Its boss's age: the clock its barrels' recoil follows (WPN-03)."""
        return self._boss.age

    @property
    def health(self) -> float:
        """Its health; none once it has retired (D-228)."""
        return 0 if self.retired else self._health

    @health.setter
    def health(self, value: float) -> None:
        """Damage only counts once the boss is in place (BOSS-09), and the part revealed."""
        if not self._boss.vulnerable or self.hidden:
            return
        next_health = max(0, value)
        if next_health < self._health:
            self.since_hit = 0
        self._health = next_health

    @property
    def destroyed(self) -> bool:
        """Whether its health is used up."""
        return self._health <= 0

    @property
    def hidden(self) -> bool:
        """Whether it is out of the fight.

        Still hidden (the transformation that reveals it has not happened, BOSS-38), or retired.
        """
        reveal = self.spec.reveal
        return (reveal is not None and self._boss.form < reveal) or self.retired

    @property
    def retired(self) -> bool:
        """Whether it has left the fight (D-228, BOSS-46).

        The transformation it retires at has started.
        """
        retire = self.spec.retire
        if retire is None:
            return False
        boss = self._boss
        return boss.form >= retire or boss.transforming_into == retire

    @property
    def gone(self) -> bool:
        """Whether its boss is gone or it is destroyed."""
        return self._boss.gone or self.destroyed

    @property
    def emitter(self) -> PlanePoint:
        """Where its lasers leave from: one radius ahead of its centre, along its heading."""
        return _emitter_of(self.x, self.y, self.radius, self.heading)

    def place(self, muzzle: Muzzle, on_turret: bool = False) -> RaisedPoint:
        """Where `muzzle` (from the boss's centre, as drawn at rest) is now.

        Through its turret if `on_turret` and it has one, then moved by its joint, then turned with
        the boss.
        """
        if on_turret and self.turret is not None:
            x, y, height = self.turret.turned(muzzle)
        else:
            x, y, height = muzzle
        x2, y2 = self._boss.joints.move(self.spec.joint, x, y)
        moved: Muzzle = (x2, y2, height)
        return muzzle_point(self._boss, moved, self._boss.spin if self.spec.orbits else 0)

    def destroy(self) -> None:
        """Destroys it at once, whatever the boss is doing (its death, a debug key)."""
        self._health = 0


class BossCore:
    """The core of a `Boss` as its shots see it: shielded while its shielding parts stand."""

    def __init__(self, boss: "Boss") -> None:
        self._boss = boss
        self.since_hit = INFINITY
        self.radius = boss.stats.core_radius
        self.max_health = boss.stats.health
        self.turret = _turret_of(boss, "core")

    @property
    def id(self) -> int:
        """The id of the boss: the core shares it."""
        return self._boss.id

    @property
    def heading(self) -> float:
        """The way its nose points: its boss's."""
        return self._boss.heading

    @property
    def age(self) -> float:
        """Its boss's age: the clock its barrels' recoil follows (WPN-03)."""
        return self._boss.age

    @property
    def x(self) -> float:
        """X of the boss's centre."""
        return self._boss.x

    @property
    def y(self) -> float:
        """Y of the boss's centre."""
        return self._boss.y

    @property
    def health(self) -> float:
        """Health the core has left: 0 while the boss is dying."""
        return self._boss.core_health

    @health.setter
    def health(self, value: float) -> None:
        """Shots that hit a shielded core (or one coming in) spark but do no damage (BOSS-14)."""
        if not self._boss.vulnerable or self._boss.core_shielded:
            return
        if value < self._boss.core_health:
            self.since_hit = 0
        self._boss.hurt_core(value)

    @property
    def gone(self) -> bool:
        """Whether the boss is gone or dying."""
        return self._boss.gone or self._boss.state == "dying"

    @property
    def emitter(self) -> PlanePoint:
        """Where its lasers leave from: one radius ahead of its centre, along its heading."""
        return _emitter_of(self.x, self.y, self.radius, self.heading)

    def place(self, muzzle: Muzzle, on_turret: bool = False) -> RaisedPoint:
        """Where `muzzle` is now on the boss.

        Through the core's turret when `on_turret` and it has one.
        """
        if on_turret and self.turret is not None:
            return muzzle_point(self._boss, self.turret.turned(muzzle))
        return muzzle_point(self._boss, muzzle)

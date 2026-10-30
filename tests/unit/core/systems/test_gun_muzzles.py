"""Tests of where a gun's shots leave from (phase 7 review), `core/systems/gun_muzzles.py`."""

import math

import pytest

from core.entities.muzzle import PlanePoint, RaisedPoint
from core.systems.gun_muzzles import TIE, GunMuzzles, fire_aimed


class _Source:
    """A body with muzzles: `place` puts a muzzle at its centre plus the muzzle's offset."""

    def __init__(self, x: float = 0, y: float = 0, heading: float = math.pi) -> None:
        self.x = x
        self.y = y
        self.heading = heading
        self.gone = False
        self.health = 10
        self.placed: list[tuple[tuple[float, float, float], bool]] = []

    @property
    def emitter(self) -> PlanePoint:
        return PlanePoint(self.x, self.y)

    def place(self, muzzle, on_turret=False):  # type: ignore[no-untyped-def]
        self.placed.append((muzzle, on_turret))
        mx, my, mh = muzzle
        return RaisedPoint(self.x + mx, self.y + my, mh)


class _PlainSource:
    """A source that cannot place muzzles (no `place`)."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.heading = math.pi
        self.gone = False
        self.health = 10

    @property
    def emitter(self) -> PlanePoint:
        return PlanePoint(self.x, self.y)


class _Ctx:
    player_x = 0.0
    player_y = 100.0

    def seen(self, point: RaisedPoint) -> PlanePoint:
        return PlanePoint(point.x, point.y)


def test_p07_r09_a_gun_without_muzzles_fires_from_the_source() -> None:
    point = GunMuzzles().along(_Ctx(), _Source(3, 4), 0)
    assert (point.x, point.y) == (3, 4)


def test_p07_r09_a_source_that_cannot_place_muzzles_fires_from_its_centre() -> None:
    guns = GunMuzzles([(5, 0, 0), (-5, 0, 0)])
    point = guns.along(_Ctx(), _PlainSource(3, 4), 0)
    assert (point.x, point.y) == (3, 4)


def test_p07_r09_a_single_muzzle_is_used_and_placed_with_the_turret_flag() -> None:
    source = _Source(0, 0)
    guns = GunMuzzles([(5, 0, 1)], on_turret=True)
    point = guns.along(_Ctx(), source, 0)
    assert (point.x, point.y) == (5, 0)
    assert source.placed == [((5, 0, 1), True)]


def test_p07_r09_the_muzzle_furthest_along_the_heading_fires() -> None:
    # Heading 90 degrees (+X): the right muzzle is further along.
    guns = GunMuzzles([(-10, 0, 0), (10, 0, 0)])
    for _ in range(3):
        point = guns.along(_Ctx(), _Source(0, 0), math.pi / 2)
        assert (point.x, point.y) == (10, 0)


def test_p07_r09_side_by_side_muzzles_take_turns() -> None:
    # Heading straight down: both muzzles are level, so they fire in turn.
    guns = GunMuzzles([(-10, 0, 0), (10, 0, 0)])
    xs = [guns.along(_Ctx(), _Source(0, 0), math.pi).x for _ in range(4)]
    assert xs == [-10, 10, -10, 10]


def test_p07_r09_muzzles_within_the_tie_margin_take_turns() -> None:
    guns = GunMuzzles([(0, -TIE / 2, 0), (0, 0, 0)])
    xs = [guns.along(_Ctx(), _Source(0, 0), math.pi).y for _ in range(2)]
    assert xs == pytest.approx([-TIE / 2, 0])


def test_p07_r09_a_laser_from_a_muzzle_follows_the_source_through_its_muzzle() -> None:
    source = _Source(0, 0, heading=0.3)
    guns = GunMuzzles([(5, 0, 0), (-5, 0, 0)], on_turret=True)
    owner = guns.laser(source)
    assert owner.heading == 0.3
    assert owner.gone is False
    assert owner.health == 10
    emitter = owner.emitter
    assert (emitter.x, emitter.y) in {(5, 0), (-5, 0)}
    source.gone = True
    source.health = 3
    assert owner.gone is True
    assert owner.health == 3


def test_p07_r09_a_laser_without_muzzles_follows_the_source_itself() -> None:
    source = _Source()
    assert GunMuzzles().laser(source) is source
    assert GunMuzzles([(1, 1, 1), (2, 2, 2)]).laser(_PlainSource(0, 0)).__class__ is _PlainSource


def test_p07_r09_fire_aimed_fans_shots_around_the_player() -> None:
    source = _Source(0, 0)
    shots: list[tuple[float, float, float]] = []
    fire_aimed(
        _Ctx(),
        GunMuzzles(),
        source,
        (3, 10),
        lambda x, y, h: shots.append((x, y, h)),
    )
    assert len(shots) == 3
    headings = [h for _, _, h in shots]
    assert headings == pytest.approx([math.radians(-10), 0, math.radians(10)])
    assert all((x, y) == (0, 0) for x, y, _ in shots)


def test_p07_r09_fire_aimed_leaves_from_the_muzzle_and_aims_from_there() -> None:
    source = _Source(0, 0)
    shots: list[tuple[float, float, float]] = []
    fire_aimed(
        _Ctx(), GunMuzzles([(5, 0, 0)]), source, (1, 0), lambda x, y, h: shots.append((x, y, h))
    )
    x, y, heading = shots[0]
    assert (x, y) == (5, 0)
    assert heading == pytest.approx(math.atan2(-5, 100))

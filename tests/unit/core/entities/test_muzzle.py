"""Where enemy shots leave from (`core.entities.muzzle`, phase 7 review)."""

import math
from dataclasses import dataclass

import pytest

from core.entities.muzzle import RaisedPoint, muzzle_point, seen_on_playfield


@dataclass
class Eye:
    x: float
    y: float
    height: float


@dataclass
class Body:
    x: float
    y: float
    heading: float


@dataclass
class RolledBody(Body):
    roll: float = 0.0


def test_a_point_on_the_playfield_is_seen_where_it_is() -> None:
    no_eye = seen_on_playfield(None, RaisedPoint(3, 4, 50))
    assert (no_eye.x, no_eye.y) == (3, 4)
    on_playfield = seen_on_playfield(Eye(0, 0, 100), RaisedPoint(3, 4, 0))
    assert (on_playfield.x, on_playfield.y) == (3, 4)


def test_a_raised_point_is_seen_further_out_from_the_eye() -> None:
    seen = seen_on_playfield(Eye(0, 0, 100), RaisedPoint(10, 10, 50))
    assert (seen.x, seen.y) == pytest.approx((20, 20))


def test_the_eye_clamps_its_distance_when_it_is_level_with_the_point() -> None:
    seen = seen_on_playfield(Eye(0, 0, 10), RaisedPoint(10, 10, 10))
    assert (seen.x, seen.y) == pytest.approx((100, 100))


def test_a_muzzle_facing_down_keeps_its_offset() -> None:
    body = Body(100, 200, math.pi)
    point = muzzle_point(body, (3, 4, 2))
    assert (point.x, point.y, point.height) == pytest.approx((103, 204, 2))


def test_a_muzzle_turns_with_the_nose() -> None:
    body = Body(100, 200, 0)
    point = muzzle_point(body, (3, 4, 2))
    assert (point.x, point.y) == pytest.approx((97, 196))


def test_a_muzzle_turns_with_the_spin_first() -> None:
    body = Body(0, 0, math.pi)
    point = muzzle_point(body, (3, 4, 2), spin=math.pi / 2)
    assert (point.x, point.y) == pytest.approx((4, -3))


def test_a_rolled_body_dips_its_muzzles_out_of_the_height() -> None:
    body = RolledBody(0, 0, math.pi, roll=math.pi / 2)
    point = muzzle_point(body, (0, 0, 10))
    assert (point.x, point.y, point.height) == pytest.approx((10, 0, 0))


def test_a_body_without_a_roll_is_not_rolled() -> None:
    point = muzzle_point(Body(0, 0, math.pi), (0, 0, 10))
    assert point.height == pytest.approx(10)

"""Unit tests of `src/game/view/enemies/elite_shapes.py`."""

import math

import pytest
from helpers.view_probes import paths, recorder

from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies.elite_shapes import QUARTER, WHITE, ahead, barrel, strip


def test_ahead_moves_along_the_yaw_from_plus_z_towards_plus_x():
    assert ahead([1, 2, 3], 0, 4) == pytest.approx([1, 2, 7])
    x, y, z = ahead([0, 5, 0], math.pi / 2, 2)
    assert (x, y, z) == pytest.approx((2, 5, 0), abs=1e-12)


def test_ahead_stays_at_the_same_height():
    assert ahead([0, -3, 0], 0.7, 10)[1] == -3


def test_barrel_is_a_steel_tube_with_a_charge_light_and_a_marked_muzzle():
    builder, log = recorder()
    barrel(builder, [0, 0, 0], 0, [0.5, 2], kind="gun")
    assert paths(log) == ["hull.cylinder", "charge.cylinder", "muzzle"]
    hull_args = log[0][1]
    radius, length, sides, color, place = hull_args
    assert radius == 0.5
    assert length == 2
    assert sides == 6
    assert color is ENEMY_LOOK.hull.dark
    # The tube stands behind the tip, its length plus half a unit back.
    assert place.at == pytest.approx([0, 0, -2.5])
    assert place.pitch == QUARTER
    charge = log[1][1]
    assert charge[1] == 0.5
    assert charge[3] is WHITE
    assert charge[4].at == pytest.approx([0, 0, -0.5])
    assert log[2][1] == ([0, 0, 0], "gun")


def test_barrel_is_placed_at_its_tip_turned_by_its_yaw():
    builder, log = recorder()
    barrel(builder, [0, 0, 0], math.pi / 2, [1, 1], kind="cannon")
    place = log[0][1][4]
    assert place.yaw == pytest.approx(math.pi / 2)
    # Behind the tip along the yaw: x goes minus the 1.5 back.
    assert place.at == pytest.approx([-1.5, 0, 0], abs=1e-9)
    assert log[2][1][1] == "cannon"


def test_strip_is_a_thin_box_centred_along_the_yaw():
    builder, log = recorder()
    strip(builder, [0, 1, 0], 0, [3, 4, 0.5], [1, 0, 0])
    assert paths(log) == ["box"]
    size, color, place = log[0][1]
    assert size == [0.5, 0.5, 4]
    assert color == [1, 0, 0]
    assert place.at == pytest.approx([0, 1, 3])
    assert place.yaw == 0

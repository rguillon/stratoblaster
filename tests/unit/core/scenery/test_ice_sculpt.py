"""Unit tests of `src/core/scenery/ice_sculpt.py`."""

import pytest

from core.math.noise import create_noise2d
from core.scenery.ice_sculpt import LakeField, crevasse_depth, with_lakes
from core.scenery.scenery_level import Crevasses, Lakes

LAKES = Lakes(spacing=100, chance=1, radius=(20, 20), level=-5, edge=10)


def test_p08_r03_a_lake_flattens_the_ground_to_its_level_and_leaves_the_rest() -> None:
    field = LakeField(LAKES, 7)
    # Somewhere in the first square the lake's middle is at the level.
    lowest = min(field.apply(x, z, 10) for x in range(0, 100, 2) for z in range(0, 100, 2))
    assert lowest == pytest.approx(-5)
    # Far from every lake, the ground is as it was.
    assert field.apply(1000, 1000, 10) == 10


def test_a_lake_rises_back_to_the_ground_over_its_edge() -> None:
    field = LakeField(LAKES, 7)
    heights = [field.apply(x, z, 10) for x in range(0, 100) for z in range(0, 100)]
    assert any(-5 < h < 10 for h in heights)


def test_with_lakes_is_a_lake_field_once() -> None:
    assert with_lakes(LAKES, 7, 50, 50, 10) == LakeField(LAKES, 7).apply(50, 50, 10)


def test_lakes_are_kept_within_their_square_and_cached() -> None:
    field = LakeField(LAKES, 7)
    lake = field._lake(0, 0)
    assert lake is not None
    # With the edge and the radius, the centre lies at least radius + edge from the square's edge
    # (room is then 20 either way, so the centre is in [30, 70]).
    assert 30 <= lake.cx <= 70
    assert 30 <= lake.cz <= 70
    assert lake.radius == 20
    assert field._lake(0, 0) is lake


def test_p08_r07_crevasses_cut_deepest_on_their_line() -> None:
    noise = create_noise2d(5)
    crevasses = Crevasses(spacing=100, width=20, depth=8, angle_deg=0, warp=0, share=1)
    # Along X at angle 0: the lines are at Z = 0, 100, ...
    assert crevasse_depth(crevasses, noise, 37, 0) == pytest.approx(8)
    assert crevasse_depth(crevasses, noise, 37, 50) == 0


def test_crevasse_depth_follows_lines_at_an_angle() -> None:
    noise = create_noise2d(5)
    angled = Crevasses(spacing=100, width=20, depth=8, angle_deg=90, warp=0, share=1)
    # At 90 degrees the lines run along Z: X = 0 is on one.
    assert crevasse_depth(angled, noise, 0, 37) == pytest.approx(8)
    assert crevasse_depth(angled, noise, 50, 37) == 0

"""Unit tests of `src/game/view/enemies/basic_parts.py`."""

import math

import pytest

from game.view.enemies.basic_parts import eye_pair, gun_barrel, mirror, sinew, wing_pair
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import SolidBuilder


class _Muzzles:
    """Records where the muzzles of the barrels are marked."""

    def __init__(self) -> None:
        self.marks: list[tuple[list[float], str]] = []

    def __call__(self, at: list[float], kind: str) -> None:
        self.marks.append((at, kind))


class _Parts:
    """The parts a basic model draws: real solid builders, with the muzzle and flap hooks."""

    def __init__(self) -> None:
        self.hull = SolidBuilder()
        self.charge = SolidBuilder()
        self.flesh = SolidBuilder()
        self.neon = SolidBuilder()
        self.vein = SolidBuilder()
        self.muzzle = _Muzzles()
        self.flaps: list[tuple[list[float], float, float, object]] = []

    def flap(self, pivot, side, span, draw) -> None:
        self.flaps.append((pivot, side, span, draw))


def test_mirror_flips_the_outline_across_by_the_sign():
    outline = [[1, 2], [3, 4]]
    assert mirror(outline, -1) == [[-1, 2], [-3, 4]]
    assert mirror(outline, 1) == [[1, 2], [3, 4]]


def test_gun_barrel_is_a_metal_barrel_with_a_charge_light_and_a_marked_muzzle():
    parts = _Parts()
    gun_barrel(parts, [0, 1, 2], 3)
    assert len(parts.hull.geometry.positions) > 0
    assert len(parts.charge.geometry.positions) > 0
    # The muzzle is marked 0.8 past the barrel's end, on its axis (the nose, +Z).
    (at, kind) = parts.muzzle.marks[0]
    assert at == pytest.approx([0, 1, 5.8])
    assert kind == "gun"


def test_gun_barrel_turned_by_its_yaw_points_its_muzzle_that_way():
    parts = _Parts()
    gun_barrel(parts, [0, 0, 0], 2, yaw=math.pi / 2)
    (at, _kind) = parts.muzzle.marks[0]
    assert at == pytest.approx([2.8, 0, 0], abs=1e-9)


def test_sinew_is_a_flesh_tube_from_start_to_end():
    parts = _Parts()
    sinew(parts, [0, 0, 0], [0, 0, 4], [0, 1, 0], 0.5)
    zs = parts.flesh.geometry.positions[2::3]
    # The tube reaches from its start to its end, give or take its radius at the ends.
    assert -0.5 <= min(zs) <= 0.5
    assert 3.5 <= max(zs) <= 4.5


def test_eye_pair_is_two_glowing_beads_mirrored_either_side_of_the_centre():
    parts = _Parts()
    eye_pair(parts, [0, 0, 0], 2.0, 1.0, [1, 0, 0])
    xs = parts.vein.geometry.positions[0::3]
    # Two beads, each about `size` across, centred on x = -1 and x = +1: the group is symmetric
    # and reaches past each centre.
    assert (min(xs) + max(xs)) / 2 == pytest.approx(0, abs=0.01)
    assert min(xs) <= -1 <= 0 and max(xs) >= 1
    # Each bead is lit in the glow colour.
    assert parts.vein.geometry.colors[0:3] == pytest.approx([1, 0, 0])


def test_wing_pair_hinges_one_membrane_wing_per_side_at_its_root():
    parts = _Parts()
    shape = {"root": [1, 0], "tips": [[4, 3], [3, 6]], "y": 2, "strut": 0.3}
    wing_pair(parts, shape, [0, 1, 0])
    assert [side for _pivot, side, _span, _draw in parts.flaps] == SIDES
    pivots = [pivot for pivot, _side, _span, _draw in parts.flaps]
    assert [v for pivot in pivots for v in pivot] == pytest.approx([-1, 2, 0, 1, 2, 0])
    # The span is how far the tips reach across from the root (x = 1): 3 to either tip.
    spans = [span for _pivot, _side, span, _draw in parts.flaps]
    assert spans == pytest.approx([3, 3])


def test_wing_draw_builds_membrane_struts_and_the_steady_lights_when_given():
    parts = _Parts()
    light = [[4, 0], [3, 0], [3, 1]]
    shape = {"root": [1, 0], "tips": [[4, 0]], "y": 2, "strut": 0.3, "lights": [light]}
    wing_pair(parts, shape, [0, 1, 0])
    _pivot, side, _span, draw = parts.flaps[1]
    wing = _Parts()
    draw(wing)
    assert len(wing.flesh.geometry.positions) > 0
    # The lights are decals on the wing's neon, not veins.
    assert len(wing.neon.geometry.positions) > 0
    assert len(wing.vein.geometry.positions) == 0


def test_wing_draw_without_lights_runs_a_vein_along_its_leading_strut():
    parts = _Parts()
    shape = {"root": [1, 0], "tips": [[4, 0]], "y": 2, "strut": 0.3}
    wing_pair(parts, shape, [0, 1, 0])
    _pivot, _side, _span, draw = parts.flaps[0]
    wing = _Parts()
    draw(wing)
    assert len(wing.vein.geometry.positions) > 0
    assert len(wing.neon.geometry.positions) == 0

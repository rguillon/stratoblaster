"""Unit tests of `src/render/geometry/organic.py`."""

import math

import pytest
from helpers.render_geometry import enclosed_volume, points_of

from core.math.rng import create_rng
from render.geometry.organic import (
    MembraneWing,
    RibSpec,
    SegmentedBody,
    carapace,
    curve,
    grown,
    membrane_wing,
    organ,
    plate,
    ribs,
    segment_stations,
    segmented_body,
    tendril,
    vein,
)
from render.geometry.solids import Placement, SolidBuilder

RED = [1.0, 0.0, 0.0]
BLUE = [0.0, 0.0, 1.0]
GREEN = [0.0, 1.0, 0.0]


def _body(**overrides: object) -> SegmentedBody:
    values: dict[str, object] = {
        "tail": 0,
        "nose": 10,
        "segments": 2,
        "width": 1,
        "bottom": 0,
        "top": 2,
    }
    values.update(overrides)
    return SegmentedBody(**values)  # type: ignore[arg-type]


def test_a_body_has_a_waist_between_each_pair_of_segments() -> None:
    stations = segment_stations(_body(girth=lambda _t: 1))
    assert len(stations) == 2 * 2 + 1
    assert [s[0] for s in stations] == pytest.approx([0, 2.5, 5, 7.5, 10])
    # The waist (pinch 0.3 by default) is 70 % of the swollen middle.
    assert stations[2][1] == pytest.approx(0.7)
    assert stations[1][1] == pytest.approx(1)


def test_closed_ends_shrink_to_a_point_on_the_middle_line() -> None:
    stations = segment_stations(_body())
    assert stations[0] == pytest.approx([0, 0, 1, 1])
    assert stations[-1] == pytest.approx([10, 0, 1, 1])


def test_open_ends_keep_their_width() -> None:
    # The end stations are waists (70 % of the width), not swollen middles.
    stations = segment_stations(_body(closed=[False, False], girth=lambda _t: 1))
    assert stations[0][1] == pytest.approx(0.7)
    assert stations[-1][1] == pytest.approx(0.7)


def test_a_custom_pinch_sets_the_waists() -> None:
    stations = segment_stations(_body(pinch=0.5, girth=lambda _t: 1))
    assert stations[2][1] == pytest.approx(0.5)


def test_a_segmented_body_is_a_closed_solid_by_default() -> None:
    b = SolidBuilder()
    segmented_body(b, _body(), RED)
    assert enclosed_volume(b.geometry.positions, b.geometry.indices) > 0


def test_a_segmented_body_takes_its_own_section() -> None:
    default = SolidBuilder()
    segmented_body(default, _body(), RED)
    square = SolidBuilder()
    segmented_body(
        square,
        _body(),
        RED,
        section=[[-1, -1], [1, -1], [1, 1], [-1, 1]],
    )
    assert len(square.geometry.indices) != len(default.geometry.indices)


def test_a_carapace_alternates_the_plate_colours_along_z() -> None:
    b = SolidBuilder()
    carapace(b, _body(), [RED, BLUE])
    colours = {tuple(b.geometry.colors[i : i + 3]) for i in range(0, len(b.geometry.colors), 4)}
    assert colours == {tuple(RED), tuple(BLUE)}


def test_a_tube_with_equal_radii_is_a_closed_cylinder() -> None:
    b = tendril(SolidBuilder(), [[0, 0, 0], [0, 0, 2]], [1, 1], 4, RED)
    # The sides of a 4-faceted tube with radius 1 form a diamond of area 2, two units long.
    assert enclosed_volume(b.geometry.positions, b.geometry.indices) == pytest.approx(4)


def test_a_tube_tapering_to_a_point_is_a_cone() -> None:
    b = tendril(SolidBuilder(), [[0, 0, 0], [0, 0, 2]], [1, 0], 4, RED)
    assert enclosed_volume(b.geometry.positions, b.geometry.indices) == pytest.approx(2 * 2 / 3)


def test_a_tube_tapering_from_a_point_is_a_cone_too() -> None:
    b = tendril(SolidBuilder(), [[0, 0, 0], [0, 0, 2]], [0, 1], 4, RED)
    assert enclosed_volume(b.geometry.positions, b.geometry.indices) == pytest.approx(2 * 2 / 3)


def test_a_tube_along_a_tilted_path_still_has_the_same_volume() -> None:
    path = [[0, 0, 0], [1, 1, 1], [2, 2, 2]]
    b = tendril(SolidBuilder(), path, [1, 1], 4, RED)
    length = 2 * math.sqrt(3)
    assert enclosed_volume(b.geometry.positions, b.geometry.indices) == pytest.approx(
        2 * length, rel=1e-6
    )


def test_a_tendril_needs_two_points() -> None:
    with pytest.raises(ValueError, match="2 points"):
        tendril(SolidBuilder(), [[0, 0, 0]], [1, 1], 4, RED)


def test_a_curve_bows_at_its_middle_and_ends_at_its_points() -> None:
    pts = curve([0, 0, 0], [2, 0, 0], [0, 1, 0], 4)
    assert len(pts) == 5
    assert pts[0] == pytest.approx([0, 0, 0])
    assert pts[-1] == pytest.approx([2, 0, 0])
    assert pts[2] == pytest.approx([1, 1, 0])


def test_a_curve_without_bow_is_a_straight_line() -> None:
    pts = curve([0, 0, 0], [0, 0, 4], [0, 0, 0], 2)
    assert [p[2] for p in pts] == pytest.approx([0, 2, 4])


def test_ribs_are_arches_across_the_body() -> None:
    b = SolidBuilder()
    ribs(b, [0, 1], RibSpec(half_width=1, y=0, height=1, thickness=0.1), RED)
    # Each arch is a 3-sided tube along 6 segments: 36 triangles and 2 end caps.
    assert len(b.geometry.indices) == 2 * 38 * 3
    tops = points_of(b.geometry.positions)
    assert max(p[1] for p in tops) == pytest.approx(1, abs=0.2)


def test_an_organ_stands_on_its_base_and_is_stretched_tall() -> None:
    b = organ(SolidBuilder(), 1, 6, RED, stretch=1.5)
    ys = [p[1] for p in points_of(b.geometry.positions)]
    assert min(ys) == pytest.approx(0)
    assert max(ys) == pytest.approx(3)
    assert enclosed_volume(b.geometry.positions, b.geometry.indices) > 0


def test_a_membrane_wing_is_a_membrane_with_one_strut_per_tip() -> None:
    skin = SolidBuilder()
    bone = SolidBuilder()
    wing = MembraneWing(
        root=[0, 0],
        tips=[[2, 1], [2, -1]],
        y=0.5,
        thickness=0.1,
        strut=0.2,
    )
    membrane_wing(skin, bone, wing, [RED, BLUE])
    assert len(skin.geometry.indices) > 0
    # A strut through 4 points (3 segments) on 4 sides, with two end caps: 28 triangles each.
    assert len(bone.geometry.indices) == 2 * 28 * 3
    assert {
        tuple(bone.geometry.colors[i : i + 3]) for i in range(0, len(bone.geometry.colors), 4)
    } == {tuple(BLUE)}


def test_a_vein_is_a_thin_three_sided_tube() -> None:
    b = vein(SolidBuilder(), [[0, 0, 0], [0, 0, 1]], 0.4, GREEN)
    assert len(b.geometry.indices) > 0
    assert {tuple(b.geometry.colors[i : i + 3]) for i in range(0, len(b.geometry.colors), 4)} == {
        tuple(GREEN)
    }


def test_a_plate_is_a_bevelled_slab_with_a_rivet_at_each_corner() -> None:
    outline = [[0, 0], [2, 0], [2, 2], [0, 2]]
    b = plate(SolidBuilder(), outline, [0, 1], [RED, BLUE])
    rivets = [
        p
        for p in points_of(b.geometry.positions)
        if p[1] > 1  # Above the slab's top face.
    ]
    assert len(rivets) > 0
    assert max(p[1] for p in points_of(b.geometry.positions)) == pytest.approx(1 + 0.4)


def test_a_plate_is_moved_by_its_placement() -> None:
    outline = [[0, 0], [2, 0], [2, 2], [0, 2]]
    b = plate(SolidBuilder(), outline, [0, 1], [RED, BLUE], Placement(at=[5, 0, 0]))
    xs = [p[0] for p in points_of(b.geometry.positions)]
    assert min(xs) > 4


def test_grown_moves_each_point_by_up_to_the_amount() -> None:
    outline = [[0, 0], [1, 0]]
    assert grown(outline, 0.5, lambda: 0.5) == [[0, 0], [1, 0]]
    assert grown(outline, 0.5, lambda: 1.0) == [[0.5, 0.5], [1.5, 0.5]]


def test_grown_is_repeatable_with_the_same_seed() -> None:
    outline = [[0, 0], [1, 0], [1, 1]]
    first = grown(outline, 0.2, create_rng(7))
    second = grown(outline, 0.2, create_rng(7))
    assert first == second
    for p, q in zip(first, outline, strict=True):
        assert abs(p[0] - q[0]) <= 0.2 and abs(p[1] - q[1]) <= 0.2

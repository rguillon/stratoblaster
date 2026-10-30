"""Unit tests of `src/render/geometry/solids.py`."""

import math

import pytest
from helpers.render_geometry import babylon_normal, enclosed_volume, points_of, triangles

from render.geometry.solids import (
    LoftOptions,
    Placement,
    SolidBuilder,
    place_at,
)

RED = [1.0, 0.0, 0.0]
BLUE = [0.0, 0.0, 1.0]
SQUARE = [[0, 0], [2, 0], [2, 2], [0, 2]]
L_SHAPE = [[0, 0], [2, 0], [2, 1], [1, 1], [1, 2], [0, 2]]
# A regular octagon of circumradius 1: n / 2 * sin(2 pi / n).
OCTAGON_AREA = 8 / 2 * math.sin(2 * math.pi / 8)


def _polygon_points(builder: SolidBuilder) -> list[list[float]]:
    return points_of(builder.geometry.positions)


def test_a_face_is_a_fan_of_triangles_with_one_colour_per_vertex() -> None:
    b = SolidBuilder().face([[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1]], RED)
    assert len(b.geometry.positions) == 4 * 3
    assert b.geometry.colors == [1, 0, 0, 1] * 4
    assert len(b.geometry.indices) == 6


def test_a_face_with_fewer_than_three_corners_has_no_triangle() -> None:
    b = SolidBuilder().face([[0, 0, 0], [1, 0, 0]], RED)
    assert b.geometry.indices == []


def test_a_box_is_six_closed_faces_with_outward_normals() -> None:
    b = SolidBuilder().box([2, 2, 2], RED)
    assert len(b.geometry.indices) == 36
    assert enclosed_volume(b.geometry.positions, b.geometry.indices) == pytest.approx(8)


def test_a_box_stands_on_its_base_at_zero() -> None:
    b = SolidBuilder().box([2, 4, 2], RED)
    ys = [p[1] for p in _polygon_points(b)]
    assert min(ys) == 0 and max(ys) == 4


def test_an_open_bottom_box_leaves_out_its_bottom_face() -> None:
    b = SolidBuilder(open_bottoms=True).box([2, 2, 2], RED)
    assert len(b.geometry.indices) == 30
    assert min(p[1] for p in _polygon_points(b)) == 0


def test_an_open_bottom_is_kept_for_a_tilted_box() -> None:
    b = SolidBuilder(open_bottoms=True).box([2, 2, 2], RED, Placement(pitch=0.3))
    assert len(b.geometry.indices) == 36


def test_a_box_with_a_different_top_colour_paints_only_its_top() -> None:
    b = SolidBuilder().box([1, 1, 1], RED, top=BLUE)
    colours = [tuple(b.geometry.colors[i : i + 3]) for i in range(0, len(b.geometry.colors), 4)]
    assert colours[:4] == [tuple(BLUE)] * 4
    assert tuple(RED) in colours[4:]


def test_yaw_turns_the_box_about_the_vertical_axis() -> None:
    b = SolidBuilder().box([4, 1, 2], RED, Placement(yaw=math.pi / 2))
    xs = [abs(p[0]) for p in _polygon_points(b)]
    zs = [abs(p[2]) for p in _polygon_points(b)]
    assert max(xs) == pytest.approx(1)
    assert max(zs) == pytest.approx(2)


def test_placement_moves_the_solid_to_its_position() -> None:
    b = SolidBuilder().box([2, 2, 2], RED, Placement(at=[10, 0, -5]))
    xs = [p[0] for p in _polygon_points(b)]
    zs = [p[2] for p in _polygon_points(b)]
    assert (min(xs), max(xs)) == (9, 11)
    assert (min(zs), max(zs)) == (-6, -4)


def test_place_at_keeps_the_turns_and_moves_the_position() -> None:
    moved = place_at(Placement(None, yaw=1, pitch=2, roll=3), [4, 5, 6])
    assert (moved.at, moved.yaw, moved.pitch, moved.roll) == ([4, 5, 6], 1, 2, 3)


def test_a_cylinder_is_an_octagonal_prism() -> None:
    b = SolidBuilder().cylinder(1, 2, 8, RED)
    assert enclosed_volume(b.geometry.positions, b.geometry.indices) == pytest.approx(
        OCTAGON_AREA * 2
    )


def test_a_tapered_cylinder_is_a_frustum() -> None:
    b = SolidBuilder().cylinder(1, 2, 8, RED, top_radius=0.5)
    a1 = OCTAGON_AREA
    a2 = OCTAGON_AREA * 0.25
    frustum = 2 / 3 * (a1 + a2 + math.sqrt(a1 * a2))
    assert enclosed_volume(b.geometry.positions, b.geometry.indices) == pytest.approx(frustum)


def test_a_lathe_closed_to_a_point_at_the_bottom_is_a_cone() -> None:
    b = SolidBuilder().lathe([[0, 0], [1, 2]], 8, RED)
    assert enclosed_volume(b.geometry.positions, b.geometry.indices) == pytest.approx(
        OCTAGON_AREA * 2 / 3
    )


def test_a_lathe_without_caps_is_an_open_band() -> None:
    capped = SolidBuilder().lathe([[1, 0], [1, 2]], 8, RED)
    band = SolidBuilder().lathe([[1, 0], [1, 2]], 8, RED, caps=False)
    assert len(band.geometry.indices) == 8 * 6
    assert len(capped.geometry.indices) > len(band.geometry.indices)


def test_a_ring_is_an_open_band_around_the_y_axis() -> None:
    b = SolidBuilder().ring(2, 3, 6, RED)
    assert len(b.geometry.indices) == 6 * 6
    radii = {round(math.hypot(p[0], p[2]), 9) for p in _polygon_points(b)}
    assert radii == {2}


def test_a_slab_is_its_outline_extruded_between_two_heights() -> None:
    b = SolidBuilder().slab(SQUARE, [1, 3], RED)
    assert enclosed_volume(b.geometry.positions, b.geometry.indices) == pytest.approx(4 * 2)


@pytest.mark.parametrize("outline", [L_SHAPE, list(reversed(L_SHAPE))], ids=["ccw", "cw"])
def test_a_concave_slab_has_the_area_of_its_outline(outline: list[list[float]]) -> None:
    b = SolidBuilder().slab(outline, [0, 1], RED)
    assert enclosed_volume(b.geometry.positions, b.geometry.indices) == pytest.approx(3)


def test_a_slab_with_a_top_colour_paints_its_top_faces() -> None:
    b = SolidBuilder().slab(SQUARE, [0, 1], RED, top=BLUE)
    first_top = tuple(b.geometry.colors[0:3])
    assert first_top == tuple(BLUE)


def test_a_bevelled_slab_without_insets_is_a_plain_slab() -> None:
    b = SolidBuilder().bevel_slab(SQUARE, [0, 0, 1], [0, 0], RED)
    assert enclosed_volume(b.geometry.positions, b.geometry.indices) == pytest.approx(4)


def test_a_bevelled_slab_narrows_its_bottom_below_the_waist() -> None:
    # Bottom face inset by 0.5 (a 1 × 1 square), full width at the waist and at the top:
    # a frustum of 1 → 4 over 0.5 high, then a 2 × 2 prism of 0.5 high.
    b = SolidBuilder().bevel_slab(SQUARE, [0, 0.5, 1], [0.5, 0], RED)
    frustum = 0.5 / 3 * (1 + 4 + 2)
    assert enclosed_volume(b.geometry.positions, b.geometry.indices) == pytest.approx(
        frustum + 4 * 0.5
    )


def test_a_loft_of_a_square_section_is_a_box() -> None:
    section = [[-1, -1], [1, -1], [1, 1], [-1, 1]]
    # The section is scaled to a width of 2 and a height of 2 (its y runs from -1 to 1).
    b = SolidBuilder().loft(section, [[0, 1, 0, 1], [2, 1, 0, 1]], RED)
    assert enclosed_volume(b.geometry.positions, b.geometry.indices) == pytest.approx(8)


def test_a_loft_closed_to_a_point_at_the_nose_is_a_pyramid() -> None:
    section = [[-1, -1], [1, -1], [1, 1], [-1, 1]]
    # The nose: a station of no width and no height, at the middle of the base.
    b = SolidBuilder().loft(section, [[0, 1, 0, 1], [2, 0, 0.5, 0.5]], RED)
    base_area = 2 * 2  # The section is 2 wide and 2 high here.
    assert enclosed_volume(b.geometry.positions, b.geometry.indices) == pytest.approx(
        base_area * 2 / 3
    )


def test_an_open_loft_is_a_polyline_section_without_caps_or_closing_side() -> None:
    # Open: the section is a polyline, so its last side (back to the first point) is left out.
    section = [[-1, -1], [1, -1], [1, 1], [-1, 1]]
    opened = SolidBuilder().loft(
        section, [[0, 1, 0, 1], [2, 1, 0, 1]], RED, options=LoftOptions(open_=True)
    )
    assert len(opened.geometry.indices) == 3 * 6


def test_a_loft_paint_colours_the_faces_it_is_asked_for() -> None:
    section = [[-1, -1], [1, -1], [1, 1], [-1, 1]]
    seen: list[tuple[int, int]] = []

    def paint(side: int, band: int) -> list[float] | None:
        seen.append((side, band))
        return BLUE if band == 1 else None

    b = SolidBuilder().loft(
        section,
        [[0, 1, 0, 1], [1, 1, 0, 1], [2, 1, 0, 1]],
        RED,
        options=LoftOptions(paint=paint),
    )
    assert sorted(set(seen)) == [(s, k) for s in range(4) for k in range(2)]
    blues = [tuple(b.geometry.colors[i : i + 3]) for i in range(0, len(b.geometry.colors), 4)]
    assert tuple(BLUE) in blues and tuple(RED) in blues


def test_the_babylon_normal_of_a_box_top_points_up() -> None:
    b = SolidBuilder().box([2, 2, 2], RED)
    top = triangles(b.geometry.positions, b.geometry.indices)[0]
    assert babylon_normal(top)[1] > 0

"""Unit tests of `src/game/view/enemies/enemy_shapes.py`."""

import math

import pytest
from helpers.view_probes import paths, recorder

from game.view.enemies.enemy_shapes import (
    CANOPY_SECTION,
    CANOPY_SIDES,
    FIGHTER_SECTION,
    HULL_SECTION,
    LOBE_SECTION,
    POD_SECTION,
    SIDES,
    angry_eyes,
    around,
    canopy_paint,
    decal,
    flip_x,
    radial,
    shift_x,
    side_stripe,
)


def test_radial_puts_the_angle_zero_on_the_nose():
    assert radial(0, 2, 1) == pytest.approx([0, 1, 2])


def test_radial_quarter_turn_points_along_plus_x():
    x, y, z = radial(math.pi / 2, 3, 0.5)
    assert (x, y) == pytest.approx((3, 0.5))
    assert z == pytest.approx(0, abs=1e-12)


def test_around_spreads_count_angles_evenly_from_the_nose():
    angles = around(4)
    assert angles == pytest.approx([0, math.pi / 2, math.pi, 3 * math.pi / 2])
    assert len(around(7)) == 7


def test_shift_and_flip_move_the_outline_across():
    outline = [[1.0, 2.0], [-3.0, 4.0]]
    assert shift_x(outline, 0.5) == [[1.5, 2.0], [-2.5, 4.0]]
    assert flip_x(outline) == [[-1.0, 2.0], [3.0, 4.0]]
    # The input is not changed.
    assert outline == [[1.0, 2.0], [-3.0, 4.0]]


def test_sides_are_left_then_right():
    assert SIDES == [-1, 1]


def test_angry_eyes_are_two_slits_mirrored_about_the_centre():
    slits = angry_eyes([0, 5], gap=2, size=[3, 1], slant=0)
    assert len(slits) == 2
    for slit in slits:
        assert len(slit) == 4
    left, right = slits
    # The inner corners sit gap/2 either side of the centre, on its line.
    assert left[0] == pytest.approx([-1, 5])
    assert right[0] == pytest.approx([1, 5])
    # Without slant the outer ends run straight out, length 3 and width 1 deep.
    assert left[1] == pytest.approx([-4, 5])
    assert left[2] == pytest.approx([-4, 4])
    assert left[3] == pytest.approx([-1, 4])


def test_angry_eyes_outer_ends_swing_back_by_the_slant():
    slant = math.pi / 6
    left, _ = angry_eyes([0, 0], gap=0, size=[2, 0.5], slant=slant)
    outer = left[1]
    assert outer[0] == pytest.approx(-2 * math.cos(slant))
    assert outer[1] == pytest.approx(-2 * math.sin(slant))


def _flat(points):
    return [v for point in points for v in point]


def _shoelace(outline):
    total = 0.0
    for i in range(len(outline)):
        x1, z1 = outline[i]
        x2, z2 = outline[(i + 1) % len(outline)]
        total += x1 * z2 - x2 * z1
    return total / 2


def test_decal_faces_up_and_is_clockwise_whichever_way_the_outline_winds():
    square_ccw = [[1, 1], [-1, 1], [-1, -1], [1, -1]]
    for outline in (square_ccw, list(reversed(square_ccw))):
        builder, log = recorder()
        decal(builder, outline, 2.0, [1, 0, 0])
        (path, args, _kwargs) = log[0]
        assert path == "face"
        corners = args[0]
        # Every corner is lifted to the decal's height, and the face is clockwise seen in (x, z).
        assert all(c[1] == 2.0 for c in corners)
        assert _shoelace([[c[0], c[2]] for c in corners]) < 0
        assert args[1] == [1, 0, 0]


def test_side_stripe_runs_along_one_side_of_the_section_with_its_lift():
    section = [[0, 0], [2, 0], [2, 2], [0, 2]]
    stripe = side_stripe(section, 0, [0, 1], lift=1.5)
    # From the first to the second point of side 0, the u is lifted and the v is not.
    assert _flat(stripe) == pytest.approx(_flat([[0, 0], [3, 0]]))


def test_side_stripe_spans_a_fraction_of_the_side_and_wraps_at_the_end():
    section = [[0, 0], [2, 0], [2, 2], [0, 2]]
    stripe = side_stripe(section, 3, [0.25, 0.75], lift=1)
    # Side 3 goes from (0, 2) back to (0, 0): the wrap uses point 0.
    assert _flat(stripe) == pytest.approx(_flat([[0, 1.5], [0, 0.5]]))


def test_side_stripe_out_of_range_start_is_the_origin_and_the_end_wraps():
    stripe = side_stripe([[1, 1], [2, 2]], 9, [0, 1], lift=1.04)
    # Side 9 is not on the 2-point section: its start is the origin, its end the wrapped point 0.
    assert _flat(stripe) == pytest.approx([0, 0, 1.04, 1])


def test_canopy_paint_colours_only_the_canopy_sides_in_the_given_bands():
    color = [0.1, 0.2, 0.3]
    paint = canopy_paint([1, 2], color)
    for side in CANOPY_SIDES:
        assert paint(side, 1) is color
        assert paint(side, 2) is color
        assert paint(side, 3) is None
    assert paint(0, 1) is None
    assert paint(6, 1) is None


def test_section_shapes_have_the_facets_their_models_expect():
    assert len(HULL_SECTION) == 6
    assert len(FIGHTER_SECTION) == 9
    assert CANOPY_SIDES == [2, 3, 4, 5]
    assert len(POD_SECTION) == 6
    assert len(CANOPY_SECTION) == 5
    assert len(LOBE_SECTION) == 7
    # A section is symmetric in u about the middle of the list: each point has a mirror.
    for section in (HULL_SECTION, FIGHTER_SECTION, POD_SECTION, LOBE_SECTION):
        us = sorted(round(p[0], 6) for p in section)
        assert us == sorted(round(-p[0], 6) for p in section)


def test_paths_helper_lists_recorded_calls_in_order():
    builder, log = recorder()
    builder.face([1], [0, 0, 0])
    builder.hull.box()
    assert paths(log) == ["face", "hull.box"]

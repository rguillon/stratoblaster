"""Moving regions (D-230, BOSS-45; docs/superpowers/specs/2026-11-01-boss-weapon-variety-and-
shape-shifts-design.md, Part B): how a piece's motion moves points, mirrored and back."""

import pytest

from game.config.bosses.moving_regions import (
    drawn_spot,
    end_spot,
    is_moving,
    mirrored_motion,
    motion_value,
    move_point,
    moving_region,
    slide,
    swing,
)
from game.config.bosses.hidden_weapons import armour_region


def _approx(points: list[float]) -> object:
    return pytest.approx(points, abs=1e-9)


def test_a_swing_up_turns_counter_clockwise_seen_from_above() -> None:
    m = swing([10, 0, 0], "up", [0, 90])
    assert move_point(m, 90, [20, 0, 3]) == _approx([10, 10, 3])


def test_a_swing_along_the_boss_lifts_its_right_side_for_a_negative_angle() -> None:
    m = swing([10, 0, 5], "along", [-90, 0])
    # A wingtip out to the right of a hinge at x 10, folded up by -90 degrees.
    assert move_point(m, -90, [30, 4, 5]) == _approx([10, 4, 25])


def test_a_swing_across_the_boss_tips_its_nose_up_for_a_negative_angle() -> None:
    m = swing([0, 0, 0], "across", [0, -90])
    assert move_point(m, -90, [0, -10, 0]) == _approx([0, 0, 10])


def test_a_slide_moves_by_its_offset() -> None:
    m = slide([[0, 0, 0], [12, -4, 1]])
    assert motion_value(m, 0.5) == [6, -2, 0.5]
    assert move_point(m, [12, -4, 1], [1, 1, 1]) == [13, -3, 2]


def test_the_mirror_of_a_motion_moves_the_mirror_point_to_the_mirror_place() -> None:
    motions = [
        swing([10, 5, 2], "up", [0, 40]),
        swing([10, 5, 2], "along", [-70, 0]),
        swing([10, 5, 2], "across", [0, 30]),
        slide([[0, 0, 0], [15, 3, -1]]),
    ]
    for m in motions:
        value = motion_value(m, 1)
        moved = move_point(m, value, [20, -8, 4])
        twin = mirrored_motion(m)
        mirrored = move_point(twin, motion_value(twin, 1), [-20, -8, 4])
        assert mirrored == _approx([-moved[0], moved[1], moved[2]])


def test_an_unknown_axis_is_refused() -> None:
    with pytest.raises(ValueError, match="Unknown swing axis"):
        swing([0, 0, 0], "sideways", [0, 1])


def test_a_mirrored_moving_region_is_two_pieces_moving_the_mirror_way() -> None:
    m = swing([20, 0, 0], "up", [0, 30])
    right, left = moving_region("wings", 1, [[20, 0], [60, 0], [60, 20]], m)
    assert right.id == "wings-right" and left.id == "wings-left"
    assert right.outlines == [[[20, 0], [60, 0], [60, 20]]]
    assert left.outlines == [[[-60, 20], [-60, 0], [-20, 0]]]
    assert right.motion == m
    assert left.motion.angles == [0, -30]
    assert right.frame is None
    assert is_moving(right)
    assert not is_moving(armour_region("back", 1, [[0, 0], [1, 0], [0, 1]], "shell"))


def test_a_single_moving_region_keeps_its_name_and_may_leave_a_frame() -> None:
    [piece] = moving_region(
        "bow", 2, [[-5, 0], [5, 0], [0, 9]], slide([[0, 0, 0], [0, 5, 0]]), "shell", None, False
    )
    assert piece.id == "bow" and piece.frame == "shell"
    with pytest.raises(ValueError, match="Unknown armour frame"):
        moving_region("bow", 2, [[-5, 0], [5, 0], [0, 9]], slide([[0, 0, 0], [0, 5, 0]]), "grid")


def test_a_point_on_the_drawn_piece_ends_up_at_its_end_spot_and_back() -> None:
    [piece] = moving_region(
        "arm", 1, [[0, 0], [9, 0], [9, 9]], swing([0, 0, 0], "up", [10, 75]), None, None, False
    )
    end = end_spot(piece, [6, 2, 1])
    assert drawn_spot(piece, end) == _approx([6, 2, 1])

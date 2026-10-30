"""Unit tests of `src/game/view/bonuses/bonus_geometry.py`."""

import math
from types import SimpleNamespace

import pytest

from game.view.bonuses.bonus_geometry import (
    _chevron,
    _circle,
    _hexagon,
    _letter_b,
    _rect,
    build_bomb_badge,
    build_bonus_badge,
    build_life_badge,
)

FACE = [0.1, 0.1, 0.1]
FRAME = [0.9, 0.5, 0.1]
CHEVRON = [1.0, 1.0, 0.0]
BADGE = SimpleNamespace(inset=0.7, face=FACE, frame=FRAME, chevrons=CHEVRON)
LIFE = SimpleNamespace(inset=0.6, rim=[1.0, 0.2, 0.2], heart=[1.0, 0.8, 0.8])
BOMB = SimpleNamespace(shell=[0.2, 0.2, 0.8], highlight=[0.8, 0.8, 1.0], letter=[1, 1, 1])


def points_of(geo):
    return [tuple(geo.positions[3 * i : 3 * i + 3]) for i in range(len(geo.positions) // 3)]


def test_p11_r07_hexagon_has_six_corners_on_its_radius_flat_side_down():
    corners = _hexagon(2.0)
    assert len(corners) == 6
    for x, y in corners:
        assert math.hypot(x, y) == pytest.approx(2.0)
    assert corners[0] == pytest.approx([2.0, 0.0])


def test_circle_is_a_regular_polygon_around_its_centre():
    corners = _circle(1.0, -2.0, 0.5, 10)
    assert len(corners) == 10
    for x, y in corners:
        assert math.hypot(x - 1.0, y + 2.0) == pytest.approx(0.5)


def test_rect_is_four_corners_in_order():
    assert _rect(0, 0, 2, 1) == [[0, 0], [2, 0], [2, 1], [0, 1]]


def test_chevron_has_two_arms_pointing_up_to_its_tip():
    arms = _chevron(0.5, 0.2)
    assert len(arms) == 2
    # The left arm ends at the tip on its second corner, the right arm starts from it.
    assert arms[0][1] == [0, 0.5]
    assert arms[1][0] == [0, 0.5]
    assert arms[0][0][0] < 0 < arms[1][1][0]


def test_letter_b_is_six_strokes_inside_its_box():
    strokes = _letter_b(1.0)
    assert len(strokes) == 6
    xs = [x for stroke in strokes for x, _ in stroke]
    ys = [y for stroke in strokes for _, y in stroke]
    assert min(ys) == pytest.approx(-0.5)
    assert max(ys) == pytest.approx(0.5)
    assert min(xs) == pytest.approx(-0.31)
    assert max(xs) == pytest.approx(0.31)


def test_p11_r07_the_weapon_badge_is_a_hexagon_frame_and_two_chevrons():
    geo = build_bonus_badge(BADGE)
    # Face: 6 corners, frame: 6 quads of 4 corners, chevrons: 2 arms of 4 corners each, twice.
    assert len(geo.positions) // 3 == 6 + 6 * 4 + 2 * 2 * 4
    assert len(geo.indices) == 3 * (4 + 6 * 2 + 4 * 2)
    assert max(geo.indices) == len(geo.positions) // 3 - 1


def test_p11_r07_the_weapon_badge_draws_the_face_frame_and_chevrons_in_their_colours():
    geo = build_bonus_badge(BADGE)
    rgb = [tuple(geo.colors[4 * i : 4 * i + 3]) for i in range(len(geo.colors) // 4)]
    assert rgb[0] == tuple(FACE)
    assert tuple(FRAME) in rgb
    assert tuple(CHEVRON) in rgb
    assert all(geo.colors[4 * i + 3] == 1 for i in range(len(geo.colors) // 4))


def test_p11_r07_the_weapon_badge_chevrons_stand_in_front_of_the_plate():
    geo = build_bonus_badge(BADGE)
    depths = {round(z, 3) for _, _, z in points_of(geo)}
    assert depths == {0, -0.02}


def test_p11_r07_life_badge_is_a_heart_in_a_rim_with_a_lighter_heart_in_front():
    geo = build_life_badge(LIFE)
    rgb = {tuple(geo.colors[4 * i : 4 * i + 3]) for i in range(len(geo.colors) // 4)}
    assert tuple(LIFE.rim) in rgb
    assert tuple(LIFE.heart) in rgb
    depths = {round(z, 3) for _, _, z in points_of(geo)}
    assert depths == {0, -0.02}


def test_p11_r07_the_heart_is_two_lobes_over_a_point():
    geo = build_life_badge(LIFE)
    rim_points = [p for p in points_of(geo) if p[2] == 0]
    assert max(y for _, y, _ in rim_points) > 0
    assert min(y for _, y, _ in rim_points) == pytest.approx(-0.8)


def test_p11_r07_bomb_badge_is_a_round_shell_with_a_highlight_and_a_letter_b():
    geo = build_bomb_badge(BOMB)
    rgb = {tuple(geo.colors[4 * i : 4 * i + 3]) for i in range(len(geo.colors) // 4)}
    assert {tuple(BOMB.shell), tuple(BOMB.highlight), tuple(BOMB.letter)} <= rgb
    # Shell: 18 sides; highlight: 10; the letter: 6 strokes of 4 corners.
    assert len(geo.positions) // 3 == 18 + 10 + 6 * 4

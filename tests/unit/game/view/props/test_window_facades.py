"""Unit tests of `src/game/view/props/window_facades.py` (D-210)."""

import pytest
from helpers.geometry_checks import bounds, check_colored

from core.math.rng import create_rng
from game.config.window_look import (
    DOOR_STYLES,
    WINDOW_ATLAS,
    WINDOW_CELL,
    WINDOW_OFFSET,
    WINDOW_STYLES,
)
from game.view.props.window_facades import (
    doorway,
    facade_windows,
    round_windows,
    tint_of,
    wall_uv,
    wall_windows,
)
from render.geometry.textured import QuadBuilder

CELLS = 64
# D-215: 15 columns a window style, the doors' bands taking the last 4.
BAND = 15


def test_d210_the_tint_is_half_the_window_colour_over_white():
    assert tint_of([1.0, 0.5, 0.0]) == pytest.approx([1.0, 0.75, 0.5])


def test_d210_a_wall_maps_on_one_cell_per_window_in_its_style_band():
    random = create_rng(1)
    for _ in range(50):
        u0, v0, u1, v1 = wall_uv(random, 2, 5 * WINDOW_CELL.width, 4 * WINDOW_CELL.height)
        assert (u1 - u0) * CELLS == pytest.approx(5)
        assert (v1 - v0) * CELLS == pytest.approx(4)
        assert u0 * CELLS >= 2 * BAND
        assert u1 * CELLS <= 3 * BAND


def test_d210_a_wall_wider_than_a_band_gets_the_whole_band():
    u0, _, u1, _ = wall_uv(create_rng(1), 0, 100 * WINDOW_CELL.width, 3)
    assert (u0, u1) == (0, BAND / CELLS)


def test_d210_a_tiny_wall_gets_one_cell():
    u0, v0, u1, v1 = wall_uv(create_rng(1), 1, 0.5, 0.5)
    assert (u1 - u0, v1 - v0) == pytest.approx((1 / CELLS, 1 / CELLS))


def test_d210_a_box_gets_one_quad_per_wall_just_off_it():
    quads = QuadBuilder()
    facade_windows(quads, create_rng(2), [0.0, 0.0, 10.0, 6.0], [1.0, 9.0], [1.0, 1.0, 1.0])
    geo = quads.geometry
    check_colored(geo)
    assert len(geo.indices) == 4 * 6
    assert len(geo.uvs) == 2 * len(geo.positions) // 3
    low, high = bounds(geo)
    assert low == pytest.approx([-5 - WINDOW_OFFSET, 1.0, -3 - WINDOW_OFFSET])
    assert high == pytest.approx([5 + WINDOW_OFFSET, 9.0, 3 + WINDOW_OFFSET])


def _bands(geo: object) -> list[int]:
    """The style band of each quad of `geo`."""
    uvs = geo.uvs  # type: ignore[attr-defined]
    return [int(min(uvs[i], uvs[i + 4]) * CELLS) // BAND for i in range(0, len(uvs), 8)]


def test_d210_a_box_is_one_style_unless_mixed():
    for seed in range(10):
        quads = QuadBuilder()
        facade_windows(quads, create_rng(seed), [0.0, 0.0, 10.0, 10.0], [0.0, 9.0], [1, 1, 1])
        assert len(set(_bands(quads.geometry))) == 1
    mixed = set()
    for seed in range(10):
        quads = QuadBuilder()
        facade_windows(quads, create_rng(seed), [0.0, 0.0, 10.0, 10.0], [0.0, 9.0], [1, 1, 1], True)
        mixed.add(len(set(_bands(quads.geometry))))
    assert max(mixed) > 1


def test_d210_a_wall_too_low_or_too_narrow_gets_no_quad():
    quads = QuadBuilder()
    facade_windows(quads, create_rng(2), [0.0, 0.0, 10.0, 6.0], [1.0, 1.5], [1, 1, 1])
    assert quads.geometry.indices == []
    facade_windows(quads, create_rng(2), [0.0, 0.0, 10.0, 0.5], [1.0, 6.0], [1, 1, 1])
    assert len(quads.geometry.indices) == 2 * 6


def test_d210_the_atlas_has_as_many_bands_as_styles():
    assert len(WINDOW_ATLAS.styles) * BAND + len(WINDOW_ATLAS.doors) * 2 == CELLS


def test_d210_a_round_tower_gets_one_quad_per_facet_following_its_taper():
    quads = QuadBuilder()
    tower = [2.0, 3.0, 5.0, 20.0, 4.0, 2.0, 6]
    round_windows(quads, create_rng(2), tower, [5.0, 25.0], [1.0, 1.0, 1.0])
    geo = quads.geometry
    check_colored(geo)
    assert len(geo.indices) == 6 * 6
    # The first facet's first corners: at the foot, radius 4 (+ offset); at the top, radius 2.
    assert geo.positions[0:3] == pytest.approx([2.0 + 4 + WINDOW_OFFSET, 5.0, 3.0])
    assert geo.positions[3:6] == pytest.approx([2.0 + 2 + WINDOW_OFFSET, 25.0, 3.0])
    assert len(set(_bands(geo))) == 1


def test_d210_a_round_tower_too_low_gets_no_windows():
    quads = QuadBuilder()
    round_windows(quads, create_rng(2), [0.0, 0.0, 0.0, 10.0, 3.0, 3.0, 8], [2.0, 2.5], [1, 1, 1])
    assert quads.geometry.indices == []


def test_d215_a_box_may_have_the_style_it_asks_for():
    for seed in range(10):
        quads = QuadBuilder()
        facade_windows(
            quads, create_rng(seed), [0.0, 0.0, 10.0, 10.0], [0.0, 9.0], [1, 1, 1], False, 2
        )
        assert set(_bands(quads.geometry)) == {2}


def test_d215_one_wall_gets_one_quad_of_its_style_just_off_it_facing_its_way():
    for facing in [-1, 1]:
        quads = QuadBuilder()
        wall_windows(
            quads,
            create_rng(1),
            [2.0, 3.0, facing],
            [6.0, 1.0, 4.0],
            WINDOW_STYLES.curtain,
            [1, 1, 1],
        )
        geo = quads.geometry
        check_colored(geo)
        assert len(geo.indices) == 6
        assert _bands(geo) == [WINDOW_STYLES.curtain]
        low, high = bounds(geo)
        z = 3.0 + facing * WINDOW_OFFSET
        assert low == pytest.approx([-1.0, 1.0, z])
        assert high == pytest.approx([5.0, 4.0, z])


def test_d215_one_wall_faces_out():
    for facing in [-1, 1]:
        quads = QuadBuilder()
        wall_windows(quads, create_rng(1), [0.0, 0.0, facing], [4.0, 0.0, 3.0], 0, [1, 1, 1])
        p = quads.geometry.positions
        # The quad's corners: foot, top, top, foot, its normal (c1 - c0) × (c2 - c0) along Z.
        e1 = [p[3] - p[0], p[4] - p[1], p[5] - p[2]]
        e2 = [p[6] - p[0], p[7] - p[1], p[8] - p[2]]
        nz = e1[0] * e2[1] - e1[1] * e2[0]
        assert nz * facing > 0


def test_d215_a_wall_too_narrow_or_too_low_gets_no_quad():
    quads = QuadBuilder()
    wall_windows(quads, create_rng(1), [0.0, 0.0, -1], [0.5, 0.0, 3.0], 0, [1, 1, 1])
    wall_windows(quads, create_rng(1), [0.0, 0.0, -1], [4.0, 1.0, 1.5], 0, [1, 1, 1])
    assert quads.geometry.positions == []


def test_d215_a_door_is_one_cell_of_its_band_standing_on_the_ground():
    random = create_rng(4)
    for door in [DOOR_STYLES.door, DOOR_STYLES.bay]:
        for _ in range(20):
            quads = QuadBuilder()
            doorway(quads, random, [1.0, 0.5, -2.0], -1, door, [1, 1, 1])
            geo = quads.geometry
            uvs = geo.uvs
            u0 = min(uvs[0::2])
            u1 = max(uvs[0::2])
            v0 = min(uvs[1::2])
            v1 = max(uvs[1::2])
            assert (u1 - u0, v1 - v0) == pytest.approx((1 / CELLS, 1 / CELLS))
            assert int(u0 * CELLS + 0.5) in [4 * BAND + 2 * door, 4 * BAND + 2 * door + 1]
            low, high = bounds(geo)
            assert low == pytest.approx([1.0 - WINDOW_CELL.width / 2, 0.5, -2 - WINDOW_OFFSET])
            assert high == pytest.approx(
                [1.0 + WINDOW_CELL.width / 2, 0.5 + WINDOW_CELL.height, -2 - WINDOW_OFFSET]
            )

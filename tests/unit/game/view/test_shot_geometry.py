"""Unit tests of `src/game/view/shot_geometry.py`."""

import math

import pytest

from game.view import shot_geometry
from game.view.shot_geometry import build_glow_bar, build_glow_disc, build_swirl, build_tracer

WHITE = [1.0, 1.0, 1.0]
RED = [1.0, 0.0, 0.0]
BLUE = [0.0, 0.0, 1.0]


@pytest.fixture
def range_errors(monkeypatch):
    """`throw new RangeError` is JavaScript: CPython raises a ValueError instead."""

    def raise_error(message):
        raise ValueError(message)

    monkeypatch.setattr(shot_geometry, "_range_error", raise_error)


def vertex(geo, i):
    """Position (x, y, z) of vertex `i`."""
    return geo.positions[3 * i : 3 * i + 3]


def colour(geo, i):
    """RGBA colour of vertex `i`."""
    return geo.colors[4 * i : 4 * i + 4]


def test_mirrored_columns_go_down_then_back_up():
    assert shot_geometry._mirrored_columns(3) == [2, 1, 0, 1, 2]
    assert shot_geometry._mirrored_columns(2) == [1, 0, 1]
    assert shot_geometry._mirrored_columns(1) == [0]


def test_p03_r01_glow_disc_colours_the_centre_then_one_ring_per_colour():
    segments = 6
    geo = build_glow_disc(segments, [WHITE, RED, BLUE])
    # Colours: the centre, then two rings of `segments` vertices.
    assert len(geo.colors) // 4 == 1 + 2 * segments
    assert colour(geo, 0) == [1.0, 1.0, 1.0, 1]
    assert colour(geo, 1) == [1.0, 0.0, 0.0, 1]
    assert colour(geo, 1 + segments) == [0.0, 0.0, 1.0, 1]


def test_p03_r01_glow_disc_rings_sit_at_the_radius_of_their_colour():
    geo = build_glow_disc(8, [WHITE, RED, BLUE])
    # The ring vertices are the positions (the centre has none, see the bug below).
    points = [geo.positions[3 * i : 3 * i + 3] for i in range(len(geo.positions) // 3)]
    assert len(points) == 16
    for x, y, _ in points[:8]:
        assert math.hypot(x, y) == pytest.approx(0.5)
    for x, y, _ in points[8:]:
        assert math.hypot(x, y) == pytest.approx(1.0)


@pytest.mark.xfail(
    strict=True,
    reason="BUG: build_swirl never pushes a position for the centre vertex, so a disc has one "
    "position less than colours and its fan indices (the centre is index 0) run past the end",
)
def test_p03_r01_glow_disc_has_a_position_for_every_vertex():
    geo = build_glow_disc(6, [WHITE, RED, BLUE])
    assert len(geo.positions) // 3 == len(geo.colors) // 4
    assert max(geo.indices) < len(geo.positions) // 3


def test_p03_r01_glow_disc_indices_form_a_fan_then_quads():
    segments = 4
    geo = build_glow_disc(segments, [WHITE, RED])
    assert len(geo.indices) == 3 * segments
    assert geo.indices[:3] == [0, 1, 2]
    assert geo.indices[-3:] == [0, segments, 1]


def test_p03_r01_a_disc_with_three_rings_is_stitched_into_quads():
    geo = build_glow_disc(3, [WHITE, RED, BLUE, RED])
    # Three fan triangles, then two strips of two triangles per side (six indices each).
    assert len(geo.indices) == 3 * 3 + 2 * 3 * 6


def test_p03_r01_swirl_with_no_lobes_is_a_plain_disc():
    plain = build_swirl(5, [WHITE, RED], {"lobes": 0, "depth": 0, "twist": 0})
    disc = build_glow_disc(5, [WHITE, RED])
    assert plain.positions == pytest.approx(disc.positions)
    assert plain.indices == disc.indices


def test_p03_r01_swirl_arms_make_the_rim_uneven():
    arms = build_swirl(12, [WHITE, RED], {"lobes": 3, "depth": 0.5, "twist": 0})
    points = [geo_point for geo_point in [arms.positions[3 * i : 3 * i + 3] for i in range(12)]]
    radii = [math.hypot(x, y) for x, y, _ in points]
    assert max(radii) == pytest.approx(1.0)
    assert min(radii) == pytest.approx(0.5)


def test_p03_r01_swirl_twist_turns_the_rim_away_from_the_centre():
    straight = build_swirl(8, [WHITE, RED], {"lobes": 0, "depth": 0, "twist": 0})
    turned = build_swirl(8, [WHITE, RED], {"lobes": 0, "depth": 0, "twist": 0.5})
    assert turned.positions[:2] != pytest.approx(straight.positions[:2])
    assert math.hypot(turned.positions[0], turned.positions[1]) == pytest.approx(
        math.hypot(straight.positions[0], straight.positions[1])
    )


@pytest.mark.parametrize(
    ("segments", "colors"),
    [(2, [WHITE, RED]), (3, [WHITE])],
)
def test_p03_r01_a_swirl_needs_three_sides_and_two_colours(range_errors, segments, colors):
    with pytest.raises(ValueError, match="Need 3 segments and 2 colours"):
        build_swirl(segments, colors, {"lobes": 0, "depth": 0, "twist": 0})


def test_p03_r01_tracer_is_a_streak_with_a_row_per_entry():
    colors = [RED, WHITE, RED]
    rows = [{"at": 0.0, "tint": [1, 1, 1]}, {"at": 1.0, "tint": [0.5, 0.5, 0.5]}]
    geo = build_tracer(colors, rows)
    columns = len(shot_geometry._mirrored_columns(3))
    assert len(geo.positions) // 3 == 2 * columns
    # The streak is centred: its first and last columns sit at the edges of [-0.5, 0.5].
    assert vertex(geo, 0)[0] == pytest.approx(-0.5)
    assert vertex(geo, columns - 1)[0] == pytest.approx(0.5)
    assert vertex(geo, 0)[1] == 0.0
    assert vertex(geo, columns)[1] == 1.0


def test_p03_r01_tracer_rows_tint_the_colours_along_the_streak():
    rows = [{"at": 0.0, "tint": [1, 1, 1]}, {"at": 1.0, "tint": [0, 0, 0]}]
    geo = build_tracer([WHITE, WHITE], rows)
    columns = len(shot_geometry._mirrored_columns(2))
    assert colour(geo, 0) == [1, 1, 1, 1]
    assert colour(geo, columns) == [0, 0, 0, 1]


def test_p03_r01_tracer_fills_quads_between_rows_and_columns():
    rows = [{"at": 0.0, "tint": [1, 1, 1]}, {"at": 1.0, "tint": [1, 1, 1]}]
    geo = build_tracer([WHITE, WHITE], rows)
    # Columns: 1 across 2 colours (3 columns). Two quads of two triangles each.
    assert len(geo.indices) == 2 * 2 * 3


def test_p03_r01_tracer_needs_two_colours_and_two_rows(range_errors):
    with pytest.raises(ValueError, match="Need 2 colours and 2 rows"):
        build_tracer([WHITE], [{"at": 0, "tint": [1, 1, 1]}, {"at": 1, "tint": [1, 1, 1]}])
    with pytest.raises(ValueError, match="Need 2 colours and 2 rows"):
        build_tracer([WHITE, RED], [{"at": 0, "tint": [1, 1, 1]}])


def test_p03_r01_glow_bar_runs_from_y0_to_y1_across_its_width():
    geo = build_glow_bar([RED, WHITE, RED])
    columns = len(shot_geometry._mirrored_columns(3))
    assert len(geo.positions) // 3 == 2 * columns
    assert vertex(geo, 0)[:2] == pytest.approx([-0.5, 0])
    assert vertex(geo, 1)[:2] == pytest.approx([-0.5, 1])
    assert vertex(geo, 2 * (columns - 1))[0] == pytest.approx(0.5)


def test_p03_r01_glow_bar_is_coloured_from_the_centre_line_out():
    geo = build_glow_bar([RED, WHITE])
    # Columns are [edge, centre, edge]: the centre line takes colours[0].
    assert colour(geo, 0) == [1.0, 1.0, 1.0, 1]
    assert colour(geo, 2) == [1.0, 0.0, 0.0, 1]
    assert colour(geo, 4) == [1.0, 1.0, 1.0, 1]


def test_p03_r01_glow_bar_needs_two_colours(range_errors):
    with pytest.raises(ValueError, match="Need 2 colours"):
        build_glow_bar([WHITE])

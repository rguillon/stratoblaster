"""Unit tests of `src/render/scenery/imposters.py` (D-211)."""

import math

import pytest
from helpers.geometry_checks import check_colored

from game.config.record import record
from render.geometry.gradient_shapes import ColoredGeometry
from render.scenery.imposters import (
    atlas_rows,
    atlas_size,
    bake_geometry,
    frame_centre,
    frame_of,
    frame_uv,
    imposter_quad,
    quad_lift,
    view_axes,
)

LOOK = record({"headings": 8, "framePx": 64, "frameSize": 10, "centre": 1.5, "ambient": 0.75})
TILT = math.radians(35)


def test_d211_the_atlas_has_a_row_per_kind_rounded_up_to_a_power_of_two():
    assert [atlas_rows(n) for n in [1, 2, 3, 6, 8, 9]] == [1, 2, 4, 8, 8, 16]
    assert atlas_size(LOOK, 6) == [8 * 64, 8 * 64]


@pytest.mark.parametrize(
    ("rotation", "frame"),
    [(0, 0), (math.pi / 4, 1), (math.pi, 4), (-math.pi / 4, 7), (2 * math.pi - 0.01, 0)],
)
def test_d211_the_frame_is_the_nearest_heading(rotation, frame):
    assert frame_of(rotation, 8) == frame


def test_d211_frame_uvs_put_row_0_at_the_top():
    assert frame_uv(LOOK, 3, 0, 0) == pytest.approx([0, 0.75, 0.125, 1])
    assert frame_uv(LOOK, 3, 2, 7) == pytest.approx([0.875, 0.25, 1, 0.5])


def test_d211_the_view_axes_are_unit_and_square_to_each_other():
    right, up, towards = view_axes(TILT)
    for a in (right, up, towards):
        assert sum(c * c for c in a) == pytest.approx(1)
    assert sum(u * t for u, t in zip(up, towards, strict=True)) == pytest.approx(0)
    # The camera looks down: towards it goes up.
    assert towards[1] > 0


def test_d211_frames_sit_side_by_side_in_the_camera_plane():
    a = frame_centre(LOOK, 1, [0, 0], TILT)
    b = frame_centre(LOOK, 1, [0, 1], TILT)
    assert b[0] - a[0] == pytest.approx(10)


def _cube() -> ColoredGeometry:
    geo = ColoredGeometry()
    geo.positions = [0, 0, 0, 0, 1, 0, 1, 1, 0]
    geo.indices = [0, 2, 1]
    geo.colors = [1, 1, 1, 1] * 3
    return geo


def test_d211_the_bake_holds_every_frame_of_every_model_shaded():
    baked = bake_geometry([_cube(), _cube()], LOOK, TILT)
    check_colored(baked)
    assert len(baked.indices) == 2 * 8 * 3
    assert max(baked.colors) <= 1
    assert min(c for i, c in enumerate(baked.colors) if i % 4 != 3) < 1


def test_d211_a_quad_is_lifted_towards_the_camera_to_clear_the_ground():
    assert quad_lift(LOOK, TILT) > 0
    quad = imposter_quad(LOOK, TILT, [0, 0, 1, 1])
    check_colored(quad)
    assert min(quad.positions[1::3]) == pytest.approx(0.05)
    assert sorted(set(quad.uvs)) == [0, 1]


def test_d211_a_frame_high_enough_needs_no_lift():
    assert quad_lift(record({**LOOK, "centre": 10}), TILT) == 0

"""Unit tests of `src/render/environment/gradient_cube.py`."""

import math

import pytest

from render.environment import gradient_cube
from render.environment.gradient_cube import (
    GradientStop,
    build_gradient_cube_faces,
    sample_gradient,
)

BLACK = [0.0, 0.0, 0.0]
WHITE = [1.0, 1.0, 1.0]
STOPS = [GradientStop(-1, BLACK), GradientStop(0, [0.5, 0.5, 0.5]), GradientStop(1, WHITE)]


def test_a_stop_is_sampled_exactly_at_its_height() -> None:
    assert sample_gradient(STOPS, 0) == pytest.approx([0.5, 0.5, 0.5])


def test_between_two_stops_the_colour_is_interpolated() -> None:
    assert sample_gradient(STOPS, 0.5) == pytest.approx([0.75, 0.75, 0.75])
    assert sample_gradient(STOPS, -0.5) == pytest.approx([0.25, 0.25, 0.25])


def test_below_the_first_or_above_the_last_stop_the_end_colour_holds() -> None:
    assert sample_gradient(STOPS, -5) == pytest.approx(BLACK)
    assert sample_gradient(STOPS, 5) == pytest.approx(WHITE)


def test_a_sample_is_a_copy_of_the_stop_colour() -> None:
    colour = sample_gradient(STOPS, -5)
    colour[0] = 9
    assert STOPS[0].color == BLACK


def test_a_gradient_needs_a_stop() -> None:
    with pytest.raises(ValueError, match="at least one stop"):
        sample_gradient([], 0)


def test_the_faces_of_the_cube_are_rgba_bytes_of_the_gradient(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(gradient_cube, "uint8_array", lambda n: [0] * n)
    faces = build_gradient_cube_faces(2, [GradientStop(-1, [0, 0, 0]), GradientStop(1, WHITE)])
    assert len(faces) == 6
    assert all(len(face) == 2 * 2 * 4 for face in faces)
    # Alpha is always opaque.
    assert all(face[i] == 255 for face in faces for i in range(3, len(face), 4))
    # The top face is the top of the gradient (white), the bottom face the bottom (black).
    assert all(v == 255 for v in faces[2][0:3])
    assert all(v == 0 for v in faces[3][0:3])


def test_a_channel_is_clamped_and_rounded_to_a_byte(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gradient_cube, "uint8_array", lambda n: [0] * n)
    faces = build_gradient_cube_faces(
        1, [GradientStop(-1, [2.0, 0.5, -1]), GradientStop(1, [2.0, 0.5, -1])]
    )
    assert faces[0][0:4] == [255, 128, 0, 255]


def test_the_side_faces_fall_towards_the_bottom_of_the_cube() -> None:
    # Looking at the top row of a side face (v = -1), the direction points up (above the horizon).
    assert gradient_cube._side_height(0, -1) == pytest.approx(1 / math.hypot(1, 0, -1))
    # The bottom row (v = 1) points down.
    assert gradient_cube._side_height(0, 1) < 0
    assert gradient_cube._top_height(0.3, 0.3) == 1
    assert gradient_cube._bottom_height(0.3, 0.3) == -1

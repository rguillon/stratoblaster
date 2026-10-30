"""Unit tests of `src/render/environment/showcase_environment_visual.py`."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeWeakMap, patch_babylon

import render.environment.showcase_environment_visual as showcase_environment
from render.environment.gradient_cube import GradientStop
from render.environment.showcase_environment_visual import _sky_key, update_sky_environment

STOPS = [GradientStop(-1, [0, 0, 0]), GradientStop(1, [1, 0.5, 0.25])]


@pytest.fixture
def cube(monkeypatch: pytest.MonkeyPatch) -> list[Any]:
    patch_babylon(monkeypatch, showcase_environment)
    monkeypatch.setattr(showcase_environment, "LAST_SKY", FakeWeakMap())
    monkeypatch.setattr(showcase_environment, "is_raw_cube_texture", lambda t: t is not None)
    calls: list[Any] = []
    monkeypatch.setattr(
        showcase_environment,
        "update_raw_cube_texture",
        lambda texture, faces, fmt, kind, flag: calls.append((texture, faces)),
    )
    monkeypatch.setattr(
        showcase_environment,
        "build_gradient_cube_faces",
        lambda size, stops: [size] * 6,
    )
    return calls


def test_the_sky_key_is_the_rounded_colours_of_the_stops() -> None:
    assert _sky_key(STOPS) == "0,0,0;255,128,64"


def test_two_gradients_with_the_same_colours_have_the_same_key() -> None:
    same = [GradientStop(-1, [0, 0, 0]), GradientStop(1, [1, 0.5, 0.25])]
    assert _sky_key(same) == _sky_key(STOPS)


def test_the_environment_intensity_is_always_set() -> None:
    scene = SimpleNamespace(environmentIntensity=0, environmentTexture=None)
    update_sky_environment(scene, 4, STOPS, 0.6)
    assert scene.environmentIntensity == 0.6


def test_a_cube_is_rebuilt_only_when_the_gradient_changed(cube: list[Any]) -> None:
    texture = object()
    scene = SimpleNamespace(environmentIntensity=0, environmentTexture=texture)
    update_sky_environment(scene, 4, STOPS, 1)
    update_sky_environment(scene, 4, STOPS, 1)
    assert len(cube) == 1
    update_sky_environment(scene, 4, [GradientStop(0, [1, 1, 1])], 1)
    assert len(cube) == 2


def test_the_cube_is_rebuilt_with_six_faces_of_the_cube_size(cube: list[Any]) -> None:
    texture = object()
    scene = SimpleNamespace(environmentIntensity=0, environmentTexture=texture)
    update_sky_environment(scene, 8, STOPS, 1)
    assert cube == [(texture, [8] * 6)]


def test_a_scene_without_a_cube_texture_is_left_alone(cube: list[Any]) -> None:
    scene = SimpleNamespace(environmentIntensity=0, environmentTexture=None)
    update_sky_environment(scene, 4, STOPS, 1)
    assert cube == []

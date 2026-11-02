# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/environment/showcase_environment_visual.py`."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeWeakMap, patch_babylon

import render.environment.showcase_environment_visual as showcase_environment
from render.environment.gradient_cube import GradientStop
from render.environment.showcase_environment_visual import (
    ShowcaseEnvironmentOptions,
    ShowcaseGlow,
    _sky_key,
    apply_showcase_environment,
    update_sky_environment,
)

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
        lambda texture, faces, _fmt, _kind, _flag: calls.append((texture, faces)),
    )
    monkeypatch.setattr(
        showcase_environment,
        "build_gradient_cube_faces",
        lambda size, _stops: [size] * 6,
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


def test_perf_30_the_sky_lighting_is_set_from_the_new_faces_after_each_update(
    cube: list[Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    # An update keeps the old polynomial, and reading the cube back from the GPU stalls.
    lit: list[Any] = []
    monkeypatch.setattr(
        showcase_environment,
        "set_cube_sphere_lighting",
        lambda texture, faces, size: lit.append((texture, faces, size)),
    )
    texture = object()
    scene = SimpleNamespace(environmentIntensity=0, environmentTexture=texture)
    update_sky_environment(scene, 4, STOPS, 1)
    assert lit == [(texture, cube[0][1], 4)]


def test_gfx_art_02_a_scene_is_lit_by_its_sky_gradient_tone_mapped_and_given_a_glow_layer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ENG-114, ENG-126, PERF-30: the lighting comes from the faces built here, not the GPU."""
    patch_babylon(monkeypatch, showcase_environment)
    faces = ["face"] * 6
    built: list[Any] = []
    textures: list[Any] = []
    lit: list[Any] = []
    layers: list[Any] = []
    texture = SimpleNamespace()
    layer = SimpleNamespace()

    def build(size: int, stops: list[GradientStop]) -> list[str]:
        built.append((size, stops))
        return faces

    def raw_cube(*args: Any) -> SimpleNamespace:
        textures.append(args)
        return texture

    def glow(*args: Any) -> SimpleNamespace:
        layers.append(args)
        return layer

    monkeypatch.setattr(showcase_environment, "build_gradient_cube_faces", build)
    monkeypatch.setattr(showcase_environment, "new_raw_cube_texture", raw_cube)
    monkeypatch.setattr(
        showcase_environment, "set_cube_sphere_lighting", lambda *args: lit.append(args)
    )
    monkeypatch.setattr(showcase_environment, "image_processing_tone_mapping_aces", lambda: "ACES")
    monkeypatch.setattr(showcase_environment, "new_glow_layer", glow)
    scene = SimpleNamespace(imageProcessingConfiguration=SimpleNamespace())
    options = ShowcaseEnvironmentOptions(16, 0.9, STOPS, ShowcaseGlow(0.6, 32, 0.25, 4))

    result = apply_showcase_environment(scene, options)

    assert built == [(16, STOPS)]
    assert textures == [
        (scene, faces, 16, "TEXTUREFORMAT_RGBA", "TEXTURETYPE_UNSIGNED_BYTE", True),
    ]
    assert lit == [(texture, faces, 16)]
    assert scene.environmentTexture is texture
    assert scene.environmentIntensity == 0.9
    assert scene.imageProcessingConfiguration.toneMappingEnabled is True
    assert scene.imageProcessingConfiguration.toneMappingType == "ACES"
    assert layers == [("glow", scene, 32, 0.25, 4)]
    assert result is layer
    assert layer.intensity == 0.6


def test_gfx_terrain_15_a_glow_leaves_its_resolution_to_babylon_by_default() -> None:
    glow = ShowcaseGlow(1.0, 16)
    assert (glow.intensity, glow.blur_kernel_size) == (1.0, 16)
    assert glow.ratio is None
    assert glow.samples is None

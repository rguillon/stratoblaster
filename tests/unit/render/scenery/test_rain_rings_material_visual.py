# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/rain_rings_material_visual.py`: rings (GFX-WEATHER-09)."""

from types import SimpleNamespace

import pytest
from helpers.render_core_shaders import RecordingMaterial, check_uniforms, patch_shader_babylon

from render.scenery import rain_rings_material_visual
from render.scenery.rain_rings_material_visual import create_rain_rings_material

RINGS = SimpleNamespace(
    cell=4.0, per_cell=0.6, radius=1.5, period=1.2, alpha=0.4, color=[0.7, 0.8, 1]
)
FOG = SimpleNamespace(color=[0.4, 0.45, 0.5], start=60, end=500)


@pytest.fixture
def made(monkeypatch: pytest.MonkeyPatch) -> list[RecordingMaterial]:
    return patch_shader_babylon(monkeypatch, rain_rings_material_visual)


def test_gfx_weather_09_the_rings_are_blended_without_writing_depth(
    made: list[RecordingMaterial],
) -> None:
    rings = create_rain_rings_material(SimpleNamespace(activeCamera=None), RINGS)
    (material,) = made
    assert rings.material is material
    assert material.label == "rain-rings"
    assert material.need_alpha_blending is True
    assert material.disableDepthWrite is True
    assert material.uniforms == {"rings": (4.0, 0.6, 1.5, 1.2), "ringColor": (0.7, 0.8, 1)}


def test_gfx_weather_09_each_frame_sets_the_time_strength_haze_and_camera(
    made: list[RecordingMaterial],
) -> None:
    eye = object()
    scene = SimpleNamespace(activeCamera=SimpleNamespace(globalPosition=eye))
    rings = create_rain_rings_material(scene, RINGS)
    rings.set(SimpleNamespace(time=9.0, strength=0.5, fog=FOG))
    (material,) = made
    assert material.uniforms["state"] == (9.0, 0.5, 0.4)
    assert material.uniforms["fogColor"] == (0.4, 0.45, 0.5)
    assert material.uniforms["fogRange"] == (60, 500)
    assert material.uniforms["cameraPosition"] is eye
    check_uniforms(material)


def test_without_a_camera_the_rings_keep_their_last_camera_position(
    made: list[RecordingMaterial],
) -> None:
    rings = create_rain_rings_material(SimpleNamespace(activeCamera=None), RINGS)
    rings.set(SimpleNamespace(time=1.0, strength=1.0, fog=FOG))
    (material,) = made
    assert "cameraPosition" not in material.uniforms
    assert material.uniforms["state"] == (1.0, 1.0, 0.4)

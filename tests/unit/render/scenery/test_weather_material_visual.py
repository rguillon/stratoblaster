# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/weather_material_visual.py`: particles (GFX-WEATHER-02)."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_core_shaders import RecordingMaterial, check_uniforms, patch_shader_babylon

from render.scenery import weather_material_visual
from render.scenery.weather_material_visual import create_weather_material

VOLUME = SimpleNamespace(half_width=300, length_=500, bottom=-20, top=200)
FOG = SimpleNamespace(color=[0.5, 0.5, 0.55], start=100, end=900)


def _kind(**fields: Any) -> SimpleNamespace:
    """Return snow: soft discs drifting down, blended, blown by a wind growing with the strength."""
    kind = SimpleNamespace(
        align="camera",
        blend="alpha",
        flicker=None,
        fade_high=None,
        volume=VOLUME,
        color=[1, 1, 1],
        alpha=0.6,
        wind=[2.0, 10.0],
        fall=[3.0, 5.0],
        size=[0.4, 0.8],
        streak=4.0,
        sway=[0.5, 0.25],
    )
    for key, value in fields.items():
        setattr(kind, key, value)
    return kind


def _frame(strength: float) -> SimpleNamespace:
    return SimpleNamespace(
        time=7.0,
        strength=strength,
        start=1.5,
        camera_position="eye",
        right="right",
        up="up",
        fog=FOG,
    )


@pytest.fixture
def made(monkeypatch: pytest.MonkeyPatch) -> list[RecordingMaterial]:
    return patch_shader_babylon(monkeypatch, weather_material_visual)


def test_gfx_weather_07_snow_is_blended_discs_in_a_box_of_air(
    made: list[RecordingMaterial],
) -> None:
    weather = create_weather_material(object(), _kind())
    (material,) = made
    assert weather.material is material
    assert material.label == "weather"
    assert material.attributes == ["position", "flake"]
    assert material.need_alpha_blending is True
    assert material.backFaceCulling is False
    assert material.disableDepthWrite is True
    # Blended, Babylon's default alpha mode.
    assert not hasattr(material, "alphaMode")
    assert material.uniforms == {
        "additive": 0,
        "spark": (0, 0, 0),
        "volume": (300, 500, -20, 200),
        "particleColor": (1, 1, 1),
        "particleAlpha": 0.6,
        "align": 0,
    }


def test_gfx_weather_14_embers_are_added_sparks_that_flicker_and_fade_high(
    made: list[RecordingMaterial],
) -> None:
    kind = _kind(blend="add", flicker=SimpleNamespace(amount=0.5, hz=3.0), fade_high=0.8)
    create_weather_material(object(), kind)
    (material,) = made
    assert material.alphaMode == "ALPHA_ONEONE"
    assert material.uniforms["additive"] == 1
    assert material.uniforms["spark"] == (0.5, 3.0, 0.8)


def test_gfx_weather_08_rain_is_drawn_along_its_fall_streaked_at_every_strength(
    made: list[RecordingMaterial],
) -> None:
    weather = create_weather_material(object(), _kind(align="fall"))
    weather.set(_frame(0.5))
    (material,) = made
    assert material.uniforms["align"] == 1
    assert material.uniforms["shape"] == (0.4, 0.8, 4.0, 0.5)


def test_gfx_weather_02_each_frame_sets_motion_shape_drift_camera_and_haze(
    made: list[RecordingMaterial],
) -> None:
    weather = create_weather_material(object(), _kind())
    weather.set(_frame(0.5))
    (material,) = made
    # The wind grows with the strength; the streaks grow with its square.
    assert material.uniforms["motion"] == (7.0, 3.0, 5.0, 6.0)
    assert material.uniforms["shape"] == (0.4, 0.8, 4.0 * 0.25, 0.5)
    assert material.uniforms["drift"] == (1.5, 0.25)
    assert material.uniforms["cameraPosition"] == "eye"
    assert material.uniforms["cameraRight"] == "right"
    assert material.uniforms["cameraUp"] == "up"
    assert material.uniforms["fogColor"] == (0.5, 0.5, 0.55)
    assert material.uniforms["fogRange"] == (100, 900)
    check_uniforms(material)


@pytest.mark.parametrize(("strength", "wind"), [(-1.0, 2.0), (3.0, 10.0)])
def test_the_strength_is_kept_between_0_and_1(
    made: list[RecordingMaterial], strength: float, wind: float
) -> None:
    weather = create_weather_material(object(), _kind())
    weather.set(_frame(strength))
    (material,) = made
    assert material.uniforms["motion"][3] == wind

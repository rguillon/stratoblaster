# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/cloud_material_visual.py`: the clouds (GFX-SKY-11)."""

from types import SimpleNamespace

import pytest
from helpers.render_core_shaders import RecordingMaterial, check_uniforms, patch_shader_babylon

from render.scenery import cloud_material_visual
from render.scenery.cloud_material_visual import UNIFORMS, create_cloud_material

LOOK = SimpleNamespace(altitude=120, softness=0.1, tileSize=400)


@pytest.fixture
def made(monkeypatch: pytest.MonkeyPatch) -> list[RecordingMaterial]:
    return patch_shader_babylon(monkeypatch, cloud_material_visual)


def test_gfx_sky_11_a_cloud_layer_is_blended_over_its_noise_texture(
    made: list[RecordingMaterial],
) -> None:
    texture = object()
    clouds = create_cloud_material(object(), LOOK, texture, lambda: None)
    (material,) = made
    assert clouds.material is material
    assert material.label == "cloud-120"
    assert material.samplers == ["cloudTexture"]
    assert material.need_alpha_blending is True
    assert material.backFaceCulling is False
    assert material.disableDepthWrite is True
    assert material.uniforms == {"cloudTexture": texture}
    # The material gets its own copy of the uniform names.
    assert material.declared == UNIFORMS
    assert material.declared is not UNIFORMS


def test_gfx_sky_13_each_frame_sets_coverage_colours_haze_and_camera(
    made: list[RecordingMaterial],
) -> None:
    camera = SimpleNamespace(x=0, y=50, z=-10)
    clouds = create_cloud_material(object(), LOOK, object(), lambda: camera)
    state = SimpleNamespace(
        coverage=0.3,
        opacity=0.8,
        offset_x=5,
        offset_z=-7,
        color=[1, 0.9, 0.8],
        shade=[0.4, 0.4, 0.5],
        fog=SimpleNamespace(color=[0.6, 0.7, 0.8], start=200, end=1600),
    )
    clouds.set(state)
    (material,) = made
    assert material.uniforms["cloudParams"] == (0.3, 0.8, 0.1, 1 / 400)
    assert material.uniforms["cloudOffset"] == (5, -7)
    assert material.uniforms["cloudColor"] == (1, 0.9, 0.8)
    assert material.uniforms["cloudShade"] == (0.4, 0.4, 0.5)
    assert material.uniforms["fogColor"] == (0.6, 0.7, 0.8)
    assert material.uniforms["fogRange"] == (200, 1600)
    assert material.uniforms["cameraPosition"] is camera
    check_uniforms(material)

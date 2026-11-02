# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/aurora_material_visual.py`: the aurora (GFX-SKY-17)."""

from types import SimpleNamespace

import pytest
from helpers.render_core_shaders import RecordingMaterial, check_uniforms, patch_shader_babylon

from render.scenery import aurora_material_visual
from render.scenery.aurora_material_visual import create_aurora_material


@pytest.fixture
def made(monkeypatch: pytest.MonkeyPatch) -> list[RecordingMaterial]:
    return patch_shader_babylon(monkeypatch, aurora_material_visual)


def test_gfx_sky_17_the_aurora_is_added_on_top_without_writing_depth(
    made: list[RecordingMaterial],
) -> None:
    scene = object()
    aurora = create_aurora_material(scene)
    (material,) = made
    assert aurora.material is material
    assert material.label == "aurora"
    assert material.scene is scene
    assert material.attributes == ["position"]
    assert material.samplers is None
    assert material.need_alpha_blending is True
    assert material.alphaMode == "ALPHA_ADD"
    assert material.backFaceCulling is False
    assert material.disableDepthWrite is True


def test_gfx_sky_17_each_frame_sets_the_time_strength_fog_and_camera(
    made: list[RecordingMaterial],
) -> None:
    aurora = create_aurora_material(object())
    camera = SimpleNamespace(x=1, y=2, z=3)
    frame = SimpleNamespace(
        time=12.5, strength=0.75, fog=SimpleNamespace(start=100, end=900), camera_position=camera
    )
    aurora.set(frame)
    (material,) = made
    assert material.uniforms == {
        "auroraParams": (12.5, 0.75),
        "fogRange": (100, 900),
        "cameraPosition": camera,
    }
    check_uniforms(material)

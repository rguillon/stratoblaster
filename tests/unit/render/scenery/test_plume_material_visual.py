# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/plume_material_visual.py`: a plume's puffs (GFX-PROP-18)."""

from types import SimpleNamespace

import pytest
from helpers.render_core_shaders import RecordingMaterial, check_uniforms, patch_shader_babylon

from render.scenery import plume_material_visual
from render.scenery.plume_material_visual import _lit_channel, create_plume_material

KIND = SimpleNamespace(
    seconds=6.0,
    height=40.0,
    lean=0.3,
    size=[2.0, 9.0],
    alpha=0.7,
    color=[0.8, 0.6, 0.4],
    self_lit=0.25,
)


@pytest.fixture
def made(monkeypatch: pytest.MonkeyPatch) -> list[RecordingMaterial]:
    return patch_shader_babylon(monkeypatch, plume_material_visual)


def test_gfx_prop_18_a_plume_is_blended_puffs_with_their_rise_and_size(
    made: list[RecordingMaterial],
) -> None:
    plume = create_plume_material(object(), KIND)
    (material,) = made
    assert plume.material is material
    assert material.label == "plume"
    assert material.attributes == ["position", "puff", "puffScale"]
    assert material.need_alpha_blending is True
    assert material.backFaceCulling is False
    assert material.disableDepthWrite is True
    assert material.uniforms == {
        "motion": (0, 6.0, 40.0, 0.3),
        "size": (2.0, 9.0),
        "plumeAlpha": 0.7,
    }


def test_gfx_prop_18_a_channel_is_lit_by_the_scene_but_never_below_its_self_lit_share() -> None:
    # Dark night: the self-lit share; daylight: the light, up to the full colour.
    assert _lit_channel(KIND, [0.1, 0.5, 2.0], 0) == pytest.approx(0.8 * 0.25)
    assert _lit_channel(KIND, [0.1, 0.5, 2.0], 1) == pytest.approx(0.6 * 0.5)
    assert _lit_channel(KIND, [0.1, 0.5, 2.0], 2) == pytest.approx(0.4 * 1)


def test_gfx_prop_18_each_frame_sets_the_time_the_light_the_camera_and_the_haze(
    made: list[RecordingMaterial],
) -> None:
    plume = create_plume_material(object(), KIND)
    eye, right, up = object(), object(), object()
    frame = SimpleNamespace(
        time=2.5,
        light=[1.0, 1.0, 0.1],
        camera_position=eye,
        right=right,
        up=up,
        fog=SimpleNamespace(color=[0.5, 0.5, 0.6], start=80, end=700),
    )
    plume.set(frame)
    (material,) = made
    assert material.uniforms["motion"] == (2.5, 6.0, 40.0, 0.3)
    assert material.uniforms["plumeColor"] == pytest.approx((0.8, 0.6, 0.4 * 0.25))
    assert material.uniforms["cameraPosition"] is eye
    assert material.uniforms["cameraRight"] is right
    assert material.uniforms["cameraUp"] is up
    assert material.uniforms["fogColor"] == (0.5, 0.5, 0.6)
    assert material.uniforms["fogRange"] == (80, 700)
    check_uniforms(material)

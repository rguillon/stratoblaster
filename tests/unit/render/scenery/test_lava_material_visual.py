# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/lava_material_visual.py`: the lava (GFX-TERRAIN-16)."""

from types import SimpleNamespace

import pytest
from helpers.render_core_shaders import RecordingMaterial, check_uniforms, patch_shader_babylon

from render.scenery import lava_material_visual
from render.scenery.lava_material_visual import LavaFrame, create_lava_material

LOOK = SimpleNamespace(
    cell=6,
    crack=0.2,
    churn=0.05,
    intensity=1.5,
    crust=[0.1, 0.05, 0.05],
    plate=[0.2, 0.1, 0.1],
    glow=[1, 0.3, 0],
    hot=[1, 0.9, 0.6],
)
FOG = SimpleNamespace(color=[0.3, 0.2, 0.2], start=50, end=800)


@pytest.fixture
def made(monkeypatch: pytest.MonkeyPatch) -> list[RecordingMaterial]:
    return patch_shader_babylon(monkeypatch, lava_material_visual)


def test_gfx_terrain_16_the_lava_gets_its_plates_and_colours_once(
    made: list[RecordingMaterial],
) -> None:
    lava = create_lava_material(SimpleNamespace(activeCamera=None), LOOK, (1.0, -2.0))
    (material,) = made
    assert lava.material is material
    assert material.label == "lava"
    # Opaque: no samplers, Babylon's own blending.
    assert material.samplers is None
    assert material.need_alpha_blending is None
    assert material.uniforms == {
        "shape": (6, 0.2, 0.05, 1.5),
        "crustColor": (0.1, 0.05, 0.05),
        "plateColor": (0.2, 0.1, 0.1),
        "glowColor": (1, 0.3, 0),
        "hotColor": (1, 0.9, 0.6),
    }


def test_gfx_terrain_16_each_frame_sets_the_flow_the_haze_and_the_camera(
    made: list[RecordingMaterial],
) -> None:
    eye = SimpleNamespace(x=0, y=40, z=-60)
    scene = SimpleNamespace(activeCamera=SimpleNamespace(globalPosition=eye))
    lava = create_lava_material(scene, LOOK, (1.0, -2.0))
    lava.set(LavaFrame(3.5, FOG))
    (material,) = made
    assert material.uniforms["motion"] == (3.5, 1.0, -2.0)
    assert material.uniforms["fogColor"] == (0.3, 0.2, 0.2)
    assert material.uniforms["fogRange"] == (50, 800)
    assert material.uniforms["cameraPosition"] is eye
    check_uniforms(material)


@pytest.mark.parametrize(
    "camera", [None, SimpleNamespace(globalPosition=None)], ids=["no-camera", "no-position"]
)
def test_the_camera_position_waits_for_a_camera_with_a_position(
    made: list[RecordingMaterial], camera: object
) -> None:
    lava = create_lava_material(SimpleNamespace(activeCamera=camera), LOOK, (0.0, 0.0))
    lava.set(LavaFrame(1.0, FOG))
    (material,) = made
    assert "cameraPosition" not in material.uniforms
    assert material.uniforms["motion"] == (1.0, 0.0, 0.0)

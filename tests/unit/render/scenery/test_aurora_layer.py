# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/aurora_layer.py`: its sheet and frames (GFX-SKY-17)."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeNode, FakeVector, patch_babylon

from render.scenery import aurora_layer
from render.scenery.aurora_layer import AURORA_ALPHA_INDEX, AuroraFrame, AuroraLayer
from render.scenery.cloud_layers import BELOW_CLOUDS_GROUP

GROUNDS: list[tuple[Any, ...]] = []


class _Material:
    """The aurora's material: the frames it was set to."""

    def __init__(self) -> None:
        self.material = "aurora-material"
        self.frames: list[AuroraFrame] = []

    def set(self, frame: AuroraFrame) -> None:
        self.frames.append(frame)


def _create_ground(name: str, width: float, length: float, subdivisions: int, scene: Any) -> Any:
    GROUNDS.append((name, width, length, subdivisions, scene))
    return FakeNode(name, is_mesh=True)


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    GROUNDS.clear()
    patch_babylon(monkeypatch, aurora_layer)
    monkeypatch.setattr(aurora_layer, "create_ground", _create_ground)


# What the camera sees of the aurora's plane: 100 either side, from 50 to 650 ahead.
SEEN = SimpleNamespace(half_width=100, z_near=50, z_far=650)


def _layer() -> tuple[AuroraLayer, _Material]:
    material = _Material()
    return AuroraLayer("scene", material, (SEEN, 180, 10)), material


def test_gfx_sky_17_an_aurora_frame_keeps_what_it_shows() -> None:
    camera = FakeVector(0, 1, 2)
    frame = AuroraFrame(3.5, 0.7, camera, "fog")
    assert (frame.time, frame.strength) == (3.5, 0.7)
    assert frame.camera_position is camera
    assert frame.fog == "fog"


def test_gfx_sky_17_the_sheet_covers_the_view_with_its_margin_high_above_hidden() -> None:
    layer, _material = _layer()
    assert GROUNDS == [("aurora", 2 * (100 + 10), 600 + 2 * 10, 1, "scene")]
    mesh = layer.mesh
    assert mesh.position.y == 180
    assert mesh.material == "aurora-material"
    assert mesh.isPickable is False
    # Drawn after the clouds and the weather, over the ground's depth.
    assert mesh.renderingGroupId == BELOW_CLOUDS_GROUP + 1
    assert mesh.alphaIndex == AURORA_ALPHA_INDEX
    assert mesh.enabled is False


def test_gfx_sky_17_the_aurora_shows_and_follows_the_camera_while_the_sky_has_one() -> None:
    layer, material = _layer()
    camera = FakeVector(0, 300, 1000)
    layer.update(SimpleNamespace(aurora=0.6, fog="fog"), 12.0, camera)
    assert layer.mesh.enabled is True
    # The sheet's middle stays over the middle of the view.
    assert layer.mesh.position.z == 1000 + (50 + 650) / 2
    [frame] = material.frames
    assert (frame.time, frame.strength, frame.fog) == (12.0, 0.6, "fog")
    assert frame.camera_position is camera


def test_gfx_sky_17_without_an_aurora_the_sheet_is_hidden_and_its_material_left_alone() -> None:
    layer, material = _layer()
    layer.update(SimpleNamespace(aurora=0.6, fog="fog"), 1.0, FakeVector(0, 0, 0))
    layer.mesh.position.z = 77
    layer.update(SimpleNamespace(aurora=0, fog="fog"), 2.0, FakeVector(0, 0, 500))
    assert layer.mesh.enabled is False
    assert layer.mesh.position.z == 77
    assert len(material.frames) == 1

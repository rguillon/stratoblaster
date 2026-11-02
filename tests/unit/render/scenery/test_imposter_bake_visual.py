# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/imposter_bake_visual.py`: the imposters' bake (D-211).

The Babylon objects are fakes: a scene with its render targets and its after-render observable, a
mesh that is ready when the test says, a camera, a render target texture, materials.
"""

import math
from types import SimpleNamespace
from typing import Any

import pytest
from fixtures.sample_game import record
from helpers.render_fakes import FakeSettable, FakeVector, patch_babylon

from render.geometry.gradient_shapes import ColoredGeometry
from render.scenery import imposter_bake_visual
from render.scenery.imposter_bake_visual import (
    BAKE_AT,
    BAKE_DISTANCE,
    BAKE_LAYER,
    BRIGHTER,
    READY_FRAMES,
    ImposterAtlas,
)
from render.scenery.imposters import atlas_size, bake_geometry, view_axes

LOOK = record({"headings": 4, "framePx": 64, "frameSize": 10, "centre": 1.5, "ambient": 0.75})
TILT = math.radians(35)
# The JavaScript-only helper as the module defines it, taken before the fixture replaces it.
REMOVE = imposter_bake_visual._remove


class Disposable:
    """A Babylon object (material, mesh, camera) that can be disposed of."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.disposed = False

    def dispose(self) -> None:
        self.disposed = True


class FakeMesh(Disposable):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.data: Any = None
        self.ready = False
        self.material: Any = None

    def isReady(self, complete: bool) -> bool:
        assert complete
        return self.ready


class FakeCamera(Disposable):
    def __init__(self, name: str, position: FakeVector) -> None:
        super().__init__(name)
        self.position = position
        self.target: FakeVector | None = None

    def setTarget(self, target: FakeVector) -> None:
        self.target = target


class FakeObservable:
    """`scene.onAfterRenderObservable`: the callbacks added, by the token `add` returns."""

    def __init__(self) -> None:
        self.callbacks: dict[int, Any] = {}

    def add(self, callback: Any) -> int:
        token = len(self.callbacks) + 1
        self.callbacks[token] = callback
        return token

    def remove(self, token: int) -> None:
        del self.callbacks[token]

    def notify(self) -> None:
        for callback in list(self.callbacks.values()):
            callback()


class FakeScene:
    def __init__(self) -> None:
        self.customRenderTargets: list[Any] = ["other target"]
        self.onAfterRenderObservable = FakeObservable()
        self.meshes: list[FakeMesh] = []
        self.cameras: list[FakeCamera] = []


BABYLON_CLASSES = {
    "Camera": SimpleNamespace(ORTHOGRAPHIC_CAMERA="orthographic"),
    "Texture": SimpleNamespace(CLAMP_ADDRESSMODE="clamp"),
}


@pytest.fixture
def scene(monkeypatch: pytest.MonkeyPatch) -> FakeScene:
    module = imposter_bake_visual
    patch_babylon(monkeypatch, module)

    def new_mesh(name: str, in_scene: FakeScene) -> FakeMesh:
        mesh = FakeMesh(name)
        in_scene.meshes.append(mesh)
        return mesh

    def new_free_camera(name: str, position: FakeVector, in_scene: FakeScene) -> FakeCamera:
        camera = FakeCamera(name, position)
        in_scene.cameras.append(camera)
        return camera

    monkeypatch.setattr(module, "new_mesh", new_mesh)
    monkeypatch.setattr(module, "new_vertex_data", SimpleNamespace)
    monkeypatch.setattr(module, "apply_vertex_data", lambda data, mesh: setattr(mesh, "data", data))
    monkeypatch.setattr(module, "new_standard_material", lambda name, _scene: Disposable(name))
    monkeypatch.setattr(module, "new_free_camera", new_free_camera)
    monkeypatch.setattr(module, "babylon_class", BABYLON_CLASSES.__getitem__)
    monkeypatch.setattr(
        module,
        "new_render_target_texture",
        lambda name, size, _scene: SimpleNamespace(name=name, size=size),
    )
    monkeypatch.setattr(
        module, "_remove", lambda array, value: array.remove(value) if value in array else None
    )
    return FakeScene()


def _model() -> ColoredGeometry:
    geo = ColoredGeometry()
    geo.positions = [0, 0, 0, 1, 0, 0, 0, 0, 1]
    geo.indices = [0, 1, 2]
    geo.colors = [1, 0.5, 0.25, 1] * 3
    return geo


def _values(color: Any) -> tuple[float, ...]:
    settable: FakeSettable = color
    return settable.values


def test_d211_the_removal_from_a_javascript_array_is_javascript_only() -> None:
    """`array.splice(array.indexOf(value), 1)` is a `__pragma__("js")` body.

    CPython runs nothing of it: the list is left as it is.
    """
    array = ["a", "b"]
    assert REMOVE(array, "a") is None
    assert array == ["a", "b"]


def test_d211_the_atlas_is_a_clear_clamped_render_target_of_every_frame(scene: FakeScene) -> None:
    atlas = ImposterAtlas(scene, LOOK, 3, 0.8)
    texture = atlas.texture
    assert texture.name == "imposter-atlas"
    assert texture.size == atlas_size(LOOK, 3)
    assert _values(texture.clearColor) == (0, 0, 0, 0)
    assert texture.hasAlpha
    assert (texture.wrapU, texture.wrapV) == ("clamp", "clamp")
    assert not atlas.baked


def test_d211_the_imposters_are_drawn_from_the_atlas_a_little_brighter(scene: FakeScene) -> None:
    material = ImposterAtlas(scene, LOOK, 3, 0.8).material
    assert material.name == "imposters"
    assert material.diffuseTexture.name == "imposter-atlas"
    assert _values(material.diffuseColor) == pytest.approx((0.8 * BRIGHTER,) * 3)
    assert _values(material.specularColor) == (0, 0, 0)
    assert material.backFaceCulling is False


def test_d211_the_bake_mesh_holds_every_frame_unlit_out_of_every_view(scene: FakeScene) -> None:
    atlas = ImposterAtlas(scene, LOOK, 1, 1)
    atlas.bake([_model()], TILT)
    [mesh] = scene.meshes
    expected = bake_geometry([_model()], LOOK, TILT)
    assert mesh.data.positions == expected.positions
    assert mesh.data.indices == expected.indices
    assert mesh.data.colors == expected.colors
    assert (mesh.position.x, mesh.position.y, mesh.position.z) == tuple(BAKE_AT)
    assert mesh.layerMask == BAKE_LAYER
    assert mesh.isPickable is False
    material = mesh.material
    assert material.disableLighting
    assert _values(material.emissiveColor) == (1, 1, 1)
    assert _values(material.diffuseColor) == (0, 0, 0)
    assert _values(material.specularColor) == (0, 0, 0)
    assert material.fogEnabled is False
    assert material.backFaceCulling is True


def test_d211_the_bake_camera_sees_the_frames_as_the_playfield_camera(scene: FakeScene) -> None:
    atlas = ImposterAtlas(scene, LOOK, 3, 1)
    atlas.bake([_model()], TILT)
    [camera] = scene.cameras
    towards = view_axes(TILT)[2]
    position = (camera.position.x, camera.position.y, camera.position.z)
    assert position == pytest.approx([BAKE_AT[i] + towards[i] * BAKE_DISTANCE for i in range(3)])
    assert camera.target is not None
    assert (camera.target.x, camera.target.y, camera.target.z) == tuple(BAKE_AT)
    assert camera.mode == "orthographic"
    # 4 frames of 10 units across, 4 rows (3 kinds) of 10 units up.
    assert (camera.orthoLeft, camera.orthoRight) == (-20, 20)
    assert (camera.orthoBottom, camera.orthoTop) == (-20, 20)
    assert (camera.minZ, camera.maxZ) == (1, BAKE_DISTANCE * 2)
    assert camera.layerMask == BAKE_LAYER
    texture = atlas.texture
    assert texture.activeCamera is camera
    assert texture.renderList == scene.meshes
    assert scene.customRenderTargets == ["other target", texture]


def test_d211_the_bake_waits_for_its_mesh_to_be_ready(scene: FakeScene) -> None:
    atlas = ImposterAtlas(scene, LOOK, 1, 1)
    atlas.bake([_model()], TILT)
    for _ in range(READY_FRAMES + 2):
        scene.onAfterRenderObservable.notify()
    assert not atlas.baked
    assert atlas.texture in scene.customRenderTargets


def test_d211_once_drawn_ready_the_bake_drops_what_drew_it(scene: FakeScene) -> None:
    atlas = ImposterAtlas(scene, LOOK, 1, 1)
    atlas.bake([_model()], TILT)
    [mesh] = scene.meshes
    [camera] = scene.cameras
    mesh.ready = True
    for _ in range(READY_FRAMES - 1):
        scene.onAfterRenderObservable.notify()
    assert not atlas.baked
    scene.onAfterRenderObservable.notify()
    assert atlas.baked
    assert scene.customRenderTargets == ["other target"]
    assert scene.onAfterRenderObservable.callbacks == {}
    assert atlas.texture.renderList == []
    assert atlas.texture.activeCamera is None
    assert mesh.material.disposed
    assert mesh.disposed
    assert camera.disposed

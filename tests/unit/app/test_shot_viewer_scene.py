# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/shot_viewer_scene.py`: the ship lying on the playfield.

The Babylon helpers are the `render_fakes` ones (with recorded world matrices here).
"""

import math
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeNode, FakeScene, FakeVector, patch_babylon

from app import shot_viewer_scene
from app.shot_viewer_scene import PlayfieldShip


class FakeScaling:
    def __init__(self) -> None:
        self.all: float | None = None

    def setAll(self, value: float) -> None:
        self.all = value


class ModelNode(FakeNode):
    """A node of a ship model: its vertices and top, and when its world matrix was computed."""

    def __init__(
        self, scene: "ModelScene", name: str, is_mesh: bool, top: float = 0, vertices: int = 0
    ) -> None:
        super().__init__(name, scene.next_id(), is_mesh)
        self.scene = scene
        self.scaling = FakeScaling()
        self.vertices = vertices
        self.top = top

    def computeWorldMatrix(self, _force: bool) -> None:
        assert self.scene is not None
        self.scene.computed.append(self.name)

    def getTotalVertices(self) -> int:
        return self.vertices

    def getBoundingInfo(self) -> Any:
        return SimpleNamespace(boundingBox=SimpleNamespace(maximumWorld=FakeVector(0, self.top, 0)))


class ModelScene(FakeScene):
    """A scene whose nodes are `ModelNode`s, and the order their world matrices were computed in."""

    def __init__(self) -> None:
        super().__init__()
        self.computed: list[str] = []

    def add_node(self, name: str = "", is_mesh: bool = False) -> FakeNode:
        node = ModelNode(self, name, is_mesh)
        (self.meshes if is_mesh else self.transformNodes).append(node)
        return node


class Recorder:
    def __init__(self) -> None:
        self.animated: list[tuple[Any, float]] = []


@pytest.fixture
def render(monkeypatch: pytest.MonkeyPatch) -> Recorder:
    patch_babylon(monkeypatch, shot_viewer_scene)
    fake = Recorder()
    monkeypatch.setattr(
        shot_viewer_scene,
        "is_instance_of",
        # A light of a model is a node, but no transform node.
        lambda node, name: name == "TransformNode" and not node.name.startswith("light"),
    )
    monkeypatch.setattr(
        shot_viewer_scene,
        "step_model_animations",
        lambda node, dt: fake.animated.append((node, dt)),
    )
    return fake


def _xyz(vector: Any) -> tuple[float, float, float]:
    return (vector.x, vector.y, vector.z)


def _model(meshes: list[tuple[str, float, int]]) -> Any:
    """Return a ship model factory: a root and its meshes, each with its top and vertex count."""

    def factory(scene: ModelScene) -> ModelNode:
        root = ModelNode(scene, "model", False)
        ModelNode(scene, "light", False).parent = root
        for name, top, vertices in meshes:
            ModelNode(scene, name, True, top, vertices).parent = root
        return root

    return factory


def test_gfx_shot_05_the_muzzle_is_at_the_ship_s_nose_tip(render: Recorder) -> None:
    """Also DEV-MENU-12 (the ship lies nose up, top towards the camera)."""
    del render
    scene = ModelScene()
    ship = PlayfieldShip(scene, 2.5, 100, 40)
    assert _xyz(ship.pivot.position) == (100, 40, 0)
    # The empty mesh's bounding box is left out.
    nose = ship.show(_model([("hull", 70, 30), ("nothing", 300, 0), ("wing", 55, 12)]))
    assert nose == 70
    (holder,) = ship.pivot.children
    assert holder.name == "playfield-ship-model"
    assert holder.rotation.x == pytest.approx(-math.pi / 2)
    assert holder.scaling.all == 2.5
    assert [child.name for child in holder.children] == ["model"]
    # Parents first: each world matrix uses its parent's, up to date; the light has none.
    assert scene.computed == [
        "playfield-ship",
        "playfield-ship-model",
        "model",
        "hull",
        "nothing",
        "wing",
    ]


def test_gfx_shot_05_a_model_without_meshes_has_its_muzzle_at_the_pivot(render: Recorder) -> None:
    del render
    ship = PlayfieldShip(ModelScene(), 1, 0, 25)
    assert ship.show(_model([])) == 25
    # A nose under the pivot does not move the muzzle down.
    assert ship.show(_model([("low", 10, 3)])) == 25


def test_dev_menu_12_showing_another_ship_replaces_the_model(render: Recorder) -> None:
    del render
    ship = PlayfieldShip(ModelScene(), 1, 0, 0)
    ship.show(_model([("hull", 5, 3)]))
    first = ship._model
    ship.show(_model([("hull", 8, 3)]))
    assert first.disposed is True
    assert ship._model is not first
    assert ship._model.disposed is False


def test_dev_menu_12_the_model_s_animation_advances_once_shown(render: Recorder) -> None:
    ship = PlayfieldShip(ModelScene(), 1, 0, 0)
    ship.update(0.02)
    assert render.animated == []
    ship.show(_model([("hull", 5, 3)]))
    ship.update(0.02)
    assert render.animated == [(ship._model, 0.02)]

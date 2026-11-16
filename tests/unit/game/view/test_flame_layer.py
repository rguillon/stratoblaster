# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/flame_layer.py`: a scene's flames drawn together (D-428)."""

from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from game.view import flame_layer as fl

IDENTITY = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


class FakeScene:
    """A scene: its frame number, its glow layers and what runs before its meshes are found."""

    def __init__(self) -> None:
        self.frame = 0
        self.effectLayers: list[Any] | None = []
        self.before: list[Any] = []
        self.onBeforeActiveMeshesEvaluationObservable = SimpleNamespace(add=self.before.append)

    def getFrameId(self) -> int:
        return self.frame

    def next_frame(self) -> None:
        self.frame += 1
        for callback in self.before:
            callback(self, None)


class FakeFlame:
    """A flame: a node, and one cone written per call."""

    def __init__(self, batch: Any, shown: bool = True) -> None:
        self.node = MagicMock()
        self.node.isDisposed.return_value = False
        self.node.isEnabled.return_value = shown
        self._batch = batch
        self.worlds: list[Any] = []

    def write(self, world: Any) -> None:
        self.worlds.append(list(world))
        self._batch.add(world, [1, 1, 1], 0, [1, 1, 1], 1)


@pytest.fixture
def babylon(monkeypatch: Any) -> SimpleNamespace:
    """Babylon stand-ins: the meshes and materials made, matrices as lists, layers by scene."""
    made = SimpleNamespace(meshes=[], materials=[], layers={}, marked=[], world=list(IDENTITY))

    def mesh(name: str, options: Any, _scene: Any) -> Any:
        made.meshes.append(MagicMock(name=name))
        made.meshes[-1].label = name
        made.meshes[-1].options = options
        return made.meshes[-1]

    def material(name: str, _scene: Any) -> Any:
        made.materials.append(MagicMock(name=name))
        return made.materials[-1]

    def relative(_node: Any, _inverse: Any, target: Any) -> None:
        target.m = list(made.world)

    monkeypatch.setattr(fl, "create_cylinder", mesh)
    monkeypatch.setattr(fl, "create_polyhedron", mesh)
    monkeypatch.setattr(fl, "_cone_options", lambda sides: ("cone", sides))
    monkeypatch.setattr(fl, "_polyhedron_options", lambda kind: ("polyhedron", kind))
    monkeypatch.setattr(fl, "new_standard_material", material)
    monkeypatch.setattr(fl, "color3", lambda r, g, b: (r, g, b))
    monkeypatch.setattr(fl, "color3_black", lambda: (0, 0, 0))
    monkeypatch.setattr(fl, "babylon_constant", lambda key: key)
    monkeypatch.setattr(fl, "mark_glows_as_drawn", made.marked.append)
    monkeypatch.setattr(fl, "_new_matrix", lambda: MagicMock(m=list(IDENTITY)))
    monkeypatch.setattr(fl, "_world_to_ref", lambda _node, _target: None)
    monkeypatch.setattr(fl, "_relative_to_ref", relative)
    monkeypatch.setattr(fl, "weak_map_get", lambda _map, key: made.layers.get(id(key)))
    monkeypatch.setattr(
        fl, "weak_map_set", lambda _map, key, value: made.layers.__setitem__(id(key), value)
    )
    return made


def test_the_javascript_helpers_have_python_fallbacks() -> None:
    assert fl._floats(3) == [0.0, 0.0, 0.0]
    assert fl._cone_options(6) is None
    assert fl._polyhedron_options(0) is None
    assert fl._new_matrix() is None
    assert fl._world_to_ref(None, None) is None
    assert fl._relative_to_ref(None, None, None) is None


@pytest.mark.usefixtures("babylon")
def test_d428_a_scene_has_one_flame_layer() -> None:
    scene = FakeScene()
    layer = fl.flame_layer(scene)
    assert fl.flame_layer(scene) is layer
    assert fl.flame_layer(FakeScene()) is not layer
    # It draws before the scene works out its meshes, once.
    assert len(scene.before) == 1


@pytest.mark.usefixtures("babylon")
def test_d428_the_cones_of_a_number_of_sides_share_one_unit_mesh() -> None:
    layer = fl.FlameLayer(FakeScene())
    cones = layer.cones(6)
    assert layer.cones(6) is cones
    assert layer.cones(8) is not cones
    mesh = cones.mesh
    assert (mesh.label, mesh.options) == ("flame-cones-6", ("cone", 6))
    # Its tip to -Z, its base at the origin, baked into its vertices.
    assert mesh.rotation.x == pytest.approx(-3.141592653589793 / 2)
    assert mesh.position.z == -0.5
    mesh.bakeCurrentTransformIntoVertices.assert_called_once_with()


def test_d428_a_batch_s_mesh_is_unlit_blended_never_culled_and_glows_as_drawn(
    babylon: SimpleNamespace,
) -> None:
    layer = fl.FlameLayer(FakeScene())
    puffs = layer.puffs(3)
    assert layer.puffs(3) is puffs
    mesh = puffs.mesh
    assert (mesh.label, mesh.options) == ("flame-puffs-3", ("polyhedron", 3))
    # One material for every batch.
    (material,) = babylon.materials
    assert layer.cones(6).mesh.material is material
    assert mesh.material is material
    assert material.emissiveColor == (1, 1, 1)
    assert material.disableLighting is True
    assert material.backFaceCulling is False
    assert material.alphaMode == "ALPHA_COMBINE"
    assert material.alpha < 1
    assert material.disableDepthWrite is True
    assert mesh.hasVertexAlpha is True
    assert mesh.isPickable is False
    assert mesh.alwaysSelectAsActiveMesh is True
    assert mesh.doNotSyncBoundingInfo is True
    assert mesh in babylon.marked
    # Nothing to draw yet.
    mesh.setEnabled.assert_called_once_with(False)


def test_d428_an_instance_is_scaled_moved_along_z_then_placed_and_tinted() -> None:
    batch = fl.Batch(MagicMock())
    # A world matrix turned a quarter round Y (X to -Z, Z to X), moved to (10, 20, 30).
    world = [0, 0, -1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 10, 20, 30, 1]
    batch.add(world, [2, 3, 4], 5, [0.1, 0.2, 0.3], 0.5)
    assert batch.count == 1
    assert batch.matrices[:16] == [0, 0, -2, 0, 0, 3, 0, 0, 4, 0, 0, 0, 15, 20, 30, 1]
    assert batch.colors[:4] == [0.1, 0.2, 0.3, 0.5]


def test_d428_a_batch_s_buffers_grow_and_keep_what_they_held() -> None:
    mesh = MagicMock()
    batch = fl.Batch(mesh)
    for i in range(fl.LEAST_CAPACITY + 1):
        batch.add(IDENTITY, [i, 1, 1], 0, [i, 0, 0], 1)
    assert batch.capacity == fl.LEAST_CAPACITY * 2
    assert [batch.matrices[i * 16] for i in range(batch.count)] == list(
        range(fl.LEAST_CAPACITY + 1)
    )
    assert [batch.colors[i * 4] for i in range(batch.count)] == list(range(fl.LEAST_CAPACITY + 1))
    # New buffers are handed to the mesh; the same ones are only updated.
    batch.upload()
    assert mesh.thinInstanceCount == fl.LEAST_CAPACITY + 1
    assert [call.args[0] for call in mesh.thinInstanceSetBuffer.call_args_list] == [
        "matrix",
        "color",
    ]
    mesh.thinInstanceBufferUpdated.assert_not_called()
    batch.add(IDENTITY, [1, 1, 1], 0, [1, 1, 1], 1)
    batch.upload()
    assert mesh.thinInstanceCount == 1
    assert [call.args[0] for call in mesh.thinInstanceBufferUpdated.call_args_list] == [
        "matrix",
        "color",
    ]
    assert mesh.thinInstanceSetBuffer.call_count == 2


def test_d428_a_batch_with_no_instance_is_hidden() -> None:
    mesh = MagicMock()
    batch = fl.Batch(mesh)
    batch.upload()
    mesh.setEnabled.assert_called_once_with(False)
    mesh.thinInstanceBufferUpdated.assert_not_called()
    batch.add(IDENTITY, [1, 1, 1], 0, [1, 1, 1], 1)
    batch.upload()
    mesh.setEnabled.assert_called_with(True)
    assert batch.count == 0


def test_d428_each_frame_the_flames_shown_are_written_once(babylon: SimpleNamespace) -> None:
    scene = FakeScene()
    layer = fl.flame_layer(scene)
    # No flame, no mesh: nothing to do.
    scene.next_frame()
    cones = layer.cones(6)
    shown = FakeFlame(cones)
    hidden = FakeFlame(cones, shown=False)
    layer.add(shown)
    layer.add(hidden)
    babylon.world = [2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 7, 8, 9, 1]
    scene.next_frame()
    # The flame is given its node's matrix, seen from the layer's meshes.
    assert shown.worlds == [babylon.world]
    assert hidden.worlds == []
    assert cones.mesh.thinInstanceCount == 1
    # The scene finds its meshes several times a frame (a glow layer): written once.
    for callback in scene.before:
        callback(scene, None)
    assert len(shown.worlds) == 1
    scene.next_frame()
    assert len(shown.worlds) == 2


@pytest.mark.usefixtures("babylon")
def test_d428_a_flame_whose_node_is_disposed_is_dropped() -> None:
    scene = FakeScene()
    layer = fl.flame_layer(scene)
    cones = layer.cones(6)
    gone = FakeFlame(cones)
    kept = FakeFlame(cones)
    layer.add(gone)
    layer.add(kept)
    gone.node.isDisposed.return_value = True
    scene.next_frame()
    assert gone.worlds == []
    assert len(kept.worlds) == 1
    gone.node.isDisposed.return_value = False
    scene.next_frame()
    # Dropped for good.
    assert gone.worlds == []


@pytest.mark.usefixtures("babylon")
def test_d428_every_glow_layer_draws_the_flames_with_their_own_material_once() -> None:
    scene = FakeScene()
    layer = fl.flame_layer(scene)
    cones = layer.cones(6)
    glow = MagicMock()
    other = SimpleNamespace(referenceMeshToUseItsOwnMaterial=None)
    scene.effectLayers = [glow, other]
    scene.next_frame()
    glow.referenceMeshToUseItsOwnMaterial.assert_called_once_with(cones.mesh)
    scene.next_frame()
    assert glow.referenceMeshToUseItsOwnMaterial.call_count == 1
    # A mesh made later, and a layer added later, are each told of the other, once.
    puffs = layer.puffs(0)
    late = MagicMock()
    scene.effectLayers.append(late)
    scene.next_frame()
    assert [call.args[0] for call in glow.referenceMeshToUseItsOwnMaterial.call_args_list] == [
        cones.mesh,
        puffs.mesh,
    ]
    assert [call.args[0] for call in late.referenceMeshToUseItsOwnMaterial.call_args_list] == [
        cones.mesh,
        puffs.mesh,
    ]


@pytest.mark.usefixtures("babylon")
def test_d428_a_scene_without_glow_layers_still_draws_its_flames() -> None:
    scene = FakeScene()
    scene.effectLayers = None
    layer = fl.flame_layer(scene)
    flame = FakeFlame(layer.cones(6))
    layer.add(flame)
    scene.next_frame()
    assert len(flame.worlds) == 1

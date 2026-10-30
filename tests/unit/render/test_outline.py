"""Unit tests of `src/render/outline.py`."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeNode, FakeScene, patch_babylon

from render import outline
from render.outline import (
    OutlineLayer,
    OutlineLook,
    compile_outlines,
    outline_model,
    outline_of,
    outlines_ready,
    set_outline,
)


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, outline)


def _mesh(**fields: Any) -> FakeNode:
    node = FakeNode("mesh", is_mesh=True)
    node.material = fields.pop("material", SimpleNamespace(alpha=1, alphaMode=0))
    for key, value in fields.items():
        setattr(node, key, value)
    return node


def test_a_mesh_asks_for_a_rim_glow_by_its_outline_colour() -> None:
    mesh = _mesh()
    set_outline(mesh, [1, 0.5, 0])
    assert outline_of(mesh) == [1, 0.5, 0]


def test_setting_an_outline_keeps_the_other_metadata() -> None:
    mesh = _mesh()
    mesh.metadata = {"kind": "ship"}
    set_outline(mesh, [0, 1, 0])
    assert mesh.metadata == {"kind": "ship", "outline": [0, 1, 0]}


def test_a_mesh_without_an_outline_has_none() -> None:
    assert outline_of(_mesh()) is None


def test_outline_model_outlines_only_the_solid_meshes() -> None:
    scene = FakeScene()
    root = scene.add_node("root")
    solid = scene.add_node("solid", is_mesh=True)
    solid.material = SimpleNamespace(alpha=1, alphaMode=0)
    glass = scene.add_node("glass", is_mesh=True)
    glass.material = SimpleNamespace(alpha=0.5, alphaMode=0)
    flame = scene.add_node("flame", is_mesh=True)
    flame.material = SimpleNamespace(alpha=1, alphaMode="ALPHA_ADD")
    vertex_alpha = scene.add_node("veined", is_mesh=True)
    vertex_alpha.material = SimpleNamespace(alpha=1, alphaMode=0)
    vertex_alpha.hasVertexAlpha = True
    no_material = scene.add_node("bare", is_mesh=True)
    no_material.material = None
    root.children = [solid, glass, flame, vertex_alpha, no_material]

    outline_model(root, [0, 0, 1])

    assert outline_of(solid) == [0, 0, 1]
    assert outline_of(glass) is None
    assert outline_of(flame) is None
    assert outline_of(vertex_alpha) is None
    assert outline_of(no_material) is None


def test_the_layer_gives_a_rim_only_to_a_mesh_that_asks_for_one() -> None:
    layer = OutlineLayer(OutlineLook(width=2, intensity=0.5))
    mesh = _mesh()
    assert layer.add(mesh) is False
    set_outline(mesh, [1, 0, 0])
    assert layer.add(mesh) is True
    assert mesh.renderOutline is True
    assert mesh.outlineColor.values == pytest.approx((0.5, 0, 0))
    assert mesh.outlineWidth == pytest.approx(2)


def test_the_rim_width_undoes_the_scale_of_the_mesh() -> None:
    layer = OutlineLayer(OutlineLook(width=2, intensity=1))
    mesh = _mesh()
    mesh.absoluteScaling = SimpleNamespace(x=-4, y=4, z=4)
    set_outline(mesh, [0, 1, 0])
    layer.add(mesh)
    assert mesh.outlineWidth == pytest.approx(0.5)


def test_a_zero_scale_counts_as_one() -> None:
    layer = OutlineLayer(OutlineLook(width=3, intensity=1))
    mesh = _mesh()
    mesh.absoluteScaling = SimpleNamespace(x=0, y=1, z=1)
    set_outline(mesh, [0, 1, 0])
    layer.add(mesh)
    assert mesh.outlineWidth == pytest.approx(3)


def test_a_node_that_is_not_a_mesh_gets_no_rim() -> None:
    layer = OutlineLayer(OutlineLook(width=1, intensity=1))
    node = FakeNode("transform")
    set_outline(node, [0, 1, 0])
    assert layer.add(node) is False


class _Renderer:
    def __init__(self, ready_after: int) -> None:
        self.calls = 0
        self.ready_after = ready_after

    def isReady(self, sub: Any, use_instances: bool) -> bool:  # noqa: N802
        self.calls += 1
        return self.calls > self.ready_after


def _outlined(renderer: _Renderer, subs: int = 2) -> FakeNode:
    mesh = _mesh()
    mesh.renderOutline = True
    mesh.subMeshes = [object()] * subs
    mesh.scene = SimpleNamespace(getOutlineRenderer=lambda: renderer)  # type: ignore[assignment]
    mesh.getScene = lambda: mesh.scene  # type: ignore[method-assign]
    return mesh


def test_compile_asks_the_rim_shader_of_each_sub_mesh_once() -> None:
    renderer = _Renderer(ready_after=0)
    compile_outlines([_outlined(renderer, subs=3)])
    assert renderer.calls == 3


def test_outlines_are_ready_once_every_shader_is_compiled() -> None:
    renderer = _Renderer(ready_after=2)
    meshes = [_outlined(renderer, subs=2)]
    assert outlines_ready(meshes) is False  # The first sub-mesh is not compiled yet.
    assert outlines_ready(meshes) is False
    assert outlines_ready(meshes) is True  # Both are ready from the third call on.


def test_meshes_without_a_rim_are_skipped_when_compiling() -> None:
    renderer = _Renderer(ready_after=0)
    plain = _mesh()
    compile_outlines([plain])
    assert renderer.calls == 0
    assert outlines_ready([plain]) is True

"""Unit tests of `src/render/edge_trim_mesh.py`: models get their glowing edge trim as child
meshes."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeNode, FakeScene, FakeWeakMap, patch_babylon

from render import edge_trim_mesh
from render.edge_trim_mesh import (
    add_edge_trim,
    clear_trim,
    is_solid,
    request_trim,
    set_trim,
    set_trim_group,
    trim_of,
)
from render.geometry.edge_trim import IDENTITY, TrimOptions
from render.geometry.solids import SolidBuilder

CYAN = [0.3, 0.9, 1.0]


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, edge_trim_mesh)
    monkeypatch.setattr(edge_trim_mesh, "_MATERIALS", FakeWeakMap())
    monkeypatch.setattr(edge_trim_mesh, "mesh_positions", lambda mesh: mesh.positions)
    monkeypatch.setattr(edge_trim_mesh, "mesh_indices", lambda mesh: mesh.indices)
    monkeypatch.setattr(edge_trim_mesh, "world_matrix", lambda node: node.matrix)
    monkeypatch.setattr(edge_trim_mesh, "compute_normals", lambda p, i: [])
    monkeypatch.setattr(
        edge_trim_mesh,
        "vertex_data_of",
        lambda p, i, n, c: SimpleNamespace(positions=p, indices=i, colors=c),
    )

    def apply(data: Any, mesh: Any) -> None:
        mesh.data = data

    monkeypatch.setattr(edge_trim_mesh, "apply_vertex_data", apply)
    monkeypatch.setattr(
        edge_trim_mesh, "new_standard_material", lambda label, scene: SimpleNamespace(name=label)
    )


def _box_mesh(scene: FakeScene, parent: FakeNode, name: str, size: list[float]) -> FakeNode:
    geo = SolidBuilder().box(size, [1, 1, 1]).geometry
    mesh = scene.add_node(name, is_mesh=True)
    mesh.scene = scene
    mesh.positions = geo.positions
    mesh.indices = geo.indices
    mesh.matrix = list(IDENTITY)
    mesh.material = SimpleNamespace(alpha=1, alphaMode=0)
    mesh.parent = parent
    return mesh


def _root(scene: FakeScene) -> FakeNode:
    root = scene.add_node("root")
    root.matrix = list(IDENTITY)
    return root


def test_a_mesh_asks_for_a_trim_and_keeps_its_metadata() -> None:
    mesh = FakeNode("m", is_mesh=True)
    mesh.metadata = {"kind": "ship"}
    set_trim(mesh, CYAN)
    assert trim_of(mesh) == CYAN
    assert mesh.metadata["kind"] == "ship"


def test_only_solid_meshes_are_asked_to_trim() -> None:
    scene = FakeScene()
    root = _root(scene)
    solid = _box_mesh(scene, root, "solid", [1, 1, 1])
    glass = _box_mesh(scene, root, "glass", [1, 1, 1])
    glass.material = SimpleNamespace(alpha=0.5, alphaMode=0)
    flame = _box_mesh(scene, root, "flame", [1, 1, 1])
    flame.material = SimpleNamespace(alpha=1, alphaMode="ALPHA_ADD")
    request_trim(root, CYAN)
    assert trim_of(solid) == CYAN
    assert trim_of(glass) is None
    assert trim_of(flame) is None
    assert not is_solid(FakeNode("bare", is_mesh=True))


def test_each_trimmed_mesh_gets_a_child_trim_in_its_colour() -> None:
    scene = FakeScene()
    root = _root(scene)
    mesh = _box_mesh(scene, root, "hull", [2, 1, 2])
    set_trim(mesh, CYAN)
    (trim,) = add_edge_trim(root, TrimOptions(0.1, 0))
    assert trim.parent is mesh
    assert trim.name == "hull-trim"
    assert trim.material.emissiveColor.values == (0.3, 0.9, 1.0)
    assert trim.material.disableLighting is True
    assert trim.applyFog is False
    assert trim.material.backFaceCulling is False
    assert len(trim.data.indices) // 3 == 12
    # The trim does not ask for a trim of its own.
    assert trim_of(trim) is None


def test_meshes_of_one_colour_share_a_material() -> None:
    scene = FakeScene()
    root = _root(scene)
    a = _box_mesh(scene, root, "a", [1, 1, 1])
    b = _box_mesh(scene, root, "b", [1, 1, 1])
    b.matrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 5, 0, 0, 1]
    request_trim(root, CYAN)
    trims = add_edge_trim(root, TrimOptions(0.1, 0))
    assert len(trims) == 2
    assert trims[0].material is trims[1].material
    assert a.children and b.children


def test_a_covered_mesh_gets_no_trim_and_a_cleared_one_neither() -> None:
    scene = FakeScene()
    root = _root(scene)
    big = _box_mesh(scene, root, "big", [4, 1, 4])
    small = _box_mesh(scene, root, "small", [1, 1, 1])
    small.matrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1]
    stump_node = scene.add_node("stump")
    stump_node.parent = root
    stump = _box_mesh(scene, stump_node, "stump-mesh", [1, 1, 1])
    stump.matrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 9, 0, 0, 1]
    request_trim(root, CYAN)
    clear_trim(stump_node)
    trims = add_edge_trim(root, TrimOptions(0.1, 0))
    assert [t.parent for t in trims] == [big]


def test_a_model_with_nothing_to_trim_gets_nothing() -> None:
    scene = FakeScene()
    assert add_edge_trim(_root(scene), TrimOptions(0.1, 0)) == []


def test_a_trim_group_is_trimmed_along_its_own_outline() -> None:
    scene = FakeScene()
    root = _root(scene)
    big = _box_mesh(scene, root, "hull", [4, 1, 4])
    group = scene.add_node("part")
    group.parent = root
    set_trim_group(group)
    small = _box_mesh(scene, group, "part-mesh", [1, 1, 1])
    small.matrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1]
    request_trim(root, CYAN)
    trims = add_edge_trim(root, TrimOptions(0.1, 0))
    # The part on the hull keeps its outline; the hull keeps its own.
    assert sorted(t.parent.name for t in trims) == ["hull", "part-mesh"]
    assert big.children and small.children

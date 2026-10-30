"""Unit tests of `src/render/node_adopter.py`."""

import pytest
from helpers.render_fakes import NUMBER_MAX_VALUE, FakeNode, FakeScene, patch_babylon

from render import node_adopter
from render.node_adopter import ON_TOP_ALPHA_INDEX, NodeAdopter, newer


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, node_adopter)


def test_newer_keeps_the_items_created_after_the_given_number() -> None:
    scene = FakeScene()
    nodes = [scene.add_node(f"n{i}") for i in range(4)]
    assert newer(nodes, 2) == nodes[2:]
    assert newer(nodes, 0) == nodes
    assert newer(nodes, 99) == []
    assert newer([], 0) == []


def test_run_returns_what_create_returned() -> None:
    scene = FakeScene()
    adopter = NodeAdopter(scene, FakeNode("root"), 1)
    assert adopter.run(lambda: 42) == 42


def test_nodes_created_by_run_are_parented_to_the_root() -> None:
    scene = FakeScene()
    root = FakeNode("root")
    old = scene.add_node("old")
    adopter = NodeAdopter(scene, root, 2)

    def create() -> str:
        scene.add_node("made-node")
        return "done"

    adopter.run(create)
    made = scene.transformNodes[1]
    assert made.parent is root
    assert old.parent is None


def test_a_node_that_already_has_a_parent_keeps_it() -> None:
    scene = FakeScene()
    root = FakeNode("root")
    other = FakeNode("other")
    adopter = NodeAdopter(scene, root, 2)

    def create() -> None:
        node = scene.add_node("kept")
        node.parent = other

    adopter.run(create)
    assert scene.transformNodes[0].parent is other


def test_the_root_is_never_parented_to_itself() -> None:
    scene = FakeScene()
    root = scene.add_node("root")
    adopter = NodeAdopter(scene, root, 2)
    adopter.run(lambda: None)
    assert root.parent is None


def test_new_meshes_get_the_rendering_group_and_the_on_top_draw_order() -> None:
    scene = FakeScene()
    adopted: list[FakeNode] = []
    adopter = NodeAdopter(scene, FakeNode("root"), 3, on_mesh=adopted.append)

    def create() -> None:
        scene.add_node("plain", is_mesh=True)
        ordered = scene.add_node("ordered", is_mesh=True)
        ordered.alphaIndex = 5

    adopter.run(create)
    plain, ordered = scene.meshes
    assert plain.renderingGroupId == 3
    assert plain.alphaIndex == ON_TOP_ALPHA_INDEX - 1
    assert ordered.alphaIndex == 5
    assert adopted == [plain, ordered]
    assert NUMBER_MAX_VALUE > ON_TOP_ALPHA_INDEX


def test_meshes_are_adopted_even_when_create_fails() -> None:
    scene = FakeScene()
    root = FakeNode("root")
    adopter = NodeAdopter(scene, root, 1)

    def create() -> None:
        scene.add_node("half-built")
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        adopter.run(create)
    assert scene.transformNodes[0].parent is root

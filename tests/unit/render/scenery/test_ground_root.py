"""Unit tests of `src/render/scenery/ground_root.py`."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeNode, FakeScene, FakeSettable, patch_babylon

from render import node_adopter
from render.scenery import ground_root
from render.scenery.ground_root import GroundRoot, ground_window_of
from render.scenery.playfield_framing import PlayfieldFraming


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, ground_root)
    # `newer` (node_adopter) reads the node numbers too.
    patch_babylon(monkeypatch, node_adopter)

    def transform(label: str, scene: FakeScene) -> FakeNode:
        node = scene.add_node(label)
        node.scaling = FakeSettable(1, 1, 1)
        node.scaling.setAll = lambda value: node.scaling.set(value, value, value)  # type: ignore[attr-defined]
        return node

    monkeypatch.setattr(ground_root, "new_transform_node", transform)


def test_the_ground_node_is_scaled_by_the_ground_scale() -> None:
    root = GroundRoot(FakeScene(), 2.5)
    assert root.node.scaling.values == (2.5, 2.5, 2.5)


def test_moving_the_view_moves_the_ground_so_the_scale_is_kept() -> None:
    root = GroundRoot(FakeScene(), 2)
    root.move_to(100)
    assert root.node.position.z == pytest.approx(-100)
    # The ground under the view is still where it was: it moves 1 unit in ground for 2 in world.
    assert root.to_ground(root.to_world(40)) == pytest.approx(40)


def test_a_scale_of_one_leaves_the_ground_where_it_is() -> None:
    root = GroundRoot(FakeScene(), 1)
    root.move_to(50)
    assert root.node.position.z == 0
    assert root.to_world(7) == pytest.approx(7)


def test_ground_and_world_coordinates_are_inverse_of_each_other() -> None:
    root = GroundRoot(FakeScene(), 3)
    root.move_to(30)
    for z in (-5.0, 0.0, 12.5):
        assert root.to_world(root.to_ground(z)) == pytest.approx(z)


def test_the_transform_describes_the_scale_and_the_offset_for_the_terrain() -> None:
    root = GroundRoot(FakeScene(), 2)
    root.move_to(10)
    transform = root.transform
    assert transform.scale == 2
    assert transform.offset_z == pytest.approx(-10)


def test_adopt_hangs_what_is_made_from_the_ground_unless_it_has_a_parent() -> None:
    scene = FakeScene()
    root = GroundRoot(scene, 2)
    other = FakeNode("other")

    def create() -> None:
        scene.add_node("tree", is_mesh=True)
        kept = scene.add_node("kept")
        kept.parent = other

    root.adopt(create)
    tree = scene.meshes[0]
    assert tree.parent is root.node
    assert scene.transformNodes[1].parent is other
    assert root.node.parent is None


def test_the_ground_window_is_the_visible_ground_in_ground_units(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[tuple[Any, ...]] = []

    def fake_visible(framing: Any, aspect: float, camera_y: float, low: float, high: float) -> Any:
        seen.append((aspect, camera_y, low, high))
        return SimpleNamespace(z_near=8.0, z_far=40.0, half_width=12.0)

    monkeypatch.setattr(ground_root, "visible_ground", fake_visible)
    monkeypatch.setattr(ground_root, "lowest_ground", lambda level: 5.0)
    options = SimpleNamespace(
        screen=SimpleNamespace(width=400, height=600),
        camera=SimpleNamespace(flightAltitude=100),
        level=object(),
    )
    framing = PlayfieldFraming(0.5, 0.3, 200, -10, (0, 1))
    window = ground_window_of(options, framing, scale=2)

    assert seen == [(400 / 600, 100 + 200, 10.0, 100)]
    assert (window.z_near, window.z_far, window.half_width) == (4, 20, 6)

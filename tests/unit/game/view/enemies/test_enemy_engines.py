"""Unit tests of `src/game/view/enemies/enemy_engines.py`."""

import math
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from game.view.enemies import enemy_engines as ee
from game.view.enemies.enemy_engines import Reactor, add_reactors, add_rotors, spin_animation
from render.geometry.solids import SolidBuilder


def test_spin_animation_turns_its_node_about_y_by_its_rate_each_step():
    node = SimpleNamespace(rotation=SimpleNamespace(y=0.0))
    animate = spin_animation(node, 2.0)
    animate(0.5)
    assert node.rotation.y == pytest.approx(1.0)
    animate(0.25)
    assert node.rotation.y == pytest.approx(1.5)


def test_reactor_is_a_place_and_a_radius():
    reactor = Reactor([1, 2, 3], 0.5)
    assert reactor.at == [1, 2, 3]
    assert reactor.radius == 0.5


def _scene_root():
    root = MagicMock()
    root.getScene.return_value = "scene"
    return root


@pytest.fixture
def babylon(monkeypatch):
    """Nodes are mocks; meshes built from geometry are recorded; flames are not drawn."""
    nodes: list[MagicMock] = []

    def new_node(label, scene):
        node = MagicMock(name=label)
        node.label = label
        nodes.append(node)
        return node

    meshes: list[tuple[str, object]] = []

    def mesh_of(name, geo, material, scene):
        meshes.append((name, geo))
        return MagicMock()

    flames: list[object] = []
    monkeypatch.setattr(ee, "new_transform_node", new_node)
    monkeypatch.setattr(ee, "node_name", lambda node: node.label)
    monkeypatch.setattr(ee, "mesh_of", mesh_of)
    monkeypatch.setattr(ee, "enemy_color", lambda color: color)
    monkeypatch.setattr(ee, "flame_materials", lambda scene, color: ("flame", color))
    monkeypatch.setattr(
        ee, "build_reactor_flame", lambda name, options, node, mats: flames.append(options)
    )
    monkeypatch.setattr(ee, "add_model_animation", lambda node, animation: None)
    return SimpleNamespace(nodes=nodes, meshes=meshes, flames=flames)


def test_p05_each_rotor_is_a_hub_and_a_set_of_blades_on_a_node_at_its_place(babylon):
    root = _scene_root()
    add_rotors("gnat", [Reactor([2, 0, 0], 2.1)], MagicMock(), root)
    node = babylon.nodes[0]
    assert node.label == "gnat-rotor-0"
    node.position.set.assert_called_once_with(2, 0, 0)
    assert node.parent is root
    name, geo = babylon.meshes[0]
    assert name == "gnat-rotor-0-blades"
    # The blades are slabs of the rotor's look, and the hub is a cylinder: both have faces.
    assert len(geo.positions) > 0


def test_p05_the_blades_of_a_rotor_are_spread_round_its_hub(babylon):
    add_rotors("gnat", [Reactor([0, 0, 0], 1.0)], MagicMock(), _scene_root())
    geo = babylon.meshes[0][1]
    xz = list(zip(geo.positions[0::3], geo.positions[2::3], strict=True))
    radii = [math.hypot(x, z) for x, z in xz]
    # The blade's far corner is (-0.08, 0.95) of the rotor's radius: the blades reach that far.
    assert max(radii) == pytest.approx(math.hypot(-0.08, 0.95), abs=1e-6)


def test_a_reactor_is_a_nozzle_and_a_flame_on_a_node_at_its_place(babylon):
    parts = SimpleNamespace(hull=SolidBuilder(), neon=SolidBuilder())
    add_reactors("gnat", [Reactor([0, 1, -4], 1.0)], parts, _scene_root())
    node = babylon.nodes[0]
    assert node.label == "gnat-reactor-0"
    node.position.set.assert_called_once_with(0, 1, 0)
    options = babylon.flames[0]
    assert options["nozzleZ"] == pytest.approx(-4 - 0.05)
    assert options["light"] == {"puffs": ee.ENEMY_LOOK.reactor.puffs}
    # The nozzle is a hull ring and its core lies in the neon.
    assert len(parts.hull.geometry.positions) > 0
    assert len(parts.neon.geometry.positions) > 0

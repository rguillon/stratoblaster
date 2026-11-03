# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/enemy_mesh.py`."""

from types import SimpleNamespace
from typing import Any

import pytest

from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies import enemy_mesh
from game.view.enemies.enemy_materials import body_color, enemy_color, rim_of
from game.view.enemies.enemy_mesh import (
    Wing,
    WingParts,
    collect_parts,
    flutter_animation,
    wing_parts_new,
)
from game.view.enemies.living_motion import flutter_angle
from render.geometry.solids import SolidBuilder


def _draw_everything(p: Any) -> None:
    p.hull.box([1, 1, 1], [0, 0, 0])
    p.flesh.box([1, 1, 1], [0, 0, 0])
    p.neon.box([1, 1, 1], [1, 0, 0])
    p.reactor([0, 0, -4], 1.0)
    p.rotor([2, 0, 0], 2.1)
    p.rotor([-2, 0, 0], 2.1)
    p.muzzle([0, 0, 5], "gun")
    p.muzzle([1, 0, 5], "cannon")
    p.muzzle([2, 0, 5], None)
    p.flap([1, 0, 0], 1, 3.0, lambda w: w.flesh.box([1, 1, 1], [0, 0, 0]))


def test_collect_parts_gathers_the_reactors_rotors_muzzles_and_wings_of_a_drawing() -> None:
    collected = collect_parts(_draw_everything)
    assert [r.at for r in collected["reactors"]] == [[0, 0, -4]]
    assert [r.radius for r in collected["reactors"]] == [1.0]
    assert [r.at for r in collected["rotors"]] == [[2, 0, 0], [-2, 0, 0]]
    assert len(collected["wings"]) == 1
    assert collected["muzzles"] == [[[0, 0, 5], "gun"], [[1, 0, 5], "cannon"], [[2, 0, 5], "gun"]]


def test_collect_parts_keeps_the_body_builders_with_their_geometry() -> None:
    parts = collect_parts(_draw_everything)["parts"]
    assert len(parts.hull.geometry.positions) > 0
    assert len(parts.flesh.geometry.positions) > 0
    assert len(parts.neon.geometry.positions) > 0
    # Nothing was drawn as a charge light, nor on the vein.
    assert len(parts.charge.geometry.positions) == 0
    assert len(parts.vein.geometry.positions) == 0


def test_collect_parts_draws_a_wing_on_its_own_builders_with_its_hinge_and_span() -> None:
    collected = collect_parts(_draw_everything)
    wing = collected["wings"][0]
    assert isinstance(wing, Wing)
    assert wing.pivot == [1, 0, 0]
    assert wing.side == 1
    assert wing.span == 3.0
    assert len(wing.parts.flesh.geometry.positions) > 0


def test_collect_parts_of_an_empty_drawing_is_empty() -> None:
    collected = collect_parts(lambda _p: None)
    assert collected["reactors"] == []
    assert collected["rotors"] == []
    assert collected["wings"] == []
    assert collected["muzzles"] == []
    assert len(collected["parts"].charge.geometry.positions) == 0


def test_wing_parts_new_is_four_empty_solid_builders() -> None:
    parts = wing_parts_new()
    assert isinstance(parts, WingParts)
    for builder in (parts.hull, parts.flesh, parts.neon, parts.vein):
        assert isinstance(builder, SolidBuilder)
        assert len(builder.geometry.positions) == 0


def test_enm_42_flutter_animation_rolls_the_wing_node_as_the_clock_says() -> None:
    node = SimpleNamespace(rotation=SimpleNamespace(z=0.0))
    clock = [0.0]
    animate = flutter_animation(node, -1, 5.0, clock)
    clock[0] = 0.3
    animate(0.016)
    assert node.rotation.z == pytest.approx(flutter_angle(-1, 5.0, 0.3))


def test_enm_42_the_flutter_clock_is_read_at_each_frame_not_when_made() -> None:
    node = SimpleNamespace(rotation=SimpleNamespace(z=0.0))
    clock = [0.0]
    animate = flutter_animation(node, 1, 0.5, clock)
    animate(0)
    assert node.rotation.z == pytest.approx(0)
    clock[0] = 0.1
    animate(0)
    assert node.rotation.z == pytest.approx(flutter_angle(1, 0.5, 0.1))


def test_enemy_parts_store_the_builders_they_are_given() -> None:
    builders = [object() for _ in range(9)]
    parts = enemy_mesh.EnemyParts(*builders)
    assert parts.hull is builders[0]
    assert parts.muzzle is builders[8]


# --- The model built from a drawing, over Babylon stand-ins (ENG-47). ---


class _Node:
    """A node stand-in: its name, scene, parent, position (as set), rotation and emissive colour."""

    def __init__(self, label: str, scene: Any = "scene") -> None:
        self.name = label
        self.scene = scene
        self.parent: Any = None
        self.at: list[float] | None = None
        self.position = SimpleNamespace(set=self._set)
        self.rotation = SimpleNamespace(z=0.0)

    def _set(self, x: float, y: float, z: float) -> None:
        self.at = [x, y, z]

    def getScene(self) -> Any:
        return self.scene


class _Material:
    """A material stand-in: its name and the colour last set on its emissive colour."""

    def __init__(self, label: str) -> None:
        self.name = label
        self.emissive: tuple[float, ...] = ()
        self.emissiveColor = SimpleNamespace(set=self._set)

    def _set(self, *rgb: float) -> None:
        self.emissive = rgb


@pytest.fixture
def scene(monkeypatch: Any) -> SimpleNamespace:
    """Record what the model is built of: nodes, meshes, trims, animations, materials."""
    made = SimpleNamespace(
        nodes={}, meshes=[], trims=[], animations=[], steps=[], unlit={}, reactors=[], rotors=[]
    )

    def node(label: str, scene: Any) -> _Node:
        made.nodes[label] = _Node(label, scene)
        return made.nodes[label]

    def mesh_of(name: str, geo: Any, material: Any, scene: Any) -> _Node:
        mesh = _Node(name, scene)
        mesh.geo = geo
        mesh.material = material
        made.meshes.append(mesh)
        return mesh

    def unlit(name: str, _scene: Any) -> _Material:
        made.unlit[name] = _Material(name)
        return made.unlit[name]

    def tinted_hull(_scene: Any, tint: Any, flesh: bool) -> _Material:
        return _Material(("flesh" if flesh else "hull") + ":" + ",".join(str(c) for c in tint))

    monkeypatch.setattr(enemy_mesh, "new_transform_node", node)
    monkeypatch.setattr(enemy_mesh, "node_name", lambda n: n.name)
    monkeypatch.setattr(enemy_mesh, "mesh_of", mesh_of)
    monkeypatch.setattr(enemy_mesh, "in_body_shades", lambda geo: ("body-shades", geo))
    monkeypatch.setattr(enemy_mesh, "in_enemy_family", lambda geo: ("enemy-family", geo))
    monkeypatch.setattr(enemy_mesh, "set_trim", lambda mesh, rim: made.trims.append((mesh, rim)))
    monkeypatch.setattr(
        enemy_mesh, "add_model_animation", lambda n, anim: made.animations.append((n, anim))
    )
    monkeypatch.setattr(
        enemy_mesh, "step_model_animations", lambda root, dt: made.steps.append((root, dt))
    )
    monkeypatch.setattr(enemy_mesh, "unlit", unlit)
    monkeypatch.setattr(enemy_mesh, "tinted_hull", tinted_hull)
    monkeypatch.setattr(enemy_mesh, "matte_of", lambda name, _albedo, _scene: _Material(name))
    monkeypatch.setattr(
        enemy_mesh, "enemy_materials", lambda _scene: SimpleNamespace(neon=_Material("enemy-neon"))
    )
    monkeypatch.setattr(enemy_mesh, "add_reactors", lambda *args: made.reactors.append(args))
    monkeypatch.setattr(enemy_mesh, "add_rotors", lambda *args: made.rotors.append(args))
    monkeypatch.setattr(enemy_mesh, "new_breath", lambda: "new-breath")
    monkeypatch.setattr(enemy_mesh, "glow_level", lambda _breath, time: 0.5 if time > 0 else 0.25)
    monkeypatch.setattr(enemy_mesh, "is_living_motion", lambda: True)
    return made


def _materials() -> enemy_mesh.SurfaceMaterials:
    return enemy_mesh.SurfaceMaterials(
        _Material("hull"), _Material("flesh"), _Material("neon"), _Material("vein")
    )


def test_a_model_s_surface_materials_are_its_hull_flesh_neon_and_veins() -> None:
    mats = _materials()
    assert [m.name for m in (mats.hull, mats.flesh, mats.neon, mats.vein)] == [
        "hull",
        "flesh",
        "neon",
        "vein",
    ]


def _hull_and_neon(p: Any) -> None:
    p.hull.box([1, 1, 1], [0, 0, 0])
    p.neon.box([1, 1, 1], [1, 0, 0])


def test_gfx_trim_06_the_hull_is_in_body_shades_with_an_edge_trim(scene: SimpleNamespace) -> None:
    """Also ENM-38 and D-231: the lights in the enemies' family, no trim; nothing is drawn empty."""
    parts = collect_parts(_hull_and_neon)["parts"]
    root = _Node("root")
    neon = [0.2, 1.0, 0.3]
    enemy_mesh.add_surfaces("gnat", parts, _materials(), neon, root)
    hull, lights = scene.meshes
    assert hull.name == "gnat-hull"
    assert hull.geo == ("body-shades", parts.hull.geometry)
    assert hull.parent is root
    assert hull.scene == "scene"
    assert lights.name == "gnat-neon"
    assert lights.geo == ("enemy-family", parts.neon.geometry)
    assert lights.parent is root
    # Only the hull is trimmed, in the rim colour of the neon.
    assert scene.trims == [(hull, rim_of(neon))]


def test_gfx_trim_06_the_flesh_and_veins_are_drawn_when_there_are_some(
    scene: SimpleNamespace,
) -> None:
    def flesh_and_vein(p: Any) -> None:
        p.flesh.box([1, 1, 1], [0, 0, 0])
        p.vein.box([1, 1, 1], [0, 0, 0])

    parts = collect_parts(flesh_and_vein)["parts"]
    enemy_mesh.add_surfaces("hive", parts, _materials(), [1, 1, 0], _Node("root"))
    assert [m.name for m in scene.meshes] == ["hive-flesh", "hive-vein"]
    assert [m for m, _rim in scene.trims] == [scene.meshes[0]]


def test_enm_42_each_wing_hangs_at_its_pivot_and_flutters(scene: SimpleNamespace) -> None:
    def wing(w: Any) -> None:
        w.flesh.box([1, 1, 1], [3, 0, 0])

    wings = collect_parts(lambda p: p.flap([2, 0, 1], -1, 4.0, wing))["wings"]
    body = _Node("moth-body")
    clock = [0.0]
    enemy_mesh.add_wings("moth", wings, _materials(), [1, 1, 0], body, clock)
    node = scene.nodes["moth-wing-0"]
    skin = scene.nodes["moth-wing-0-skin"]
    assert node.parent is body
    assert node.at == [2, 0, 1]
    # The skin is drawn in model space: back from the pivot.
    assert skin.parent is node
    assert skin.at == [-2, 0, -1]
    assert [m.name for m in scene.meshes] == ["moth-wing-0-flesh"]
    assert scene.meshes[0].parent is skin
    animated, animate = scene.animations[0]
    assert animated is node
    clock[0] = 0.2
    animate(0.016)
    assert node.rotation.z == pytest.approx(flutter_angle(-1, 4.0, 0.2))


def _gnat(p: Any) -> None:
    p.hull.box([1, 1, 1], [0, 0, 0])
    p.neon.box([1, 1, 1], [1, 0, 0])
    p.charge.box([1, 1, 1], [0, 0, 2])
    p.reactor([0, 0, -4], 1.0)
    p.rotor([2, 0, 0], 2.0)
    p.muzzle([0, 0, 5], "gun")
    p.muzzle([1, 0, 5], "cannon")
    p.flap([1, 0, 0], 1, 3.0, lambda w: w.flesh.box([1, 1, 1], [0, 0, 0]))


def test_enm_34_a_model_is_a_root_with_its_body_reactors_and_muzzles(
    scene: SimpleNamespace,
) -> None:
    """Also ENM-45 and GFX-ART-18: the muzzles are not on the body, so shots leave from them."""
    model = enemy_mesh.build_enemy_model("gnat", "scene", [1.0, 0.1, 0.1], _gnat)
    root = scene.nodes["gnat"]
    body = scene.nodes["gnat-body"]
    assert model.root is root
    assert body.parent is root
    gun = scene.nodes["gnat-muzzle-gun-0"]
    cannon = scene.nodes["gnat-muzzle-cannon-1"]
    assert (gun.parent, gun.at) == (root, [0, 0, 5])
    assert (cannon.parent, cannon.at) == (root, [1, 0, 5])
    # The reactors hang on the root, the rotors on the body, with the hull material.
    name, reactors, _parts, reactor_root, neon = scene.reactors[0]
    assert (name, reactor_root, neon) == ("gnat", root, [1.0, 0.1, 0.1])
    assert [r.at for r in reactors] == [[0, 0, -4]]
    rotor_name, rotors, rotor_mat, rotor_parent = scene.rotors[0]
    assert (rotor_name, rotor_parent) == ("gnat", body)
    assert [r.at for r in rotors] == [[2, 0, 0]]
    assert rotor_mat.name == "gnat-blades"


def test_gfx_art_05_the_body_is_tinted_by_the_neon_moved_into_the_enemies_family(
    scene: SimpleNamespace,
) -> None:
    """Also D-231: the hull and flesh in the body shade of that colour."""
    neon = [1.0, 0.1, 0.1]
    enemy_mesh.build_enemy_model("gnat", "scene", neon, _gnat)
    tint = body_color(enemy_color(neon))
    names = {m.name: m for m in scene.meshes}
    assert set(names) == {
        "gnat-hull:" + ",".join(str(c) for c in tint),
        "gnat-enemy-neon",
        "gnat-wing-0-flesh:" + ",".join(str(c) for c in tint),
        "gnat-charge",
    }
    assert all(m.parent is not scene.nodes["gnat"] for m in scene.meshes)
    charge = names["gnat-charge"]
    assert charge.parent is scene.nodes["gnat-body"]
    assert charge.material is scene.unlit["gnat-charge"]
    # The hull's trim is in the rim colour of the enemy colour, not of the raw neon.
    assert scene.trims[0][1] == rim_of(enemy_color(neon))


def test_a_model_without_charge_lights_has_no_charge_mesh(scene: SimpleNamespace) -> None:
    enemy_mesh.build_enemy_model("blob", "scene", [0.2, 1, 0.2], _hull_and_neon, "breath")
    assert "blob-charge" not in [m.name for m in scene.meshes]
    # The charge material is still made: the sync lights it.
    assert "blob-charge" in scene.unlit


@pytest.mark.usefixtures("scene")
def test_enm_44_a_model_breathes_with_the_breath_it_is_given_or_a_new_one(
    monkeypatch: Any,
) -> None:
    breaths: list[Any] = []
    monkeypatch.setattr(enemy_mesh, "glow_level", lambda breath, _t: breaths.append(breath) or 1)
    enemy = SimpleNamespace(charge=0.0)
    enemy_mesh.build_enemy_model("a", "scene", [1, 1, 0], _hull_and_neon).sync(enemy, 0.1)
    enemy_mesh.build_enemy_model("b", "scene", [1, 1, 0], _hull_and_neon, "shared").sync(enemy, 0.1)
    assert breaths == ["new-breath", "shared"]


def test_enm_42_the_veins_pulse_on_the_sim_clock_and_the_animations_step(
    scene: SimpleNamespace,
) -> None:
    model = enemy_mesh.build_enemy_model("gnat", "scene", [1.0, 0.1, 0.1], _gnat)
    vein = scene.unlit["gnat-vein"]
    model.sync(SimpleNamespace(charge=0.0), 0.5)
    # The clock has moved on: the stand-in glow level for a time past 0.
    assert vein.emissive == (0.5, 0.5, 0.5)
    assert scene.steps == [(scene.nodes["gnat"], 0.5)]


def test_enm_42_with_the_living_motion_off_the_model_holds_still_at_rest(
    scene: SimpleNamespace, monkeypatch: Any
) -> None:
    living = [True]
    monkeypatch.setattr(enemy_mesh, "is_living_motion", lambda: living[0])
    model = enemy_mesh.build_enemy_model("gnat", "scene", [1.0, 0.1, 0.1], _gnat)
    wing = scene.nodes["gnat-wing-0"]
    animate = scene.animations[0][1]
    model.sync(SimpleNamespace(charge=0.0), 0.3)
    animate(0.3)
    assert wing.rotation.z == pytest.approx(flutter_angle(1, 3.0, 0.3))
    # Switched off: the veins are fully lit and the clock goes back to rest.
    living[0] = False
    model.sync(SimpleNamespace(charge=0.0), 0.3)
    animate(0.3)
    assert scene.unlit["gnat-vein"].emissive == (1, 1, 1)
    assert wing.rotation.z == pytest.approx(flutter_angle(1, 3.0, 0))


@pytest.mark.parametrize("charge", [0.0, 0.5, 1.0])
def test_enm_23_the_charge_lights_brighten_as_the_attack_charges(
    scene: SimpleNamespace, charge: float
) -> None:
    neon = [1.0, 0.1, 0.1]
    model = enemy_mesh.build_enemy_model("gnat", "scene", neon, _gnat)
    model.sync(SimpleNamespace(charge=charge), 0.016)
    k = ENEMY_LOOK.chargeIdle + (1 - ENEMY_LOOK.chargeIdle) * charge
    color = enemy_color(neon)
    assert scene.unlit["gnat-charge"].emissive == pytest.approx(tuple(c * k for c in color))


def test_the_fan_blades_are_matte_not_the_shiny_hull(scene: SimpleNamespace) -> None:
    """The rotors' blades get their own matte material, so they show no highlight."""
    enemy_mesh.build_enemy_model("gnat", "scene", [1.0, 0.1, 0.1], _gnat)
    (_name, _rotors, blades, _body) = scene.rotors[0]
    assert blades.name == "gnat-blades"
    assert not blades.name.startswith("hull")

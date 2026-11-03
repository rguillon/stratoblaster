# Copyright (c) 2026 Renaud Guillon
"""Builds an enemy model from its parts, generated in code (ENM-34).

The model is a node tree: a root, a body (hull, flesh, lights and wings) and, outside the body,
reactors, rotors and muzzles (so shots leave from the same points, GFX-ART-18).
"""

from core.entities.enemy import Enemy
from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies.enemy_engines import Reactor, add_reactors, add_rotors
from game.view.enemies.enemy_materials import (
    body_color,
    enemy_color,
    enemy_materials,
    in_body_shades,
    in_enemy_family,
    matte_of,
    mesh_of,
    rim_of,
    tinted_hull,
    unlit,
)
from game.view.enemies.living_motion import (
    flutter_angle,
    glow_level,
    is_living_motion,
    new_breath,
)
from render.babylon import (
    color3,
    new_transform_node,
    node_name,
)
from render.edge_trim_mesh import set_trim
from render.geometry.solids import SolidBuilder
from render.model_animation import (
    add_model_animation,
    step_model_animations,
)

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Sequence
from typing import Any

type Rgb = list[float]
type Vec3 = list[float]
# __pragma__ ("noskip")


class EnemyParts:
    """Builders for the three parts of an enemy model."""

    def __init__(
        self,
        hull: Any,
        flesh: Any,
        vein: Any,
        flap: Any,
        neon: Any,
        charge: Any,
        reactor: Any,
        rotor: Any,
        muzzle: Any,
    ) -> None:
        # Dark metal (use the `ENEMY_LOOK.hull` shades): the cyber parts grafted on (GFX-ART-12).
        self.hull = hull
        # Dark flesh (use the `ENEMY_LOOK.flesh` shades): the living body (ENM-35).
        self.flesh = flesh
        # Glowing veins, eyes and glands, pulsing slowly (ENM-42); in the enemies' colour family.
        self.vein = vein
        # Adds a wing hinged along Z at `pivot`, fluttering (ENM-42) on its own node: `draw`
        # draws it in model space, as at rest. `side` (-1 left, 1 right) sets which way it flaps;
        # `span` picks the slower beat of big wings.
        self.flap = flap
        # Neon lights, always lit.
        self.neon = neon
        # Lights that brighten as the next attack charges (`Enemy.charge`, ENM-23); white, tinted.
        self.charge = charge
        # Adds a reactor whose nozzle opens at `at`, thrusting towards -Z (phase 5 review).
        self.reactor = reactor
        # Adds a rotor turning around +Y at `at` (phase 5 review: the Gnat's ducted fans).
        self.rotor = rotor
        # Marks the tip of a gun's barrel at `at` (phase 7 review: the game's muzzles must match,
        # GFX-SHOT-09): an empty node `<name>-muzzle-<kind>-<i>`.
        self.muzzle = muzzle


class WingParts:
    """The builders a fluttering wing is drawn with."""

    def __init__(self, hull: Any, flesh: Any, neon: Any, vein: Any) -> None:
        self.hull = hull
        self.flesh = flesh
        self.neon = neon
        self.vein = vein


class Wing:
    """A wing: its hinge, which way it flaps, its span and its parts."""

    def __init__(self, pivot: Vec3, side: float, span: float, parts: WingParts) -> None:
        self.pivot = pivot
        self.side = side
        self.span = span
        self.parts = parts


class SurfaceMaterials:
    """The materials of a model's surfaces."""

    def __init__(self, hull: Any, flesh: Any, neon: Any, vein: Any) -> None:
        self.hull = hull
        self.flesh = flesh
        self.neon = neon
        self.vein = vein


class BuiltEnemyModel:
    """What `build_enemy_model` returns: the root node and the per-frame sync."""

    def __init__(self, root: Any, sync: Any) -> None:
        self.root = root
        self.sync = sync


def wing_parts_new() -> WingParts:
    """Return a set of empty builders for one wing (or the body's parts)."""
    return WingParts(SolidBuilder(), SolidBuilder(), SolidBuilder(), SolidBuilder())


def add_surfaces(
    name: str, parts: Any, mats: SurfaceMaterials, neon_color: Sequence[float], root: Any
) -> None:
    """Add the hull and flesh, and the neon lights, of an enemy model whose neon is `neon_color`.

    The hull and flesh use the body shades (D-231) and ask for an edge trim (GFX-TRIM-06); the neon
    lights use the enemies' colour family (ENM-38). Everything goes under `root`.
    """
    scene = root.getScene()
    for geo, mat in [(parts.hull.geometry, mats.hull), (parts.flesh.geometry, mats.flesh)]:
        if len(geo.positions) == 0:
            continue
        mesh = mesh_of(name + "-" + node_name(mat), in_body_shades(geo), mat, scene)
        mesh.parent = root
        set_trim(mesh, rim_of(neon_color))
    for geo, mat in [(parts.neon.geometry, mats.neon), (parts.vein.geometry, mats.vein)]:
        if len(geo.positions) == 0:
            continue
        mesh_of(name + "-" + node_name(mat), in_enemy_family(geo), mat, scene).parent = root


def flutter_animation(node: Any, side: float, span: float, clock: list[float]) -> Any:
    """Return the wing's animation: rolls the node as the clock says (ENM-42)."""

    def animate(_dt: float) -> None:
        node.rotation.z = flutter_angle(side, span, clock[0])

    return animate


def add_wings(
    name: str,
    wings: list[Wing],
    mats: SurfaceMaterials,
    neon_color: Sequence[float],
    body: Any,
    clock: list[float],
) -> None:
    """Add the wings, each on a node at its pivot rolling as it flutters (ENM-42), under `body`."""
    scene = body.getScene()
    for i, wing in enumerate(wings):
        pivot = wing.pivot
        node = new_transform_node(name + "-wing-" + str(i), scene)
        node.position.set(pivot[0], pivot[1], pivot[2])
        node.parent = body
        inner = new_transform_node(node_name(node) + "-skin", scene)
        inner.position.set(-pivot[0], -pivot[1], -pivot[2])
        inner.parent = node
        add_surfaces(node_name(node), wing.parts, mats, neon_color, inner)
        # Left and right wings of a pair beat together.
        add_model_animation(node, flutter_animation(node, wing.side, wing.span, clock))


def collect_parts(build: Any) -> dict[str, Any]:
    """Return the parts `build` draws, and the reactors, rotors, wings and muzzles it adds.

    The muzzles are where the shots leave from (ENM-21).
    """
    reactors: list[Reactor] = []
    rotors: list[Reactor] = []
    wings: list[Wing] = []
    muzzles: list[list[Any]] = []

    def reactor(at: Vec3, radius: float) -> None:
        reactors.append(Reactor(at, radius))

    def rotor(at: Vec3, radius: float) -> None:
        rotors.append(Reactor(at, radius))

    def muzzle(at: Vec3, kind: Any = None) -> None:
        # `kind` is 'gun' when the caller leaves it out.
        muzzles.append([at, kind if kind != None else "gun"])

    def flap(pivot: Vec3, side: float, span: float, draw: Any) -> None:
        wing = Wing(pivot, side, span, wing_parts_new())
        draw(wing.parts)
        wings.append(wing)

    body_parts = wing_parts_new()
    parts = EnemyParts(
        body_parts.hull,
        body_parts.flesh,
        body_parts.vein,
        flap,
        body_parts.neon,
        SolidBuilder(),
        reactor,
        rotor,
        muzzle,
    )
    build(parts)
    return {
        "parts": parts,
        "reactors": reactors,
        "rotors": rotors,
        "wings": wings,
        "muzzles": muzzles,
    }


def build_enemy_model(
    name: str, scene: Any, neon_color: Rgb, build: Any, breath: Any = None
) -> BuiltEnemyModel:
    """Build an enemy model from the parts `build` draws (logical pixels, nose +Z, Y up).

    The charge lights get their own material, brightened to `chargeColor` by the enemy's charge; the
    hull is tinted towards `chargeColor`, the enemy's neon colour. Its body (hull, flesh, lights,
    wings) is on a node of its own, `<name>-body`, its veins pulsing (ENM-42; it never swells,
    ENM-43); its reactors and muzzles are not, so shots leave from the same points (ENM-45).
    """
    if breath is None:
        breath = new_breath()
    # GFX-ART-05: every enemy's lights in the enemies' colour family.
    charge_color = enemy_color(neon_color)
    collected = collect_parts(build)
    parts = collected["parts"]
    reactors = collected["reactors"]
    rotors = collected["rotors"]
    wings = collected["wings"]
    muzzles = collected["muzzles"]
    vein = unlit(name + "-vein", scene)
    # D-231: the body tinted and lit by the neon in the body shades (a green enemy's metal faintly
    # green, a yellow one's neutral: dark metal lit yellow turns khaki).
    body_tint = body_color(charge_color)
    mats = SurfaceMaterials(
        tinted_hull(scene, body_tint, False),
        tinted_hull(scene, body_tint, True),
        enemy_materials(scene).neon,
        vein,
    )
    root = new_transform_node(name, scene)
    body = new_transform_node(name + "-body", scene)
    body.parent = root
    clock = [0.0]
    add_reactors(name, reactors, parts, root, neon_color)
    # The blades are matte (no highlight on the fan), not the shiny metal of the hull.
    dark = ENEMY_LOOK.hull.dark
    blades = matte_of(name + "-blades", color3(dark[0], dark[1], dark[2]), scene)
    add_rotors(name, rotors, blades, body)
    for i, entry in enumerate(muzzles):
        at = entry[0]
        node = new_transform_node(name + "-muzzle-" + entry[1] + "-" + str(i), scene)
        node.position.set(at[0], at[1], at[2])
        node.parent = root
    add_surfaces(name, parts, mats, charge_color, body)
    add_wings(name, wings, mats, charge_color, body, clock)
    charge_mat = unlit(name + "-charge", scene)
    if len(parts.charge.geometry.positions) > 0:
        mesh_of(name + "-charge", parts.charge.geometry, charge_mat, scene).parent = body

    def sync(enemy: Enemy, dt: float) -> None:
        # ENM-42: driven by the frames' sim time, so a paused game holds still.
        if is_living_motion():
            clock[0] += dt
        else:
            clock[0] = 0
        living = is_living_motion()
        glow = glow_level(breath, clock[0]) if living else 1
        vein.emissiveColor.set(glow, glow, glow)
        step_model_animations(root, dt)
        k = ENEMY_LOOK.chargeIdle + (1 - ENEMY_LOOK.chargeIdle) * enemy.charge
        charge_mat.emissiveColor.set(charge_color[0] * k, charge_color[1] * k, charge_color[2] * k)

    return BuiltEnemyModel(root, sync)

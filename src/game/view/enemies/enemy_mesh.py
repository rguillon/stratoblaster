# Copyright (c) 2026 Renaud Guillon
"""Builds an enemy model from its parts, generated in code (ENM-34).

The model is a node tree: a root, a body (hull, flesh, lights and wings) and, outside the body,
reactors, rotors and muzzles (so shots leave from the same points, GFX-ART-18).
"""

import math

from core.entities.enemy import Enemy
from game.config.enemy_look import ENEMY_LOOK
from game.config.enemy_tiers import tier_look
from game.config.weapons import WEAPONS
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
from game.view.enemies.weapon_ports import (
    DEFAULT_MISSILE,
    LENS_LENGTH,
    LENS_RADIUS,
    hex_port,
    laser_lens,
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
        slide: Any = None,
        bare: Any = None,
        bare_flesh: Any = None,
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
        # Adds a piece that slides back along the direction `[x, z]` by `distance` model units at
        # the full recoil of the enemy's barrel number `index` (WPN-03; `Enemy.barrels`): `draw`
        # draws it in model space, as at rest, on a `WingParts`.
        self.slide = slide
        # Dark metal as `hull`, but with no edge trim (GFX-TRIM-06): a part that must not glow
        # where it ends, e.g. a launcher's mouth lit along its sides instead (WPN-07).
        self.bare = bare if bare is not None else SolidBuilder()
        # Flesh as `flesh`, with no edge trim: a model that must show no highlight at all.
        self.bare_flesh = bare_flesh if bare_flesh is not None else SolidBuilder()


class WingParts:
    """The builders a fluttering wing is drawn with."""

    def __init__(
        self,
        hull: Any,
        flesh: Any,
        neon: Any,
        vein: Any,
        bare: Any = None,
        bare_flesh: Any = None,
    ) -> None:
        self.hull = hull
        self.flesh = flesh
        self.neon = neon
        self.vein = vein
        # Metal and flesh with no edge trim (`EnemyParts.bare`, `EnemyParts.bare_flesh`).
        self.bare = bare if bare is not None else SolidBuilder()
        self.bare_flesh = bare_flesh if bare_flesh is not None else SolidBuilder()


class Wing:
    """A wing: its hinge, which way it flaps, its span and its parts."""

    def __init__(self, pivot: Vec3, side: float, span: float, parts: WingParts) -> None:
        self.pivot = pivot
        self.side = side
        self.span = span
        self.parts = parts


class Slide:
    """A piece that slides back with a barrel's recoil: its place, its way back and its parts."""

    def __init__(
        self,
        pivot: Vec3,
        back: list[float],
        distance: float,
        index: int,
        parts: WingParts,
        swivel: bool = False,
        centre: Vec3 | None = None,
        kind: str = "barrel",
        down: float = 0,
        turret: int | None = None,
    ) -> None:
        # `swivel`: it also turns with the enemy's turret (`Enemy.turret`), about its own pivot, or
        # about `centre` (the turret's, in model space) when given.
        self.swivel = swivel
        self.centre = centre
        # "barrel": it recoils with `Enemy.barrels[index]`; "rocket": a rocket in a port, sunk
        # out of sight down its well while launcher `Enemy.launchers[index]` reloads (WPN-07);
        # "track": as far along as the enemy's own `tracks[index]` says (doors, lifts).
        # `down` is how far it moves along Y per unit of `distance` (an upward port's sinks).
        self.kind = kind
        self.down = down
        # A swivelling piece of an enemy with several turrets (`Enemy.turrets`) turns with this
        # one; with the enemy's only `turret` when None.
        self.turret = turret
        self.pivot = pivot
        self.back = back
        self.distance = distance
        self.index = index
        self.parts = parts


class SurfaceMaterials:
    """The materials of a model's surfaces, and the hues its lights are drawn in (a tier's)."""

    def __init__(self, hull: Any, flesh: Any, neon: Any, vein: Any, hues: Any = None) -> None:
        self.hull = hull
        self.flesh = flesh
        self.neon = neon
        self.vein = vein
        self.hues = hues


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
    # The bare metal and flesh: the hull's and the flesh's, with no trim (`EnemyParts.bare`,
    # `EnemyParts.bare_flesh`).
    if hasattr(parts, "bare") and len(parts.bare.geometry.positions) > 0:
        bare = in_body_shades(parts.bare.geometry)
        mesh_of(name + "-bare", bare, mats.hull, scene).parent = root
    if hasattr(parts, "bare_flesh") and len(parts.bare_flesh.geometry.positions) > 0:
        bare_flesh = in_body_shades(parts.bare_flesh.geometry)
        mesh_of(name + "-bare-flesh", bare_flesh, mats.flesh, scene).parent = root
    for geo, mat in [(parts.neon.geometry, mats.neon), (parts.vein.geometry, mats.vein)]:
        if len(geo.positions) == 0:
            continue
        mesh_of(
            name + "-" + node_name(mat), in_enemy_family(geo, mats.hues), mat, scene
        ).parent = root


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


def add_slides(name: str, slides: list[Slide], mats: SurfaceMaterials, neon: Any, body: Any) -> Any:
    """Add the pieces that slide back with a recoil, each on a node at its pivot (WPN-03).

    Returns the nodes, in the order of the slides.
    """
    scene = body.getScene()
    nodes: list[Any] = []
    for i, piece in enumerate(slides):
        pivot = piece.pivot
        node = new_transform_node(name + "-slide-" + str(i), scene)
        node.position.set(pivot[0], pivot[1], pivot[2])
        node.parent = body
        inner = new_transform_node(node_name(node) + "-skin", scene)
        inner.position.set(-pivot[0], -pivot[1], -pivot[2])
        inner.parent = node
        add_surfaces(node_name(node), piece.parts, mats, neon, inner)
        nodes.append(node)
    return nodes


def slide_back(node: Any, piece: Slide, recoil: float, aim: float = 0) -> None:
    """Put `node` back along its slide by `recoil` (0 at rest, 1 thrown fully back).

    Turned about its pivot by `aim` (radians, as a barrel's yaw) when it swivels.
    """
    k = recoil * piece.distance
    c = math.cos(aim)
    s = math.sin(aim)
    # From the centre it turns about (its own pivot, or its turret's) to where it slides back to.
    centre = piece.centre if piece.centre is not None else piece.pivot
    bx = piece.pivot[0] - centre[0] + piece.back[0] * k
    bz = piece.pivot[2] - centre[2] + piece.back[1] * k
    node.rotation.y = aim
    node.position.set(
        centre[0] + bx * c + bz * s, piece.pivot[1] + piece.down * k, centre[2] - bx * s + bz * c
    )


def sync_slides(slides: list[Slide], nodes: list[Any], enemy: Any) -> None:
    """Move the sliding pieces: the barrels and the rockets.

    Each barrel back by its recoil (WPN-03), each rocket down its well as its launcher reloads
    (WPN-07), each track as far along as the enemy says (`Enemy.tracks`).
    """
    for i, piece in enumerate(slides):
        if piece.kind == "rocket":
            show_rocket(nodes[i], piece, enemy)
        elif piece.kind == "track":
            show_track(nodes[i], piece, enemy)
        elif piece.index < len(enemy.barrels):
            slide_back(
                nodes[i],
                piece,
                enemy.barrels[piece.index].recoil_at(enemy.age),
                swivel_aim(piece, enemy),
            )


def swivel_aim(piece: Slide, enemy: Any) -> float:
    """Return how far a piece has turned with its turret.

    Its own of the enemy's `turrets`, or the enemy's `turret`; 0 for a piece that does not swivel.
    """
    if not piece.swivel:
        return 0
    if piece.turret is not None:
        turrets = enemy.turrets if hasattr(enemy, "turrets") else []
        return turrets[piece.turret].aim if piece.turret < len(turrets) else 0
    return enemy.turret.aim if enemy.turret is not None else 0


def show_track(node: Any, piece: Slide, enemy: Any) -> None:
    """Move a piece the enemy drives itself along its slide: `enemy.tracks[index]` of the way.

    0 at rest, 1 its whole `distance` along; hidden while it is below 0 (a part gone for now). A
    track the enemy does not report stays at rest.
    """
    tracks = enemy.tracks if hasattr(enemy, "tracks") else []
    value: float = tracks[piece.index] if piece.index < len(tracks) else 0
    node.setEnabled(value >= 0)
    slide_back(node, piece, max(0, value))


def rocket_sunk(enemy: Any, index: int) -> float:
    """Return how far down its well a port's rocket is: 0 loaded, 1 out of sight (WPN-07).

    Gone as its launcher (`Enemy.launchers[index]`) launches, it rises back over the reload, eased
    out; a launcher the enemy does not report is always loaded.
    """
    if not hasattr(enemy, "launchers") or index >= len(enemy.launchers):
        return 0
    since: float = enemy.launchers[index].since_fired(enemy.age)
    reload: float = WEAPONS.missileReloadSeconds
    show: float = WEAPONS.missileReloadShow
    loaded = since / reload
    if loaded < show:
        return 1
    u = min(1, (loaded - show) / (1 - show))
    return (1 - u) * (1 - u)


def show_rocket(node: Any, piece: Slide, enemy: Any) -> None:
    """Place a port's rocket down its well as its launcher reloads; hidden while it is empty."""
    sunk = rocket_sunk(enemy, piece.index)
    node.setEnabled(sunk < 1)
    slide_back(node, piece, sunk)


def collect_parts(build: Any) -> dict[str, Any]:
    """Return the parts `build` draws, and the reactors, rotors, wings and muzzles it adds.

    The muzzles are where the shots leave from (ENM-21).
    """
    reactors: list[Reactor] = []
    rotors: list[Reactor] = []
    wings: list[Wing] = []
    muzzles: list[list[Any]] = []
    slides: list[Slide] = []

    def slide(
        pivot: Vec3,
        back: list[float],
        distance: float,
        index: int,
        draw: Any,
        swivel: Any = False,
        centre: Any = None,
        kind: Any = "barrel",
        down: Any = 0,
        turret: Any = None,
    ) -> None:
        piece = Slide(
            pivot, back, distance, index, wing_parts_new(), bool(swivel), centre, kind, down, turret
        )
        draw(piece.parts)
        slides.append(piece)

    def reactor(at: Vec3, radius: float) -> None:
        reactors.append(Reactor(at, radius))

    def rotor(at: Vec3, radius: float) -> None:
        rotors.append(Reactor(at, radius))

    # The missile ports drawn so far: a port's launcher number, unless the model gives it.
    ports = [0]

    def muzzle(
        at: Vec3,
        kind: Any = None,
        direction: Any = None,
        size: Any = None,
        index: Any = None,
        rim: Any = True,
        well: Any = None,
        yaw: Any = None,
    ) -> None:
        # `kind` is 'gun' when the caller leaves it out. A missile muzzle is drawn as a hexagonal
        # port (up unless `direction` says "forward"), a laser's as a lens (forward unless "up").
        name = kind if kind != None else "gun"
        muzzles.append([at, name])
        if name == "missile":
            hex_port(
                parts,
                at,
                direction if direction != None else "up",
                size if size != None else DEFAULT_MISSILE,
                index if index != None else ports[0],
                rim is not False,
                well if well != None else None,
            )
            ports[0] += 1
        elif name == "laser":
            # A laser's `size` is its barrel's radius, `well` its length (the default lens's
            # when left out) and `yaw` the way it points from the nose (straight ahead by default).
            laser_lens(
                parts,
                at,
                direction if direction != None else "forward",
                well if well != None else LENS_LENGTH,
                size if size != None else LENS_RADIUS,
                yaw if yaw != None else 0,
            )

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
        slide,
        SolidBuilder(),
    )
    build(parts)
    return {
        "parts": parts,
        "reactors": reactors,
        "rotors": rotors,
        "wings": wings,
        "muzzles": muzzles,
        "slides": slides,
    }


def bank_roll(turn: list[Any], enemy: Any, dt: float, bank: Any) -> float:
    """Return the roll of an enemy's body after `dt` seconds, rolling into its turn.

    `turn` is `[last heading, roll so far]`, updated; `bank` is `gain`, `max` and `follow` (see
    `build_enemy_model`), or None for an enemy that never rolls.
    """
    if bank is None or dt <= 0:
        return float(turn[1])
    heading = enemy.heading
    if turn[0] is not None:
        diff = heading - turn[0]
        while diff > math.pi:
            diff -= 2 * math.pi
        while diff < -math.pi:
            diff += 2 * math.pi
        target = max(-bank["max"], min(bank["max"], -(diff / dt) * bank["gain"]))
        turn[1] = turn[1] + (target - turn[1]) * min(1, dt * bank["follow"])
    turn[0] = heading
    return float(turn[1])


def build_enemy_model(
    name: str, scene: Any, neon_color: Rgb, build: Any, breath: Any = None, bank: Any = None
) -> BuiltEnemyModel:
    """Build an enemy model from the parts `build` draws (logical pixels, nose +Z, Y up).

    The charge lights get their own material, brightened to `chargeColor` by the enemy's charge; the
    hull is tinted towards `chargeColor`, the enemy's neon colour. Its body (hull, flesh, lights,
    wings) is on a node of its own, `<name>-body`, its veins pulsing (ENM-42; it never swells,
    ENM-43); its reactors and muzzles are not, so shots leave from the same points (ENM-45).

    With `bank` (`gain`, `max`, `follow`), the body rolls around its nose axis as the enemy turns:
    `gain` radians per radian/s of turn, at most `max`, following at `follow` per second.
    """
    if breath is None:
        breath = new_breath()
    # ENM-49: an enemy of a tier is lit in its tier's hue, on a hull tinted in its tier's colour.
    theme = tier_look(name)
    hues = [theme.hue] if theme is not None else None
    # GFX-ART-05: every enemy's lights in the enemies' colour family.
    charge_color = enemy_color(neon_color, hues)
    collected = collect_parts(build)
    parts = collected["parts"]
    reactors = collected["reactors"]
    rotors = collected["rotors"]
    wings = collected["wings"]
    muzzles = collected["muzzles"]
    slides = collected["slides"]
    vein = unlit(name + "-vein", scene)
    # D-231: the body tinted and lit by the neon in the body shades (a green enemy's metal faintly
    # green, a yellow one's neutral: dark metal lit yellow turns khaki).
    body_tint = theme.hull if theme is not None else body_color(charge_color)
    mats = SurfaceMaterials(
        tinted_hull(scene, body_tint, False),
        tinted_hull(scene, body_tint, True),
        enemy_materials(scene).neon,
        vein,
        hues,
    )
    root = new_transform_node(name, scene)
    body = new_transform_node(name + "-body", scene)
    body.parent = root
    clock = [0.0]
    add_reactors(name, reactors, parts, root, neon_color, hues)
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
    slide_nodes = add_slides(name, slides, mats, charge_color, body)
    charge_mat = unlit(name + "-charge", scene)
    if len(parts.charge.geometry.positions) > 0:
        mesh_of(name + "-charge", parts.charge.geometry, charge_mat, scene).parent = body

    # The last heading and the roll so far, for `bank`.
    turn: list[Any] = [None, 0.0]

    def sync(enemy: Enemy, dt: float) -> None:
        body.rotation.z = bank_roll(turn, enemy, dt, bank)
        # ENM-42: driven by the frames' sim time, so a paused game holds still.
        if is_living_motion():
            clock[0] += dt
        else:
            clock[0] = 0
        living = is_living_motion()
        glow = glow_level(breath, clock[0]) if living else 1
        vein.emissiveColor.set(glow, glow, glow)
        sync_slides(slides, slide_nodes, enemy)
        step_model_animations(root, dt)
        k = ENEMY_LOOK.chargeIdle + (1 - ENEMY_LOOK.chargeIdle) * enemy.charge
        charge_mat.emissiveColor.set(charge_color[0] * k, charge_color[1] * k, charge_color[2] * k)

    return BuiltEnemyModel(root, sync)

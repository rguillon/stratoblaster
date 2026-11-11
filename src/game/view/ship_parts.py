# Copyright (c) 2026 Renaud Guillon
"""Parts shared by the player ships: panels, plates, lights, rods, and the reactors.

Each part is a Babylon mesh made by the render layer, parented to a node of the ship.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.ship_look import REACTOR_FLAME
from game.view.reactor_flame import build_reactor_flame
from game.view.ship_materials import get_ship_materials

# Not in render/babylon.py yet.
from render.babylon import (
    create_disc,
    new_transform_node,
)
from render.geometry.lathe_z import (
    LatheHalves,
    create_faceted_lathe_along_z,
)
from render.geometry.prism import create_prism
from render.geometry.section_loft import create_section_loft, polygon_lathe_sections

# isort: split
# __pragma__ ("skip")
from typing import Any

Scene = Any
# __pragma__ ("noskip")


# Sides of polygonal parts (nacelles, canopies, intakes, pods): a hexagonal section (GFX-ART-09).
PART_FACETS = 6


# Section of fuselages: a smooth top (24 facets, smooth-shaded) over a low-poly 3-facet belly
# (GFX-SHIP-05): the triangles go where the playfield camera, above the ship, sees them.
BODY_SECTION = LatheHalves(24, 3)
# Section of the round parts sitting on the hull (canopy, spine, intakes, nacelles): a smooth top
# over a 3-facet belly.
SMOOTH_PART_SECTION = LatheHalves(12, 3)

PLATE_THICKNESS = 0.012

EXHAUST_LENGTH = 0.8  # relative to the nacelle length
EXHAUST_WIDTH = 1.5  # relative to the nacelle radius
CORE_RADIUS = 0.8  # relative to the nacelle radius

# The reactors' section (owner, 2026-11-11: "make the ship reactor rounded hexagons", D-330): a
# hexagon, a flat face on top, its corners rounded by arcs of `REACTOR_CORNER_STEPS` points whose
# radius is `REACTOR_ROUNDING` times the nacelle's. The flame's cones are hexagonal too.
REACTOR_SIDES = 6
REACTOR_ROUNDING = 0.3
REACTOR_CORNER_STEPS = 3
# The rings round them: fewer points a corner (they are thin; flat-shaded).
RING_CORNER_STEPS = 2

# A reactor's intake (D-330), at the nacelle's front, in nacelle radii: a hollow rounded hexagon
# scoop, its outer skin from inside the nacelle out to a flared lip, then its duct turning in and
# back to the fan face (the profile runs back on itself, so the duct looks inwards); the loft's cap
# closes the duct's end. `[z from the nacelle's front, radius]`.
REACTOR_INTAKE = [
    [-0.15, 0.9],
    [0.12, 1.0],
    [0.24, 1.02],
    [0.3, 0.94],
    [0.26, 0.74],
    [0.08, 0.7],
]
# Its accent lip, its dark fan face (a hair ahead of the duct's end) and the fan's spinner.
REACTOR_INTAKE_LIP = {"z": 0.27, "radius": 0.99, "half": 0.06}
REACTOR_INTAKE_FAN = {"z": 0.09, "radius": 0.68}
REACTOR_INTAKE_SPINNER = [[0.09, 0.28], [0.16, 0.18], [0.21, 0]]


def disc_options(radius: float, tessellation: int) -> Any:
    """Options for `CreateDisc`: `{ radius, tessellation }`."""
    options: Any = None
    __pragma__("js", "{}", "options = {radius: radius, tessellation: tessellation};")
    return options


def mirror_x(outline: list[Any]) -> list[Any]:
    """Mirrors a planform outline across the ship's centre line (X = 0)."""
    return [[-point[0], point[1]] for point in outline]


def panel(
    name: str,
    outline: list[Any],
    thickness: float,
    material: Any,
    parent: Any,
) -> Any:
    """Create a flat panel (wing, tail...) with the given material, parented to `parent`."""
    mesh = create_prism(name, outline, thickness, parent.getScene())
    mesh.material = material
    mesh.parent = parent
    return mesh


def edge_strip(
    name: str,
    edge: list[list[float]],
    inside: list[float],
    size: dict[str, float],
    material: Any,
    parent: Any,
) -> Any:
    """Create a thin strip along a panel's edge, from `edge[0]` to `edge[1]` (planform points).

    It lies across the edge, half on the panel and half out past it (away from `inside`, a point
    of the panel), `size["width"]` wide and `size["thickness"]` thick, so it caps the edge seen
    from above and from ahead: a glowing edge (D-335).
    """
    a = edge[0]
    b = edge[1]
    dx = b[0] - a[0]
    dz = b[1] - a[1]
    length = math.sqrt(dx * dx + dz * dz)
    nx = dz / length
    nz = -dx / length
    if nx * (inside[0] - a[0]) + nz * (inside[1] - a[1]) > 0:
        nx = -nx
        nz = -nz
    half = size["width"] / 2
    outline = [
        [a[0] - nx * half, a[1] - nz * half],
        [b[0] - nx * half, b[1] - nz * half],
        [b[0] + nx * half, b[1] + nz * half],
        [a[0] + nx * half, a[1] + nz * half],
    ]
    return panel(name, outline, size["thickness"], material, parent)


def plate(
    name: str,
    outline: list[Any],
    y: float,
    material: Any,
    parent: Any,
) -> Any:
    """Create a thin trim or stripe panel `y` above (or below, if negative) its parent's plane."""
    mesh = panel(name, outline, PLATE_THICKNESS, material, parent)
    mesh.position.y = y
    return mesh


def faceted_rod(
    name: str,
    size: dict[str, float],
    position: Any,
    material: Any,
    parent: Any,
    sides: int = 4,
) -> Any:
    """Create a polygonal bar along Z (4 sides: a diamond section), centred on `position`."""
    length = size["length"]
    radius = size["radius"]
    mesh = create_faceted_lathe_along_z(
        name,
        [
            [length / 2, 0],
            [length / 2, radius],
            [-length / 2, radius],
            [-length / 2, 0],
        ],
        sides,
        parent.getScene(),
    )
    mesh.position.copyFrom(position)
    mesh.material = material
    mesh.parent = parent
    return mesh


def _hexagon_sections(profile: list[list[float]], steps: int) -> list[Any]:
    """Return the sections of a body round Z with the reactors' rounded hexagon section."""
    return polygon_lathe_sections(profile, REACTOR_SIDES, REACTOR_ROUNDING, steps)


def hexagon_body(name: str, profile: list[list[float]], material: Any, parent: Any) -> Any:
    """Create a smooth body round the Z axis with the reactors' rounded hexagon section.

    `profile` as a lathe's (`[z, radius]`); smooth-shaded all round, so the rounded corners read as
    one curved skin with flat sides.
    """
    sections = _hexagon_sections(profile, REACTOR_CORNER_STEPS)
    mesh = create_section_loft(name, sections, len(sections[0][1]), parent.getScene())
    mesh.material = material
    mesh.parent = parent
    return mesh


def hexagon_band(
    name: str, z: float, radius: float, half: float, material: Any, parent: Any
) -> Any:
    """Create a band round the Z axis at `z`, a rounded hexagon `radius` out, `2 * half` wide.

    Its front, outer and back faces (its inner side lies in the body it rings), flat-shaded: the
    band's edges are sharp.
    """
    inner = radius - half
    outer = radius + half
    profile = [[-half, inner], [-half, outer], [half, outer], [half, inner]]
    sections = _hexagon_sections(profile, RING_CORNER_STEPS)
    mesh = create_section_loft(name, sections, 0, parent.getScene())
    mesh.position.z = z
    mesh.material = material
    mesh.parent = parent
    return mesh


def _add_reactor_rings(name: str, size: dict[str, float], root: Any) -> None:
    """Accent rings around the front of the nacelle and its nozzle, rounded hexagons as it is."""
    radius = size["radius"]
    length = size["length"]
    half = radius * 0.09  # half the ring's width and thickness
    accent = get_ship_materials(root.getScene()).accent
    for ring, z, scale in [("front", length * 0.3, 1.02), ("rear", -length / 2, 0.9)]:
        hexagon_band(name + "-" + ring + "-ring", z, radius * scale, half, accent, root)


def _add_reactor_intake(name: str, radius: float, front: float, root: Any) -> None:
    """Add an intake at the nacelle's `front`: hull-metal scoop, accent lip, dark fan, spinner."""
    scene = root.getScene()
    mats = get_ship_materials(scene)
    node = new_transform_node(name + "-intake", scene)
    node.position.z = front
    node.parent = root
    profile = [[p[0] * radius, p[1] * radius] for p in REACTOR_INTAKE]
    sections = _hexagon_sections(profile, REACTOR_CORNER_STEPS)
    shell = create_section_loft(name + "-intake-shell", sections, len(sections[0][1]), scene)
    shell.material = mats.hull
    shell.parent = node
    lip = REACTOR_INTAKE_LIP
    hexagon_band(
        name + "-intake-lip",
        lip["z"] * radius,
        lip["radius"] * radius,
        lip["half"] * radius,
        mats.accent,
        node,
    )
    fan = REACTOR_INTAKE_FAN
    face = create_disc(name + "-intake-fan", disc_options(fan["radius"] * radius, 6), scene)
    face.convertToFlatShadedMesh()
    # A disc faces -Z: turned round, it faces the mouth.
    face.rotation.y = math.pi
    face.position.z = fan["z"] * radius
    face.material = mats.canopy
    face.parent = node
    spinner_profile = [[p[0] * radius, p[1] * radius] for p in REACTOR_INTAKE_SPINNER]
    spinner = create_faceted_lathe_along_z(name + "-intake-spinner", spinner_profile, 6, scene)
    spinner.material = mats.hullMid
    spinner.parent = node


def build_reactor(name: str, size: dict[str, float], scene: Scene, intake: bool = False) -> Any:
    """Build a reactor centred on its origin, thrusting towards -Z: a rounded hexagon nacelle.

    Plus a glowing blue core at the nozzle and an animated blue flame behind it (GFX-SHIP-06), and
    with `intake`, an intake at its front (D-330).
    """
    mats = get_ship_materials(scene)
    radius = size["radius"]
    length = size["length"]
    root = new_transform_node(name, scene)

    profile = [
        [length / 2, 0],
        [length / 2, radius * 0.75],
        [length * 0.3, radius],
        [-length * 0.4, radius * 0.95],
        [-length / 2, radius * 0.85],
        [-length / 2, 0],
    ]
    hexagon_body(name + "-nacelle", profile, mats.nozzle, root)

    _add_reactor_rings(name, size, root)
    if intake:
        _add_reactor_intake(name, radius, length / 2, root)

    # A hexagon, its corners on the nacelle's (a disc's first corner is on +X too).
    core = create_disc(name + "-core", disc_options(radius * CORE_RADIUS, REACTOR_SIDES), scene)
    core.convertToFlatShadedMesh()
    core.position.z = -length / 2 - 0.01
    core.material = mats.reactorCore
    core.parent = root

    flame_size = {
        "nozzleZ": core.position.z,
        "length": length * EXHAUST_LENGTH,
        "diameter": radius * EXHAUST_WIDTH,
        "puffDiameter": radius * REACTOR_FLAME.puffSize,
        "sides": PART_FACETS,
    }
    build_reactor_flame(name, flame_size, root)
    return root

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

# A reactor's intake (D-330, D-337), at the nacelle's front, in nacelle radii: a hollow rounded
# hexagon scoop (owner, D-337: "make it start flat, then angled inward a little, and make a better
# inner part"): its outer skin runs on straight and flush from the nacelle (D-340, owner: "remove
# the circular bump around the intakes": it stood proud of the nacelle, with an accent band,
# before), then angles inward to a thin lip, then its duct turns in and back to the fan face
# (the profile runs back on itself); the loft's cap closes the duct's end. `[z from the
# nacelle's front, radius]`.
REACTOR_INTAKE = [
    [0.0, 1.0],
    [0.24, 1.0],
    [0.44, 0.86],
    [0.47, 0.8],
    [0.44, 0.75],
    [0.08, 0.7],
]
# The duct seen through the mouth: a dark lining facing inwards, a hair inside the skin's.
# Its back end lies behind the fan face: the duct's cap there and the fan face fought for depth
# when they lay in one plane (D-341).
REACTOR_INTAKE_DUCT = [[0.45, 0.74], [0.3, 0.71], [0.04, 0.67]]
# The dark fan face, a hair ahead of the duct's end, and the horizontal fins across the duct in
# front of it (owner, D-338: "replace the central helix by horizontal fins in the reactors"). In
# nacelle radii: the fins' front, just behind the lip's (0.47); how far out their ends reach, into
# the ring's wall between its lining and its skin, so they merge into the ring (owner, D-351:
# "make the fins merge into the outer ring on all reactors"); the room they have, the duct
# lining's radius.
REACTOR_INTAKE_FAN = {"z": 0.1, "radius": 0.68}
REACTOR_INTAKE_FINS: dict[str, Any] = {"front": 0.46, "ring": 0.8, "room": 0.71}
# Every intake's fins (the main reactors', the wing tips', the secondary scoops') are this thick
# and this deep in model units, whatever the size of the intake and the stretch of its frame
# (owner: "equalize the size of the fins between the different intakes", D-350): only their width
# follows the mouth they span. The depth runs back from the fins' front; it is the most the small
# wing-tip intakes hold ahead of their fan face. D-351 ("equalize the spacing too"): they stand
# `spacing` apart, one in the middle, as many as the mouth holds.
INTAKE_FIN_SIZE = {"thickness": 0.016, "depth": 0.035, "spacing": 0.038}


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


def polygon_turn(sides: int) -> float:
    """Return how far a reactor polygon is turned round Z so it lies with a flat side on top.

    A hexagon with a corner on +X already does; an octagon (D-339) is turned an eighth of a half
    turn, so its top, bottom and sides are flat.
    """
    return math.pi / sides if sides % 4 == 0 else 0.0


def _hexagon_sections(
    profile: list[list[float]], steps: int, sides: int = REACTOR_SIDES
) -> list[Any]:
    """Return the sections of a body round Z with a reactor's rounded polygon section."""
    return polygon_lathe_sections(profile, sides, REACTOR_ROUNDING, steps, polygon_turn(sides))


def hexagon_band(
    name: str,
    z: float,
    radius: float,
    half: float,
    material: Any,
    parent: Any,
    sides: int = REACTOR_SIDES,
) -> Any:
    """Create a band round the Z axis at `z`, a rounded hexagon `radius` out, `2 * half` wide.

    Its front, outer and back faces (its inner side lies in the body it rings), flat-shaded: the
    band's edges are sharp.
    """
    inner = radius - half
    outer = radius + half
    profile = [[-half, inner], [-half, outer], [half, outer], [half, inner]]
    sections = _hexagon_sections(profile, RING_CORNER_STEPS, sides)
    mesh = create_section_loft(name, sections, 0, parent.getScene())
    mesh.position.z = z
    mesh.material = material
    mesh.parent = parent
    return mesh


def _add_reactor_rings(name: str, size: dict[str, float], root: Any, sides: int) -> None:
    """Accent rings around the front of the nacelle and its nozzle, rounded hexagons as it is."""
    radius = size["radius"]
    length = size["length"]
    half = radius * 0.09  # half the ring's width and thickness
    accent = get_ship_materials(root.getScene()).accent
    for ring, z, scale in [("front", length * 0.3, 1.02), ("rear", -length / 2, 0.9)]:
        hexagon_band(name + "-" + ring + "-ring", z, radius * scale, half, accent, root, sides)


def add_reactor_intake(
    name: str,
    radius: float,
    front: float,
    root: Any,
    sides: int = REACTOR_SIDES,
    stretch: float = 1.0,
) -> Any:
    """Add an intake at `front` along Z of `root`, `sides` round (D-337); return its node.

    A hull-metal scoop, straight and flush with the nacelle, then angled in; inside, a
    matte black duct (D-347), a dark fan face and horizontal fins across the duct (D-338).
    `stretch` is how much `root`'s frame is stretched upright, so the fins keep their size (D-350).
    """
    scene = root.getScene()
    mats = get_ship_materials(scene)
    node = new_transform_node(name + "-intake", scene)
    node.position.z = front
    node.parent = root
    profile = [[p[0] * radius, p[1] * radius] for p in REACTOR_INTAKE]
    sections = _hexagon_sections(profile, REACTOR_CORNER_STEPS, sides)
    shell = create_section_loft(name + "-intake-shell", sections, len(sections[0][1]), scene)
    shell.material = mats.hull
    shell.parent = node
    # The duct's lining: a loft faces outward, turned round it faces the axis, seen through the
    # mouth (the metals cull their back faces).
    duct_profile = [[p[0] * radius, p[1] * radius] for p in REACTOR_INTAKE_DUCT]
    duct_sections = _hexagon_sections(duct_profile, REACTOR_CORNER_STEPS, sides)
    duct = create_section_loft(name + "-intake-duct", duct_sections, 0, scene)
    duct.flipFaces(True)
    duct.material = mats.intakeBlack
    duct.parent = node
    fan = REACTOR_INTAKE_FAN
    face = create_disc(name + "-intake-fan", disc_options(fan["radius"] * radius, sides), scene)
    face.convertToFlatShadedMesh()
    # A disc faces -Z: turned round, it faces the mouth (and turned as the duct's polygon is).
    face.rotation.y = math.pi
    face.rotation.z = polygon_turn(sides)
    face.position.z = fan["z"] * radius
    face.material = mats.intakeBlack
    face.parent = node
    _add_intake_fins(name, radius, mats.hullMid, node, sides, stretch)
    return node


def polygon_flat(sides: int) -> float:
    """Return how far out a reactor polygon's flat top lies, as a share of its radius."""
    if sides == 8:
        return math.cos(math.pi / 8)
    return math.sqrt(3) / 2


def intake_fin_half_width(y: float, sides: int = REACTOR_SIDES) -> float:
    """Half width of an intake fin at height `y` (in nacelle radii): the ring's polygon there.

    Its ends lie in the ring's wall (D-351). The hexagon has a corner on each side (+X, -X) and a
    flat top and bottom: each side narrows by 1 / sqrt(3) of the height. The octagon (D-339) has
    flat sides, top and bottom, `cos(pi / 8)` of the radius out, its slanted sides cutting the
    corners.
    """
    ring: float = REACTOR_INTAKE_FINS["ring"]
    if sides == 8:
        flat = ring * math.cos(math.pi / 8)
        return min(flat, flat * math.sqrt(2) - abs(y))
    return ring - abs(y) / math.sqrt(3)


def intake_fin_heights(room: float) -> list[float]:
    """Return the fins' heights round a mouth's middle, in model units (D-351).

    `spacing` apart, one in the middle, as many as fit within `room` of it, thickness included.
    """
    size = INTAKE_FIN_SIZE
    count = int((room - size["thickness"] / 2) / size["spacing"] + 1e-9)
    return [k * size["spacing"] for k in range(-count, count + 1)]


def intake_fin_thickness(stretch: float) -> float:
    """Return an intake fin's thickness in a frame stretched upright by `stretch` (D-350)."""
    thickness: float = INTAKE_FIN_SIZE["thickness"] / stretch
    return thickness


def _add_intake_fins(
    name: str, radius: float, material: Any, parent: Any, sides: int, stretch: float
) -> None:
    """Add the horizontal fins across the intake's duct, in front of its fan face (D-338)."""
    fins = REACTOR_INTAKE_FINS
    front = fins["front"] * radius
    back = front - INTAKE_FIN_SIZE["depth"]
    thickness = intake_fin_thickness(stretch)
    # The room in model units: the duct's flat top, stretched as the frame is.
    room = fins["room"] * polygon_flat(sides) * radius * stretch
    for k, height in enumerate(intake_fin_heights(room)):
        y = height / stretch
        half = intake_fin_half_width(y / radius, sides) * radius
        outline = [[-half, front], [half, front], [half, back], [-half, back]]
        fin = panel(name + "-intake-fin-" + str(k), outline, thickness, material, parent)
        fin.position.y = y


def build_reactor(
    name: str,
    size: dict[str, float],
    scene: Scene,
    intake: bool = False,
    sides: int = REACTOR_SIDES,
    stretch: float = 1.0,
) -> Any:
    """Build a reactor centred on its origin, thrusting towards -Z: a rounded hexagon nacelle.

    Plus a glowing blue core at the nozzle and an animated blue flame behind it (GFX-SHIP-06), and
    with `intake`, an intake at its front (D-330).
    """
    mats = get_ship_materials(scene)
    radius = size["radius"]
    length = size["length"]
    root = new_transform_node(name, scene)

    # With an intake, the nacelle runs on at full size to its front, where the intake's skin
    # carries it on flush (D-340: no bump round the intake); without one, it closes in.
    front = radius if intake else radius * 0.75
    profile = [
        [length / 2, 0],
        [length / 2, front],
        [length * 0.3, radius],
        [-length * 0.4, radius * 0.95],
        [-length / 2, radius * 0.85],
        [-length / 2, 0],
    ]
    sections = _hexagon_sections(profile, REACTOR_CORNER_STEPS, sides)
    nacelle = create_section_loft(name + "-nacelle", sections, len(sections[0][1]), scene)
    nacelle.material = mats.nozzle
    nacelle.parent = root

    _add_reactor_rings(name, size, root, sides)
    if intake:
        add_reactor_intake(name, radius, length / 2, root, sides, stretch)

    # A hexagon, its corners on the nacelle's (a disc's first corner is on +X too).
    core = create_disc(name + "-core", disc_options(radius * CORE_RADIUS, sides), scene)
    core.convertToFlatShadedMesh()
    core.rotation.z = polygon_turn(sides)
    core.position.z = -length / 2 - 0.01
    core.material = mats.reactorCore
    core.parent = root

    flame_size = {
        "nozzleZ": core.position.z,
        "length": length * EXHAUST_LENGTH,
        "diameter": radius * EXHAUST_WIDTH,
        "puffDiameter": radius * REACTOR_FLAME.puffSize,
        "sides": sides,
    }
    build_reactor_flame(name, flame_size, root)
    return root

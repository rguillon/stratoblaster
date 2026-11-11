# Copyright (c) 2026 Renaud Guillon
"""Parts shared by the player ships: panels, plates, lights, rods, and the reactors.

Each part is a Babylon mesh made by the render layer, parented to a node of the ship.
"""

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
    create_smooth_top_lathe_along_z,
)
from render.geometry.prism import create_prism

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


def _add_reactor_rings(name: str, size: dict[str, float], root: Any) -> None:
    """Accent rings around the front of the nacelle and its nozzle."""
    scene = root.getScene()
    radius = size["radius"]
    length = size["length"]
    half = radius * 0.09  # half the ring's width and thickness
    for ring, z, scale in [("front", length * 0.3, 1.02), ("rear", -length / 2, 0.9)]:
        # A band round the nacelle: an open lathe, its front and back faces and its outer side
        # (its inner side lies on the nacelle). The outer side runs towards +Z, so its faces point
        # outward.
        mesh = create_faceted_lathe_along_z(
            name + "-" + ring + "-ring",
            [
                [-half, radius * scale - half],
                [-half, radius * scale + half],
                [half, radius * scale + half],
                [half, radius * scale - half],
            ],
            SMOOTH_PART_SECTION,
            scene,
        )
        mesh.position.z = z
        mesh.material = get_ship_materials(scene).accent
        mesh.parent = root


def build_reactor(name: str, size: dict[str, float], scene: Scene) -> Any:
    """Build a reactor centred on its origin, thrusting towards -Z: a hexagonal metal nacelle.

    Plus a glowing blue core at the nozzle and an animated blue flame behind it (GFX-SHIP-06).
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
    nacelle = create_smooth_top_lathe_along_z(
        name + "-nacelle", profile, SMOOTH_PART_SECTION, scene
    )
    nacelle.material = mats.nozzle
    nacelle.parent = root

    _add_reactor_rings(name, size, root)

    core = create_disc(
        name + "-core",
        disc_options(radius * CORE_RADIUS, SMOOTH_PART_SECTION.upper),
        scene,
    )
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

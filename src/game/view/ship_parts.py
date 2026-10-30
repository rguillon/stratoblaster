"""Parts shared by the player ships: panels, plates, lights, rods, and the reactors Each part is a
Babylon mesh made by the render layer, parented to a node of the
ship.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.ship_look import REACTOR_FLAME
from game.view.reactor_flame import build_reactor_flame
from game.view.ship_materials import get_ship_materials

# Not in render/babylon.py yet.
from render.babylon import (
    create_disc,
    create_polyhedron,
    new_transform_node,
)
from render.geometry.lathe_z import LatheHalves, create_faceted_lathe_along_z
from render.geometry.prism import create_prism

__pragma__("skip")
from typing import Any  # noqa: E402

Scene = Any  # noqa: E402


__pragma__("noskip")

# Sides of polygonal parts (nacelles, canopies, intakes, pods): a hexagonal section.
PART_FACETS = 6


# Section of fuselages: a smooth, finely faceted top over a low-poly 3-facet belly.
BODY_SECTION = LatheHalves(20, 3)

PLATE_THICKNESS = 0.012
NAV_LIGHT_SIZE = 0.07

EXHAUST_LENGTH = 0.8  # relative to the nacelle length
EXHAUST_WIDTH = 1.5  # relative to the nacelle radius
CORE_RADIUS = 0.8  # relative to the nacelle radius


def _set_part_metadata(node: Any, part: str) -> None:
    """`node.metadata = { part }`: the object Babylon keeps as metadata."""
    __pragma__("js", "{}", "node.metadata = {part: part};")


def _part_of_metadata(node: Any) -> Any:
    """`node.metadata?.part`, or undefined."""
    result: Any = None
    __pragma__("js", "{}", "result = node.metadata ? node.metadata.part : undefined;")
    return result


def _polyhedron_options(kind: int, size: float) -> Any:
    """Options for `CreatePolyhedron`: `{ type, size }`."""
    options: Any = None
    __pragma__("js", "{}", "options = {type: kind, size: size};")
    return options


def disc_options(radius: float, tessellation: int) -> Any:
    """Options for `CreateDisc`: `{ radius, tessellation }`."""
    options: Any = None
    __pragma__("js", "{}", "options = {radius: radius, tessellation: tessellation};")
    return options


def tag_part(node: Any, part: str) -> Any:
    """Tags a node with its ship part and returns it."""
    _set_part_metadata(node, part)
    return node


def part_of(node: Any) -> Any:
    """Returns the ship part a node was tagged with, if any."""
    return _part_of_metadata(node)


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
    """Creates a flat panel (wing, tail...) with the given material, parented to `parent`."""
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
    """Creates a thin panel lying `y` above (or below, if negative) its parent's plane: trim,
    stripes."""
    mesh = panel(name, outline, PLATE_THICKNESS, material, parent)
    mesh.position.y = y
    return mesh


def nav_light(name: str, position: Any, parent: Any) -> Any:
    """Creates a small blue light (tagged `light`) at `position` in `parent`'s space."""
    scene = parent.getScene()
    # An octahedron (8 triangles): at this size and glowing, it reads as a round light.
    mesh = tag_part(
        create_polyhedron(name, _polyhedron_options(1, NAV_LIGHT_SIZE / 2), scene),
        "light",
    )
    mesh.material = get_ship_materials(scene).navLight
    mesh.position.copyFrom(position)
    mesh.parent = parent
    return mesh


def faceted_rod(
    name: str,
    size: dict[str, float],
    position: Any,
    material: Any,
    parent: Any,
    sides: int = 4,
) -> Any:
    """Creates a polygonal bar along Z (4 sides: a diamond section), centred on `position`."""
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
        # A polygonal band: an open lathe around the nacelle. Closed loop; the outer side runs
        # towards +Z so its faces point outward.
        mesh = create_faceted_lathe_along_z(
            name + "-" + ring + "-ring",
            [
                [half, radius * scale - half],
                [-half, radius * scale - half],
                [-half, radius * scale + half],
                [half, radius * scale + half],
                [half, radius * scale - half],
            ],
            PART_FACETS,
            scene,
        )
        mesh.position.z = z
        mesh.material = get_ship_materials(scene).accent
        mesh.parent = root


def build_reactor(name: str, size: dict[str, float], scene: Scene) -> Any:
    """Builds a reactor centred on its origin, thrusting towards -Z: a hexagonal metal nacelle, a
    glowing blue core at the nozzle and an animated blue flame behind it."""
    mats = get_ship_materials(scene)
    radius = size["radius"]
    length = size["length"]
    root = tag_part(new_transform_node(name, scene), "reactor")

    profile = [
        [length / 2, 0],
        [length / 2, radius * 0.75],
        [length * 0.3, radius],
        [-length * 0.4, radius * 0.95],
        [-length / 2, radius * 0.85],
        [-length / 2, 0],
    ]
    nacelle = create_faceted_lathe_along_z(name + "-nacelle", profile, PART_FACETS, scene)
    nacelle.material = mats.nozzle
    nacelle.parent = root

    _add_reactor_rings(name, size, root)

    core = create_disc(
        name + "-core",
        disc_options(radius * CORE_RADIUS, PART_FACETS),
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

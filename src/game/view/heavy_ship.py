"""The heavy player ship (P02-R02): inspired by modern flying-wing
stealth bombers (B-2 / B-21): no fuselage and no tail, swept leading edges with accent bands,
sawtooth trailing edge with elevons, a raised cockpit with a dark visor, dorsal intakes feeding 2
reactors, bomb bay doors underneath. Wingspan 6 units. Low-poly and polygonal like the other
ships: faceted hump and visor.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.view.ship_materials import get_ship_materials
from game.view.ship_parts import (
    BODY_SECTION,
    PART_FACETS,
    build_reactor,
    disc_options,
    mirror_x,
    nav_light,
    panel,
    plate,
    tag_part,
)

# create_disc: render/babylon.py.
from render.babylon import (
    create_disc,
    new_transform_node,
    vector3,
)
from render.geometry.lathe_z import create_faceted_lathe_along_z

# Right half of the planform (X >= 0), nose to wing tip to centre line.
HALF_WING = [
    [0, 1.7],
    [3.0, -0.55],
    [2.85, -0.8],
    [1.85, -0.2],
    [1.15, -0.9],
    [0.55, -0.45],
    [0, -0.95],
]


def _heavy_planform() -> list[list[float]]:
    """Full planform, clockwise from the nose: the right half, then the left half reversed."""
    mirrored = mirror_x(HALF_WING[1:-1])
    mirrored.reverse()
    planform = [point for point in HALF_WING]
    planform.extend(mirrored)
    return planform


# Full planform, clockwise from the nose.
HEAVY_PLANFORM = _heavy_planform()
# Accent band just behind the right leading edge.
LEADING_BAND = [
    [0.12, 1.55],
    [2.9, -0.53],
    [2.8, -0.6],
    [0.12, 1.4],
]
# Elevons along the right sawtooth trailing edge.
ELEVONS = [
    [
        [1.9, -0.12],
        [2.7, -0.6],
        [2.72, -0.69],
        [1.92, -0.21],
    ],
    [
        [0.62, -0.38],
        [1.1, -0.74],
        [1.12, -0.83],
        [0.6, -0.46],
    ],
]
# Right bomb bay door, under the centre body.
BAY_DOOR = [
    [0.03, 0.55],
    [0.38, 0.5],
    [0.38, -0.3],
    [0.03, -0.35],
]
WING_THICKNESS = 0.12
REACTOR_OFFSET_X = 0.7
REACTOR = {"radius": 0.2, "length": 1.1}

__pragma__("skip")
from typing import Any  # noqa: E402

Scene = Any
__pragma__("noskip")

SIDES = [("right", 1), ("left", -1)]


def _for_side(sign: float, outline: list[list[float]]) -> list[list[float]]:
    """The outline as it stands for the right side (sign > 0), mirrored for the left."""
    return outline if sign > 0 else mirror_x(outline)


def _build_wing(root: Any, scene: Any) -> None:
    """The flying wing: its planform, accent bands, elevons and bay doors."""
    mats = get_ship_materials(scene)
    wing = tag_part(new_transform_node("heavy-wing", scene), "wing")
    wing.parent = root
    panel("heavy-wing-panel", HEAVY_PLANFORM, WING_THICKNESS, mats.hull, wing)
    top = WING_THICKNESS / 2
    for side, sign in SIDES:
        plate("heavy-band-" + side, _for_side(sign, LEADING_BAND), top, mats.accent, wing)
        for i, elevon in enumerate(ELEVONS):
            plate(
                "heavy-elevon-" + side + "-" + str(i),
                _for_side(sign, elevon),
                top,
                mats.trim,
                wing,
            )
        plate("heavy-bay-door-" + side, _for_side(sign, BAY_DOOR), -top, mats.trim, wing)
        nav_light("heavy-wing-" + side + "-light", vector3(sign * 2.95, 0, -0.6), wing)


def _build_cockpit(root: Any, scene: Any) -> None:
    """The raised cockpit hump with its dark visor and dorsal light."""
    mats = get_ship_materials(scene)
    frame = create_faceted_lathe_along_z(
        "heavy-cockpit",
        [
            [1.25, 0],
            [1.15, 0.2],
            [0.95, 0.28],
            [0.7, 0],
        ],
        BODY_SECTION,
        scene,
    )
    frame.scaling.set(1.05, 0.3, 1)
    frame.position.y = 0.13
    frame.material = mats.trim
    frame.parent = root

    # Dark visor set into the front of the cockpit hump.
    visor = tag_part(
        create_faceted_lathe_along_z(
            "heavy-visor",
            [
                [1.29, 0],
                [1.22, 0.15],
                [1.08, 0.21],
                [0.92, 0],
            ],
            BODY_SECTION,
            scene,
        ),
        "canopy",
    )
    visor.scaling.y = 0.32
    visor.position.y = 0.15
    visor.material = mats.canopy
    visor.parent = root
    nav_light("heavy-dorsal-light", vector3(0, 0.22, 0.1), root)


def _build_centre_body(root: Any, scene: Any) -> None:
    """The lens-shaped centre body that joins the wing to the cockpit."""
    mats = get_ship_materials(scene)
    body = create_faceted_lathe_along_z(
        "heavy-body",
        [
            [1.65, 0],
            [1.1, 0.3],
            [0.2, 0.5],
            [-0.6, 0.38],
            [-0.85, 0],
        ],
        BODY_SECTION,
        scene,
    )
    body.scaling.set(1.7, 0.42, 1)
    body.material = mats.hull
    body.parent = tag_part(new_transform_node("heavy-body-root", scene), "body")
    body.parent.parent = root


def _build_intake(side: str, sign: float, root: Any, scene: Any) -> None:
    """A dorsal intake hump with its dark mouth, facing forward."""
    mats = get_ship_materials(scene)
    hump = create_faceted_lathe_along_z(
        "heavy-intake-" + side,
        [
            [0.55, 0],
            [0.55, 0.2],
            [0.2, 0.25],
            [-0.5, 0.24],
            [-0.5, 0],
        ],
        PART_FACETS,
        scene,
    )
    hump.scaling.y = 0.6
    hump.position.set(sign * REACTOR_OFFSET_X, 0.06, -0.1)
    hump.material = mats.accent
    hump.parent = root
    # Dark intake mouth, facing forward.
    mouth = create_disc(
        "heavy-intake-" + side + "-mouth",
        disc_options(0.17, PART_FACETS),
        scene,
    )
    mouth.convertToFlatShadedMesh()
    mouth.rotation.y = math.pi
    mouth.scaling.y = 0.6
    mouth.position.set(sign * REACTOR_OFFSET_X, 0.06, 0.46)
    mouth.material = mats.canopy
    mouth.parent = root


def build_heavy_ship(scene: Any) -> Any:
    """Builds the heavy player ship (P02-R02)."""
    root = new_transform_node("ship-heavy", scene)
    _build_wing(root, scene)
    _build_centre_body(root, scene)
    _build_cockpit(root, scene)
    for side, sign in SIDES:
        _build_intake(side, sign, root, scene)
        reactor = build_reactor("heavy-reactor-" + side, REACTOR, scene)
        reactor.position.set(sign * REACTOR_OFFSET_X, 0.05, -0.55)
        reactor.parent = root
    return root

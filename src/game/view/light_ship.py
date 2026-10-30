"""The light player ship (P02-R03): a faceted tandem-wing interceptor,
like a dragonfly. A small front wing pair sits low (anhedral) and a larger swept rear pair sits
high (dihedral); each of the 4 wings carries a hexagonal reactor at its tip, so the front flames
stream under the rear wings. Everything is polygonal: fuselage with a smooth top and a faceted
belly, hexagonal canopy and nacelles, diamond-section cannons.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

Scene = Any
__pragma__("noskip")

from game.view.ship_materials import get_ship_materials  # noqa: E402
from game.view.ship_parts import (  # noqa: E402
    BODY_SECTION,
    PART_FACETS,
    build_reactor,
    faceted_rod,
    mirror_x,
    nav_light,
    panel,
    plate,
    tag_part,
)
from render.babylon import new_transform_node, vector3  # noqa: E402
from render.geometry.lathe_z import create_faceted_lathe_along_z  # noqa: E402

# Right front wing (X > 0): short, swept back.
FRONT_WING = [
    [0.18, 1.0],
    [0.85, 0.62],
    [0.85, 0.3],
    [0.18, 0.25],
]
FRONT_STRIPE = [
    [0.4, 0.82],
    [0.78, 0.6],
    [0.78, 0.52],
    [0.4, 0.72],
]
# Right rear wing (X > 0): larger, swept back, with a cranked trailing edge.
REAR_WING = [
    [0.18, -0.1],
    [1.68, -0.66],
    [1.68, -1.0],
    [0.9, -0.95],
    [0.18, -1.2],
]
REAR_STRIPE = [
    [0.5, -0.3],
    [1.6, -0.72],
    [1.6, -0.82],
    [0.5, -0.42],
]
# Darker panel where the rear wing meets the fuselage.
REAR_ROOT = [
    [0.18, -0.1],
    [0.5, -0.22],
    [0.5, -1.08],
    [0.18, -1.2],
]
# Dorsal blade, standing up (X becomes height).
FIN = [
    [0, -0.35],
    [0.36, -1.0],
    [0.36, -1.18],
    [0, -1.3],
]
# Canopy profile, `[z, radius]`.
CANOPY = [
    [1.35, 0],
    [1.2, 0.07],
    [0.9, 0.1],
    [0.65, 0],
]
WING_THICKNESS = 0.05
CANNON = {"length": 0.9, "radius": 0.035}


def _light_wings() -> list[dict[str, Any]]:
    """The 4 wings: front or rear pair, side, tilt around the nose axis and tip reactor."""
    wings: list[dict[str, Any]] = []
    for side in ["right", "left"]:
        wings.append(
            {
                "name": "front-" + side,
                "pair": "front",
                "side": 1 if side == "right" else -1,
                "outline": FRONT_WING,
                "stripe": FRONT_STRIPE,
                "tilt": -0.22,  # anhedral: tips down
                "reactor": {"radius": 0.1, "length": 0.7, "x": 0.92, "z": 0.42},
            }
        )
    for side in ["right", "left"]:
        wings.append(
            {
                "name": "rear-" + side,
                "pair": "rear",
                "side": 1 if side == "right" else -1,
                "outline": REAR_WING,
                "stripe": REAR_STRIPE,
                "tilt": 0.16,  # dihedral: tips up
                "reactor": {"radius": 0.13, "length": 1.0, "x": 1.76, "z": -0.78},
            }
        )
    return wings


LIGHT_WINGS = _light_wings()


def _build_body(root: Any, scene: Any) -> None:
    """The fuselage, with its accent collar between the cockpit and the wings."""
    mats = get_ship_materials(scene)
    body_root = tag_part(new_transform_node("light-body-root", scene), "body")
    body_root.parent = root
    body = create_faceted_lathe_along_z(
        "light-body",
        [
            [2.15, 0],
            [1.85, 0.08],
            [1.5, 0.15],
            [1.0, 0.21],
            [0.5, 0.25],
            [-0.3, 0.25],
            [-0.9, 0.21],
            [-1.25, 0.15],
            [-1.4, 0],
        ],
        BODY_SECTION,
        scene,
    )
    body.scaling.y = 0.75
    body.material = mats.hull
    body.parent = body_root
    # Accent collar between the cockpit and the wings.
    collar = create_faceted_lathe_along_z(
        "light-collar",
        [
            [0.2, 0],
            [0.2, 0.27],
            [0.05, 0.27],
            [0.05, 0],
        ],
        BODY_SECTION,
        scene,
    )
    collar.scaling.y = 0.78
    collar.material = mats.accent
    collar.parent = body_root


def _build_fin_and_cannons(root: Any, scene: Any) -> None:
    """Dorsal blade and the twin cannons under the front wing roots."""
    mats = get_ship_materials(scene)
    fin = new_transform_node("light-fin", scene)
    fin.position.y = 0.14
    fin.rotation.z = math.pi / 2
    fin.parent = root
    panel("light-fin-panel", FIN, 0.04, mats.accent, fin)
    nav_light("light-fin-light", vector3(0.36, 0, -1.09), fin)

    # Diamond section.
    for sign in [1, -1]:
        x = sign * 0.3
        side = "right" if sign > 0 else "left"
        faceted_rod(
            "light-cannon-" + side,
            CANNON,
            vector3(x, -0.1, 1.0),
            mats.trim,
            root,
        )
        nav_light(
            "light-cannon-" + side + "-muzzle",
            vector3(x, -0.1, 1.0 + CANNON["length"] / 2),
            root,
        )


def _build_cockpit(root: Any, scene: Any) -> None:
    """The cockpit: a dark frame and the canopy."""
    mats = get_ship_materials(scene)

    def profile(scale: float) -> list[list[float]]:
        return [[point[0], point[1] * scale] for point in CANOPY]

    frame = create_faceted_lathe_along_z("light-canopy-frame", profile(1.2), PART_FACETS, scene)
    frame.scaling.y = 0.8
    frame.position.y = 0.1
    frame.material = mats.trim
    frame.parent = root

    canopy = tag_part(
        create_faceted_lathe_along_z("light-canopy", profile(1), PART_FACETS, scene),
        "canopy",
    )
    canopy.scaling.y = 0.9
    canopy.position.y = 0.13
    canopy.material = mats.canopy
    canopy.parent = root


def _build_wing(wing_def: dict[str, Any], root: Any, scene: Any) -> None:
    """One wing of the ship, with its reactor and wing-tip light."""
    mats = get_ship_materials(scene)
    name = wing_def["name"]
    side = wing_def["side"]
    tilt = wing_def["tilt"]
    pod = wing_def["reactor"]

    def for_side(outline: list[list[float]]) -> list[list[float]]:
        return outline if side > 0 else mirror_x(outline)

    wing = tag_part(new_transform_node("light-wing-" + name, scene), "wing")
    # Tilt around the nose axis: a positive tilt raises the tip of a right wing.
    wing.rotation.z = side * tilt
    wing.parent = root
    panel(
        "light-wing-" + name + "-panel",
        for_side(wing_def["outline"]),
        WING_THICKNESS,
        mats.hull,
        wing,
    )
    plate(
        "light-wing-" + name + "-stripe",
        for_side(wing_def["stripe"]),
        WING_THICKNESS / 2,
        mats.accent,
        wing,
    )
    if wing_def["pair"] == "rear":
        plate(
            "light-wing-" + name + "-root",
            for_side(REAR_ROOT),
            WING_THICKNESS / 2,
            mats.trim,
            wing,
        )

    reactor = build_reactor("light-reactor-" + name, pod, scene)
    reactor.position.set(side * pod["x"], 0, pod["z"])
    reactor.parent = wing
    nav_light(
        "light-wing-" + name + "-light",
        vector3(side * (pod["x"] + pod["radius"]), 0, pod["z"] + pod["length"] * 0.3),
        wing,
    )


def build_light_ship(scene: Any) -> Any:
    """Builds the light player ship (P02-R03)."""
    root = new_transform_node("ship-light", scene)
    _build_body(root, scene)
    _build_fin_and_cannons(root, scene)
    _build_cockpit(root, scene)
    for wing in LIGHT_WINGS:
        _build_wing(wing, root, scene)
    return root

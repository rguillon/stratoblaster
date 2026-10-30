"""The balanced player ship (P02-R01): inspired by the Macross
Delta VF-31J: long pointed nose, framed bubble canopy, canards, dual reactors fed by side intakes,
forward-swept wings, canted twin tails and ventral fins, a gun pod under the belly. Model units:
nose towards +Z, about 4.8 units long. Low-poly and polygonal like the other ships: fuselage with
a smooth top and a faceted belly, canopy, intakes and pods.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.view.ship_materials import get_ship_materials
from game.view.ship_parts import (
    BODY_SECTION,
    PART_FACETS,
    build_reactor,
    disc_options,
    faceted_rod,
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

__pragma__("skip")
from typing import Any  # noqa: E402

Scene = Any
__pragma__("noskip")

# Right main wing (X > 0). The tip's leading edge is ahead of the root's: forward-swept.
BALANCED_WING = [
    [0.35, 0.15],
    [2.0, 0.7],
    [2.05, 0.4],
    [0.35, -0.95],
]
WING_THICKNESS = 0.07
# Accent band near the wing tip, following the forward sweep.
WING_BAND = [
    [1.45, 0.48],
    [1.75, 0.58],
    [1.78, 0.3],
    [1.48, 0.12],
]
# Trailing-edge flap line.
WING_FLAP = [
    [0.45, -0.72],
    [1.3, -0.1],
    [1.36, -0.2],
    [0.45, -0.86],
]
STRAKE = [
    [0.2, 1.3],
    [0.62, 0.35],
    [0.2, 0.2],
]
CANARD = [
    [0.22, 1.12],
    [0.68, 0.86],
    [0.7, 0.74],
    [0.22, 0.8],
]
TAIL = [
    [0, -0.75],
    [0.85, -1.35],
    [0.85, -1.6],
    [0, -1.55],
]
TAIL_STRIPE = [
    [0.5, -1.15],
    [0.75, -1.3],
    [0.75, -1.4],
    [0.5, -1.27],
]
VENTRAL_FIN = [
    [0, -0.95],
    [0.38, -1.25],
    [0.38, -1.4],
    [0, -1.35],
]
TAIL_CANT = 0.4  # rad from vertical, outwards
VENTRAL_CANT = 0.55  # rad from vertical, outwards
REACTOR_OFFSET_X = 0.42
REACTOR = {"radius": 0.22, "length": 1.7}

# Canopy profile, `[z, radius]`.
CANOPY = [
    [1.4, 0],
    [1.25, 0.08],
    [1.1, 0.11],
    [0.9, 0.08],
    [0.8, 0],
]
# Middle of the canopy along Z, for scaling the frame around it.
CANOPY_MID_Z = 1.1


def _build_body(root: Any, scene: Any) -> None:
    """The fuselage, its dorsal spine, and the gun pod under the belly."""
    mats = get_ship_materials(scene)
    body_root = tag_part(new_transform_node("balanced-body-root", scene), "body")
    body_root.parent = root
    body = create_faceted_lathe_along_z(
        "balanced-body",
        [
            [2.4, 0],
            [2.2, 0.07],
            [1.8, 0.14],
            [0.9, 0.3],
            [-0.2, 0.36],
            [-1.4, 0.3],
            [-1.6, 0],
        ],
        BODY_SECTION,
        scene,
    )
    body.scaling.y = 0.7
    body.material = mats.hull
    body.parent = body_root

    # Dorsal spine running from the canopy to the tails.
    spine = create_faceted_lathe_along_z(
        "balanced-spine",
        [
            [0.7, 0],
            [0.3, 0.12],
            [-1.2, 0.11],
            [-1.55, 0],
        ],
        PART_FACETS,
        scene,
    )
    spine.position.y = 0.17
    spine.scaling.x = 0.8
    spine.material = mats.hull
    spine.parent = body_root

    faceted_rod(
        "balanced-gun-pod",
        {"length": 1.7, "radius": 0.065},
        vector3(0, -0.28, 0.2),
        mats.trim,
        root,
        PART_FACETS,
    )
    nav_light("balanced-gun-muzzle", vector3(0, -0.28, 1.06), root)


def _build_cockpit(root: Any, scene: Any) -> None:
    """The bubble canopy and its frame."""
    mats = get_ship_materials(scene)
    # The frame is the canopy profile, a bit larger and longer.
    frame_profile = [
        [CANOPY_MID_Z + (point[0] - CANOPY_MID_Z) * 1.2, point[1] * 1.2] for point in CANOPY
    ]
    frame = create_faceted_lathe_along_z("balanced-canopy-frame", frame_profile, PART_FACETS, scene)
    frame.scaling.y = 0.8
    frame.position.y = 0.15
    frame.material = mats.trim
    frame.parent = root

    canopy = tag_part(
        create_faceted_lathe_along_z("balanced-canopy", CANOPY, PART_FACETS, scene),
        "canopy",
    )
    canopy.position.y = 0.17
    canopy.material = mats.canopy
    canopy.parent = root


def _build_intake(side: str, sign: float, root: Any, scene: Any) -> None:
    """A side intake with its dark mouth, facing forward."""
    mats = get_ship_materials(scene)
    intake = create_faceted_lathe_along_z(
        "balanced-intake-" + side,
        [
            [0.35, 0],
            [0.35, 0.15],
            [-0.2, 0.2],
            [-0.2, 0],
        ],
        PART_FACETS,
        scene,
    )
    intake.scaling.x = 0.8
    intake.position.set(sign * REACTOR_OFFSET_X, -0.06, 0.05)
    intake.material = mats.trim
    intake.parent = root
    # Dark intake mouth, facing forward.
    mouth = create_disc(
        "balanced-intake-" + side + "-mouth",
        disc_options(0.12, PART_FACETS),
        scene,
    )
    mouth.convertToFlatShadedMesh()
    mouth.rotation.y = math.pi
    mouth.scaling.x = 0.8
    mouth.position.set(sign * REACTOR_OFFSET_X, -0.06, 0.41)
    mouth.material = mats.canopy
    mouth.parent = root


def _build_wing(side: str, sign: float, root: Any, scene: Any) -> None:
    """A forward-swept main wing with its band, flap, strake, canard and wing-tip light."""
    mats = get_ship_materials(scene)

    def mirror(outline: list[list[float]]) -> list[list[float]]:
        return outline if sign > 0 else mirror_x(outline)

    wing = tag_part(new_transform_node("balanced-wing-" + side, scene), "wing")
    wing.parent = root
    panel(
        "balanced-wing-" + side + "-panel", mirror(BALANCED_WING), WING_THICKNESS, mats.hull, wing
    )
    plate(
        "balanced-wing-" + side + "-band", mirror(WING_BAND), WING_THICKNESS / 2, mats.accent, wing
    )
    plate("balanced-wing-" + side + "-flap", mirror(WING_FLAP), WING_THICKNESS / 2, mats.trim, wing)
    panel("balanced-strake-" + side, mirror(STRAKE), 0.05, mats.accent, wing)
    canard = panel("balanced-canard-" + side, mirror(CANARD), 0.04, mats.hull, wing)
    canard.position.y = 0.08
    nav_light("balanced-wing-" + side + "-light", vector3(sign * 2.03, 0, 0.55), wing)


def _build_tails(side: str, sign: float, root: Any, scene: Any) -> None:
    """The canted twin tail and the ventral fin on one side."""
    mats = get_ship_materials(scene)
    tail = tag_part(new_transform_node("balanced-tail-" + side, scene), "tail")
    tail.position.set(sign * 0.38, 0.12, 0)
    # Stand the panel up (X becomes height), then cant it outwards.
    tail.rotation.z = math.pi / 2 - sign * TAIL_CANT
    tail.parent = root
    panel("balanced-tail-" + side + "-panel", TAIL, 0.05, mats.hull, tail)
    plate("balanced-tail-" + side + "-stripe", TAIL_STRIPE, sign * 0.03, mats.accent, tail)
    nav_light("balanced-tail-" + side + "-light", vector3(0.85, 0, -1.47), tail)

    # Ventral fin: same trick, pointing down and outwards.
    fin = new_transform_node("balanced-ventral-" + side, scene)
    fin.position.set(sign * 0.3, -0.16, 0)
    fin.rotation.z = -math.pi / 2 + sign * VENTRAL_CANT
    fin.parent = root
    panel("balanced-ventral-" + side + "-panel", VENTRAL_FIN, 0.04, mats.accent, fin)


def build_balanced_ship(scene: Any) -> Any:
    """Builds the balanced player ship (P02-R01)."""
    root = new_transform_node("ship-balanced", scene)
    _build_body(root, scene)
    _build_cockpit(root, scene)
    for side, sign in [("right", 1), ("left", -1)]:
        _build_intake(side, sign, root, scene)
        _build_wing(side, sign, root, scene)
        _build_tails(side, sign, root, scene)
        reactor = build_reactor("balanced-reactor-" + side, REACTOR, scene)
        reactor.position.set(sign * REACTOR_OFFSET_X, -0.05, -0.95)
        reactor.parent = root
    return root

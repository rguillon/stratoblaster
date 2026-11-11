# Copyright (c) 2026 Renaud Guillon
"""The balanced player ship (GFX-SHIP-01), inspired by the Macross Delta VF-31J.

Long pointed nose, framed bubble canopy, canards, dual reactors fed by side intakes, forward-swept
wings, canted twin tails and ventral fins, a gun pod under the belly. Model units: nose towards +Z,
about 4.8 units long. The hull is one blended skin (`balanced_hull.py`): the fuselage's back,
the nacelle shoulders and the chines sweeping into the wing roots melt into each other through
fillets, instead of being separate shapes put together. The hull, canopy, intakes and nacelles have
a smooth-shaded top over a low-poly faceted belly: the triangles go on the upper half, which the
playfield camera sees (GFX-SHIP-05).
"""

import math

from game.view.balanced_hull import TOP_POINTS, hull_sections
from game.view.ship_materials import get_ship_materials
from game.view.ship_parts import (
    PART_FACETS,
    SMOOTH_PART_SECTION,
    build_reactor,
    disc_options,
    faceted_rod,
    mirror_x,
    panel,
    plate,
)

# create_disc: render/babylon.py.
from render.babylon import (
    create_disc,
    new_transform_node,
    vector3,
)
from render.geometry.lathe_z import (
    LatheHalves,
    create_faceted_lathe_along_z,
    create_smooth_top_lathe_along_z,
    smooth_profile,
)
from render.geometry.section_loft import create_section_loft

# isort: split
# __pragma__ ("skip")
from typing import Any

Scene = Any
# __pragma__ ("noskip")


# Right main wing (X > 0). The tip's leading edge is ahead of the root's: forward-swept.
BALANCED_WING = [
    [0.35, 0.15],
    [2.0, 0.7],
    [2.05, 0.4],
    [0.35, -0.95],
]
WING_THICKNESS = 0.07
# Trailing-edge flap line.
WING_FLAP = [
    [0.45, -0.72],
    [1.3, -0.1],
    [1.36, -0.2],
    [0.45, -0.86],
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
VENTRAL_FIN = [
    [0, -0.95],
    [0.38, -1.25],
    [0.38, -1.4],
    [0, -1.35],
]
TAIL_CANT = 0.4  # rad from vertical, outwards
VENTRAL_CANT = 0.55  # rad from vertical, outwards
REACTOR_OFFSET_X = 0.42
# The reactors sit low, inside the hull's shoulders: only their nozzles show behind its tail.
REACTOR_Y = -0.08
REACTOR = {"radius": 0.22, "length": 1.7}

# Segments of each hand-set profile are cut into this many along a smooth curve.
PROFILE_STEPS = 3

# Canopy profile, `[z, radius]`: a teardrop bubble, its peak ahead of its middle.
CANOPY = [
    [1.45, 0],
    [1.33, 0.065],
    [1.15, 0.11],
    [0.95, 0.105],
    [0.8, 0.06],
    [0.7, 0],
]
# Reactor intake, hollow: its outer skin runs from the reactor's front to a flared lip, then the
# duct turns in and runs back to the fan face (the profile runs back on itself, so the duct's
# faces look inwards). In the intake's own frame; its node sits at the reactor's front.
INTAKE = [
    [-0.15, 0],
    [-0.15, 0.2],
    [0.15, 0.205],
    [0.45, 0.215],
    [0.55, 0.2],
    [0.52, 0.15],
    [0.38, 0.14],
    [0.38, 0],
]
# The accent lip round the mouth, the blue ring round the fan face, the fan's spinner.
INTAKE_LIP = {"z": 0.5, "radius": 0.212, "half": 0.022}
INTAKE_FAN = {"z": 0.385, "radius": 0.135, "ringRadius": 0.12, "ringHalf": 0.012}
INTAKE_SPINNER = [[0.385, 0.055], [0.43, 0.035], [0.46, 0]]
# The intakes' oval section and their place, ahead of the reactors.
INTAKE_SCALE_X = 0.85
INTAKE_Y = -0.07
INTAKE_Z = 0.05
# The canopy's smooth top: finer than the other parts, it is the shiniest thing on the ship.
CANOPY_SECTION = LatheHalves(16, 3)
CANOPY_FRAME_SECTION = LatheHalves(8, 2)
# Middle of the canopy along Z, for scaling the frame around it.
CANOPY_MID_Z = 1.08


def _build_body(root: Any, scene: Any) -> None:
    """Build the blended hull (fuselage, nacelle shoulders, chines) and the gun pod under it."""
    mats = get_ship_materials(scene)
    body_root = new_transform_node("balanced-body-root", scene)
    body_root.parent = root
    # One skin, smooth on top: the first `TOP_POINTS` of each section are its upper half.
    body = create_section_loft("balanced-body", hull_sections(), TOP_POINTS, scene)
    body.material = mats.hull
    body.parent = body_root

    faceted_rod(
        "balanced-gun-pod",
        {"length": 1.7, "radius": 0.065},
        vector3(0, -0.28, 0.2),
        mats.trim,
        root,
        PART_FACETS,
    )


def _build_cockpit(root: Any, scene: Any) -> None:
    """Build the bubble canopy and its frame."""
    mats = get_ship_materials(scene)
    # The frame is the canopy profile, a bit larger and longer.
    frame_profile = [
        [CANOPY_MID_Z + (point[0] - CANOPY_MID_Z) * 1.2, point[1] * 1.2] for point in CANOPY
    ]
    # Mostly hidden under the canopy: only its rim shows, so it stays coarse.
    frame = create_smooth_top_lathe_along_z(
        "balanced-canopy-frame", frame_profile, CANOPY_FRAME_SECTION, scene
    )
    frame.scaling.y = 0.8
    frame.position.y = 0.15
    frame.material = mats.trim
    frame.parent = root

    canopy = create_smooth_top_lathe_along_z(
        "balanced-canopy", smooth_profile(CANOPY, PROFILE_STEPS), CANOPY_SECTION, scene
    )
    canopy.position.y = 0.17
    canopy.material = mats.canopy
    canopy.parent = root


def _band(name: str, z: float, radius: float, half: float, material: Any, parent: Any) -> Any:
    """Add a band round the Z axis at `z`: its front, back and outer faces, `2 * half` wide."""
    mesh = create_faceted_lathe_along_z(
        name,
        [
            [-half, radius - half],
            [-half, radius + half],
            [half, radius + half],
            [half, radius - half],
        ],
        SMOOTH_PART_SECTION,
        parent.getScene(),
    )
    mesh.position.z = z
    mesh.material = material
    mesh.parent = parent
    return mesh


def _build_intake(side: str, sign: float, root: Any, scene: Any) -> None:
    """Build a reactor intake ahead of the reactor, its mouth facing forward (GFX-SHIP-01).

    A hollow, flared hull-metal scoop with an accent lip, its duct running back to a dark fan face
    ringed in blue metal, a spinner at its centre.
    """
    mats = get_ship_materials(scene)
    name = "balanced-intake-" + side
    node = new_transform_node(name, scene)
    node.position.set(sign * REACTOR_OFFSET_X, INTAKE_Y, INTAKE_Z)
    node.scaling.x = INTAKE_SCALE_X
    node.parent = root
    shell = create_smooth_top_lathe_along_z(name + "-shell", INTAKE, SMOOTH_PART_SECTION, scene)
    shell.material = mats.hull
    shell.parent = node
    lip = INTAKE_LIP
    _band(name + "-lip", lip["z"], lip["radius"], lip["half"], mats.accent, node)
    fan = INTAKE_FAN
    face = create_disc(name + "-fan", disc_options(fan["radius"], SMOOTH_PART_SECTION.upper), scene)
    face.convertToFlatShadedMesh()
    # A disc faces -Z: turned round, it faces the mouth.
    face.rotation.y = math.pi
    face.position.z = fan["z"]
    face.material = mats.canopy
    face.parent = node
    _band(
        name + "-fan-ring",
        fan["z"] + 0.004,
        fan["ringRadius"],
        fan["ringHalf"],
        mats.accent,
        node,
    )
    spinner = create_faceted_lathe_along_z(name + "-spinner", INTAKE_SPINNER, PART_FACETS, scene)
    spinner.material = mats.hullMid
    spinner.parent = node


def _build_wing(side: str, sign: float, root: Any, scene: Any) -> None:
    """Build a forward-swept main wing with its band, flap, canard and wing-tip light.

    Its root lies under the hull's chine, which sweeps into it (the old strake is the chine now).
    """
    mats = get_ship_materials(scene)

    def mirror(outline: list[list[float]]) -> list[list[float]]:
        return outline if sign > 0 else mirror_x(outline)

    wing = new_transform_node("balanced-wing-" + side, scene)
    wing.parent = root
    panel(
        "balanced-wing-" + side + "-panel",
        mirror(BALANCED_WING),
        WING_THICKNESS,
        mats.hullMid,
        wing,
    )
    flap = mirror(WING_FLAP)
    plate("balanced-wing-" + side + "-flap", flap, WING_THICKNESS / 2, mats.hullDark, wing)
    canard = panel("balanced-canard-" + side, mirror(CANARD), 0.04, mats.hullMid, wing)
    canard.position.y = 0.08


def _build_tails(side: str, sign: float, root: Any, scene: Any) -> None:
    """Build the canted twin tail and the ventral fin on one side."""
    mats = get_ship_materials(scene)
    tail = new_transform_node("balanced-tail-" + side, scene)
    tail.position.set(sign * 0.38, 0.12, 0)
    # Stand the panel up (X becomes height), then cant it outwards.
    tail.rotation.z = math.pi / 2 - sign * TAIL_CANT
    tail.parent = root
    panel("balanced-tail-" + side + "-panel", TAIL, 0.05, mats.hullDark, tail)

    # Ventral fin: same trick, pointing down and outwards.
    fin = new_transform_node("balanced-ventral-" + side, scene)
    fin.position.set(sign * 0.3, -0.16, 0)
    fin.rotation.z = -math.pi / 2 + sign * VENTRAL_CANT
    fin.parent = root
    panel("balanced-ventral-" + side + "-panel", VENTRAL_FIN, 0.04, mats.hullDark, fin)


def build_balanced_ship(scene: Any) -> Any:
    """Build the balanced player ship (GFX-SHIP-01)."""
    root = new_transform_node("ship-balanced", scene)
    _build_body(root, scene)
    _build_cockpit(root, scene)
    for side, sign in [("right", 1), ("left", -1)]:
        _build_intake(side, sign, root, scene)
        _build_wing(side, sign, root, scene)
        _build_tails(side, sign, root, scene)
        reactor = build_reactor("balanced-reactor-" + side, REACTOR, scene)
        reactor.position.set(sign * REACTOR_OFFSET_X, REACTOR_Y, -0.95)
        reactor.parent = root
    return root

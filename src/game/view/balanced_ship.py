# Copyright (c) 2026 Renaud Guillon
"""The player ship (GFX-SHIP-01, D-328): a heavy variable fighter carrying a full assault pack.

An original design. A long, flat lifting body with a slim nose and a bubble canopy set forward;
wide cranked wings swept back, a kink halfway out; two big engine nacelles fed by intakes on the
hull's flanks, running out past its tail; canted twin tails and ventral fins; canards; a gun pod
under the belly. The pack on top: two booster engines on the back, an armour plate laid over each
nacelle shoulder, a missile pod on each wing root, its six launch tubes facing forward, and a long
rail cannon on the right shoulder.

Model units: nose towards +Z, about 4.8 units long. The hull is one blended skin
(`balanced_hull.py`); the hull, canopy, intakes, nacelles, boosters and armour have a smooth-shaded
top over a low-poly faceted belly: the triangles go on the upper half, which the playfield camera
sees (GFX-SHIP-05).
"""

import math

from game.view.balanced_hull import (
    TOP_POINTS,
    hull_sections,
    plate_sections,
    station_at,
    top_height,
)
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


# Right main wing (X > 0): a cranked arrow, swept back, the leading edge sweeping less past the
# kink, a square-cut tip.
BALANCED_WING = [
    [0.4, 0.35],
    [1.2, -0.3],
    [2.05, -0.78],
    [2.1, -1.0],
    [1.3, -1.0],
    [0.4, -1.1],
]
WING_THICKNESS = 0.07
# Trailing-edge flap line, on the wing's top.
WING_FLAP = [
    [0.5, -0.95],
    [1.3, -0.88],
    [1.95, -0.88],
    [1.98, -0.99],
    [1.3, -0.99],
    [0.5, -1.08],
]
# Gunmetal panel lines on the wing's top: along the kink's chord, and a strip near the tip.
WING_LINES = [
    [[1.2, -0.3], [1.23, -0.3], [1.33, -0.88], [1.3, -0.88]],
    [[1.75, -0.62], [1.78, -0.6], [1.8, -0.88], [1.77, -0.88]],
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
# The nacelles sit low, inside the hull's shoulders, and run out past its tail, their back third
# and nozzles in the open.
REACTOR_Y = -0.08
REACTOR_Z = -1.15
REACTOR = {"radius": 0.22, "length": 2.0}

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

# The back boosters: a casing (`[z, radius]` in its own frame, nose cone ahead), its place on the
# back either side of the centre line, and the engine at its back, its nozzle out behind the casing.
BOOSTER_CASING = [
    [0.75, 0],
    [0.6, 0.07],
    [0.35, 0.115],
    [-0.5, 0.12],
    [-0.7, 0.11],
    [-0.7, 0],
]
BOOSTER_AT = {"x": 0.18, "y": 0.3, "z": -0.95}
BOOSTER_ENGINE = {"radius": 0.1, "length": 0.5, "z": -0.85}
# The accent band round each casing.
BOOSTER_BAND = {"z": 0.25, "half": 0.03}

# The armour plates over the nacelle shoulders: across, front to back, and their thickness.
ARMOUR_XS = [0.29, 0.57]
ARMOUR_ZS = [0.35, -0.6]
ARMOUR_THICKNESS = 0.035
ARMOUR_POINTS = 9

# A missile pod on each wing root: across, front and back (on the wing's top), its height; the
# six launch tubes in its front face, three across in two rows, their missiles' tips.
MISSILE_POD: dict[str, Any] = {"xs": [0.84, 1.18], "zs": [-0.15, -0.86], "height": 0.15}
MISSILE_TUBES: dict[str, Any] = {
    "xs": [-0.11, 0, 0.11],
    "ys": [0.04, 0.105],
    "radius": 0.032,
    "tip": 0.05,
}

# The rail cannon on the right shoulder: its housing on the armour, the barrel between two rails,
# the muzzle band. Z of each part's middle; the housing's height over the shoulder's top.
CANNON: dict[str, Any] = {
    "x": 0.43,
    "housing": {"length": 0.95, "radius": 0.075, "z": -0.1},
    "lift": 0.11,
    "barrel": {"length": 1.7, "radius": 0.03, "z": 1.2},
    "rail": {"length": 1.5, "width": 0.022, "height": 0.08, "gap": 0.05},
    "muzzle": {"radius": 0.045, "half": 0.03},
}


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
    """Build a cranked, swept-back main wing with its flap, panel lines and canard.

    Its root lies under the hull's chine, which sweeps into it.
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
    for k, line in enumerate(WING_LINES):
        name = "balanced-wing-" + side + "-line-" + str(k)
        plate(name, mirror(line), WING_THICKNESS / 2, mats.hullDark, wing)
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


def _build_booster(side: str, sign: float, root: Any, scene: Any) -> None:
    """Build a booster engine on the back: a steel casing, an accent band, a reactor behind."""
    mats = get_ship_materials(scene)
    name = "balanced-booster-" + side
    node = new_transform_node(name, scene)
    node.position.set(sign * BOOSTER_AT["x"], BOOSTER_AT["y"], BOOSTER_AT["z"])
    node.parent = root
    casing = create_smooth_top_lathe_along_z(
        name + "-casing", BOOSTER_CASING, SMOOTH_PART_SECTION, scene
    )
    casing.material = mats.hullMid
    casing.parent = node
    band = BOOSTER_BAND
    _band(name + "-band", band["z"], BOOSTER_CASING[3][1], band["half"], mats.accent, node)
    engine = BOOSTER_ENGINE
    reactor = build_reactor(name + "-reactor", engine, scene)
    reactor.position.z = engine["z"]
    reactor.parent = node


def _build_armour(side: str, sign: float, root: Any, scene: Any) -> None:
    """Build the gunmetal armour plate laid over a nacelle shoulder, following the hull."""
    mats = get_ship_materials(scene)
    xs = ARMOUR_XS if sign > 0 else [-ARMOUR_XS[1], -ARMOUR_XS[0]]
    sections = plate_sections(xs, ARMOUR_ZS, ARMOUR_THICKNESS, ARMOUR_POINTS)
    armour = create_section_loft("balanced-armour-" + side, sections, ARMOUR_POINTS, scene)
    armour.material = mats.hullDark
    armour.parent = root


def _build_missile_pod(side: str, sign: float, root: Any, scene: Any) -> None:
    """Build a missile pod on a wing root: a silver box, six tubes in front, an accent stripe."""
    mats = get_ship_materials(scene)
    pod = MISSILE_POD
    name = "balanced-missiles-" + side
    node = new_transform_node(name, scene)
    node.position.y = WING_THICKNESS / 2 + pod["height"] / 2
    node.parent = root
    xs = [sign * pod["xs"][0], sign * pod["xs"][1]]
    front = pod["zs"][0]
    back = pod["zs"][1]
    outline = [[xs[0], front], [xs[1], front], [xs[1], back], [xs[0], back]]
    panel(name + "-box", outline, pod["height"], mats.hull, node)
    # The accent stripe along its top.
    middle = (xs[0] + xs[1]) / 2
    stripe = [[middle - 0.03, front - 0.08], [middle + 0.03, front - 0.08]]
    stripe.append([middle + 0.03, back + 0.06])
    stripe.append([middle - 0.03, back + 0.06])
    plate(name + "-stripe", stripe, pod["height"] / 2, mats.accent, node)
    # The dark face the tubes open in, then a missile's tip in each.
    tubes = MISSILE_TUBES
    face = [[xs[0] + sign * 0.015, front], [xs[1] - sign * 0.015, front]]
    face.append([xs[1] - sign * 0.015, front + 0.01])
    face.append([xs[0] + sign * 0.015, front + 0.01])
    panel(name + "-face", face, pod["height"] - 0.03, mats.trim, node)
    tip = [[tubes["tip"], 0], [0, tubes["radius"]], [0, 0]]
    for row, y in enumerate(tubes["ys"]):
        for column, dx in enumerate(tubes["xs"]):
            missile = create_faceted_lathe_along_z(
                name + "-tip-" + str(row) + "-" + str(column), tip, 4, scene
            )
            missile.position.set(middle + dx, y - pod["height"] / 2, front + 0.01)
            missile.material = mats.accent
            missile.parent = node


def _build_cannon(root: Any, scene: Any) -> None:
    """Build the rail cannon on the right shoulder: housing, barrel, twin rails, muzzle band."""
    mats = get_ship_materials(scene)
    cannon = CANNON
    housing = cannon["housing"]
    x = cannon["x"]
    shoulder = top_height(station_at(housing["z"]), x) + ARMOUR_THICKNESS
    node = new_transform_node("balanced-cannon", scene)
    node.position.set(x, shoulder + cannon["lift"], 0)
    node.parent = root
    # The mount, from the armour up to the housing.
    mount = [[-0.04, housing["z"] + 0.3], [0.04, housing["z"] + 0.3]]
    mount.append([0.04, housing["z"] - 0.3])
    mount.append([-0.04, housing["z"] - 0.3])
    mount_mesh = panel("balanced-cannon-mount", mount, cannon["lift"], mats.hullDark, node)
    mount_mesh.position.y = -cannon["lift"] / 2
    faceted_rod(
        "balanced-cannon-housing",
        {"length": housing["length"], "radius": housing["radius"]},
        vector3(0, 0, housing["z"]),
        mats.hullDark,
        node,
        PART_FACETS,
    )
    barrel = cannon["barrel"]
    faceted_rod(
        "balanced-cannon-barrel",
        {"length": barrel["length"], "radius": barrel["radius"]},
        vector3(0, 0, barrel["z"]),
        mats.trim,
        node,
        PART_FACETS,
    )
    rail = cannon["rail"]
    front = barrel["z"] + barrel["length"] / 2
    for k, side in enumerate([-1, 1]):
        inner = side * rail["gap"]
        outer = side * (rail["gap"] + rail["width"])
        outline = [[inner, front - 0.05], [outer, front - 0.05]]
        outline.append([outer, front - 0.05 - rail["length"]])
        outline.append([inner, front - 0.05 - rail["length"]])
        panel("balanced-cannon-rail-" + str(k), outline, rail["height"], mats.accent, node)
    muzzle = cannon["muzzle"]
    _band(
        "balanced-cannon-muzzle",
        front - muzzle["half"],
        muzzle["radius"],
        muzzle["half"],
        mats.hullDark,
        node,
    )


def build_balanced_ship(scene: Any) -> Any:
    """Build the player ship (GFX-SHIP-01)."""
    root = new_transform_node("ship-balanced", scene)
    _build_body(root, scene)
    _build_cockpit(root, scene)
    for side, sign in [("right", 1), ("left", -1)]:
        _build_intake(side, sign, root, scene)
        _build_wing(side, sign, root, scene)
        _build_tails(side, sign, root, scene)
        _build_booster(side, sign, root, scene)
        _build_armour(side, sign, root, scene)
        _build_missile_pod(side, sign, root, scene)
        reactor = build_reactor("balanced-reactor-" + side, REACTOR, scene)
        reactor.position.set(sign * REACTOR_OFFSET_X, REACTOR_Y, REACTOR_Z)
        reactor.parent = root
    _build_cannon(root, scene)
    return root

# Copyright (c) 2026 Renaud Guillon
"""The player ship (GFX-SHIP-01, D-328, D-330): a heavy variable fighter with an assault pack.

An original design. A long, flat lifting body with a slim nose and a bubble canopy set forward;
wide forward-swept wings, a reactor pod on each tip with two small fins at 45°; two big engine
nacelles fed by intakes on the hull's flanks; canted twin tails and ventral fins; canards; a gun
pod under the belly. Every reactor is a rounded hexagon. The pack on top: two booster engines in
humps swelling out of the hull's back (one engine block with the nacelles, all four nozzles out of
its tail face), an armour plate laid over each nacelle shoulder, and a missile pod on each wing
root, its six launch tubes facing forward.

Model units: nose towards +Z, about 4.8 units long. The hull is one blended skin
(`balanced_hull.py`); the hull, canopy, intakes, nacelles and armour have a smooth-shaded
top over a low-poly faceted belly: the triangles go on the upper half, which the playfield camera
sees (GFX-SHIP-05).
"""

import math

from game.view.balanced_hull import (
    TOP_POINTS,
    hull_sections,
    plate_sections,
)
from game.view.ship_materials import get_ship_materials
from game.view.ship_parts import (
    PART_FACETS,
    SMOOTH_PART_SECTION,
    build_reactor,
    disc_options,
    faceted_rod,
    hexagon_band,
    hexagon_body,
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


# Right main wing (X > 0), forward-swept (owner, 2026-11-11, D-330: "make the wings front
# sided"): the tip's leading edge well ahead of the root's, the trailing edge swept forward too, a
# square-cut tip carrying a reactor pod.
BALANCED_WING = [
    [0.4, 0.05],
    [1.8, 0.55],
    [1.9, 0.55],
    [1.9, -0.15],
    [0.4, -1.05],
]
WING_THICKNESS = 0.07


def _leading_edge(x: float) -> float:
    """Return the Z of the right wing's leading edge at `x`, from its root to its tip."""
    root = BALANCED_WING[0]
    tip = BALANCED_WING[1]
    return root[1] + (x - root[0]) * (tip[1] - root[1]) / (tip[0] - root[0])


def _trailing_edge(x: float) -> float:
    """Return the Z of the right wing's trailing edge at `x`, from its root to its tip."""
    root = BALANCED_WING[4]
    tip = BALANCED_WING[3]
    return root[1] + (x - root[0]) * (tip[1] - root[1]) / (tip[0] - root[0])


# The trailing-edge flap: a band `FLAP_DEPTH` deep along the trailing edge, on the wing's top.
FLAP_XS = [0.5, 1.8]
FLAP_DEPTH = 0.13
WING_FLAP = [
    [FLAP_XS[0], _trailing_edge(FLAP_XS[0]) + 0.01],
    [FLAP_XS[1], _trailing_edge(FLAP_XS[1]) + 0.01],
    [FLAP_XS[1], _trailing_edge(FLAP_XS[1]) + FLAP_DEPTH],
    [FLAP_XS[0], _trailing_edge(FLAP_XS[0]) + FLAP_DEPTH],
]
# Gunmetal panel lines on the wing's top, chordwise from the leading edge to the flap.
WING_LINE_XS = [1.35, 1.65]
WING_LINES = [
    [
        [x, _leading_edge(x) - 0.02],
        [x + 0.03, _leading_edge(x + 0.03) - 0.02],
        [x + 0.03, _trailing_edge(x + 0.03) + FLAP_DEPTH],
        [x, _trailing_edge(x) + FLAP_DEPTH],
    ]
    for x in WING_LINE_XS
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
# rad from vertical, outwards: the tips stay inside the hull's edge seen from above (D-330), so
# the trim runs along that edge unbroken.
TAIL_CANT = 0.3
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

# The accent band laid across each of the hull's humps on the back (D-328; their engines, the
# small reactors between the nacelles, were removed, D-331: owner, "remove the central tony
# reactors"), following it.
BOOSTER_BAND: dict[str, Any] = {
    "xs": [0.04, 0.32],
    "zs": [-0.85, -0.97],
    "thickness": 0.012,
    "points": 9,
}

# The armour plates over the nacelle shoulders: across, front to back, and their thickness.
ARMOUR_XS = [0.29, 0.57]
ARMOUR_ZS = [0.35, -0.6]
ARMOUR_THICKNESS = 0.035
ARMOUR_POINTS = 9

# A missile launcher under each wing (owner, 2026-11-11: "rework the missiles pods, make them
# look cool, and under the wings", D-330): a rounded hexagon pod, as the reactors, hung on a pylon,
# its front well ahead of the leading edge so the playfield camera sees its seven missiles' tips
# in their dark launch face; an accent band behind its front, two small fins at 45° under its
# tapered tail. Its axis's place; its profile (`[z, radius]`, from its axis's middle).
MISSILE_POD: dict[str, Any] = {"x": 1.15, "y": -0.2, "z": 0.2}
MISSILE_POD_PROFILE = [
    [0.58, 0],
    [0.58, 0.085],
    [0.53, 0.1],
    [-0.3, 0.1],
    [-0.5, 0.065],
    [-0.58, 0],
]
# The band; the launch face; seven tubes (one in the middle, six round it), their missiles' tips.
MISSILE_BAND: dict[str, Any] = {"z": 0.4, "radius": 0.1, "half": 0.018}
MISSILE_FACE: dict[str, Any] = {"radius": 0.08}
MISSILE_TIPS: dict[str, Any] = {"ring": 0.05, "radius": 0.02, "length": 0.07}
# The pylon up to the wing's underside: its half width across, its front and back (Z from the
# pod's middle).
MISSILE_PYLON: dict[str, Any] = {"half": 0.012, "zs": [0.25, -0.25]}
# The tail fins: span along X from the axis, Z from the pod's middle; canted 45° under it, one
# outwards, one inwards.
MISSILE_FIN = [
    [0, -0.22],
    [0.17, -0.4],
    [0.17, -0.52],
    [0, -0.5],
]

# Twin reactors on each wing tip (owner: "add two reactors on the tip of each wing, with 45° lil
# wings on each", then "make it a dual reactor on the tip of each wing, and add intake to the
# reactors", D-330, and "make the wings reactor on of top the other, not side by side", D-331):
# one over the other, each with an intake, joined by an upright fairing; each carries a small fin
# out from its back half at 45°, the upper one's above the wing's plane, the lower one's below it.
# The reactors' X, their heights (upper, lower), middle along Z and size; the fairing's thickness.
# A fin's planform: span along X from the reactor's axis, Z from its middle.
TIP_REACTOR: dict[str, Any] = {
    "x": 1.98,
    "ys": [0.125, -0.125],
    "z": 0.2,
    "radius": 0.11,
    "length": 0.95,
}
TIP_FAIRING_THICKNESS = 0.05
TIP_FIN = [
    [0, 0.05],
    [0.34, -0.22],
    [0.34, -0.38],
    [0, -0.32],
]
TIP_FIN_CANT = math.pi / 4
TIP_FIN_THICKNESS = 0.03


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


def _build_hump_band(side: str, sign: float, root: Any, scene: Any) -> None:
    """Build the accent band laid across a hump on the hull's back."""
    mats = get_ship_materials(scene)
    band = BOOSTER_BAND
    xs = band["xs"] if sign > 0 else [-band["xs"][1], -band["xs"][0]]
    sections = plate_sections(xs, band["zs"], band["thickness"], band["points"])
    stripe = create_section_loft("balanced-hump-" + side + "-band", sections, band["points"], scene)
    stripe.material = mats.accent
    stripe.parent = root


def _build_armour(side: str, sign: float, root: Any, scene: Any) -> None:
    """Build the gunmetal armour plate laid over a nacelle shoulder, following the hull."""
    mats = get_ship_materials(scene)
    xs = ARMOUR_XS if sign > 0 else [-ARMOUR_XS[1], -ARMOUR_XS[0]]
    sections = plate_sections(xs, ARMOUR_ZS, ARMOUR_THICKNESS, ARMOUR_POINTS)
    armour = create_section_loft("balanced-armour-" + side, sections, ARMOUR_POINTS, scene)
    armour.material = mats.hullDark
    armour.parent = root


def _build_missile_tips(name: str, front: float, material: Any, parent: Any) -> None:
    """Add the seven missiles' tips poking out of a launch face at `front`.

    One in the middle, six round it, between the hexagon's corners.
    """
    tips = MISSILE_TIPS
    profile = [[tips["length"], 0], [0, tips["radius"]], [0, 0]]
    places = [[0.0, 0.0]]
    for k in range(6):
        angle = math.pi / 6 + k * math.pi / 3
        places.append([tips["ring"] * math.cos(angle), tips["ring"] * math.sin(angle)])
    for k, place in enumerate(places):
        tip = create_faceted_lathe_along_z(name + "-tip-" + str(k), profile, 4, parent.getScene())
        tip.position.set(place[0], place[1], front)
        tip.material = material
        tip.parent = parent


def _build_missile_pod(side: str, sign: float, root: Any, scene: Any) -> None:
    """Build the missile launcher under a wing: pod, launch face, missiles, band, pylon, fins."""
    mats = get_ship_materials(scene)
    pod = MISSILE_POD
    name = "balanced-missiles-" + side
    node = new_transform_node(name, scene)
    node.position.set(sign * pod["x"], pod["y"], pod["z"])
    node.parent = root
    hexagon_body(name + "-pod", MISSILE_POD_PROFILE, mats.hullMid, node)
    front = MISSILE_POD_PROFILE[0][0]
    face = create_disc(name + "-face", disc_options(MISSILE_FACE["radius"], 6), scene)
    face.convertToFlatShadedMesh()
    # A disc faces -Z: turned round, it faces forward, a hair ahead of the pod's front.
    face.rotation.y = math.pi
    face.position.z = front + 0.003
    face.material = mats.trim
    face.parent = node
    _build_missile_tips(name, front + 0.003, mats.accent, node)
    band = MISSILE_BAND
    hexagon_band(name + "-band", band["z"], band["radius"], band["half"], mats.accent, node)
    # The pylon: a thin blade from the pod's flat top up to the wing's underside.
    pylon = MISSILE_PYLON
    top = MISSILE_POD_PROFILE[3][1] * math.cos(math.pi / 6)
    height = -WING_THICKNESS / 2 - pod["y"] - top + 0.01
    outline = [[-pylon["half"], pylon["zs"][0]], [pylon["half"], pylon["zs"][0]]]
    outline.append([pylon["half"], pylon["zs"][1]])
    outline.append([-pylon["half"], pylon["zs"][1]])
    blade = panel(name + "-pylon", outline, height, mats.hullDark, node)
    blade.position.y = top + height / 2 - 0.005
    fin = MISSILE_FIN if sign > 0 else mirror_x(MISSILE_FIN)
    for label, turn in [("outer", -math.pi / 4), ("inner", -3 * math.pi / 4)]:
        fin_node = new_transform_node(name + "-fin-" + label, scene)
        fin_node.rotation.z = sign * turn
        fin_node.parent = node
        panel(name + "-fin-" + label + "-panel", fin, 0.025, mats.hullDark, fin_node)


def _build_tip_reactor(side: str, sign: float, root: Any, scene: Any) -> None:
    """Build the twin reactors on a wing tip, one over the other, their fairing and 45° fins."""
    mats = get_ship_materials(scene)
    pod = TIP_REACTOR
    name = "balanced-tip-" + side
    x = sign * pod["x"]
    fin = TIP_FIN if sign > 0 else mirror_x(TIP_FIN)
    for k, (label, up) in enumerate([("upper", 1), ("lower", -1)]):
        y = pod["ys"][k]
        reactor = build_reactor(name + "-reactor-" + label, pod, scene, True)
        reactor.position.set(x, y, pod["z"])
        reactor.parent = root
        node = new_transform_node(name + "-fin-" + label, scene)
        node.position.set(x, y, pod["z"])
        # The fin's span turns from outwards (along X) to 45° above or below the wing's plane.
        node.rotation.z = sign * up * TIP_FIN_CANT
        node.parent = root
        panel(name + "-fin-" + label + "-panel", fin, TIP_FIN_THICKNESS, mats.hullDark, node)
    # The upright fairing between them, along their middle: a blade standing from one to the other.
    half = pod["length"] * 0.3
    width = TIP_FAIRING_THICKNESS / 2
    fairing = [[x - width, pod["z"] + half], [x + width, pod["z"] + half]]
    fairing.append([x + width, pod["z"] - half])
    fairing.append([x - width, pod["z"] - half])
    web = panel(name + "-fairing", fairing, pod["ys"][0] - pod["ys"][1], mats.hullMid, root)
    web.position.y = (pod["ys"][0] + pod["ys"][1]) / 2


def build_balanced_ship(scene: Any) -> Any:
    """Build the player ship (GFX-SHIP-01)."""
    root = new_transform_node("ship-balanced", scene)
    _build_body(root, scene)
    _build_cockpit(root, scene)
    for side, sign in [("right", 1), ("left", -1)]:
        _build_intake(side, sign, root, scene)
        _build_wing(side, sign, root, scene)
        _build_tails(side, sign, root, scene)
        _build_hump_band(side, sign, root, scene)
        _build_armour(side, sign, root, scene)
        _build_missile_pod(side, sign, root, scene)
        _build_tip_reactor(side, sign, root, scene)
        reactor = build_reactor("balanced-reactor-" + side, REACTOR, scene)
        reactor.position.set(sign * REACTOR_OFFSET_X, REACTOR_Y, REACTOR_Z)
        reactor.parent = root
    return root

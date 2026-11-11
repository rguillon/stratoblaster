# Copyright (c) 2026 Renaud Guillon
"""The player ship (GFX-SHIP-01, D-328, D-330, D-332): a heavy variable fighter.

An original design. A long, slim, faceted central body with a needle nose and a bubble canopy set
forward, a spine ridge, dark seams and vents, closing to a point at its tail, with no reactor at its
back; canards; a gun pod under its belly. Two big rounded hexagon reactor nacelles stand out either
side, each with its intake, joined to the body by its strakes (D-336) and carrying a canted tail
and a ventral fin. From each nacelle a
forward-swept wing runs out to twin reactors one over the other on its tip, wrapped in one body,
each with its intake and a fin at 45°. A missile launcher hangs under each wing, its seven
missiles' tips out ahead of the leading edge.

Model units: nose towards +Z, about 5.2 units long. The body is one blended skin
(`balanced_hull.py`), flat-shaded facets; the canopy, nacelles and pods are smooth-shaded on top:
their triangles go on the upper half, which the playfield camera sees (GFX-SHIP-05).
"""

import math

from game.view.balanced_hull import (
    CHINE_EDGE,
    CHINE_HALF_WIDTH,
    hull_section,
    hull_sections,
    station_at,
    top_height,
)
from game.view.ship_materials import get_ship_materials
from game.view.ship_parts import (
    REACTOR_ROUNDING,
    add_reactor_intake,
    build_reactor,
    disc_options,
    edge_strip,
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
from render.geometry.section_loft import (
    create_section_loft,
    polygon_lathe_sections,
    rounded_rectangle,
)

# isort: split
# __pragma__ ("skip")
from typing import Any

Scene = Any
# __pragma__ ("noskip")


# Right main wing (X > 0), forward-swept (owner, 2026-11-11, D-330: "make the wings front
# sided"): the tip's leading edge well ahead of the root's, the trailing edge swept forward too, a
# square-cut tip with a chamfered front corner. Its root lies in the nacelle (D-332), towards its
# back (D-333, owner: "move the wings more to the back"; 0.6 further forward before). Its tip runs
# on past the twin tip reactors (D-339, owner: "make the wings go a little beyond the side
# reactors"; it stopped at 1.9, under them, before).
BALANCED_WING = [
    [0.8, -0.7],
    [2.25, 0.2425],
    [2.3, 0.2],
    [2.3, -0.4],
    [0.8, -1.85],
]
# D-336: the stub wings joining the body to the nacelles (D-332) are now the body's own strakes
# (`balanced_hull.py`). Their glowing leading edge follows the strakes' curve, at these Z.
STRAKE_EDGE_ZS = [0.85, 0.6, 0.35, 0.1, -0.1, -0.3]
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
FLAP_XS = [0.9, 1.8]
FLAP_DEPTH = 0.13
WING_FLAP = [
    [FLAP_XS[0], _trailing_edge(FLAP_XS[0]) + 0.01],
    [FLAP_XS[1], _trailing_edge(FLAP_XS[1]) + 0.01],
    [FLAP_XS[1], _trailing_edge(FLAP_XS[1]) + FLAP_DEPTH],
    [FLAP_XS[0], _trailing_edge(FLAP_XS[0]) + FLAP_DEPTH],
]
# Gunmetal panel lines on the wing's top, chordwise from the leading edge to the flap.
WING_LINE_XS = [1.45, 1.65]
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
# The canards' thickness; they lie with their top face at the body's chine edge, as the wings do
# (D-333, owner: "lower the front wings so their highlight is aligned to the cockpit one"; 0.045
# higher before, their trim above the body's).
CANARD_THICKNESS = 0.04
# The glowing leading edges (D-335): the strip's width across the edge and its thickness, a hair
# thicker than the panel it caps.
EDGE_GLOW = {"width": 0.035, "wing": WING_THICKNESS + 0.006, "canard": CANARD_THICKNESS + 0.006}
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
# The twin tails and ventral fins stand on the nacelles (D-332). The tails' cant, in rad from
# vertical, outwards: their tips stay inside the nacelle's edge seen from above (D-330), so the
# trim runs along that edge unbroken.
TAIL_CANT = 0.2
VENTRAL_CANT = 0.55  # rad from vertical, outwards
# The main reactors: nacelles standing out from the body (D-332: "spead the two main reactors";
# at 0.42, inside the hull's shoulders, before), joined to it by its strakes (D-336), their middle
# at the wings' plane, each with its intake.
REACTOR_OFFSET_X = 0.8
REACTOR_Y = -0.02
REACTOR_Z = -0.95
REACTOR = {"radius": 0.22, "length": 2.0}
# Taller than wide (owner, D-337: "make the main reactors higher"): their height over their width.
REACTOR_HEIGHT = 1.3
# The main reactors and the tip intakes are octagons, flat on top, bottom and sides (D-339, owner:
# "make the main reactor octogonal too"); the tip reactors and missile pods stay hexagons.
OCTAGON = 8

# The gun under the belly (D-339, owner: "rework the undergun, make a cool looking laser and add
# two miniguns on it's sides"). The laser: its place; its octagonal housing's profile (`[z from
# its place, radius]`); its barrel, the focusing coils round it (Z from its place) and the glowing
# emitter at its muzzle (a lathe profile).
LASER: dict[str, Any] = {
    "y": -0.255,
    "z": 0.3,
    "barrel": {"length": 0.75, "radius": 0.036, "z": 0.85},
    "coil": {"zs": [0.62, 0.78, 0.94], "radius": 0.052, "half": 0.014},
}
LASER_HOUSING = [
    [0.55, 0],
    [0.55, 0.07],
    [0.42, 0.1],
    [-0.45, 0.1],
    [-0.6, 0.055],
    [-0.65, 0],
]
LASER_EMITTER = [[1.29, 0], [1.25, 0.038], [1.2, 0.052], [1.19, 0]]
# The miniguns either side of it: their place; the drum; six barrels round its axis, their ring's
# radius and their middle along Z; the clamp round the barrels.
MINIGUN: dict[str, Any] = {
    "x": 0.17,
    "y": -0.215,
    "z": 0.35,
    "drum": {"length": 0.36, "radius": 0.052},
    "barrels": {"count": 6, "ring": 0.028, "radius": 0.01, "length": 0.42, "z": 0.36},
    "clamp": {"z": 0.45, "radius": 0.045, "half": 0.009},
}

# Dark panel seams round the body (D-336): their Z, their half width along Z and how much larger
# than the body's section they are.
SEAM_ZS = [1.7, 0.55, -0.75, -1.75]
SEAM: dict[str, Any] = {"half": 0.012, "grow": 1.02}
# Dark vents on the strakes, in front of and behind the wing roots (right side; mirrored left).
VENTS = [
    [
        [0.34, -0.15 - 0.12 * k],
        [0.5, -0.15 - 0.12 * k],
        [0.5, -0.21 - 0.12 * k],
        [0.34, -0.21 - 0.12 * k],
    ]
    for k in range(3)
]

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
# The canopy's smooth top: finer than the other parts, it is the shiniest thing on the ship.
CANOPY_SECTION = LatheHalves(16, 3)
CANOPY_FRAME_SECTION = LatheHalves(8, 2)
# Middle of the canopy along Z, for scaling the frame around it.
CANOPY_MID_Z = 1.08

# A missile launcher under each wing (owner, 2026-11-11: "rework the missiles pods, make them
# look cool, and under the wings", D-330): a rounded hexagon pod, as the reactors, hung on a pylon,
# its front well ahead of the leading edge so the playfield camera sees its seven missiles' tips
# in their dark launch face; an accent band behind its front, two small fins at 45° under its
# tapered tail. Its axis's place; its profile (`[z, radius]`, from its axis's middle).
MISSILE_POD: dict[str, Any] = {"x": 1.3, "y": -0.2, "z": -0.4}
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
MISSILE_PYLON: dict[str, Any] = {"half": 0.012, "zs": [0.0, -0.4]}
# The tail fins: span along X from the axis, Z from the pod's middle; canted 45° under it, one
# outwards, one inwards.
MISSILE_FIN = [
    [0, -0.22],
    [0.17, -0.4],
    [0.17, -0.52],
    [0, -0.5],
]

# Twin reactors on each wing tip (owner: "add two reactors on the tip of each wing, with 45° lil
# wings on each", "make it a dual reactor on the tip of each wing, and add intake to the
# reactors", D-330, "make the wings reactor on of top the other, not side by side", D-331): one over
# the other, each with an intake and a small fin out from its back half at 45°, the upper one's
# above the wing's plane, the lower one's below it. D-332 ("add more body to the wings reactors,
# connecting them"): one steel body wraps both, a tall rounded rectangle in section, their intakes
# and nozzles out at its ends. The reactors' X, their heights (upper, lower), middle along Z and
# size; the body's section and its profile (`[z from the reactors' middle, scale of the section]`).
# D-339 (owner: "merge the two lateral intales into a single octogonal intake"): the body runs on
# to the reactors' fronts, where one octagonal intake, stretched upright to the body's height,
# feeds both: its radius and its stretch.
TIP_REACTOR: dict[str, Any] = {
    "x": 1.98,
    "ys": [0.125, -0.125],
    "z": -0.4,
    "radius": 0.11,
    "length": 0.95,
}
TIP_BODY: dict[str, Any] = {"halfWidth": 0.125, "halfHeight": 0.255, "corner": 0.1, "steps": 3}
TIP_INTAKE: dict[str, Any] = {"radius": 0.124, "stretch": 2.05}
TIP_BODY_PROFILE = [
    [0.475, 0],
    [0.475, 0.9],
    [0.3, 1.0],
    [-0.28, 1.0],
    [-0.38, 0.82],
    [-0.42, 0],
]
TIP_FIN = [
    [0, 0.05],
    [0.34, -0.22],
    [0.34, -0.38],
    [0, -0.32],
]
TIP_FIN_CANT = math.pi / 4
TIP_FIN_THICKNESS = 0.03


def _build_body(root: Any, scene: Any) -> None:
    """Build the slim central body, its seams and vents, and the guns under it."""
    mats = get_ship_materials(scene)
    body_root = new_transform_node("balanced-body-root", scene)
    body_root.parent = root
    # One faceted skin (D-336): every face flat-shaded, so the facets' edges read crisp.
    body = create_section_loft("balanced-body", hull_sections(), 0, scene)
    body.material = mats.hull
    body.parent = body_root
    for k, z in enumerate(SEAM_ZS):
        _build_seam("balanced-seam-" + str(k), z, mats.hullDark, body_root, scene)
    for side, sign in [("right", 1), ("left", -1)]:
        for k, vent in enumerate(VENTS):
            outline = vent if sign > 0 else mirror_x(vent)
            middle = _centre(vent)
            y = top_height(station_at(middle[1]), middle[0])
            name = "balanced-vent-" + side + "-" + str(k)
            plate(name, outline, y, mats.hullDark, body_root)

    _build_laser(root, scene)
    for side, sign in [("right", 1), ("left", -1)]:
        _build_minigun(side, sign, root, scene)


def _build_laser(root: Any, scene: Any) -> None:
    """Build the laser cannon under the belly (D-339).

    A gunmetal octagonal housing, a long barrel ringed by accent focusing coils and a glowing
    emitter at its muzzle.
    """
    mats = get_ship_materials(scene)
    laser = LASER
    node = new_transform_node("balanced-laser", scene)
    node.position.set(0, laser["y"], laser["z"])
    node.parent = root
    sections = polygon_lathe_sections(
        LASER_HOUSING, OCTAGON, REACTOR_ROUNDING, 2, math.pi / OCTAGON
    )
    housing = create_section_loft("balanced-laser-housing", sections, 0, scene)
    housing.material = mats.hullDark
    housing.parent = node
    barrel = laser["barrel"]
    faceted_rod(
        "balanced-laser-barrel",
        {"length": barrel["length"], "radius": barrel["radius"]},
        vector3(0, 0, barrel["z"]),
        mats.trim,
        node,
        OCTAGON,
    )
    coil = laser["coil"]
    for k, z in enumerate(coil["zs"]):
        hexagon_band(
            "balanced-laser-coil-" + str(k),
            z,
            coil["radius"],
            coil["half"],
            mats.accent,
            node,
            OCTAGON,
        )
    emitter = create_faceted_lathe_along_z("balanced-laser-emitter", LASER_EMITTER, OCTAGON, scene)
    emitter.material = mats.reactorCore
    emitter.parent = node


def _build_minigun(side: str, sign: float, root: Any, scene: Any) -> None:
    """Build a minigun beside the laser (D-339): a drum, six barrels round its axis, a clamp."""
    mats = get_ship_materials(scene)
    gun = MINIGUN
    name = "balanced-minigun-" + side
    node = new_transform_node(name, scene)
    node.position.set(sign * gun["x"], gun["y"], gun["z"])
    node.parent = root
    drum = gun["drum"]
    faceted_rod(
        name + "-drum",
        {"length": drum["length"], "radius": drum["radius"]},
        vector3(0, 0, 0),
        mats.hullMid,
        node,
        OCTAGON,
    )
    barrels = gun["barrels"]
    for k in range(barrels["count"]):
        angle = 2 * math.pi * k / barrels["count"]
        faceted_rod(
            name + "-barrel-" + str(k),
            {"length": barrels["length"], "radius": barrels["radius"]},
            vector3(
                barrels["ring"] * math.cos(angle),
                barrels["ring"] * math.sin(angle),
                barrels["z"],
            ),
            mats.trim,
            node,
            4,
        )
    clamp = gun["clamp"]
    hexagon_band(name + "-clamp", clamp["z"], clamp["radius"], clamp["half"], mats.hullDark, node)


def _build_seam(name: str, z: float, material: Any, parent: Any, scene: Any) -> None:
    """Build a dark panel seam round the body at `z`: a thin band of its section, a bit larger."""
    sections = []
    for dz in [SEAM["half"], -SEAM["half"]]:
        _z, ring = hull_section(station_at(z + dz))
        grown = [[p[0] * SEAM["grow"], p[1] * SEAM["grow"]] for p in ring]
        sections.append([z + dz, grown])
    seam = create_section_loft(name, sections, 0, scene)
    seam.material = material
    seam.parent = parent


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
    # The frame's rim glows round the canopy (D-335: the cockpit glows, as the wings' edges do).
    frame.material = mats.edgeGlow
    frame.parent = root

    canopy = create_smooth_top_lathe_along_z(
        "balanced-canopy", smooth_profile(CANOPY, PROFILE_STEPS), CANOPY_SECTION, scene
    )
    canopy.position.y = 0.17
    canopy.material = mats.canopy
    canopy.parent = root


def _build_wing(side: str, sign: float, root: Any, scene: Any) -> None:
    """Build a forward-swept main wing, its flap and panel lines, and the canard.

    The main wing runs out of the nacelle; the body's strakes join the nacelle to the body (D-336).
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
    canard = panel("balanced-canard-" + side, mirror(CANARD), CANARD_THICKNESS, mats.hullMid, wing)
    # Its top face at the body's chine edge, so its trim runs on from the body's (D-333).
    canard.position.y = CHINE_EDGE - CANARD_THICKNESS / 2


def _centre(outline: list[list[float]]) -> list[float]:
    """Return the middle of a planform outline's points."""
    return [
        sum(p[0] for p in outline) / len(outline),
        sum(p[1] for p in outline) / len(outline),
    ]


def _build_edge_glow(side: str, sign: float, root: Any, scene: Any) -> None:
    """Build the glowing leading edges of a side's wing, strake and canard (D-335, D-336).

    The extremities glow in place of a trim round the ship: the main wing's leading edge from
    root to tip, the body's strake's, and the canard's leading edge and tip. The guns get none.
    """
    mats = get_ship_materials(scene)

    def mirror(points: list[list[float]]) -> list[list[float]]:
        return points if sign > 0 else mirror_x(points)

    wing_size = {"width": EDGE_GLOW["width"], "thickness": EDGE_GLOW["wing"]}
    canard_size = {"width": EDGE_GLOW["width"], "thickness": EDGE_GLOW["canard"]}
    name = "balanced-glow-" + side
    # The main wing's, either side of the tip reactors' body, which it runs through (D-339).
    wing = mirror(BALANCED_WING)
    gap = [TIP_REACTOR["x"] - TIP_BODY["halfWidth"], TIP_REACTOR["x"] + TIP_BODY["halfWidth"]]
    inner = mirror([[gap[0], _leading_edge(gap[0])]])[0]
    outer = mirror([[gap[1], _leading_edge(gap[1])]])[0]
    centre = _centre(wing)
    edge_strip(name + "-wing", [wing[0], inner], centre, wing_size, mats.edgeGlow, root)
    edge_strip(name + "-wing-tip", [outer, wing[1]], centre, wing_size, mats.edgeGlow, root)
    # The strake's leading edge, one strip between each two of its points (D-336).
    strake = mirror([[station_at(z)[CHINE_HALF_WIDTH], z] for z in STRAKE_EDGE_ZS])
    for k in range(len(strake) - 1):
        edge = [strake[k], strake[k + 1]]
        edge_strip(name + "-strake-" + str(k), edge, [0, -0.6], wing_size, mats.edgeGlow, root)
    canard = mirror(CANARD)
    for k in range(2):
        strip = edge_strip(
            name + "-canard-" + str(k),
            [canard[k], canard[k + 1]],
            _centre(canard),
            canard_size,
            mats.edgeGlow,
            root,
        )
        strip.position.y = CHINE_EDGE - CANARD_THICKNESS / 2


def _build_tails(side: str, sign: float, root: Any, scene: Any) -> None:
    """Build the canted tail on a nacelle's top and the ventral fin under it."""
    mats = get_ship_materials(scene)
    radius = REACTOR["radius"]
    top = REACTOR_Y + radius * math.cos(math.pi / OCTAGON) * REACTOR_HEIGHT
    tail = new_transform_node("balanced-tail-" + side, scene)
    tail.position.set(sign * REACTOR_OFFSET_X, top - 0.02, 0)
    # Stand the panel up (X becomes height), then cant it outwards.
    tail.rotation.z = math.pi / 2 - sign * TAIL_CANT
    tail.parent = root
    panel("balanced-tail-" + side + "-panel", TAIL, 0.05, mats.hullDark, tail)

    # Ventral fin: same trick, pointing down and outwards.
    fin = new_transform_node("balanced-ventral-" + side, scene)
    fin.position.set(sign * REACTOR_OFFSET_X, REACTOR_Y - radius * 0.8 * REACTOR_HEIGHT, 0)
    fin.rotation.z = -math.pi / 2 + sign * VENTRAL_CANT
    fin.parent = root
    panel("balanced-ventral-" + side + "-panel", VENTRAL_FIN, 0.04, mats.hullDark, fin)


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
    """Build the twin reactors on a wing tip, one over the other, the body round them, the fins."""
    mats = get_ship_materials(scene)
    pod = TIP_REACTOR
    name = "balanced-tip-" + side
    x = sign * pod["x"]
    fin = TIP_FIN if sign > 0 else mirror_x(TIP_FIN)
    for k, (label, up) in enumerate([("upper", 1), ("lower", -1)]):
        y = pod["ys"][k]
        reactor = build_reactor(name + "-reactor-" + label, pod, scene)
        reactor.position.set(x, y, pod["z"])
        reactor.parent = root
        node = new_transform_node(name + "-fin-" + label, scene)
        node.position.set(x, y, pod["z"])
        # The fin's span turns from outwards (along X) to 45° above or below the wing's plane.
        node.rotation.z = sign * up * TIP_FIN_CANT
        node.parent = root
        panel(name + "-fin-" + label + "-panel", fin, TIP_FIN_THICKNESS, mats.hullDark, node)
    # One body wrapping both: a tall rounded rectangle in section, scaled along the profile.
    body = TIP_BODY
    ring = rounded_rectangle(body["halfWidth"], body["halfHeight"], body["corner"], body["steps"])
    middle = (pod["ys"][0] + pod["ys"][1]) / 2
    sections = [
        [pod["z"] + p[0], [[x + p[1] * q[0], middle + p[1] * q[1]] for q in ring]]
        for p in TIP_BODY_PROFILE
    ]
    shell = create_section_loft(name + "-body", sections, len(ring), scene)
    shell.material = mats.hullMid
    shell.parent = root
    # One octagonal intake for both reactors, at the body's front.
    intake = new_transform_node(name + "-intake-root", scene)
    intake.position.set(x, middle, pod["z"] + pod["length"] / 2)
    intake.scaling.y = TIP_INTAKE["stretch"]
    intake.parent = root
    add_reactor_intake(name, TIP_INTAKE["radius"], 0, intake, OCTAGON)


def build_balanced_ship(scene: Any) -> Any:
    """Build the player ship (GFX-SHIP-01)."""
    root = new_transform_node("ship-balanced", scene)
    _build_body(root, scene)
    _build_cockpit(root, scene)
    for side, sign in [("right", 1), ("left", -1)]:
        _build_wing(side, sign, root, scene)
        _build_tails(side, sign, root, scene)
        _build_edge_glow(side, sign, root, scene)
        _build_missile_pod(side, sign, root, scene)
        _build_tip_reactor(side, sign, root, scene)
        reactor = build_reactor("balanced-reactor-" + side, REACTOR, scene, True, OCTAGON)
        reactor.position.set(sign * REACTOR_OFFSET_X, REACTOR_Y, REACTOR_Z)
        reactor.scaling.y = REACTOR_HEIGHT
        reactor.parent = root
    return root

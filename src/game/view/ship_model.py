# Copyright (c) 2026 Renaud Guillon
"""The player ship (GFX-SHIP-01, D-328, D-330, D-332): a heavy variable fighter.

An original design. A long, slim, faceted central body with a needle nose and a bubble canopy set
forward, a spine ridge, dark seams and vents, closing to a point at its tail, with no reactor at its
back; a gun pod under its belly. Two big rounded hexagon reactor nacelles stand out either
side, each with its intake, joined to the body by its strakes (D-336). From each nacelle a
forward-swept wing runs out to twin reactors one over the other on its tip, wrapped in one body
with one intake, a canted tail on its top and a ventral fin under it (D-353). A missile launcher
hangs under each wing, its seven missiles' tips out ahead of the leading edge.

Model units: nose towards +Z, about 5.2 units long. The body is one blended skin
(`ship_hull.py`), flat-shaded facets; the canopy, nacelles and pods are smooth-shaded on top:
their triangles go on the upper half, which the playfield camera sees (GFX-SHIP-05).
"""

import math

from game.config.readability import READABILITY
from game.config.ship_look import PLAYER_SHIP_SCALE
from game.view.ship_cockpit import (
    ARCH_POINTS,
    BOW,
    HELMET,
    HOOD,
    HOOD_ZS,
    SEAT,
    SEAT_ZS,
    bow_segments,
    canopy_sections,
    floor_height,
    floor_sections,
    rail_sections,
)
from game.view.ship_hull import (
    BELLY_DEPTH,
    BODY_HALF_WIDTH,
    CHINE_EDGE,
    CHINE_ROOT,
    STATIONS,
    hull_section,
    hull_sections,
    station_at,
    top_height,
    underside_height,
)
from game.view.ship_materials import get_ship_materials
from game.view.ship_parts import (
    INTAKE_FIN_SIZE,
    NACELLE_TAPER,
    PART_FACETS,
    REACTOR_CORNER_STEPS,
    REACTOR_INTAKE,
    REACTOR_INTAKE_DUCT,
    REACTOR_INTAKE_FINS,
    REACTOR_ROUNDING,
    REACTOR_SIDES,
    add_reactor_intake,
    build_reactor,
    disc_options,
    edge_strip,
    faceted_rod,
    intake_fin_heights,
    intake_fin_thickness,
    mirror_x,
    panel,
    plate,
    polygon_turn,
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
)
from render.geometry.section_loft import (
    create_section_loft,
    rounded_polygon,
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
# back (D-333, owner: "move the wings more to the back"; 0.6 further forward before). D-360 (owner:
# "make the wings stop at the junction with the outer reactors"): its tip stops at 1.78, in the
# tip fairing against the tilting pod's flank, its edges' sweep kept (it ran on past the pods to
# 2.3, D-339). D-371 (owner: "remove the ability to rotate for the secondary reactors and joint
# geometry"): with no fairing, its tip runs on along its edges' sweep to 1.87, a little into the
# fixed pod's flank (1.855).
# D-383 (owner: "move the junction between the front of the wings and the main body to the front,
# the wings will be wider at the main hull level"): its root's leading edge at z -0.3 (-0.7), its
# tip where it was, so its chord is longer where it meets the body.
MAIN_WING = [
    [0.8, -0.3],
    [1.85, -0.0175],
    [1.87, -0.0375],
    [1.87, -0.816],
    [0.8, -1.85],
]
# D-336: the stub wings joining the body to the nacelles (D-332) are now the body's own strakes
# (`ship_hull.py`); their leading edge glowed until D-370.
# D-356 (owner: "the central wing shall be oriented the other way (the entier wings will form a
# W)"): behind the body's square back the strakes run on into the nacelles, their trailing edge
# swept forward from the nacelle to the body's back corner, the way the main wings' runs from their
# tip, so the trailing edges across the ship read as a W (they ran back to the body's point
# before). Right side, mirrored left; as thick as the strake, its top at the wings' top face.
STRAKE_TAIL = [
    [0.24, -1.45],
    [0.7, -1.45],
    [0.7, -1.86],
    [0.6, -1.88],
]
# A dark plate on the body's square back: shares of the back's section, its front and back Z.
TAIL_PLATE = {"front": 0.8, "back": 0.66, "frontZ": -1.44, "backZ": -1.48}
WING_THICKNESS = 0.07


def _leading_edge(x: float) -> float:
    """Return the Z of the right wing's leading edge at `x`, from its root to its tip."""
    root = MAIN_WING[0]
    tip = MAIN_WING[1]
    return root[1] + (x - root[0]) * (tip[1] - root[1]) / (tip[0] - root[0])


def _trailing_edge(x: float) -> float:
    """Return the Z of the right wing's trailing edge at `x`, from its root to its tip."""
    root = MAIN_WING[4]
    tip = MAIN_WING[3]
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
# The glowing leading edges (D-335): the strip's width across the edge and its thickness, a hair
# thicker than the panel it caps. D-363 (owner: "remove the little front wings"): no canards.
# D-370 (owner: "remove the glow in the main body and wings, only keep the ones on the vertical
# wings"): only the tails and ventral fins glow; the main wings', strakes' and canopy rails' are
# gone. The width stays the canopy rails' scale.
EDGE_GLOW = {"width": 0.035, "wing": WING_THICKNESS + 0.006}
TAIL = [
    [0, -0.75],
    [0.85, -1.35],
    [0.85, -1.6],
    [0, -1.55],
]
# The twin tails and ventral fins stood on the main nacelles (D-332); they stand on the wing-tip
# pods now, in place of the pods' 45° fins (owner, D-353: "move the vertical wings from the big
# reactors to the small side reactors, they replace the side reactors original vertical wings"):
# the tail on the pod's top, the ventral fin under it, both brought forward by `TIP_TAIL_SHIFT`
# so their roots run along the pod. Their outlines stay as drawn (Z along the ship). The tails'
# cant, in rad from vertical, outwards. D-360 (owner: "make the lower vertical wing on the reactor
# the same as the upper ones"): the ventral fin is the tail's mirror image under the pod, its
# outline, thickness and cant (smaller, canted 0.55, before).
TIP_TAIL_SHIFT = 0.65
# D-361 (owner: "angle the vertical wings 40°"): 0.2 rad (11°) before.
TAIL_CANT = 0.698
TAIL_THICKNESS = 0.05
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
# A secondary intake on the top and the bottom of each main reactor (D-347, owner: "add secondary
# intake at the top and botton of each of the main reactors, with a slope eaching the back of the
# reactor"): a silver scoop on the nacelle's flat face, its matte black mouth facing forward, its
# back a ramp sloping down to the nacelle's back. In the nacelle's own units (before its upright
# stretch, Z from its middle): its front and back, its width at its base, its height at its mouth,
# how far its base sinks into the nacelle; the mouth's share of its width and height.
# D-348 (owner: "rework the secondary intakes, smoth them a little and add fins like the others"):
# a rounded arch, smooth-shaded (`corner`), the ramp easing down over `rampSteps` sections after a
# short straight `lip`; flat fins across the mouth at these shares of its height from its middle.
# D-367 (owner: "rework the upper side of the secondary intake, make a better looking junction
# with the main reactor"): its top a gentle arch (`crown`, a share of its half width), rounded
# shoulders, and concave fillets `flare` wide running it into the nacelle's flat top and chamfers
# (a straight-walled box sunk in them before), its base following the nacelle's taper; the ramp
# eases down over 4 sections as before. In front of the nacelle, over the main intake, the
# fillets fade out over `flareRun`. The fillets', shoulders' and crown's points per side.
# D-366 (owner: "make the auxiliary intakes on the main reactor more to the front, they shall go
# beyong the main intakes"; then "more the auxiliary intakes more to the front"): their front at
# 1.3, well out past the nacelle's front (1.0) and the main intake's lip (1.1), overhanging it
# (0.5, halfway along the nacelle, before).
# D-368 (owner: "remove the under secondary intakes on the main reactors"): on the top only.
# D-369 (owner: "rework the secondary intakes, it looks too flat, make it similar to the other
# intakes"; a short collar round a flat black face, the fins at its rim, before): its mouth is
# built as the main intakes are, on its own arch: the skin runs on straight from the scoop's
# front, angles in to a thin lip and turns back into a matte black duct, the fins across the
# duct, their ends in the lip's wall. The main intake's profiles (`REACTOR_INTAKE*`, in radii)
# scale the scoop's front section round its middle, in units of its half width (`radius`).
REACTOR_SCOOP: dict[str, Any] = {
    "front": 1.3,
    "back": -0.7,
    "width": 0.21,
    # D-398 (owner: "make those intakes a little higher"): 0.16 (0.13); the chamfer under it; full
    # height back to the nacelle's middle (`lip` 1.3 from its front, 0.06 before), the ramp down
    # to -0.7 (to its back, -1.0, before).
    "height": 0.16,
    "chamfer": 0.025,
    "sink": 0.02,
    "corner": 0.035,
    "lip": 1.3,
    "rampSteps": 4,
    "crown": 0.12,
    "flare": 0.035,
    "flareRun": 0.06,
    "filletSteps": 1,
    "cornerSteps": 2,
    "crownSteps": 1,
}

# The guns under the belly (D-339, owner: "rework the undergun, make a cool looking laser and add
# two miniguns on it's sides"; D-340: "make the lazer longer, it should go further than the tip of
# the ship, and rework those weapons, make them better integrated into the hull"). A faceted keel
# fairing of hull metal runs along the belly, its top inside the belly so the two read as one;
# `[z, half width, depth under the belly]`, back to front, closed at both ends.
# D-399 (owner: "rework completly the part connecting the miniguns and the laser to the hull, make
# something cool and aerodynamic"; a wide faceted box, the miniguns' drums half sunk in its
# flanks, before): a slim streamlined keel, smooth-shaded, an oval below the belly in section, its
# top buried in the hull; it swells behind the cockpit and narrows to a point under the laser's
# bridge, the laser out of its nose. `[z, half width, depth under the belly]`, back to front,
# closed at both ends; the points of its rounded underside.
GUN_FAIRING = [
    [-0.85, 0.0, 0.0],
    [-0.6, 0.08, 0.05],
    [-0.2, 0.14, 0.09],
    [0.4, 0.16, 0.11],
    [1.3, 0.15, 0.1],
    [2.1, 0.1, 0.1],
    [2.6, 0.08, 0.13],
    [2.85, 0.0, 0.0],
]
GUN_FAIRING_POINTS = 9
# Each minigun hangs on a swept pylon out of the keel's flank (D-399): a thin wing of an airfoil
# section, its root inside the keel, its tip inside the drum. Its root's and tip's X; their
# leading and trailing edges' Z; their thickness; the airfoil, `[share of the chord from the
# leading edge, share of the thickness over (under) the chord]`, leading edge to trailing edge.
MINIGUN_PYLON: dict[str, Any] = {
    "xs": [0.1, 0.36],
    "leading": [1.2, 1.05],
    "trailing": [0.1, 0.45],
    "thickness": [0.05, 0.036],
    "airfoil": [[0.0, 0.0], [0.25, 0.5], [0.6, 0.35], [1.0, 0.0]],
}
# The laser (D-342, owner: "review the laze design, the rings sucks"; a barrel ringed by accent
# coils before): out of the fairing's nose and past the ship's tip (3.3, D-354: everything 0.55
# further forward with the longer nose), two gunmetal rails
# taper forward into prongs either side of a glowing core rod, joined at their back by a bridge;
# a glowing emitter at the core's tip, between the prongs. Its height; the core (Z back and front,
# radius); the right rail's planform (mirrored left) and thickness; the bridge's planform; the
# emitter (a lathe profile, Z absolute).
# D-400 (owner: "move the laser down make it bigger and improve the design of the sides"): at y
# -0.19 (-0.12), half as big again, its rails shaped blades, lofted along it (flat plates before):
# each section a pentagon, its flat inner face towards the core, its outer edge sharp, bevelled
# above and below, tapering into a slim prong ahead of the emitter. A rail section: `[z, inner X,
# outer X, half height]`, back to front (the right rail; mirrored left), and how much of its
# width the bevels take.
LASER: dict[str, Any] = {
    "y": -0.19,
    "core": {"zs": [2.65, 3.61], "radius": 0.018},
    "railThickness": 0.05,
    "bevel": 0.4,
}
# D-401 (owner: "make the side parts of the laser bigger and more complex looking"): larger blades,
# a ridge along their top and bottom (a seven-sided section: the sharp outer edge, a bevel, the
# ridge, the inner face), and accent clamps round their backs, at `clamps` Z, `half` deep, a
# little proud of the blade.
# D-405 (owner: "the sides of the laser are too pointy"): full-bodied nearly to their front, a
# short chamfer into a flat front face (they tapered into slim prongs before).
LASER_RAIL_SECTIONS = [
    [2.45, 0.035, 0.1, 0.06],
    [2.75, 0.035, 0.115, 0.068],
    [3.2, 0.035, 0.11, 0.062],
    [3.55, 0.037, 0.1, 0.055],
    [3.72, 0.04, 0.09, 0.045],
    [3.78, 0.045, 0.08, 0.032],
]
LASER_CLAMPS: dict[str, Any] = {"zs": [2.58, 2.7, 2.82], "half": 0.012, "proud": 0.008}
LASER_BRIDGE = [[-0.115, 2.45], [0.115, 2.45], [0.115, 2.75], [-0.115, 2.75]]
LASER_EMITTER = [[3.71, 0], [3.665, 0.033], [3.61, 0.045], [3.6, 0]]
# The miniguns, one in each flank of the fairing: their drums half sunk in it as blisters, their
# six barrels out ahead of it. Place; drum; barrels (ring radius, radius, length, middle along Z
# from the drum's); the clamp round the barrels. D-341 (owner: "increase ther size of the
# miniguns, and make their cannons thicker"): larger drums, thicker six-sided barrels. D-345
# ("increase the minigun size again, and add hole into the barrels"): larger again, each barrel
# hollow at its muzzle, a bore of `bore.radius` of the barrel's, `bore.depth` deep. D-346 ("spread
# the minguns a little more"): 0.21 out from the centre line (0.17 before). D-349 ("and spread the
# minigun more again"): 0.27, the fairing widened under the body's flanks to keep them half in it.
# D-365 ("spread the minigun"): 0.39 (0.33, D-358), the fairing 0.06 wider again.
MINIGUN: dict[str, Any] = {
    "x": 0.39,
    "y": -0.195,
    "z": 0.75,
    "drum": {"length": 0.9, "radius": 0.085},
    # D-389 (owner: "rework the minigun body, make it look cool, better than a single tube"): the
    # drum's profile, `[z, radius]` back to front: a small rear cap and a chamfer (the motor's
    # housing), two raised cooling ribs, a long run, then a flared collar the barrels come out of;
    # its steps flat-shaded, its sides smooth (D-388).
    "drumProfile": [
        [-0.45, 0.0],
        [-0.45, 0.045],
        [-0.4, 0.07],
        [-0.32, 0.07],
        [-0.32, 0.092],
        [-0.28, 0.092],
        [-0.28, 0.08],
        [-0.2, 0.08],
        [-0.2, 0.092],
        [-0.16, 0.092],
        [-0.16, 0.085],
        [0.32, 0.085],
        [0.38, 0.098],
        [0.45, 0.098],
        [0.45, 0.0],
    ],
    "barrels": {
        "count": 6,
        "ring": 0.048,
        "radius": 0.021,
        "length": 0.5,
        "z": 0.65,
        "turn": math.pi / 6,
    },
    "bore": {"radius": 0.55, "depth": 0.06},
    # D-389 (owner: "move the small ring of the minigun to the back"): just ahead of the drum's
    # collar (0.68 before).
    "clamp": {"z": 0.5, "radius": 0.078, "half": 0.014},
    # D-386: a second, thicker clamp near the muzzles, their last 0.046 bare. D-387 (owner: "make
    # it 3 times thicker"): 0.144 deep (0.048), its front where it was, so it grows backwards.
    "muzzleClamp": {"z": 0.782, "radius": 0.08, "half": 0.072},
}

# Dark panel seams round the body (D-336): their Z, their half width along Z and how much larger
# than the body's section they are.
# D-354: the radome's joint, behind the blunt nose.
SEAM_ZS = [2.75, 1.85, 0.4, -0.75]
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

# The cockpit is `ship_cockpit.py`'s (D-354: a fighter's canopy on the deck; a teardrop bubble
# with a glowing frame under it before). The pilot's helmet and its visor, lathe profiles in units
# of the helmet's radius (`[z, radius]`, nose to tail).
HELMET_PROFILE = [[1.0, 0.0], [0.7, 0.71], [0.0, 1.0], [-0.7, 0.71], [-1.0, 0.0]]
VISOR_PROFILE = [[1.08, 0.0], [0.62, 0.86], [0.2, 1.06]]

# A missile launcher under each wing (owner, 2026-11-11: "rework the missiles pods, make them
# look cool, and under the wings", D-330): a rounded hexagon pod, as the reactors, hung on a pylon,
# its front well ahead of the leading edge so the playfield camera sees its seven missiles' tips
# in their dark launch face; an accent band behind its front, two small fins at 45° under its
# tapered tail. Its axis's place; its profile (`[z, radius]`, from its axis's middle). D-343
# (owner: "make the missile pods hexagonal, higher and make them go trough the wings"; D-344:
# "make the missile pods octogonal"): a crisp octagon, flat on top, bottom and sides, flat-shaded
# with barely rounded corners, stretched upright (`stretch`), its axis in the wing's plane so the
# wing runs through it; no pylon (it hung under the wing on one before).
# D-372 (owner: "make the missile pods wider, taking almost the entier wing, with more missiles";
# an octagon 0.2 wide and 0.27 high at x 1.3, seven missiles, before): a wide flat launcher, a
# rounded rectangle in section, spanning the wing from the main nacelle to short of the tip pod
# (x 1.09 to 1.77), the wing still running through it. Its middle's place, half width, half
# height and corners; its profile, `[z from its middle, scale of the section]`.
# D-373 (owner: "use this missile pod, but put one over and one under the wings, moving them to
# the back a little"): two per wing, their middles `y` over and under the wing's plane, so each
# sits on the wing's face (half 0.035 thick), and 0.15 further back (-0.4 before). D-374 (owner:
# "move the missile pods to the back so they dont over the edge of the wings"): their fronts behind
# the leading edge all along them, which the forward sweep puts furthest back at their inner end
# (z -0.51 at x 1.09): their middle at -1.12 (-0.55 before).
# D-376 (owner: "make the missile pods shorter, so their back dont go past the wings too, remove
# their small wings and rework the junction between the pod and the wing, make it look like it's
# part of the wing instead of something put on top of it"; rounded boxes 1.16 long sitting on
# the wing, an accent band round them and two small fins at their tails, before): each pod grows
# out of the wing's face as the scoops grow out of the main reactors (D-367): a crowned arch in
# section, its walls run into the wing by concave fillets `flare` wide, its base sunk `sink` in
# the wing; full height from its front, then its top eases down into the wing towards its back.
# It lies between the wing's edges across its whole width: the forward sweep sets its front by
# the leading edge at its inner end and its back by the trailing edge at its outer end. Its
# middle's X and its half width (at the walls); its front and back Z; its top over the wing's
# plane; how much of its length stands at full height (the rest a ramp of `rampSteps`).
MISSILE_POD: dict[str, Any] = {
    "x": 1.43,
    "halfWidth": 0.33,
    # D-393 (owner: "and move the pods to the front a little"): 0.08 forward (-0.52 to -1.1
    # before), still behind the leading edge, which runs further forward since D-383.
    # D-402 (owner: "move the front of the missile pods to the front (they will be longer) and cut
    # the back triangle shape mid width"): front -0.3 (-0.44), still behind the leading edge.
    "front": -0.3,
    "back": -1.02,
    "top": 0.25,
    "full": 0.45,
    "rampSteps": 4,
    "chamfer": 0.03,
    "tail": 0.6,
    "flare": 0.04,
    "sink": 0.02,
    "gap": 0.015,
    "corner": 0.05,
    "crown": 0.06,
    "filletSteps": 1,
    "cornerSteps": 2,
    "crownSteps": 1,
}
# D-375 (owner: "rework the missiles, pack more missiles, move the missile plate a little to the
# back"; 2 rows of 8 bare cones on a plate a hair proud of the pod's front, before): the pod's
# front is open, lined in dark trim `recess` deep (its share of the front's size), the lining's
# closed back the plate; the missiles packed in staggered rows (`columns` in the outer rows, one
# fewer in the middle ones, set half a spacing over), each a nose cone, `[z ahead of the plate,
# radius]`, its base just inside the recess (bodies behind it were out of sight in the dark and
# took the ship over its triangle budget, GFX-SHIP-05), its tip standing out of the recess.
MISSILE_FACE: dict[str, Any] = {"share": 0.85, "recess": 0.04}
MISSILE_TIPS: dict[str, Any] = {
    "rows": 3,
    "columns": 9,
    "spacing": [0.058, 0.05],
    "radius": 0.019,
}

# Twin reactors on each wing tip (owner: "add two reactors on the tip of each wing, with 45° lil
# wings on each", "make it a dual reactor on the tip of each wing, and add intake to the
# reactors", D-330, "make the wings reactor on of top the other, not side by side", D-331): one over
# the other, each with an intake and a small fin out from its back half at 45° (the fins gave way
# to the tails and ventral fins, D-353). D-332 ("add more body to the wings reactors,
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
    "length": 1.35,
}
TIP_BODY: dict[str, Any] = {"halfWidth": 0.125, "halfHeight": 0.255, "corner": 0.1, "steps": 3}
# D-364 (owner: "rework the intakes of the side reactors, I want the first upper third of the
# intake to be more on the front, then a diaginal third, and the final vertical third at it's
# current position"): the intake's mouth, and the body's front round it, are stepped in side view:
# the upper third `rake` further forward, the middle third a diagonal down to the lower third,
# upright where it stood. D-384 (owner: "rework the side reactor intakes, make them flat"): no step,
# the mouth one upright plane where its lower third stood (`rake` 0; 0.12 before).
# D-385 (owner: "there is something wrong in the side reactor intakes geometry, the link with the
# front part is ugly, it works well for the main reactors"): the body's section is the intake's
# rounded octagon, stretched upright, so the intake's skin carries it on flush, as on the main
# reactors (a rounded rectangle, shrunk at its front, met the octagon with a step before). Its
# radius 0.135 (0.124), as wide as the rectangle was, its reactors' corners inside it.
# D-404 (owner: "the side reactor collide with the hull on the outer part, make the hull wider"):
# radius 0.15 (0.135), stretched 1.845 (2.05), as tall as before, wider: the nozzles' rings clear
# its chamfered corners at its back.
TIP_INTAKE: dict[str, Any] = {"radius": 0.15, "stretch": 1.845, "rake": 0.0}
# D-395 (owner: "there are still useless reactor tubes in the side reactor inside the hulls"):
# the body runs on to the nozzles' plane, a little narrower there, and ends in a flat back face
# carrying the two nozzles' cores and rings; the reactors have no nacelle of their own (tubes in
# the body, their ends out of its pointed tail, before).
TIP_BODY_PROFILE = [
    [0.675, 0],
    [0.675, 1.0],
    [0.5, 1.0],
    [-0.48, 1.0],
    [-0.6, 0.95],
    [-0.675, 0.95],
    [-0.675, 0],
]


def _build_body(root: Any, scene: Any) -> None:
    """Build the slim central body, its seams and vents, and the guns under it."""
    mats = get_ship_materials(scene)
    body_root = new_transform_node("ship-body-root", scene)
    body_root.parent = root
    # One skin (D-336). D-380 (owner: "use the smooth shading on the main hull too"): smooth-shaded
    # as the pods and nacelles are, its normals shared round each section (every face flat-shaded,
    # its facets' edges crisp, before).
    sections = hull_sections()
    body = create_section_loft("ship-body", sections, len(sections[0][1]), scene)
    body.material = mats.hull
    body.parent = body_root
    for k, z in enumerate(SEAM_ZS):
        _build_seam("ship-seam-" + str(k), z, mats.hullDark, body_root, scene)
    for side, sign in [("right", 1), ("left", -1)]:
        for k, vent in enumerate(VENTS):
            outline = vent if sign > 0 else mirror_x(vent)
            middle = _centre(vent)
            y = top_height(station_at(middle[1]), middle[0])
            name = "ship-vent-" + side + "-" + str(k)
            plate(name, outline, y, mats.hullDark, body_root)

    for side, sign in [("right", 1), ("left", -1)]:
        outline = STRAKE_TAIL if sign > 0 else mirror_x(STRAKE_TAIL)
        panel("ship-strake-" + side + "-tail", outline, CHINE_EDGE * 2, mats.hull, body_root)
    _build_tail_plate(body_root, scene)

    _build_laser(root, scene)
    for side, sign in [("right", 1), ("left", -1)]:
        _build_minigun(side, sign, root, scene)


def tail_plate_sections() -> list[list[Any]]:
    """Return the dark plate's sections on the body's square back (D-356), front to back."""
    end = STATIONS[len(STATIONS) - 1]
    _z, ring = hull_section(end)
    # Only the body's own part of the back: the strakes are left out, flat.
    body = [p for p in ring if abs(p[0]) <= end[BODY_HALF_WIDTH] * CHINE_ROOT]
    sections: list[list[Any]] = []
    for share, z in [
        [TAIL_PLATE["front"], TAIL_PLATE["frontZ"]],
        [TAIL_PLATE["back"], TAIL_PLATE["backZ"]],
    ]:
        sections.append([z, [[p[0] * share, p[1] * share] for p in body]])
    return sections


def _build_tail_plate(parent: Any, scene: Any) -> None:
    """Build the dark plate on the body's square back (D-356)."""
    plate_mesh = create_section_loft("ship-tail-plate", tail_plate_sections(), 0, scene)
    plate_mesh.material = get_ship_materials(scene).hullDark
    plate_mesh.parent = parent


def fairing_section(z: float, size: list[float]) -> list[Any]:
    """Return the gun keel's section `[z, ring]` at `z` for `[_, half width, depth]` (D-399).

    A half oval under the belly: from its right top corner down round its underside to its left
    top corner, a little inside the hull's underside (D-349), its top edge closing it in the hull.
    """
    half = size[1]
    depth = size[2]
    station = station_at(z)
    belly = -station[BELLY_DEPTH]
    corner = max(belly + 0.02, underside_height(station, half) + 0.02)
    bottom = belly - depth
    count = GUN_FAIRING_POINTS - 1
    ring = []
    for k in range(count + 1):
        angle = math.pi * k / count
        ring.append([half * math.cos(angle), corner + (bottom - corner) * math.sin(angle)])
    return [z, ring]


def pylon_sections(sign: float) -> list[Any]:
    """Return a minigun pylon's airfoil sections, root and tip, on `sign`'s side (D-399).

    In the frame of a node turned a quarter round Y: Z there is the ship's X (`sign` times the
    span), X there the ship's -Z; Y the height, round the minigun's axis.
    """
    pylon = MINIGUN_PYLON
    sections: list[Any] = []
    for k in range(2):
        lead = pylon["leading"][k]
        chord = lead - pylon["trailing"][k]
        half = pylon["thickness"][k] / 2
        foil = pylon["airfoil"]
        upper = [[lead - p[0] * chord, MINIGUN["y"] + p[1] * half] for p in foil]
        lower = [
            [lead - foil[j][0] * chord, MINIGUN["y"] - foil[j][1] * half]
            for j in range(len(foil) - 2, 0, -1)
        ]
        ring = [[-p[0], p[1]] for p in upper]
        ring.extend([[-p[0], p[1]] for p in lower])
        sections.append([sign * pylon["xs"][k], ring])
    return sections


def _build_laser(root: Any, scene: Any) -> None:
    """Build the keel fairing under the belly and the laser out of it (D-339, D-340, D-342).

    Out of the fairing's nose, under the ship's and past its tip: twin rails tapering into prongs
    either side of a glowing core, a glowing emitter at its tip (D-342).
    """
    mats = get_ship_materials(scene)
    sections = [fairing_section(f[0], f) for f in GUN_FAIRING]
    # Smooth round its underside, its top edge (in the hull) flat (D-399).
    fairing = create_section_loft("ship-gun-fairing", sections, GUN_FAIRING_POINTS, scene)
    fairing.material = mats.hull
    fairing.parent = root
    for side, sign in [("right", 1), ("left", -1)]:
        span = new_transform_node("ship-minigun-" + side + "-pylon-root", scene)
        span.rotation.y = math.pi / 2
        span.parent = root
        foil = pylon_sections(sign)
        pylon = create_section_loft("ship-minigun-" + side + "-pylon", foil, len(foil[0][1]), scene)
        pylon.material = mats.hull
        pylon.parent = span
    laser = LASER
    node = new_transform_node("ship-laser", scene)
    node.position.y = laser["y"]
    node.parent = root
    core = laser["core"]
    back = core["zs"][0]
    front = core["zs"][1]
    faceted_rod(
        "ship-laser-core",
        {"length": front - back, "radius": core["radius"]},
        vector3(0, 0, (front + back) / 2),
        mats.reactorCore,
        node,
        OCTAGON,
    )
    thickness = laser["railThickness"]
    for side, sign in [("right", 1), ("left", -1)]:
        rail = create_section_loft("ship-laser-rail-" + side, laser_rail_sections(sign), 0, scene)
        rail.material = mats.hullDark
        rail.parent = node
    panel("ship-laser-bridge", LASER_BRIDGE, thickness * 1.4, mats.hullDark, node)
    _build_laser_clamps(mats, node)
    emitter = create_faceted_lathe_along_z("ship-laser-emitter", LASER_EMITTER, OCTAGON, scene)
    emitter.material = mats.reactorCore
    emitter.parent = node


def laser_rail_at(z: float) -> list[float]:
    """Return a laser rail's `[inner X, outer X, half height]` at `z`, between its sections."""
    rows = LASER_RAIL_SECTIONS
    for k in range(len(rows) - 1):
        a = rows[k]
        b = rows[k + 1]
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return [a[i] + (b[i] - a[i]) * t for i in range(1, 4)]
    last = rows[len(rows) - 1] if z > rows[0][0] else rows[0]
    return [last[1], last[2], last[3]]


def _build_laser_clamps(mats: Any, node: Any) -> None:
    """Add the accent clamps round the laser rails' backs, a little proud of them (D-401)."""
    clamps = LASER_CLAMPS
    proud = clamps["proud"]
    half = clamps["half"]
    for k, z in enumerate(clamps["zs"]):
        inner, outer, height = laser_rail_at(z)
        for side, sign in [("right", 1.0), ("left", -1.0)]:
            xs = [sign * (inner + proud), sign * (outer + proud)]
            outline = [
                [min(xs), z - half],
                [max(xs), z - half],
                [max(xs), z + half],
                [min(xs), z + half],
            ]
            name = "ship-laser-clamp-" + side + "-" + str(k)
            panel(name, outline, 2 * (height + proud), mats.accent, node)


def laser_rail_sections(sign: float) -> list[Any]:
    """Return a laser rail's blade sections on `sign`'s side, back to front (D-400)."""
    bevel = LASER["bevel"]
    sections: list[Any] = []
    for row in LASER_RAIL_SECTIONS:
        inner = row[1]
        outer = row[2]
        half = row[3]
        width = outer - inner
        edge = outer - width * bevel * 0.6
        ridge = outer - width * bevel * 1.4
        ring = [
            [outer, 0.0],
            [edge, half * 0.55],
            [ridge, half],
            [inner, half * 0.8],
            [inner, -half * 0.8],
            [ridge, -half],
            [edge, -half * 0.55],
        ]
        sections.append([row[0], [[sign * p[0], p[1]] for p in ring]])
    return sections


def barrel_profile(length: float, radius: float, bore: dict[str, float]) -> list[list[float]]:
    """Return a hollow barrel's lathe profile (`[z, radius]`, centred on its middle) (D-345).

    From the bore's bottom out to its wall, forward along it to the muzzle, out over the muzzle's
    rim, back along the outside and in over the breech: the lathe turns the bore's wall to face
    the axis, so the hole reads from ahead.
    """
    front = length / 2
    inner = radius * bore["radius"]
    bottom = front - bore["depth"]
    return [
        [bottom, 0],
        [bottom, inner],
        [front, inner],
        [front, radius],
        [-front, radius],
        [-front, 0],
    ]


def _build_minigun(side: str, sign: float, root: Any, scene: Any) -> None:
    """Build a minigun in a flank of the fairing (D-339, D-340).

    Its drum, of hull metal, half sunk in the fairing as a blister; six barrels round its axis out
    ahead of it, hollow at their muzzles (D-345), a clamp round them.
    """
    mats = get_ship_materials(scene)
    gun = MINIGUN
    name = "ship-minigun-" + side
    node = new_transform_node(name, scene)
    node.position.set(sign * gun["x"], gun["y"], gun["z"])
    node.parent = root
    # D-387 (owner: "apply the same smooth shader as the rest of the ship"): every part of the gun
    # smooth-shaded, lofted as the hull and pods are (`smooth_lathe`); faceted lathes before.
    shell = smooth_lathe(name + "-drum", gun["drumProfile"], OCTAGON, scene)
    shell.material = mats.hull
    shell.parent = node
    barrels = gun["barrels"]
    profile = barrel_profile(barrels["length"], barrels["radius"], gun["bore"])
    # The bore, its bottom and wall (the profile's first three points), matte black (owner, D-351:
    # "make the inner part of the minigun mat black"); the muzzle's rim and the outside, metal.
    # D-352 (owner: "the inside polygons of the gun barrel are not drawn"): the lathe turns a
    # profile to run towards the nose and faces it outward; the bore's alone already runs that way,
    # so its wall faced away from the axis and was culled. Turned round, it faces the axis.
    # D-394: the outside open at its back end, inside the drum's collar (capped there before).
    parts = [("-bore", profile[0:3], mats.intakeBlack), ("", profile[2:5], mats.trim)]
    for k in range(barrels["count"]):
        # D-378 (owner: "rotate the minigins 30° so one barrel is at the vertical top"): the ring
        # turned `turn` round the axis (a barrel on +X, none on top, before).
        angle = barrels["turn"] + 2 * math.pi * k / barrels["count"]
        for suffix, part, material in parts:
            barrel = smooth_lathe(name + "-barrel-" + str(k) + suffix, part, PART_FACETS, scene)
            barrel.position.set(
                barrels["ring"] * math.cos(angle),
                barrels["ring"] * math.sin(angle),
                barrels["z"],
            )
            if suffix == "-bore":
                barrel.flipFaces(True)
            barrel.material = material
            barrel.parent = node
    # D-386 (owner: "simplify the minigun rings, it can be full, and add a second thicker ring
    # near the point of the guns"): each clamp a solid hexagonal disc the barrels run through (a
    # hollow band before), turned with the barrels, its corners by them (D-378).
    for label, clamp in [("clamp", gun["clamp"]), ("muzzle-clamp", gun["muzzleClamp"])]:
        front = clamp["z"] + clamp["half"]
        back = clamp["z"] - clamp["half"]
        disc = [[front, 0], [front, clamp["radius"]], [back, clamp["radius"]], [back, 0]]
        ring = smooth_lathe(name + "-" + label, disc, 6, scene)
        ring.rotation.z = barrels["turn"]
        ring.material = mats.hullDark
        ring.parent = node


def smooth_lathe(name: str, profile: list[list[float]], sides: int, scene: Any) -> Any:
    """Return a smooth-shaded body of revolution round Z, `sides` round (D-387).

    A section loft as the hull's and the pods' are: a regular polygon (a corner on +X) at each
    `[z, radius]` of `profile`, its normals shared round each section and along it; a radius of
    0 closes it there. Its faces across the axis stay flat-shaded (D-388).
    """
    angles = [2 * math.pi * k / sides for k in range(sides)]
    sections = [[p[0], [[p[1] * math.cos(a), p[1] * math.sin(a)] for a in angles]] for p in profile]
    # D-388 (owner: "dont apply the shader on the front/back sides of the rings and minigun
    # body"): the flat faces across the axis (ends, rims) stay flat-shaded, edges crisp.
    flat = [k for k in range(len(profile) - 1) if profile[k][0] == profile[k + 1][0]]
    return create_section_loft(name, sections, sides, scene, False, False, flat)


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


def _build_cockpit(root: Any, scene: Any, glow_width: float) -> None:
    """Build the cockpit (D-354): canopy glass, its bow and sill rails, and what shows inside."""
    mats = get_ship_materials(scene)
    glass = create_section_loft("ship-canopy", canopy_sections(), ARCH_POINTS, scene)
    glass.material = mats.glass
    glass.parent = root
    for side, sign in [("right", 1.0), ("left", -1.0)]:
        rail = create_section_loft(
            "ship-canopy-rail-" + side,
            rail_sections(sign, glow_width / EDGE_GLOW["width"]),
            0,
            scene,
        )
        # D-370 (owner: "remove the glow in the main body and wings, only keep the ones on the
        # vertical wings"): gunmetal, as the bow (they glowed before).
        rail.material = mats.hullDark
        rail.parent = root
    bow = BOW
    half_width = bow["width"] / 2
    outline_z = [[-1.0, -half_width], [1.0, -half_width], [1.0, half_width], [-1.0, half_width]]
    for k, (x, y, angle, length) in enumerate(bow_segments()):
        bow_name = "ship-canopy-bow-" + str(k)
        node = new_transform_node(bow_name, scene)
        node.position.set(x, y, bow["z"])
        node.rotation.z = angle
        node.parent = root
        outline = [[p[0] * length / 2, p[1]] for p in outline_z]
        # D-394: its name from the string, not `node.name`, which Transcrypt reads as `py_name`
        # (undefined in the game: every bow panel was "undefined-panel").
        panel(bow_name + "-panel", outline, bow["thickness"], mats.hullDark, node)
    _build_cockpit_inside(root, scene)


def _build_cockpit_inside(root: Any, scene: Any) -> None:
    """Build what shows under the glass: the floor, the hood, the seat and the pilot's helmet."""
    mats = get_ship_materials(scene)
    floor = create_section_loft("ship-cockpit-floor", floor_sections(), 0, scene)
    floor.material = mats.intakeBlack
    floor.parent = root
    hood = HOOD
    hood_floor = floor_height(HOOD_ZS[1])
    outline = [[-hood["half"], HOOD_ZS[0]], [hood["half"], HOOD_ZS[0]]]
    outline.append([hood["half"], HOOD_ZS[1]])
    outline.append([-hood["half"], HOOD_ZS[1]])
    mesh = panel("ship-cockpit-hood", outline, hood["height"], mats.hullDark, root)
    mesh.position.y = hood_floor + hood["height"] / 2
    seat = SEAT
    seat_floor = floor_height(SEAT_ZS[0])
    for part, half, height in [
        ("seat", seat["half"], seat["height"]),
        ("headrest", seat["headHalf"], seat["headHeight"]),
    ]:
        outline = [[-half, SEAT_ZS[0]], [half, SEAT_ZS[0]], [half, SEAT_ZS[1]]]
        outline.append([-half, SEAT_ZS[1]])
        mesh = panel("ship-cockpit-" + part, outline, height, mats.hullDark, root)
        mesh.position.y = seat_floor + height / 2
    helmet = HELMET
    radius = helmet["radius"]
    centre = floor_height(helmet["z"]) + helmet["y"]
    parts: list[tuple[str, list[list[float]], Any]] = [
        ("helmet", HELMET_PROFILE, mats.hull),
        ("visor", VISOR_PROFILE, mats.canopy),
    ]
    for part, profile, material in parts:
        scaled = [[p[0] * radius, p[1] * radius] for p in profile]
        mesh = create_faceted_lathe_along_z(
            "ship-cockpit-" + part, scaled, LatheHalves(8, 3), scene
        )
        mesh.position.set(0, centre, helmet["z"])
        mesh.material = material
        mesh.parent = root


def _build_wing(side: str, sign: float, root: Any, scene: Any) -> None:
    """Build a forward-swept main wing, its flap and panel lines (no canard, D-363).

    The main wing runs out of the nacelle; the body's strakes join the nacelle to the body (D-336).
    """
    mats = get_ship_materials(scene)

    def mirror(outline: list[list[float]]) -> list[list[float]]:
        return outline if sign > 0 else mirror_x(outline)

    wing = new_transform_node("ship-wing-" + side, scene)
    wing.parent = root
    panel(
        "ship-wing-" + side + "-panel",
        mirror(MAIN_WING),
        WING_THICKNESS,
        mats.hullMid,
        wing,
    )
    flap = mirror(WING_FLAP)
    plate("ship-wing-" + side + "-flap", flap, WING_THICKNESS / 2, mats.hullDark, wing)
    for k, line in enumerate(WING_LINES):
        name = "ship-wing-" + side + "-line-" + str(k)
        plate(name, mirror(line), WING_THICKNESS / 2, mats.hullDark, wing)


def _centre(outline: list[list[float]]) -> list[float]:
    """Return the middle of a planform outline's points."""
    return [
        sum(p[0] for p in outline) / len(outline),
        sum(p[1] for p in outline) / len(outline),
    ]


def _build_tails(side: str, sign: float, root: Any, scene: Any, glow_width: float) -> None:
    """Build the canted tail on a wing-tip pod's top and the ventral fin under it (D-353)."""
    mats = get_ship_materials(scene)
    pod = TIP_REACTOR
    x = sign * pod["x"]
    middle = (pod["ys"][0] + pod["ys"][1]) / 2
    top = middle + TIP_BODY["halfHeight"]
    bottom = middle - TIP_BODY["halfHeight"]
    tail = new_transform_node("ship-tail-" + side, scene)
    tail.position.set(x, top - 0.02, TIP_TAIL_SHIFT)
    # Stand the panel up (X becomes height), then cant it outwards.
    tail.rotation.z = math.pi / 2 - sign * TAIL_CANT
    tail.parent = root
    panel("ship-tail-" + side + "-panel", TAIL, TAIL_THICKNESS, mats.hullDark, tail)
    # Their leading edge and tip glow, as the wings' do (D-346, owner: "add highlight to the
    # vertical wings too").
    _glow_edges(
        "ship-glow-" + side + "-tail", TAIL, TAIL_THICKNESS, glow_width, mats.edgeGlow, tail
    )

    # Ventral fin: same trick, pointing down and outwards.
    fin = new_transform_node("ship-ventral-" + side, scene)
    fin.position.set(x, bottom + 0.02, TIP_TAIL_SHIFT)
    fin.rotation.z = -math.pi / 2 + sign * TAIL_CANT
    fin.parent = root
    panel("ship-ventral-" + side + "-panel", TAIL, TAIL_THICKNESS, mats.hullDark, fin)
    _glow_edges(
        "ship-glow-" + side + "-ventral",
        TAIL,
        TAIL_THICKNESS,
        glow_width,
        mats.edgeGlow,
        fin,
    )


def _glow_edges(
    name: str,
    outline: list[list[float]],
    thickness: float,
    width: float,
    material: Any,
    parent: Any,
) -> None:
    """Lay glowing strips `width` across on a fin's leading edge and tip: its first two edges."""
    size = {"width": width, "thickness": thickness + 0.006}
    for k in range(2):
        edge = [outline[k], outline[k + 1]]
        edge_strip(name + "-" + str(k), edge, _centre(outline), size, material, parent)


def _build_missile_tips(name: str, plate: float, material: Any, parent: Any) -> None:
    """Add the missiles' black launch holes on a launch plate at `plate`, packed in rows.

    D-375: staggered rows. D-391 (owner: "change the look of the missiles, create black holes for
    the missiles instead of showing missile tips"): a matte black octagonal disc a hair proud of
    the plate where each missile is, facing forward (a cone standing out of it before).
    """
    tips = MISSILE_TIPS
    spacing = tips["spacing"]
    k = 0
    for row in range(tips["rows"]):
        y = (row - (tips["rows"] - 1) / 2) * spacing[1]
        # The middle rows sit half a spacing over, one missile fewer, packed in the gaps.
        columns = tips["columns"] - (row % 2)
        for column in range(columns):
            x = (column - (columns - 1) / 2) * spacing[0]
            hole = create_disc(
                name + "-hole-" + str(k), disc_options(tips["radius"], OCTAGON), parent.getScene()
            )
            hole.convertToFlatShadedMesh()
            # A disc faces -Z: turned round, it faces forward.
            hole.rotation.y = math.pi
            hole.position.set(x, y, plate + 0.002)
            hole.material = material
            hole.parent = parent
            k += 1


def missile_pod_sections(up: float) -> list[Any]:
    """Return a missile pod's sections, front to back, `up` 1 on the wing's top.

    A rounded box (D-390) `gap` clear of the wing's face (D-392), full size from its front, then
    tapering evenly to `tail` of its width and height along a half cosine, its base still on the
    wing (D-403). Both ends chamfered in to a rim the size of their recess's lining: the launch
    face at its front (D-376), the rear vent at its back (D-403).
    """
    pod = MISSILE_POD
    share = MISSILE_FACE["share"]
    front = pod["front"]
    back = pod["back"]
    chamfer = pod["chamfer"]
    ramp = front - (front - back) * pod["full"]
    end = back + chamfer
    zs = [front - chamfer]
    steps = pod["rampSteps"]
    zs.extend([ramp + (end - ramp) * k / steps for k in range(steps + 1)])
    bottom = WING_THICKNESS / 2 + pod["gap"]
    height = pod["top"] - bottom
    sections: list[Any] = []
    for z in zs:
        t = max(0.0, (ramp - z) / (ramp - end))
        # D-403 (owner: "the back of the missile pods is ugly, make up something better"; its top
        # eased down onto its base and its width cut to half, a flat sliver at its end, before):
        # an even taper in width and height to `tail` of its size.
        scale = 1 - (1 - pod["tail"]) * (1 - math.cos(math.pi * t)) / 2
        half = pod["halfWidth"] * scale
        half_height = height * scale / 2
        corner = min(pod["corner"] * scale, half, half_height)
        box = rounded_rectangle(half, half_height, corner, pod["cornerSteps"])
        centre = bottom + half_height
        sections.append([z, [[p[0], up * (centre + p[1])] for p in box]])
    # Each end chamfered in to its recess's lining, which it meets, so no gap opens onto the
    # inside of its skin.
    rims = []
    for k in [0, len(sections) - 1]:
        ring = sections[k][1]
        ys = [p[1] for p in ring]
        middle = (max(ys) + min(ys)) / 2
        rims.append([[p[0] * share, middle + (p[1] - middle) * share] for p in ring])
    sections.insert(0, [front, rims[0]])
    sections.append([back, rims[1]])
    return sections


def missile_face_middle() -> float:
    """Return the height of a missile pod's front's middle over the wing's plane (D-376, D-390)."""
    pod = MISSILE_POD
    middle: float = (pod["top"] + WING_THICKNESS / 2 + pod["gap"]) / 2
    return middle


def _build_missile_pods(side: str, sign: float, root: Any, scene: Any) -> None:
    """Build a wing's two missile launchers, one on its top and one under it (D-373)."""
    for level, up in [("upper", 1.0), ("lower", -1.0)]:
        _build_missile_pod(side + "-" + level, sign, up, root, scene)


def _build_missile_pod(side: str, sign: float, up: float, root: Any, scene: Any) -> None:
    """Build a missile launcher grown out of a wing's face: its fairing, recess and missiles.

    `up` 1 on the wing's top, -1 under it (D-373); filleted into the wing (D-376).
    """
    mats = get_ship_materials(scene)
    pod = MISSILE_POD
    face = MISSILE_FACE
    name = "ship-missiles-" + side
    node = new_transform_node(name, scene)
    node.position.x = sign * pod["x"]
    node.parent = root
    sections = missile_pod_sections(up)
    # Open at both ends, round its recesses (D-375, D-403).
    shell = create_section_loft(name + "-pod", sections, len(sections[0][1]), scene, False, False)
    shell.material = mats.hullMid
    shell.parent = node
    front = pod["front"]
    plate = front - face["recess"]
    middle = up * missile_face_middle()
    # The skin's chamfered front edge, which the lining meets.
    ring = sections[0][1]
    # The recess's dark lining, facing in; its closed back is the plate (D-375).
    lining = create_section_loft(name + "-recess", [[front, ring], [plate, ring]], 0, scene, False)
    lining.flipFaces(True)
    lining.material = mats.trim
    lining.parent = node
    # D-403: the rear vent, a recess as the front's, its lining dark, its plate facing back.
    tail = sections[len(sections) - 1][1]
    vent_back = pod["back"] + face["recess"]
    vent = create_section_loft(
        name + "-vent", [[pod["back"], tail], [vent_back, tail]], 0, scene, False
    )
    vent.flipFaces(True)
    vent.material = mats.trim
    vent.parent = node
    holder = new_transform_node(name + "-missiles", scene)
    holder.position.y = middle
    holder.parent = node
    _build_missile_tips(name, plate, mats.intakeBlack, holder)


def _build_tip_reactor(side: str, sign: float, root: Any, scene: Any) -> None:
    """Build the twin reactors on a wing tip, one over the other, and the body round them.

    The tail and ventral fin on the body are `_build_tails`' (D-353: they replace its 45° fins).
    """
    mats = get_ship_materials(scene)
    pod = TIP_REACTOR
    name = "ship-tip-" + side
    x = sign * pod["x"]
    for k, label in enumerate(["upper", "lower"]):
        y = pod["ys"][k]
        # Inside the pod's body: no front ring, which poked through its sides (D-385).
        # D-395: no nacelle, the body's back carries the nozzle (no front ring either, D-385).
        reactor = build_reactor(
            name + "-reactor-" + label, pod, scene, False, REACTOR_SIDES, 1.0, False, False
        )
        reactor.position.set(x, y, pod["z"])
        reactor.parent = root
    # One body wrapping both, scaled along the profile: the intake's rounded octagon, stretched
    # upright, so the intake's skin carries it on flush (D-385).
    intake_size = TIP_INTAKE
    octagon = rounded_polygon(
        OCTAGON,
        intake_size["radius"],
        REACTOR_ROUNDING,
        REACTOR_CORNER_STEPS,
        polygon_turn(OCTAGON),
    )
    ring = [[q[0], q[1] * intake_size["stretch"]] for q in octagon]
    middle = (pod["ys"][0] + pod["ys"][1]) / 2
    sections = [
        [pod["z"] + p[0], [[x + p[1] * q[0], middle + p[1] * q[1]] for q in ring]]
        for p in TIP_BODY_PROFILE
    ]
    # Its front ring stepped with the intake's mouth (D-364); the closed point behind stays.
    sections[1] = [
        sections[1][0],
        [[q[0], q[1], tip_intake_rake(q[1] - middle)] for q in sections[1][1]],
    ]
    # Its flat back face flat-shaded, its edge crisp (D-395).
    back = [len(sections) - 2]
    shell = create_section_loft(name + "-body", sections, len(ring), scene, True, True, back)
    shell.material = mats.hullMid
    shell.parent = root
    # One octagonal intake for both reactors, at the body's front.
    intake = new_transform_node(name + "-intake-root", scene)
    intake.position.set(x, middle, pod["z"] + pod["length"] / 2)
    intake.scaling.y = TIP_INTAKE["stretch"]
    intake.parent = root
    stretch = TIP_INTAKE["stretch"]

    def rake(y: float) -> float:
        return tip_intake_rake(y * stretch)

    add_reactor_intake(name, TIP_INTAKE["radius"], 0, intake, OCTAGON, stretch, rake)


def tip_intake_rake(height: float) -> float:
    """Return how far forward the tip intake's mouth stands at `height` over its middle (D-364).

    The upper third of the body's height `rake` forward, the middle third a diagonal, the lower
    third where it stood.
    """
    third = TIP_BODY["halfHeight"] * 2 / 3
    share = max(0.0, min(1.0, (height + third / 2) / third))
    rake: float = TIP_INTAKE["rake"] * share
    return rake


def nacelle_scale(z: float) -> float:
    """Return a main nacelle's size at `z` from its middle, a share of its radius (D-367)."""
    length = REACTOR["length"]
    taper = [[length * p[0], p[1]] for p in NACELLE_TAPER]
    if z >= taper[0][0]:
        return 1.0
    for k in range(len(taper) - 1):
        front = taper[k]
        back = taper[k + 1]
        if z >= back[0]:
            t = (front[0] - z) / (front[0] - back[0])
            scale: float = front[1] + (back[1] - front[1]) * t
            return scale
    last: float = taper[len(taper) - 1][1]
    return last


def nacelle_top(x: float, z: float) -> float:
    """Return the height of a main nacelle's top at `x` across and `z` along it (D-367).

    Its octagon's flat top, then the chamfer falling at 45° (the rounded corners ignored).
    """
    radius = REACTOR["radius"] * nacelle_scale(z)
    flat = radius * math.cos(math.pi / OCTAGON)
    half = radius * math.sin(math.pi / OCTAGON)
    top: float = flat - max(0.0, abs(x) - half)
    return top


def flat_seat(height: float) -> Any:
    """Return a scoop's seat that is flat at `height` (D-367)."""

    def seat(_x: float) -> float:
        return height

    return seat


def nacelle_seat(z: float) -> Any:
    """Return a scoop's seat on a main nacelle's top at `z` (D-367)."""

    def seat(x: float) -> float:
        return nacelle_top(x, z)

    return seat


def scoop_seat_end() -> float:
    """Return where a scoop leaves the nacelle (D-367): the main intake's straight run ends there.

    In front of it the scoop overhangs the intake, with nothing under it to blend into.
    """
    end: float = REACTOR["length"] / 2 + REACTOR_INTAKE[1][0] * REACTOR["radius"]
    return end


def scoop_ring(
    half: float, top: float, flare: float, seat: Any, sink: float = 0.0, shape: Any = None
) -> list[list[float]]:
    """Return a scoop's section: a crowned arch on `seat(x)`, filleted into it (D-367).

    `half` its half width at the wall, `top` its crown's height, `flare` how far its fillets run
    out over the seat. Counter clockwise from the right foot: the fillet, a concave curve tangent
    to the seat and to the wall; the wall; the rounded shoulder; the crown, a gentle arch; the
    same on the left; then one point of its base, `sink` under the seat's middle (on a nacelle,
    its chamfers fall away under the feet). Always the same point count. `shape` gives its corner,
    crown and point counts (the scoops' by default; the missile pods', D-376).
    """
    scoop = shape if shape is not None else REACTOR_SCOOP
    foot = [half + flare, seat(half + flare) - 0.004]
    wall = seat(half)
    room = max(0.001, top - wall)
    corner = max(0.0005, min(scoop["corner"], half / 2, room / 2))
    crown = min(scoop["crown"] * half, room / 4)
    shoulder = top - crown
    rise = max(0.0005, min(flare, shoulder - corner - wall))
    if flare < 0:
        # D-398: a negative `flare` chamfers its base's corners at 45°, `-flare` up the wall and
        # in along the base (two 45° turns in place of one at 90°), where it stands in the air.
        foot = [half + flare, seat(half + flare)]
        rise = min(-flare, max(0.0005, shoulder - corner - wall))
    right: list[list[float]] = []
    steps = scoop["filletSteps"]
    for k in range(steps + 1):
        t = k / steps
        a = (1 - t) * (1 - t)
        b = 2 * t * (1 - t)
        c = t * t
        right.append([
            a * foot[0] + b * half + c * half,
            a * foot[1] + b * wall + c * (wall + rise),
        ])
    arc = [half - corner, shoulder - corner]
    for k in range(scoop["cornerSteps"]):
        angle = math.pi / 2 * k / (scoop["cornerSteps"] - 1)
        right.append([arc[0] + corner * math.cos(angle), arc[1] + corner * math.sin(angle)])
    span = half - corner
    for k in range(1, scoop["crownSteps"] + 1):
        x = span * (1 - k / scoop["crownSteps"])
        right.append([x, top - crown * (x / span) * (x / span)])
    left = [[-p[0], p[1]] for p in reversed(right[:-1])]
    base = min(foot[1], seat(0.0) - sink)
    # Built with `extend`: Transcrypt drops `*` unpacking in a list display, and `+` on lists is
    # JavaScript's string concatenation.
    ring: list[list[float]] = []
    ring.extend(right)
    ring.extend(left)
    ring.append([0.0, base])
    return ring


def scoop_sections(up: float) -> list[Any]:
    """Return the sections of a main reactor's secondary intake, `up` 1 on top, -1 under (D-347).

    D-367: each section a crowned arch filleted into the nacelle's top (`scoop_ring`), full height
    at its mouth, then a ramp easing down along a half cosine to the nacelle's back, a little
    narrower there, its base following the nacelle's taper. Ahead of the nacelle's seat it
    overhangs the main intake, its base flat at the nacelle's top, sunk `sink` as before, and the
    fillets flare out over `flareRun` behind the seat's end.
    """
    scoop = REACTOR_SCOOP
    sink = scoop["sink"]
    front = scoop["front"]
    lip = front - scoop["lip"]
    back = scoop["back"]
    seat_end = scoop_seat_end()
    zs = [front, lip]
    steps = scoop["rampSteps"]
    zs.extend([lip + (back - lip) * k / steps for k in range(1, steps + 1)])
    joints = [seat_end - scoop["flareRun"]]
    zs.extend([z for z in joints if back < z < lip])
    zs.sort()
    ordered: list[float] = []
    for k in range(len(zs) - 1, -1, -1):
        if len(ordered) == 0 or ordered[len(ordered) - 1] - zs[k] > 1e-9:
            ordered.append(zs[k])
    sections = []
    chamfer = scoop["chamfer"]
    for z in ordered:
        t = max(0.0, (lip - z) / (lip - back))
        # D-398 (owner: "increase the back angle merging into the main reactors"): a quarter
        # cosine, steepest where it meets the nacelle (a half cosine, tangent to it, before).
        ease = math.cos(math.pi * t / 2)
        flat = nacelle_top(0.0, z)
        top = flat + max(0.004, scoop["height"] * ease)
        half = scoop["width"] / 2 * (1 - 0.15 * t)
        if z > seat_end:
            # D-398 (owner: "smooth the under part of the secondary intakes (two 45° instead of a
            # single 90°)"): its base's corners chamfered where it overhangs the main intake.
            ring = scoop_ring(half, top, -chamfer, flat_seat(flat - sink))
        else:
            reach = min(1.0, (seat_end - z) / scoop["flareRun"])
            flare = -chamfer + (scoop["flare"] * (0.5 + 0.5 * ease) + chamfer) * reach
            ring = scoop_ring(half, top, flare, nacelle_seat(z), sink)
        sections.append([z, [[p[0], up * p[1]] for p in ring]])
    return sections


def _build_scoop(name: str, up: float, reactor: Any, scene: Any) -> None:
    """Build a secondary intake on a main reactor's top or bottom (D-347, D-348).

    A smooth silver arch ramping back to the nacelle's back. Its mouth is built as the main
    intakes' (D-369): a silver skin straight on, then angled in to a lip and back into a matte
    black duct; steel fins across the duct, their ends in the lip's wall, the same size and
    spacing as every intake's (D-350, D-351).
    """
    mats = get_ship_materials(scene)
    sections = scoop_sections(up)
    # Its front inside its intake's skin and its back a sliver on the nacelle: left open (D-367).
    # D-397 (owner: "the under part of the secondary intake look wrong"): its base flat-shaded,
    # the last ring points' faces: where it overhangs the main intake its flat bottom shared the
    # walls' normals and shaded as a smear; the walls and crown stay smooth.
    # D-398: its chamfers smooth with the walls, the flat bottom alone flat-shaded.
    smooth = len(sections[0][1]) - 1
    shell = create_section_loft(name, sections, smooth, scene, False, False)
    shell.material = mats.hull
    shell.parent = reactor
    skin = scoop_intake_sections(REACTOR_INTAKE, up)
    # Its back on the scoop's open front; its end, inside the lip, closes the duct.
    # Open at its end too, just inside the lip (D-394): the duct's lining carries on from there.
    mouth = create_section_loft(name + "-intake", skin, len(skin[0][1]) - 1, scene, False, False)
    mouth.material = mats.hull
    mouth.parent = reactor
    # The lining: a loft faces outward, turned round it faces the mouth's middle (D-347).
    duct = create_section_loft(
        name + "-duct", scoop_intake_sections(REACTOR_INTAKE_DUCT, up), 0, scene
    )
    duct.flipFaces(True)
    duct.material = mats.intakeBlack
    duct.parent = reactor
    thickness = intake_fin_thickness(REACTOR_HEIGHT)
    for k, fin in enumerate(scoop_intake_fins(up)):
        height, outline = fin
        mesh = panel(name + "-fin-" + str(k), outline, thickness, mats.hullMid, reactor)
        mesh.position.y = height


def scoop_mouth_frame() -> list[float]:
    """Return a scoop's mouth's middle height and its half width, its intake's radius (D-369).

    Both from its front section (on top), in the nacelle's unscaled units.
    """
    front = scoop_sections(1)[0][1]
    ys = [p[1] for p in front]
    middle = (max(ys) + min(ys)) / 2
    radius = max([p[0] for p in front])
    return [middle, radius]


def scoop_intake_sections(profile: list[list[float]], up: float) -> list[Any]:
    """Return a scoop intake's sections along `profile`, `[z, scale]` in radii (D-369).

    Each the scoop's front section scaled round its middle by `scale`, `z` radii ahead of the
    scoop's front, as the main intakes' rings follow the same profiles round their axis.
    """
    front = scoop_sections(1)[0][1]
    frame = scoop_mouth_frame()
    middle = frame[0]
    radius = frame[1]
    z0 = REACTOR_SCOOP["front"]
    sections: list[Any] = []
    for step in profile:
        scale = step[1]
        ring = [[p[0] * scale, up * (middle + (p[1] - middle) * scale)] for p in front]
        sections.append([z0 + step[0] * radius, ring])
    return sections


def ring_half_width(ring: list[list[float]], y: float) -> float:
    """Return how far out from the middle a closed `ring` reaches at height `y` (D-369)."""
    reach = 0.0
    for k in range(len(ring)):
        a = ring[k]
        b = ring[(k + 1) % len(ring)]
        low = min(a[1], b[1])
        high = max(a[1], b[1])
        if low <= y <= high and high > low:
            x = a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1])
            reach = max(reach, abs(x))
    return reach


def scoop_intake_fins(up: float) -> list[Any]:
    """Return a scoop intake's fins, `[height, outline]`, as the main intakes' (D-351, D-369).

    One in the middle, the intakes' spacing apart within `room` of the duct, each reaching into
    the lip's wall (`REACTOR_INTAKE_FINS["ring"]` of the mouth), the same depth back from their
    front. Heights in the nacelle's unscaled units; the spacing holds once stretched upright.
    """
    fins = REACTOR_INTAKE_FINS
    front_ring = scoop_sections(1)[0][1]
    frame = scoop_mouth_frame()
    middle = frame[0]
    radius = frame[1]
    ys = [p[1] for p in front_ring]
    half_height = (max(ys) - min(ys)) / 2
    wall = [[p[0] * fins["ring"], middle + (p[1] - middle) * fins["ring"]] for p in front_ring]
    front = REACTOR_SCOOP["front"] + fins["front"] * radius
    back = front - INTAKE_FIN_SIZE["depth"]
    room = fins["room"] * half_height * REACTOR_HEIGHT
    out: list[Any] = []
    for height in intake_fin_heights(room):
        y = middle + height / REACTOR_HEIGHT
        half = ring_half_width(wall, y)
        outline = [[-half, front], [half, front], [half, back], [-half, back]]
        out.append([up * y, outline])
    return out


def build_player_ship(scene: Any, glow_width: float = EDGE_GLOW["width"]) -> Any:
    """Build the player ship (GFX-SHIP-01), its glowing edge strips `glow_width` across."""
    root = new_transform_node("ship-player", scene)
    _build_body(root, scene)
    _build_cockpit(root, scene, glow_width)
    for side, sign in [("right", 1), ("left", -1)]:
        _build_wing(side, sign, root, scene)
        # D-371: the tip pods are fixed (they tilted, D-359), with no joint geometry (D-362).
        _build_tails(side, sign, root, scene, glow_width)
        _build_missile_pods(side, sign, root, scene)
        _build_tip_reactor(side, sign, root, scene)
        reactor = build_reactor(
            "ship-reactor-" + side, REACTOR, scene, True, OCTAGON, REACTOR_HEIGHT
        )
        reactor.position.set(sign * REACTOR_OFFSET_X, REACTOR_Y, REACTOR_Z)
        reactor.scaling.y = REACTOR_HEIGHT
        reactor.parent = root
        # D-368 (owner: "remove the under secondary intakes on the main reactors"): on top only.
        _build_scoop("ship-reactor-" + side + "-scoop-top", 1, reactor, scene)
    return root


def playfield_glow_width() -> float:
    """Return the glowing strips' width on the playfield, in model units (D-355).

    `READABILITY.playerGlow.width` logical pixels at the ship's playfield scale.
    """
    width: float = READABILITY.playerGlow.width / PLAYER_SHIP_SCALE
    return width


def build_playfield_ship(scene: Any) -> Any:
    """Build the player ship for the playfield: its glowing edges wide enough to show (D-355).

    At about 40 px long, the menus' strips would be a quarter of a pixel across.
    """
    return build_player_ship(scene, playfield_glow_width())

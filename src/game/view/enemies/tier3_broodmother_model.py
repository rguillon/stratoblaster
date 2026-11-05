# Copyright (c) 2026 Renaud Guillon
"""ENM-BROODMOTHER-01: the Broodmother, a flying aircraft carrier, Cyber-Organic (tier 3, ENM-35).

A shaped flight deck (a pointed bow, the angled landing deck overhanging its left, a cut stern), an
island on its right (the screen's), a hangar at its stern behind the runway with four reactors
under its back. The Phantom rolls out of the hangar's wide, low mouth onto the runway and takes
off from there, over the deck. The deck lies below the playfield's plane, where the Phantom flies;
the hangar and the island rise above it. Nothing is drawn under the deck: the camera looks down on
it. Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from game.config.enemy_broodmother import BROODMOTHER_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies.enemy_mesh import build_enemy_model
from game.view.enemies.enemy_shapes import SIDES, decal
from game.view.enemies.tier2_hatchery_model import turret
from game.view.enemies.veteran_small_models import docked_phantom
from render.geometry.organic import organ
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
F = ENEMY_LOOK.flesh
N = ENEMY_LOOK.neon
CFG = BROODMOTHER_CONFIG
WHITE = [1, 1, 1]  # type: list[float]
QUARTER = math.pi / 2

# ENM-BROODMOTHER-01: the flight deck's top (just under the Phantom's plane, Y = 0) and bottom.
DECK_TOP = -1
DECK_BOTTOM = -3.2
DECK_HEIGHTS = [DECK_BOTTOM, DECK_TOP - 0.4, DECK_TOP]  # type: list[float]
# The deck's flanks: a rounded sponson bulging out of each, the gun turret's on its left (the
# model's +X, the screen's left), the radar's on its right: its side (+1 the model's +X), where it
# starts and ends (Z), how far out the flank is there and how far the sponson bulges past it.
LEFT_SPONSON = [1, 12, -40, 23, 10]  # type: list[float]
RIGHT_SPONSON = [-1, -44, 26, 24, 7]  # type: list[float]
SPONSON_POINTS = 7


def sponson(spec: list[float]) -> list[list[float]]:
    """Return the points of a rounded sponson along the deck's edge, from its start to its end.

    `spec` is `[side, start z, end z, flank x, bulge]`; the ends lie on the flank.
    """
    side = spec[0]
    z0 = spec[1]
    z1 = spec[2]
    points: list[list[float]] = []
    for k in range(SPONSON_POINTS + 1):
        t = k / SPONSON_POINTS
        # A rounder bulge than a sine: it rises fast off the flank and is flat on top.
        out = math.pow(math.sin(math.pi * t), 0.6)
        points.append([side * (spec[3] + spec[4] * out), z0 + (z1 - z0) * t])
    return points


def deck_outline() -> list[list[float]]:
    """Return the deck's outline (`[x, z]`, nose +Z, clockwise seen from above).

    A pointed bow, flared flanks with a rounded sponson out of each, and a cut stern.
    """
    # Extended, not added or unpacked: Transcrypt's `+` on lists concatenates strings (ENG-155)
    # and it does not unpack `*` in a list.
    outline: list[list[float]] = [[-5, 64], [5, 64], [15, 56], [21, 40], [23, 20]]
    outline.extend(sponson(LEFT_SPONSON))
    outline.extend([[23, -46], [20, -58], [-18, -58], [-23, -46]])
    outline.extend(sponson(RIGHT_SPONSON))
    outline.extend([[-21, 40], [-15, 56]])
    return outline


DECK = deck_outline()
# Only the runway down the middle is flat: a raised shoulder runs along each flank, from the
# hangar's side out over its sponson, its inner side sloping down to the runway. Its heights
# (bottom, where its slope starts, top), how far in its top is from its edge, and the runway's
# half width between them.
SHOULDER_HEIGHTS = [DECK_TOP - 0.2, 1.2, 2.4]  # type: list[float]
SHOULDER_TOP = SHOULDER_HEIGHTS[2]
SHOULDER_SLOPE = 1.8
RUNWAY_HALF = 18.5
# How far forward each shoulder reaches (Z): the left one to the end of its sponson, the right one
# past the island.
LEFT_SHOULDER_END = 12
RIGHT_SHOULDER_END = 26
# The island on the right shoulder (the screen's right is the model's -X): its base, then its
# bridge.
ISLAND = [[-21, 22], [-26, 20], [-26.5, 14], [-26.5, 2], [-21, 2]]  # type: list[list[float]]
ISLAND_HEIGHTS = [SHOULDER_TOP - 0.2, SHOULDER_TOP + 2.4, SHOULDER_TOP + 3.6]  # type: list[float]
BRIDGE = [5, 2.6, 9]  # type: list[float]
BRIDGE_AT = [-24, SHOULDER_TOP + 3.3, 11]  # type: list[float]
# The gun turret on the left shoulder, half as big again as the Hatchery's: its scale, and the
# lift that stands its pedestal's top on the shoulder (the config's barrel height and length
# match them).
TURRET_SIZE = [1.5, SHOULDER_TOP + 0.9 * 1.5]  # type: list[float]
# The two little wings either side of the bow (right one, `[x, z]`), each with a reactor in a
# nacelle at its tip: the nacelle's X, its back (Z), its length and radius, and the reactor's.
BOW_WING = [[19, 48], [32, 40], [33, 35], [20, 36]]  # type: list[list[float]]
BOW_WING_HEIGHTS = [DECK_TOP - 1.8, DECK_TOP - 1.2, DECK_TOP - 0.7]  # type: list[float]
BOW_NACELLE = {"x": 31.5, "back": 33, "length": 8, "radius": 1.8}
BOW_REACTOR = 1.4
# ENM-BROODMOTHER-02: the hangar at the stern, behind the runway. Its roof (`[x, z]`) following
# the deck's edge, and the roof's heights; its side walls' inner X (the mouth's half width), front
# and back (Z); the mouth is open from the deck up to the roof's underside.
HANGAR_ROOF = [  # type: list[list[float]]
    [-23, -24],
    [23, -24],
    [24, -40],
    [21, -57],
    [-21.5, -57],
    [-23, -44],
]
ROOF_HEIGHTS = [3.6, 5.4, 6.6]  # type: list[float]
HANGAR_INNER = 19
HANGAR_WALL = 2
HANGAR_FRONT = -24
HANGAR_BACK = -55
# Where the Phantom waits inside (its centre's Z), all of it under the roof; it rolls out to where
# `CFG.port` puts it, just past the mouth, and takes off from there.
PHANTOM_INSIDE = -43
# The shoulders start under the hangar's roof, behind the sponsons.
SHOULDER_BACK = -40
# The reactors along the stern (`[x, radius]`), just under the deck, and their Z.
REACTORS = [[-12, 2.2], [-4, 2.4], [4, 2.4], [12, 2.2]]  # type: list[list[float]]
REACTOR_Y = -2.6
REACTOR_Z = -58.4


def rect(x0: float, x1: float, z0: float, z1: float) -> list[list[float]]:
    """Return a rectangle outline (`[x, z]`) between `x0`, `x1` and `z0`, `z1`."""
    return [[x0, z0], [x1, z0], [x1, z1], [x0, z1]]


def edge_light(a: list[float], b: list[float]) -> list[list[float]]:
    """Return a light just inside the deck's edge from `a` to `b` (the deck is to its right)."""
    dx = b[0] - a[0]
    dz = b[1] - a[1]
    length = math.sqrt(dx * dx + dz * dz)
    # The deck's outline turns clockwise seen from above: inside is to the right of a→b.
    nx = dz / length
    nz = -dx / length
    near = 0.6
    far = 1.2
    return [
        [a[0] + nx * near, a[1] + nz * near],
        [b[0] + nx * near, b[1] + nz * near],
        [b[0] + nx * far, b[1] + nz * far],
        [a[0] + nx * far, a[1] + nz * far],
    ]


def under_shoulder(at: list[float]) -> bool:
    """Whether a point of the deck's edge (`[x, z]`) is under a shoulder, its light hidden."""
    if at[0] > 0:
        return SHOULDER_BACK <= at[1] <= LEFT_SHOULDER_END
    return SHOULDER_BACK <= at[1] <= RIGHT_SHOULDER_END


def shoulder_outline(side: float) -> list[list[float]]:
    """Return the shoulder on side `side` (`[x, z]`): out along the deck's edge, in to the runway.

    From the hangar's side wall at its back, out over the sponson along the deck's edge to its
    front, then back along the runway's edge, stepping out round the hangar's mouth.
    """
    end = LEFT_SHOULDER_END if side > 0 else RIGHT_SHOULDER_END
    wall = HANGAR_INNER + HANGAR_WALL
    outline: list[list[float]] = [[side * wall, SHOULDER_BACK]]
    # The deck's edge on that side, from the shoulder's back to its front.
    edge = [q for q in DECK if q[0] * side > 0 and SHOULDER_BACK < q[1] < end]
    # The deck's outline runs down its left side and up its right one: put them back to front.
    if side > 0:
        edge.reverse()
    outline.append([side * deck_edge_x(side, SHOULDER_BACK), SHOULDER_BACK])
    outline.extend(edge)
    outline.append([side * deck_edge_x(side, end), end])
    outline.append([side * (RUNWAY_HALF + 2), end + 1])
    outline.append([side * RUNWAY_HALF, end - 6])
    outline.append([side * RUNWAY_HALF, HANGAR_FRONT + 4])
    outline.append([side * wall, HANGAR_FRONT - 2])
    return outline


def deck_edge_x(side: float, z: float) -> float:
    """Return how far out the deck's edge on side `side` is at `z` (positive)."""
    n = len(DECK)
    for i in range(n):
        a = DECK[i]
        b = DECK[(i + 1) % n]
        if a[0] * side <= 0 or b[0] * side <= 0:
            continue
        if min(a[1], b[1]) <= z <= max(a[1], b[1]) and a[1] != b[1]:
            t = (z - a[1]) / (b[1] - a[1])
            return abs(a[0] + (b[0] - a[0]) * t)
    return 0


def shoulders(p: Any) -> None:
    """Add the raised shoulders along the flanks, sloping down to the runway, lit along it."""
    for s in SIDES:
        outline = shoulder_outline(s)
        p.hull.bevel_slab(outline, SHOULDER_HEIGHTS, [0, SHOULDER_SLOPE], H.base, None, H.panel)
        # A light along the top of its inner slope, the runway's edge.
        end = LEFT_SHOULDER_END if s > 0 else RIGHT_SHOULDER_END
        x0 = min(s * (RUNWAY_HALF + SHOULDER_SLOPE + 0.2), s * (RUNWAY_HALF + SHOULDER_SLOPE + 0.8))
        x1 = max(s * (RUNWAY_HALF + SHOULDER_SLOPE + 0.2), s * (RUNWAY_HALF + SHOULDER_SLOPE + 0.8))
        light = rect(x0, x1, HANGAR_FRONT + 4, end - 8)
        decal(p.neon, light, SHOULDER_TOP + 0.03, N.broodmother)


def bow_wings(p: Any) -> None:
    """Add the two little wings either side of the bow, each with a reactor in a nacelle at its tip.

    Under the deck's edge, a light along each one's leading edge.
    """
    nacelle = BOW_NACELLE
    y = BOW_WING_HEIGHTS[1]
    for s in SIDES:
        wing = [[s * q[0], q[1]] for q in BOW_WING]
        p.hull.bevel_slab(wing, BOW_WING_HEIGHTS, [0.2, 0.6], H.base, None, H.panel)
        lead = [[s * 21, 46.4], [s * 31, 40.4], [s * 31, 39.4], [s * 21, 45.4]]
        decal(p.neon, lead, BOW_WING_HEIGHTS[2] + 0.03, N.broodmother)
        x = s * nacelle["x"]
        along = Placement([x, y, nacelle["back"]], 0, QUARTER)
        r = nacelle["radius"]
        p.hull.cylinder(r, nacelle["length"], 6, H.base, along, r * 0.6)
        p.reactor([x, y, nacelle["back"] - 0.2], BOW_REACTOR)


def deck_markings(p: Any) -> None:
    """Paint the deck's lights: round its edge, the runway ahead of the hangar, the landing line."""
    y = DECK_TOP + 0.03
    n = len(DECK)
    for i in range(n):
        a = DECK[i]
        b = DECK[(i + 1) % n]
        if not under_shoulder([(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]):
            decal(p.neon, edge_light(a, b), y, N.broodmother)
    # The runway the Phantom takes off along: a dashed centre line from the hangar to the bow.
    z = HANGAR_FRONT + 4
    while z + 4 < 60:
        decal(p.neon, rect(-0.35, 0.35, z, z + 4), y, N.broodmother)
        z += 8


def phantom_draw(at: list[float]) -> Any:
    """Return what the Phantom waiting at `at` in the hangar draws (factory)."""

    def draw(piece: Any) -> None:
        docked_phantom(piece, at)

    return draw


def hangar(p: Any) -> None:
    """ENM-BROODMOTHER-02: the hangar at the stern, a wide, low mouth open on the runway.

    Its roof, side and back walls, dark inside; the mouth's lintel glows as the next launch nears
    (ENM-BROODMOTHER-03), lights run along the roof. The Phantom inside rolls out of the mouth
    (`Enemy.tracks[0]`: 0 inside, 1 out on the runway, hidden while the hangar is empty).
    """
    hull = p.hull
    hull.bevel_slab(HANGAR_ROOF, ROOF_HEIGHTS, [0, 1.4], H.base, None, H.panel)
    under = ROOF_HEIGHTS[0]
    # The walls under the roof's edge, up from the deck: dark inside, so the mouth reads as a hole.
    for s in SIDES:
        x0 = min(s * HANGAR_INNER, s * (HANGAR_INNER + HANGAR_WALL))
        x1 = max(s * HANGAR_INNER, s * (HANGAR_INNER + HANGAR_WALL))
        hull.slab(rect(x0, x1, HANGAR_BACK, HANGAR_FRONT), [DECK_TOP, under], H.dark)
        # A light down the front of each wall, either side of the mouth.
        post = Placement([s * (HANGAR_INNER + HANGAR_WALL / 2), DECK_TOP, HANGAR_FRONT + 0.1])
        p.neon.box([0.8, under - DECK_TOP, 0.2], N.broodmother, post)
    back = rect(-HANGAR_INNER, HANGAR_INNER, HANGAR_BACK - HANGAR_WALL, HANGAR_BACK)
    hull.slab(back, [DECK_TOP, under], H.dark)
    # The dark ceiling and floor inside, so nothing lit shows through the mouth.
    inside = rect(-HANGAR_INNER, HANGAR_INNER, HANGAR_BACK, HANGAR_FRONT)
    hull.slab(inside, [under - 0.3, under], H.dark)
    hull.slab(inside, [DECK_TOP, DECK_TOP + 0.02], H.dark)
    # The mouth's lintel, under the roof's front edge: the charge light.
    lintel = Placement([0, under - 0.6, HANGAR_FRONT + 0.15])
    p.charge.box([2 * HANGAR_INNER, 0.6, 0.3], WHITE, lintel)
    # Lights along the roof.
    for s in SIDES:
        x0 = min(s * 9, s * 10)
        x1 = max(s * 9, s * 10)
        decal(p.neon, rect(x0, x1, -50, -28), ROOF_HEIGHTS[2] + 0.03, N.broodmother)
    # The Phantom, rolling out of the mouth onto the runway.
    out = -CFG.port[1]
    at: list[float] = [0, 0, PHANTOM_INSIDE]
    p.slide(at, [0, 1], out - PHANTOM_INSIDE, 0, phantom_draw(at), False, None, "track", 0)
    # Where it takes off from.
    p.muzzle([0, 0, out], "launch")


def island(p: Any) -> None:
    """Add the island on the right shoulder: its base, the bridge with lit windows, a mast."""
    hull = p.hull
    hull.bevel_slab(ISLAND, ISLAND_HEIGHTS, [0.3, 1], H.base, None, H.panel)
    hull.box(BRIDGE, H.panel, Placement(BRIDGE_AT), H.dark)
    front = BRIDGE_AT[2] + BRIDGE[2] / 2
    window = Placement([BRIDGE_AT[0], BRIDGE_AT[1] + 1.4, front + 0.05])
    p.neon.box([BRIDGE[0] - 1, 0.6, 0.2], N.broodmother, window)
    top = BRIDGE_AT[1] + BRIDGE[1]
    hull.cylinder(0.5, 3, 5, H.dark, Placement([BRIDGE_AT[0], top, BRIDGE_AT[2] - 2]))
    hull.box([4, 0.4, 1.2], H.panel, Placement([BRIDGE_AT[0], top + 2.6, BRIDGE_AT[2] - 2]))


# The radar on the right shoulder: where it stands (`[x, z]`), its flesh sensor dome's radius.
RADAR_AT = [-25, -22]  # type: list[float]
RADAR_DOME = 3.2


def radar(p: Any) -> None:
    """Add the radar on the right shoulder: a metal base, a flesh sensor dome, a lit ring, a mast.

    Its dome is the carrier's flesh.
    """
    x = RADAR_AT[0]
    z = RADAR_AT[1]
    y = SHOULDER_TOP
    p.hull.cylinder(RADAR_DOME + 0.8, 1, 8, H.base, Placement([x, y - 0.2, z]), RADAR_DOME + 0.4)
    organ(p.flesh, RADAR_DOME, 6, F.membrane, Placement([x, y + 0.6, z]), 0.8)
    p.neon.ring(RADAR_DOME + 0.5, 0.3, 8, N.broodmother, Placement([x, y + 0.7, z]))
    mast = Placement([x - 0.5, y + 0.6, z + RADAR_DOME + 2])
    p.hull.cylinder(0.4, 4.5, 5, H.dark, mast)
    p.hull.box([3, 0.4, 0.8], H.panel, Placement([x - 0.5, y + 4.6, z + RADAR_DOME + 2]))


def draw_broodmother(p: Any) -> None:
    """Draw the deck, the shoulders, the bow wings, the island, the radar, the hangar, the turret.

    And the reactors along the stern.

    Nothing under the deck: the camera looks down on it.
    """
    p.hull.bevel_slab(DECK, DECK_HEIGHTS, [0.6, 0.1], H.base, None, H.panel)
    deck_markings(p)
    shoulders(p)
    bow_wings(p)
    island(p)
    radar(p)
    hangar(p)
    for k in range(len(CFG.turrets.pivots)):
        turret(p, k, CFG.turrets, N.broodmother, TURRET_SIZE)
    for r in REACTORS:
        p.reactor([r[0], REACTOR_Y, REACTOR_Z], r[1])


def build_broodmother(scene: Any) -> Any:
    """ENM-BROODMOTHER-01: a flying aircraft carrier, its Phantom launched from a hangar.

    A flight deck (pointed bow, rounded sponsons, cut stern) with lights round its edge and a flat
    runway down the middle between two raised shoulders running forward from the hangar: a big gun
    turret on the left one, a radar and an island with a lit bridge on the right one. A hangar at
    the stern with a wide, low mouth on the runway, its lintel glowing as the next launch nears
    (ENM-BROODMOTHER-03); a little wing either side of the bow with a reactor at its tip, and four
    reactors along the stern.
    """
    return build_enemy_model("broodmother", scene, N.broodmother, draw_broodmother)

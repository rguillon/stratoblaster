# Copyright (c) 2026 Renaud Guillon
"""ENM-CARRIER-01: the Carrier, Cyber-Organic (ENM-35).

Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from game.config.enemies import ENEMY_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies.enemy_mesh import build_enemy_model
from game.view.enemies.enemy_shapes import LOBE_SECTION, SIDES, decal, flip_x, shift_x
from game.view.enemies.small_enemy_models import hornet_body
from render.geometry.organic import (
    SegmentedBody,
    curve,
    organ,
    segmented_body,
    tendril,
    vein,
)
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[float]
# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
F = ENEMY_LOOK.flesh
N = ENEMY_LOOK.neon
WHITE = [1, 1, 1]  # type: list[float]
QUARTER = math.pi / 2

# The right sponson along the hull's side, its outer wall sloping in by `SPONSON_SLOPE` (across,
# up) from its waist to its top (ENM-41). The landing bays are dug right through it.
CARRIER_SPONSON = [  # type: list[list[float]]
    [12, 18],
    [21, 15],
    [24, 11],
    [24, -19],
    [21, -23],
    [12, -25],
]
SPONSON_SLOPE = [5.5, 5]  # type: list[float]
SPONSON_HEIGHTS = [-3, 0, 5]  # type: list[float]
# ENM-CARRIER-02: a landing bay's half width along the side, the X its deck runs out to, and the
# height of its deck's top: a docked Hornet (belly 1.3 under its centre) rests on it.
BAY_HALF = 5
BAY_OUTER = 24.5
DECK_TOP = -1.4
# How far into the hull a Hornet waits before it moves up into its bay (`Enemy.launchers`).
BAY_RELOAD = 12

# ENM-CARRIER-01: the brood sac's ribs, arched over its back.
CARRIER_RIBS = [-10, 10]  # type: list[float]
# A larva glowing through the sac (8 triangles), and the neon band along each side of its spine.
LARVA = [[0, -0.6], [1.4, 0], [0, 0.8]]  # type: list[list[float]]
CARRIER_BAND = [[-0.4, -13], [0.4, -13], [0.4, 13], [-0.4, 13]]  # type: list[list[float]]
CARRIER_LARVAE = [[-5, 8.6, -9], [5, 8.6, -4], [-4, 9, 5], [4, 8.6, 10]]  # type: list[list[float]]

# A docked Hornet (`small_enemy_models.build_hornet`), its wings folded back along its body: the
# right wing (`[x, z]`, nose +Z), its single eye and its stinger.
FOLDED_WING = [[1.6, 2], [4.2, -8], [3, -10], [1.6, -4]]  # type: list[list[float]]
HORNET_EYE = [[0, -0.5], [0.9, 0], [0, 0.6]]  # type: list[list[float]]


def clip_z(outline: list[list[float]], z0: float, z1: float) -> list[list[float]]:
    """Return the part of a convex outline (`[x, z]`) between `z0` and `z1`."""
    ring = outline
    for bound, keep_above in [(z0, True), (z1, False)]:
        out: list[list[float]] = []
        n = len(ring)
        for i in range(n):
            a = ring[i]
            b = ring[(i + 1) % n]
            a_in = a[1] >= bound if keep_above else a[1] <= bound
            b_in = b[1] >= bound if keep_above else b[1] <= bound
            if a_in:
                out.append(a)
            if a_in != b_in:
                t = (bound - a[1]) / (b[1] - a[1])
                out.append([a[0] + (b[0] - a[0]) * t, bound])
        ring = out
    return ring


def sponson_pieces(bays: list[float]) -> list[list[list[float]]]:
    """Return the right sponson's outline cut into the pieces left between the bays (Z)."""
    zs = sorted(bays)
    # Built by `append`: Transcrypt's `+` on lists concatenates strings (ENG-155).
    lows = [-1000.0]
    highs: list[float] = []
    for z in zs:
        lows.append(z + BAY_HALF)
        highs.append(z - BAY_HALF)
    highs.append(1000.0)
    pieces = []
    for i in range(len(lows)):
        piece = clip_z(CARRIER_SPONSON, lows[i], highs[i])
        if len(piece) >= 3:
            pieces.append(piece)
    return pieces


def docked(s: float, centre: Vec3, local: Vec3) -> Vec3:
    """Return a point of a docked Hornet (`local`, nose +Z) in its bay, its nose out to side `s`."""
    return [centre[0] + s * local[2], local[1], centre[2] - s * local[0]]


def draw_docked_hornet(parts: Any, s: float, centre: Vec3) -> None:
    """Draw a Hornet waiting in its bay, nose out, its wings folded back along its body."""
    turn = s * QUARTER
    at = [centre[0], 0, centre[2]]
    hornet_body(parts.flesh, Placement(at, turn))
    stinger = docked(s, centre, [0, 0.4, 9.3])
    parts.hull.cylinder(0.9, 3.2, 4, H.panel, Placement(stinger, turn, QUARTER), 0)
    back = curve(docked(s, centre, [0, 2.3, -7]), docked(s, centre, [0, 2.4, 6]), [0, 0.6, 0], 3)
    vein(parts.vein, back, 0.6, N.hornet)
    for w in SIDES:
        wing = []
        for pt in FOLDED_WING:
            q = docked(s, centre, [w * pt[0], 0, pt[1]])
            wing.append([q[0], q[2]])
        parts.flesh.bevel_slab(wing, [1.4, 1.6, 1.8], [0.1, 0.1], F.membrane, None, F.sinew)
    parts.neon.lathe(HORNET_EYE, 5, N.hornet, Placement(docked(s, centre, [0, 1.4, 7.4])))


def bay(p: Any, s: float, z: float, index: int) -> None:
    """ENM-CARRIER-02: a landing bay dug through the sponson at `z`, open to the side and the sky.

    A dark deck, landing lights along its edges, a threshold glowing as a launch comes, and the
    Hornet docked in it: launcher `index` (`Enemy.launchers`), gone as it launches until the next
    one has moved up out of the hull into the bay.
    """
    deck = [
        [12, z - BAY_HALF],
        [BAY_OUTER, z - BAY_HALF],
        [BAY_OUTER, z + BAY_HALF],
        [12, z + BAY_HALF],
    ]
    deck = deck if s > 0 else flip_x(deck)
    p.hull.bevel_slab(deck, [-3, -2.2, DECK_TOP], [0.2, 0.2], H.dark, None, H.dark)
    for edge in [-1, 1]:
        zl = z + edge * (BAY_HALF - 0.8)
        light = [
            [15, zl - 0.3],
            [BAY_OUTER - 1, zl - 0.3],
            [BAY_OUTER - 1, zl + 0.3],
            [15, zl + 0.3],
        ]
        decal(p.neon, light if s > 0 else flip_x(light), DECK_TOP + 0.05, N.carrier)
    threshold = [
        [BAY_OUTER - 0.9, z - 3.6],
        [BAY_OUTER - 0.1, z - 3.6],
        [BAY_OUTER - 0.1, z + 3.6],
        [BAY_OUTER - 0.9, z + 3.6],
    ]
    decal(p.charge, threshold if s > 0 else flip_x(threshold), DECK_TOP + 0.05, WHITE)
    centre = [s * ENEMY_CONFIG.carrier.ports[0][0], 0, z]

    def draw(piece: Any) -> None:
        draw_docked_hornet(piece, s, centre)

    p.slide(centre, [-s, 0], BAY_RELOAD, index, draw, False, None, "rocket", 0)


def draw_carrier(p: Any) -> None:
    """Draw the parts of the Carrier: its brood sac, ribs, larvae, sponsons, bays and reactors."""
    flesh = p.flesh
    hull = p.hull
    neon = p.neon
    segmented_body(flesh, SegmentedBody(-28, 30, 3, 19, -4.5, 9), F.graphite, None, LOBE_SECTION)
    for z in CARRIER_RIBS:
        arch = curve([-16, 1, z], [16, 1, z], [0, 10, 0], 4)
        tendril(flesh, arch, [0.9, 0.9], 3, F.bone)
    for at in CARRIER_LARVAE:
        p.vein.lathe(LARVA, 4, N.carrier, Placement(at))
    ports = ENEMY_CONFIG.carrier.ports
    # Model Z is down the screen's Y: a bay `py` up the screen sits at Z = -py.
    bays = [-entry[1] for entry in ports]
    for s in SIDES:
        decal(neon, shift_x(CARRIER_BAND, s * 3.5), 9.1, N.carrier)
        for piece in sponson_pieces(bays):
            outline = piece if s > 0 else flip_x(piece)
            # A short piece between two bays is bevelled less, so its top does not fold over.
            zs = [pt[1] for pt in piece]
            inset = min(SPONSON_SLOPE[0], (max(zs) - min(zs)) / 2 - 1)
            hull.bevel_slab(outline, SPONSON_HEIGHTS, [1, inset], H.base, None, H.panel)
        for j in range(len(ports)):
            # The bays launch in turn, front first, the screen's right before its left (the
            # Carrier's `launch_order`); the model's +X is the screen's left.
            bay(p, s, bays[j], 2 * j + (0 if s < 0 else 1))
        # Its reactor, set in a flesh sac with a vein running into the body (ENM-CARRIER-03).
        nozzle = [s * 7, 0.5, -28.5]
        organ(flesh, 3.2, 4, F.slate, Placement([s * 7, 0.5, -28], 0, QUARTER), 0.9)
        p.reactor(nozzle, 2.4)
        vein(p.vein, curve([s * 7, 3, -25], [s * 5, 6, -17], [0, 1, 0], 2), 1, N.carrier)


def build_carrier(scene: Any) -> Any:
    """ENM-CARRIER-01: a brood sac that releases Hornets.

    A fat swollen sac of three segments under bone ribs, larvae glowing through its back, a metal
    sponson grafted on each flank with two landing bays dug through it, a Hornet docked in each,
    neon bands along its spine (yellow, ENM-CARRIER-04), its reactors set in flesh sacs.
    """
    return build_enemy_model("carrier", scene, N.carrier, draw_carrier)

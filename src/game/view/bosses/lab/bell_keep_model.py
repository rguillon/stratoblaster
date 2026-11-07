# Copyright (c) 2026 Renaud Guillon
"""MB-BELL-KEEP-01, MB-BELL-KEEP-02: the Bell Keep, the Lab's L-12 mini boss.

Logical pixels, nose +Z, Y up (towards the camera). A floating castle seen from above: a chunk of
rock tapering to a point beneath, a ledge jutting out in front of its gates, gold seams of ore in it
and chains hanging off its rim; on it a round curtain wall with its merlons, a gatehouse across its
front, a drum tower either side of the gates and a bell tower at its back (`bell_keep_parts`), a
round donjon in its courtyard. Its bells and portcullises move on a rig of their own
(`bell_keep_rig`). Architecture, not a creature (the Lab's third round, user request 2026-11-06).
"""

import math

from game.config.bosses.lab.bell_keep import (
    BELL_KEEP,
    DONJON_AT,
    DONJON_RADIUS,
    DONJON_TOP,
    FLOOR,
    GATE,
    GATE_BACK,
    GATE_FRONT,
    GATE_HALF,
    GATE_OPEN,
    GATE_TOP,
    KEEP_GUN_AT,
    MERLON,
    ROCK_TOP,
    WALL_IN,
    WALL_OUT,
    WALL_TOP,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.bell_keep_parts import (
    COURSE,
    STONE,
    N,
    belfry,
    keep_armour,
    merlon_ring,
    pt,
    tower,
)
from game.view.bosses.lab.bell_keep_rig import build_keep_rig, rig_triangles
from game.view.bosses.world_1_organic_kit import M
from render.geometry.rocks import rough_chunk
from render.geometry.rough import Roughness, rough_lathe
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


ROCK = [0.07, 0.065, 0.065]
# The rock's profile, `[radius, height]` from its point beneath up to its rim and its top.
ROCK_PROFILE = [  # type: list[list[float]]
    [0, -30],
    [11, -24],
    [23, -15],
    [33, -7],
    [41, -1.5],
    [46, 2.5],
    [44.5, ROCK_TOP],
    [0, ROCK_TOP],
]
# The ledge in front of the gates: its centre, size and foot.
LEDGE_AT = [0, -40]
LEDGE = [38.0, 11.0, 22.0]
# Its crystal clusters: `[degrees round, out, height]`, on its top round the wall and under it.
CRYSTALS = [  # type: list[list[float]]
    [-10, 34, ROCK_TOP],
    [35, 38, ROCK_TOP],
    [100, 33, ROCK_TOP],
    [150, 37, ROCK_TOP],
    [215, 35, ROCK_TOP],
    [-60, 30, -9],
    [80, 28, -11],
    [190, 30, -9],
]
# Where chains hang off the rim (degrees round, config X right, Y up) and how many links.
CHAINS = [-20, 50, 130, 200]
LINKS = 5
# The curtain wall leaves out the gatehouse's sector, `GAP` degrees either side of the front.
GAP = 44
SEGMENTS = 23


def _draw_rock(p: Any) -> None:
    """Draw the floating rock (MB-BELL-KEEP-01): rough stone to a point, a ledge, gold crystals.

    Clusters of glowing crystals jut from its top round the wall and from its flanks beneath (what
    keeps it aloft); chains hang off its rim.
    """
    rough_lathe(p.flesh, ROCK_PROFILE, 14, ROCK, Roughness(0.16, 0.14, 0.35, 12), Placement())
    ledge = boss_point(LEDGE_AT[0], LEDGE_AT[1], ROCK_TOP - LEDGE[1] + 0.6)
    rough_chunk(p.flesh, LEDGE, 7, ROCK, Roughness(0.18, 0.12, 0.3, 7), Placement(ledge))
    for c in CRYSTALS:
        _crystals(p, c[0] * math.pi / 180, c[1], c[2])
    for a_deg in CHAINS:
        _chain(p, a_deg * math.pi / 180)


def _crystals(p: Any, a: float, r: float, h: float) -> None:
    """Add a cluster of three gold crystals at `a` (radians round), `r` out, `h` high."""
    for k in range(3):
        da = (k - 1) * 0.09
        c = math.cos(a + da)
        s = math.sin(a + da)
        at = boss_point((r + k % 2) * c, (r + k % 2) * s, h - 0.4)
        yaw = math.atan2(-c, -s)
        lean = 0.35 + 0.25 * k if h > 0 else 2.4 - 0.2 * k
        p.neon.cylinder(0.9 - 0.15 * k, 4.2 - 0.9 * k, 4, N, Placement(at, yaw, lean), 0)


def _chain(p: Any, a: float) -> None:
    """Add a chain hanging off the rim at `a` (radians round): links out and down, a weight."""
    c = math.cos(a)
    s = math.sin(a)
    yaw = math.atan2(-c, -s)
    for k in range(LINKS):
        r = 43 + k * 1.3
        h = 1 - k * 2.4
        q = boss_point(r * c, r * s, h - 2.2)
        size = [0.5, 2.6, 1.3] if k % 2 == 0 else [1.3, 2.6, 0.5]
        p.hull.box(size, M.base, Placement(q, yaw))
    end = 43 + (LINKS - 1) * 1.3
    q = boss_point(end * c, end * s, 1 - (LINKS - 1) * 2.4 - 2.2 - 2.4)
    p.hull.cylinder(1.6, 2.6, 6, M.panel, Placement(q), 0.9)
    p.neon.ring(1.65, 0.3, 6, N, Placement([q[0], q[1] + 1.2, q[2]]))


def _wall_point(r: float, deg: float) -> list[float]:
    a = deg * math.pi / 180
    return pt(r * math.cos(a), r * math.sin(a))


def _draw_curtain(p: Any) -> None:
    """Draw the curtain wall (MB-BELL-KEEP-02): a stone ring, merlons, lit slits, its walk.

    It leaves out the gatehouse's sector at its front.
    """
    p.flesh.slab(
        [_wall_point(WALL_IN + 0.4, k * 360 / 20) for k in range(20)], [ROCK_TOP, FLOOR], COURSE
    )
    step = (360 - 2 * GAP) / SEGMENTS
    for k in range(SEGMENTS):
        a0 = -90 + GAP + k * step
        a1 = a0 + step
        outline = [
            _wall_point(WALL_OUT, a0),
            _wall_point(WALL_OUT, a1),
            _wall_point(WALL_IN, a1),
            _wall_point(WALL_IN, a0),
        ]
        p.flesh.slab(outline, [ROCK_TOP, WALL_TOP], STONE)
        mid = (a0 + a1) / 2 * math.pi / 180
        rm = WALL_OUT - 1.6
        at = boss_point(rm * math.cos(mid), rm * math.sin(mid), WALL_TOP)
        yaw = math.atan2(-math.cos(mid), -math.sin(mid))
        p.flesh.box([2.8, MERLON, 2.2], STONE, Placement(at, yaw))
        if k % 2 == 0:
            slit = boss_point(
                (WALL_OUT + 0.05) * math.cos(mid), (WALL_OUT + 0.05) * math.sin(mid), 9
            )
            p.neon.box([0.6, 3.2, 0.6], N, Placement(slit, yaw))
    # A darker course round its foot, and its lit walk along the inner edge.
    p.flesh.ring(WALL_OUT + 0.05, 1.4, 24, COURSE, Placement([0, ROCK_TOP, 0]))


def _draw_gatehouse(p: Any) -> None:
    """Draw the gatehouse (MB-BELL-KEEP-05): piers either side of two gates, a lintel, merlons.

    Its gates' dark passages, lit arches, and the winch housings its drawbridges' chains run from.
    """
    depth = GATE_BACK - GATE_FRONT
    zc = -(GATE_FRONT + GATE_BACK) / 2
    piers = [[-GATE[0], GATE[0]], [GATE[1], GATE_HALF], [-GATE_HALF, -GATE[1]]]
    for xs in piers:
        q = [-(xs[0] + xs[1]) / 2, ROCK_TOP, zc]
        p.flesh.box([xs[1] - xs[0], GATE_TOP - ROCK_TOP, depth], STONE, Placement(q))
    p.flesh.box([2 * GATE_HALF, GATE_TOP - GATE_OPEN, depth], STONE, Placement([0, GATE_OPEN, zc]))
    p.flesh.box([2 * GATE_HALF + 0.4, 1.2, depth + 0.4], COURSE, Placement([0, GATE_OPEN, zc]))
    for k in range(7):
        x = -GATE_HALF + 1.5 + k * (2 * GATE_HALF - 3) / 6
        p.flesh.box([2.6, MERLON, 2.2], STONE, Placement([x, GATE_TOP, -GATE_FRONT - 1.2]))
    for s in [-1, 1]:
        mid = s * (GATE[0] + GATE[1]) / 2
        width = GATE[1] - GATE[0]
        # The passage's floor, dark, and a lit arch round its mouth.
        p.bare.box([width, 0.3, depth], M.dark, Placement([-mid, FLOOR - 0.2, zc]))
        p.neon.box(
            [width + 0.6, 0.5, 0.5], N, Placement([-mid, GATE_OPEN - 0.6, -GATE_FRONT + 0.1])
        )
        # A winch housing over each gate, its chain's slot lit.
        w = boss_point(mid, GATE_FRONT + 2.5, GATE_TOP)
        p.hull.box([width - 2, 2.2, 3.4], M.panel, Placement(w), M.base)
        p.neon.box([width - 3, 0.3, 0.5], N, Placement([w[0], GATE_TOP + 2.2, w[2] - 1.2]))


def _draw_donjon(p: Any) -> None:
    """Draw the donjon (MB-BELL-KEEP-02, the core): a round stone keep, corbelled and crenellated.

    Lit windows round it, a lit band under its corbels, the seat of its turret on its roof's front.
    """
    at = boss_point(DONJON_AT[0], DONJON_AT[1], 0)
    r = DONJON_RADIUS
    p.flesh.lathe(
        [
            [r + 0.8, FLOOR],
            [r, FLOOR + 2],
            [r, DONJON_TOP - 4],
            [r + 1.4, DONJON_TOP - 2.4],
            [r + 1.4, DONJON_TOP],
        ],
        12,
        STONE,
        Placement([at[0], 0, at[2]]),
    )
    p.flesh.ring(r + 0.05, 1.2, 12, COURSE, Placement([at[0], 11, at[2]]))
    p.neon.ring(r + 1.45, 0.35, 12, N, Placement([at[0], DONJON_TOP - 1.6, at[2]]))
    merlon_ring(p, [at[0], 0, at[2]], r + 0.6, DONJON_TOP, 12, 2.6)
    p.hull.cylinder(r, 0.4, 12, M.base, Placement([at[0], DONJON_TOP - 0.3, at[2]]))
    for k in range(6):
        a = (k + 0.5) * math.pi / 3
        q = [at[0] + math.cos(a) * (r + 0.05), 15, at[2] + math.sin(a) * (r + 0.05)]
        p.charge.box([1, 2.4, 1], N, Placement(q, -a))
    gun = boss_point(KEEP_GUN_AT[0], KEEP_GUN_AT[1], 0)
    p.hull.cylinder(5.6, 0.8, 10, M.panel, Placement([gun[0], DONJON_TOP - 0.2, gun[2]]))
    p.neon.ring(5.7, 0.3, 10, N, Placement([gun[0], DONJON_TOP + 0.4, gun[2]]))


def _draw_court(p: Any) -> None:
    """Draw the courtyard's flagstones and the cannons' lit tracks (MB-BELL-KEEP-10)."""
    p.flesh.slab(
        [_wall_point(WALL_IN + 0.2, k * 360 / 20) for k in range(20)],
        [FLOOR - 0.6, FLOOR],
        COURSE,
    )
    for s in [-1, 1]:
        x = s * (GATE[0] + GATE[1]) / 2
        for dx in [-3, 3]:
            a = boss_point(x + dx, GATE_BACK, FLOOR)
            p.bare.box([0.5, 0.2, 9], M.base, Placement([a[0], FLOOR, a[2] - 4.5]))
        p.neon.box([0.4, 0.2, 8], N, Placement([-x, FLOOR + 0.05, -GATE_BACK - 4.5]))


def build_bell_keep(scene: Any) -> Any:
    """MB-BELL-KEEP-01, MB-BELL-KEEP-02: the Bell Keep.

    A castle on a floating rock, warm gold light lines (shown yellow) in its windows and seams.
    """

    def core(p: Any) -> None:
        _draw_rock(p)
        _draw_court(p)
        _draw_curtain(p)
        _draw_gatehouse(p)
        _draw_donjon(p)

    return build_boss_model(
        BELL_KEEP,
        scene,
        N,
        {
            "core": core,
            "parts": {"tower-left": tower, "tower-right": tower, "belfry": belfry},
            "armour": keep_armour(),
            "rig": {"build": build_keep_rig, "triangles": rig_triangles},
        },
    )

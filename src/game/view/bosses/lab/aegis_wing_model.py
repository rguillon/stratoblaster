# Copyright (c) 2026 Renaud Guillon
"""MB-AEGIS-WING-01 to MB-AEGIS-WING-05: the Aegis Wing, the Lab's L-17 mini boss.

Logical pixels, nose +Z, Y up (towards the camera). A giant flying wing seen from above: a thin
bevelled wing, its leading edge swept straight back from a blunt nose, its trailing edge a
sawtooth, lit along both; a low blended hump down its middle with the cockpit's visor; its engines
buried in the hump, a long fairing over each from its intake (a part) to its exhaust slot in a
notch of the trailing edge. Its outer wings' skin panels (an armour region flipped over by its rig)
are in `aegis_wing_tiles`. A machine, not a creature: the Lab's fourth round builds gigantic
airplanes (user request, 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.aegis_wing import (
    AEGIS_WING,
    DORSAL_AT,
    DORSAL_H,
    EXHAUST_AT,
    HUMP,
    INTAKE_AT,
    INTAKE_GUN_AT,
    INTAKE_GUN_H,
    NOSE_GUN_AT,
    NOSE_GUN_H,
    ROTOR_AT,
    ROTOR_H,
    WING,
    WING_LOW,
    WING_TOP,
    WING_WAIST,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.aegis_wing_tiles import (
    build_tile_rig,
    draw_skin,
    draw_skin_frame,
    tile_triangles,
)
from game.view.bosses.world_1_organic_kit import F, M, polygon
from render.geometry.solids import LoftOptions, Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["aegis-wing"]
QUARTER = math.pi / 2
# The hump's section: a low lens (counter-clockwise seen from the nose), `[u, v]` across its width
# and up its height.
LENS = [
    [1, 0],
    [0.8, 0.42],
    [0.45, 0.82],
    [0, 1],
    [-0.45, 0.82],
    [-0.8, 0.42],
    [-1, 0],
]
# The engine fairings over the buried engines: from the intake to the exhaust (`[y0, y1]`), half
# width, and the rounded section's top.
FAIRING = [INTAKE_AT[1] - 4, EXHAUST_AT[1] - 3]
FAIRING_HALF = 4.6
ARCH = [[1, 0], [0.7, 0.7], [0, 1], [-0.7, 0.7], [-1, 0]]


def _whole(right: list[list[float]]) -> list[list[Any]]:
    """Return a whole outline (model XZ) from its right half (playfield, from the centre line)."""
    points = [[-q[0], -q[1]] for q in right]
    n = len(right)
    for k in range(n):
        q = right[n - 1 - k]
        if q[0] != 0:
            points.append([q[0], -q[1]])
    return points


def strip(
    layer: Any, a: list[float], b: list[float], h: float, size: list[float], color: Any
) -> None:
    """Add a box from playfield `a` to `b` at height `h`, `size` `[width, thickness]` across it."""
    pa = boss_point(a[0], a[1], h)
    pb = boss_point(b[0], b[1], h)
    dx = pb[0] - pa[0]
    dz = pb[2] - pa[2]
    length = math.hypot(dx, dz)
    yaw = math.atan2(dx, dz)
    mid = [(pa[0] + pb[0]) / 2, h, (pa[2] + pb[2]) / 2]
    layer.box([size[0], size[1], length], color, Placement(mid, yaw))


def _wing(p: Any) -> None:
    """Draw the wing (MB-AEGIS-WING-02): a thin bevelled plank in its outline, lit along its edges.

    Its leading edge lit from the nose to the tips, its sawtooth trailing edge lit along each tooth,
    a few dark panel seams on the inner wing, and a lit nav light at each tip.
    """
    p.flesh.bevel_slab(
        _whole(WING), [WING_LOW, WING_WAIST, WING_TOP], [2.2, 0.6], F.graphite, None, F.slate
    )
    n = len(WING)
    for side in [-1, 1]:
        lead = [[side * WING[1][0], WING[1][1]], [side * WING[2][0], WING[2][1]]]
        strip(p.neon, lead[0], lead[1], WING_WAIST - 0.3, [0.7, 0.9], N)
        for k in range(4, n - 1):
            a = [side * WING[k][0], WING[k][1] - 0.6]
            b = [side * WING[k + 1][0], WING[k + 1][1] - 0.6]
            strip(p.neon, a, b, WING_TOP - 0.2, [0.4, 0.3], N)
        tip = boss_point(side * 60.5, 5, WING_LOW + 1)
        p.neon.box([1.2, 2.6, 2.4], N, Placement(tip))
        # Panel seams on the inner wing, behind the leading edge.
        for x in [16, 24]:
            strip(p.bare, [side * x, -26 + x * 0.7], [side * x, 14], WING_TOP, [0.35, 0.15], M.dark)
    # The nose: a blunt cap ahead of the hump, lit underneath.
    p.neon.box([6, 0.6, 1], N, Placement(boss_point(0, WING[0][1] + 0.6, WING_LOW + 0.4)))


def _hump(p: Any) -> None:
    """Draw the blended hump down the middle (MB-AEGIS-WING-02) and the cockpit's visor.

    A low lens-shaped loft from the nose to the tail, a dark visor across its front with a lit rim,
    a lit spine seam, the dorsal turret's seat and the tail rotor's well.
    """
    stations = [[-s[0], s[1], WING_TOP - 1, s[2]] for s in reversed(HUMP)]
    p.flesh.loft(LENS, stations, F.slate, None, LoftOptions(False, None))
    visor: list[list[float]] = [[-5, -29], [5, -29], [6.5, -24], [-6.5, -24]]
    p.bare.slab([[-q[0], -q[1]] for q in visor], [14.6, 15.4], M.dark)
    p.neon.box([12, 0.4, 0.5], N, Placement(boss_point(0, -23.8, 15)))
    strip(p.neon, [0, -9], [0, 2], 16, [0.5, 0.2], N)
    seat = boss_point(DORSAL_AT[0], DORSAL_AT[1], DORSAL_H - 1.4)
    p.hull.cylinder(4.8, 1.4, 10, M.base, Placement(seat))
    p.neon.ring(4.85, 0.35, 10, N, Placement([seat[0], DORSAL_H - 0.7, seat[2]]))
    well = boss_point(ROTOR_AT[0], ROTOR_AT[1], ROTOR_H - 1.6)
    p.hull.cylinder(5.6, 1.6, 8, M.base, Placement(well, math.pi / 8))
    nose = boss_point(NOSE_GUN_AT[0], NOSE_GUN_AT[1], NOSE_GUN_H - 2)
    p.hull.cylinder(4.4, 2, 10, M.base, Placement(nose), 4)


def _engines(p: Any) -> None:
    """Draw the buried engines (MB-AEGIS-WING-02): a fairing over each along the hump's flank.

    A rounded loft from behind its intake to its exhaust, the intake gun's seat on it (its top),
    a dark intake well ahead (the intake, a part, sits in it), and the exhaust: a flat dark slot in
    the trailing edge's notch, lit inside, a scorched deck behind it.
    """
    for side in [-1, 1]:
        x = side * INTAKE_AT[0]
        stations = [
            [-FAIRING[1], FAIRING_HALF * 0.7, WING_TOP - 1, INTAKE_GUN_H - 2.6],
            [-(INTAKE_GUN_AT[1] + 4), FAIRING_HALF, WING_TOP - 1, INTAKE_GUN_H],
            [-(INTAKE_GUN_AT[1] - 4), FAIRING_HALF, WING_TOP - 1, INTAKE_GUN_H],
            [-FAIRING[0], FAIRING_HALF * 0.9, WING_TOP - 1, INTAKE_GUN_H - 1.2],
        ]
        p.hull.loft(ARCH, stations, M.panel, Placement([-x, 0, 0]), LoftOptions(False, None))
        well = boss_point(x, INTAKE_AT[1] - 5, 0)
        p.bare.box([7, 1, 4], M.dark, Placement([well[0], INTAKE_GUN_H - 2.2, well[2]]))
        slot = boss_point(side * EXHAUST_AT[0], EXHAUST_AT[1] - 2.6, WING_TOP - 1.6)
        p.bare.box([7.5, 1.8, 3.2], M.dark, Placement(slot))
        p.neon.box([6.6, 0.5, 0.5], N, Placement([slot[0], WING_TOP - 1, slot[2] - 1.6]))


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the tail rotor (BOSS-58): an octagonal cap, a lit seam round it."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.bevel_slab(
        polygon(8, 5.6),
        [ROTOR_H - 0.4, ROTOR_H + 0.2, ROTOR_H + 1.2],
        [0, 0.8],
        M.panel,
        Placement(at),
    )
    p.neon.ring(5.2, 0.25, 8, N, Placement([at[0], ROTOR_H + 0.6, at[2]], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.ring(5.6, 1.0, 12, M.base, Placement([at[0], ROTOR_H - 0.6, at[2]]))
    p.neon.ring(5.6, 0.3, 12, N, Placement([at[0], ROTOR_H + 0.2, at[2]]))


def _intake(p: Any, at: Vec3) -> None:
    """Add an intake gun (MB-AEGIS-WING-03): the raised intake lip over its engine, its gun behind.

    A wedge-shaped cowl rising from the hump to the intake's dark mouth, lit along its lip, and the
    gun's armoured ring on the fairing behind it.
    """
    x = at[0]
    z = boss_point(0, INTAKE_AT[1], 0)[2]
    cowl = [[x - 4.2, z + 5], [x + 4.2, z + 5], [x + 3.4, z - 6], [x - 3.4, z - 6]]
    p.hull.bevel_slab(cowl, [WING_TOP, INTAKE_GUN_H - 1.6, INTAKE_GUN_H - 0.4], [0, 0.6], M.panel)
    p.bare.box([6.4, 2.4, 1.2], M.dark, Placement([x, INTAKE_GUN_H - 3.6, z + 4.6]))
    p.neon.box([7.2, 0.4, 0.6], N, Placement([x, INTAKE_GUN_H - 1.0, z + 5.1]))
    gun = boss_point(0, INTAKE_GUN_AT[1], 0)
    p.hull.cylinder(4.2, 0.8, 8, M.base, Placement([x, INTAKE_GUN_H - 0.8, gun[2]], math.pi / 8))
    p.neon.ring(4.25, 0.3, 8, N, Placement([x, INTAKE_GUN_H - 0.5, gun[2]], math.pi / 8))


def _nose_gun(p: Any, at: Vec3) -> None:
    """Add the nose gun (MB-AEGIS-WING-03): an armoured drum on the nose, sensor blisters by it.

    Lit round its rim, a lit chevron on the nose ahead, two dark sensor blisters either side.
    """
    x = at[0]
    z = at[2]
    p.hull.cylinder(4.8, 1.2, 10, M.panel, Placement([x, NOSE_GUN_H - 1.2, z]), 4.2)
    p.neon.ring(4.85, 0.35, 10, N, Placement([x, NOSE_GUN_H - 0.9, z]))
    for dx in [-1, 1]:
        p.hull.cylinder(1.8, 1.6, 6, M.base, Placement([x + dx * 6.4, 9.6, z - 1]), 1)
        p.neon.box([0.6, 0.3, 0.6], N, Placement([x + dx * 6.4, 11.2, z - 1]))
        strip(p.neon, [dx * 1.2, -42.4], [dx * 3.2, -40.6], 10.2, [0.5, 0.3], N)


def build_aegis_wing(scene: Any) -> Any:
    """MB-AEGIS-WING-01, MB-AEGIS-WING-04: the Aegis Wing.

    A tailless flying wing 3.5 L across, a sawtooth trailing edge, a blended hump with its buried
    engines; periwinkle light lines (shown green).
    """

    def core(p: Any) -> None:
        _wing(p)
        _hump(p)
        _engines(p)

    return build_boss_model(
        AEGIS_WING,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "intake-left": _intake,
                "intake-right": _intake,
                "nose-gun": _nose_gun,
            },
            # MB-AEGIS-WING-10: its skin's rows flip over in a wave and the wells open like petals.
            "rig": {"build": build_tile_rig, "triangles": tile_triangles},
            "armour": {
                "skin": {"whole": draw_skin, "pieces": [], "frame": draw_skin_frame},
                "rotor-hatch": {"whole": _draw_hatch, "frame": _draw_hatch_frame},
            },
        },
    )

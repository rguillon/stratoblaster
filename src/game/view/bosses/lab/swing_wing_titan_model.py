# Copyright (c) 2026 Renaud Guillon
"""FB-SWING-WING-TITAN-01 to -05: the Swing-Wing Titan, the Lab's L-18 final boss.

Model space: logical pixels, nose +Z (down the screen), Y up towards the camera. A gigantic
variable-geometry bomber: a long blended fuselage with its cockpit glass near the nose, big wing
gloves either side of it (a weapons bay under doors in each), its swing wings spread wide, four
engines in two pods under its rear, and a cruciform tail: a tall fin, its tailplanes set across it
half way up. The wings are moving pieces (they sweep back at its first transformation); the bay
doors, the feed tubes, the dorsal fairing's flaps and the tail's rotor (the fin's skins, the
tailplanes, the hub) are its rig (`swing_wing_titan_rig`). A machine, not a creature: the Lab's
fourth round builds gigantic airplanes (user request, 2026-11-06). Its gun mounts are drawn by
`build_boss_model` (BOSS-58).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.swing_wing_titan import (
    BARBETTE_AT,
    BARBETTE_H,
    BAY,
    BAY_FLOOR,
    ENGINE_H,
    ENGINE_R,
    ENGINE_X,
    ENGINES,
    FAIRING,
    FAIRING_HALF,
    FIN,
    FUSELAGE,
    GLOVE,
    GLOVE_Y,
    NOSE_AT,
    NOSE_H,
    ORB_POD,
    PIVOT,
    RACK_POD,
    ROTOR_AT,
    ROTOR_H,
    SPINE_AT,
    SPINE_H,
    SWING_WING_TITAN,
    WING,
    WING_GUN_AT,
    WING_GUN_H,
    WING_Y,
    fuselage_at,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.swing_wing_titan_rig import STUB_TOP, build_titan_rig, titan_triangles
from game.view.bosses.world_1_organic_kit import M, polygon
from game.view.enemies.enemy_shapes import FIGHTER_SECTION, canopy_paint
from render.geometry.solids import LoftOptions, Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["swing-wing-titan"]
QUARTER = math.pi / 2
SIDES = [-1, 1]
GLASS = [0.05, 0.065, 0.08]
SOOT = [0.035, 0.035, 0.042]


def flat(x: float, y: float) -> list[Any]:
    """Return the playfield point `(x, y)` as a model outline point `[x, z]`."""
    return [-x, -y]


def sided(outline: list[Any], s: float) -> list[Any]:
    """Return a right-hand playfield outline as a model outline on side `s` (1: right)."""
    return [flat(s * q[0], q[1]) for q in outline]


def strip(builder: Any, a: list[Any], b: list[Any], width: float, heights: list[float]) -> None:
    """Add a light strip `width` wide from playfield point `a` to `b` between `heights`."""
    ax = -a[0]
    az = -a[1]
    bx = -b[0]
    bz = -b[1]
    length = math.hypot(bx - ax, bz - az) or 1
    nx = (az - bz) / length * width / 2
    nz = (bx - ax) / length * width / 2
    outline = [[ax + nx, az + nz], [bx + nx, bz + nz], [bx - nx, bz - nz], [ax - nx, az - nz]]
    builder.slab(outline, heights, N)


def _fuselage(p: Any) -> None:
    """Draw the fuselage (FB-SWING-WING-TITAN-02): a long blended body, its cockpit glass.

    Its stations from its nose to its tail, the glass painted on its back behind the nose; light
    lines down its spine and shoulders; the seats of the nose radome, the spine turret and the
    spine rotor; a refuelling boom's socket and dark panel lines.
    """
    stations = [[-q[0], q[1], q[2], q[3]] for q in reversed(FUSELAGE)]
    p.hull.loft(
        FIGHTER_SECTION, stations, M.base, None, LoftOptions(False, canopy_paint([7], GLASS))
    )
    for s in SIDES:
        strip(
            p.neon,
            [s * 3.4, -64],
            [s * 3.4, 40],
            0.6,
            [fuselage_at(0, 3) - 1.1, fuselage_at(0, 3) - 0.6],
        )
        strip(p.neon, [s * 9.2, -60], [s * 9.6, 30], 0.5, [16.4, 17])
    for y in [-58, -14, 36]:
        p.bare.box([14, 0.4, 0.6], SOOT, Placement(boss_point(0, y, fuselage_at(y, 3) - 0.1)))
    nose = boss_point(NOSE_AT[0], NOSE_AT[1], NOSE_H - 2.4)
    p.hull.cylinder(3.6, 2.3, 8, M.panel, Placement(nose, math.pi / 8))
    spine = boss_point(SPINE_AT[0], SPINE_AT[1], SPINE_H - 1.2)
    p.hull.cylinder(6.4, 1.2, 10, M.panel, Placement(spine, math.pi / 10))
    p.neon.ring(6.5, 0.4, 10, N, Placement([spine[0], SPINE_H - 0.8, spine[2]], math.pi / 10))
    rotor = boss_point(ROTOR_AT[0], ROTOR_AT[1], ROTOR_H - 1.2)
    p.hull.cylinder(7, 1.2, 8, M.panel, Placement(rotor, math.pi / 8))
    # The cockpit's frame bars and a lamp on its nose.
    for y in [-92, -88]:
        p.bare.box([7, 0.5, 0.6], SOOT, Placement(boss_point(0, y, fuselage_at(y, 3) - 0.2)))
    p.neon.box([1.2, 1, 2], N, Placement(boss_point(0, FUSELAGE[0][0] + 1.5, 13)))


def _glove(p: Any, s: float) -> None:
    """Draw a wing glove (FB-SWING-WING-TITAN-02) round its bay (its doors are the rig's).

    A solid blended body up to the bay's floor, its top skin fore, outboard and aft of the bay,
    a lit leading edge and the swing wing's pivot drum.
    """
    p.hull.bevel_slab(
        sided(GLOVE, s), [GLOVE_Y[0], BAY_FLOOR - 0.6, BAY_FLOOR], [1.2, 0], M.base, None, M.dark
    )
    out_fore = 17 + 17 * (18 / 44)
    out_aft = 34 + 2 * (2 / 28)
    fore: list[Any] = [[10, -78], [17, -62], [out_fore, -44], [10.4, -44]]
    rim: list[Any] = [[BAY[1][0], -44], [out_fore, -44], [out_aft, -16], [BAY[2][0], -16]]
    aft: list[Any] = [[10.7, -16], [out_aft, -16], [36, 10], [11, 12]]
    for piece in [fore, rim, aft]:
        p.hull.bevel_slab(
            sided(piece, s),
            [BAY_FLOOR - 0.2, GLOVE_Y[1], GLOVE_Y[2]],
            [0, 0.5],
            M.panel,
            None,
            M.base,
        )
    strip(p.neon, [s * 10.6, -76], [s * 16.8, -61.5], 0.7, [GLOVE_Y[2] - 0.6, GLOVE_Y[2] + 0.1])
    strip(p.neon, [s * 17.2, -60], [s * 33.6, -18.5], 0.7, [GLOVE_Y[2] - 0.6, GLOVE_Y[2] + 0.1])
    pivot = boss_point(s * PIVOT[0], PIVOT[1], GLOVE_Y[2] - 0.2)
    p.hull.cylinder(4.2, 1.2, 10, M.panel, Placement(pivot, math.pi / 10))
    p.neon.ring(3.4, 0.4, 10, N, Placement([pivot[0], GLOVE_Y[2] + 0.9, pivot[2]], math.pi / 10))
    # The vents on its aft skin.
    for k in range(3):
        y = -6 + k * 5
        p.bare.box([7, 0.3, 1.4], SOOT, Placement(boss_point(s * 22, y, GLOVE_Y[2])))


def _engines(p: Any, s: float) -> None:
    """Draw an engine pod under the rear (FB-SWING-WING-TITAN-02): two engines and a barbette.

    Two nacelles side by side along Z, joined by a fairing, dark intakes at their fronts, glowing
    nozzles at their backs; the barbette's pylon on the pod's tail (its stump stands on it).
    """
    length = ENGINES[1] - ENGINES[0]
    for x in ENGINE_X:
        at = boss_point(s * x, ENGINES[1], ENGINE_H)
        p.hull.cylinder(ENGINE_R, length, 8, M.panel, Placement(at, 0, QUARTER))
        front = boss_point(s * x, ENGINES[0], ENGINE_H)
        p.bare.cylinder(
            ENGINE_R * 0.8,
            0.6,
            8,
            M.dark,
            Placement([front[0], front[1], front[2] - 0.5], 0, QUARTER),
        )
        p.neon.ring(
            ENGINE_R * 0.86, 0.4, 8, N, Placement([front[0], front[1], front[2] - 0.2], 0, QUARTER)
        )
        p.reactor([at[0], at[1], at[2] - 0.3], ENGINE_R * 0.7)
    mid = (ENGINE_X[0] + ENGINE_X[1]) / 2
    fairing = [
        [ENGINE_X[0], ENGINES[0] + 3],
        [ENGINE_X[1], ENGINES[0] + 3],
        [ENGINE_X[1], ENGINES[1] - 2],
        [ENGINE_X[0], ENGINES[1] - 2],
    ]
    p.hull.bevel_slab(
        sided(fairing, s),
        [ENGINE_H - 3, ENGINE_H + ENGINE_R, ENGINE_H + ENGINE_R + 1],
        [0, 1],
        M.base,
        None,
        M.panel,
    )
    pylon = boss_point(s * BARBETTE_AT[0], BARBETTE_AT[1], ENGINE_H + ENGINE_R)
    p.hull.box([6, BARBETTE_H - ENGINE_H - ENGINE_R - 0.1, 6], M.panel, Placement(pylon), M.base)
    strip(
        p.neon,
        [s * mid, ENGINES[0] + 4],
        [s * mid, BARBETTE_AT[1] - 5],
        0.6,
        [ENGINE_H + ENGINE_R + 0.8, ENGINE_H + ENGINE_R + 1.2],
    )


def _tail(p: Any) -> None:
    """Draw the fin's root stub on the tail cone (its rotor's pylon) and the tail's lights.

    A swept plate from the tail cone up to the tailplanes' layer; the fin's skins over it, the
    tailplanes and the hub are the rig's.
    """
    root = fuselage_at(FIN[0], 3) - 1
    outline = [
        [root, -FIN[0]],
        [16, -FIN[1]],
        [STUB_TOP, -(FIN[1] + 0.5)],
        [STUB_TOP, -(FIN[0] + 2.8)],
    ]
    p.hull.slab(outline, [-1.4, 1.4], M.panel, Placement([0, 0, 0], 0, 0, QUARTER), M.base)
    p.neon.box([0.6, 0.5, 18], N, Placement([0, STUB_TOP - 1.2, -(FIN[0] + 14)]))
    p.reactor([0, 15.5, -FUSELAGE[len(FUSELAGE) - 1][0] + 1], 1.6)


def _bay_doors_seam(p: Any) -> None:
    """Draw the glove bays' seams (FB-SWING-WING-TITAN-10): a lit seam and the doors' bolts.

    What bursts off as the bays open: the doors themselves are the rig's.
    """
    for s in SIDES:
        strip(p.neon, [s * 11.6, -30], [s * 27.2, -30], 0.8, [GLOVE_Y[2] - 0.1, GLOVE_Y[2] + 0.5])
        for x in [14, 20, 25]:
            p.hull.box([1.6, 0.8, 1.6], M.base, Placement(boss_point(s * x, -30, GLOVE_Y[2] - 0.1)))


def _bolts(s: float) -> Any:
    def draw(p: Any) -> None:
        for x in [14, 20, 25]:
            p.hull.box([1.6, 0.8, 1.6], M.base, Placement(boss_point(s * x, -30, GLOVE_Y[2] - 0.1)))
        strip(p.neon, [s * 11.6, -30], [s * 27.2, -30], 0.8, [GLOVE_Y[2] - 0.1, GLOVE_Y[2] + 0.5])

    return draw


def _bay_frame(p: Any) -> None:
    """Draw the opened bays (BOSS-44): a dark floor, ribs across it, lit rails along the sides."""
    for s in SIDES:
        p.hull.slab(sided(BAY, s), [BAY_FLOOR - 0.4, BAY_FLOOR], M.dark)
        for y in [-40, -34, -22, -18]:
            p.bare.box([12, 0.5, 0.8], M.base, Placement(boss_point(s * 18, y, BAY_FLOOR)))
        strip(p.neon, [s * 11.6, -43], [s * 11.6, -17], 0.5, [BAY_FLOOR, BAY_FLOOR + 0.4])


def _tail_seam(p: Any) -> None:
    """Draw the dorsal fairing's seams (FB-SWING-WING-TITAN-11): what bursts off as the tail splits.

    A lit seam down its middle and across it, the flaps' latches.
    """
    top = RACK_POD[0] + 1.3
    strip(p.neon, [0, FAIRING[0] + 0.5], [0, FAIRING[1] - 0.5], 0.8, [top, top + 0.5])
    for s in SIDES:
        strip(p.neon, [s * 1, 54], [s * (FAIRING_HALF - 1), 54], 0.6, [top, top + 0.5])
        for y in [49, 59]:
            p.hull.box([1.4, 0.8, 1.4], M.base, Placement(boss_point(s * 1.4, y, top - 0.1)))


def _tail_bolts(s: float) -> Any:
    def draw(p: Any) -> None:
        top = RACK_POD[0] + 1.3
        for y in [49, 59]:
            p.hull.box([1.4, 0.8, 1.4], M.base, Placement(boss_point(s * 1.4, y, top - 0.1)))
        strip(p.neon, [s * 1, 54], [s * (FAIRING_HALF - 1), 54], 0.6, [top, top + 0.5])

    return draw


def _tail_frame(p: Any) -> None:
    """Draw the opened dorsal fairing (BOSS-44): its deck plate on the fuselage, ribs, lit rails."""
    deck = [
        [-FAIRING_HALF, FAIRING[0]],
        [FAIRING_HALF, FAIRING[0]],
        [FAIRING_HALF, FAIRING[1]],
        [-FAIRING_HALF, FAIRING[1]],
    ]
    p.hull.slab(
        [flat(q[0], q[1]) for q in deck], [fuselage_at(FAIRING[1], 3) - 1, RACK_POD[0]], M.dark
    )
    for y in [48, 60]:
        p.bare.box(
            [FAIRING_HALF * 2 - 2, 0.5, 0.8], M.base, Placement(boss_point(0, y, RACK_POD[0]))
        )
    for s in SIDES:
        strip(
            p.neon,
            [s * (FAIRING_HALF - 0.6), FAIRING[0] + 1],
            [s * (FAIRING_HALF - 0.6), FAIRING[1] - 1],
            0.5,
            [RACK_POD[0], RACK_POD[0] + 0.4],
        )


def _hatch(p: Any) -> None:
    """Draw the hatch over the spine rotor (BOSS-58): an octagonal cap, a lit seam round it."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.bevel_slab(
        polygon(8, 6.6),
        [ROTOR_H - 0.3, ROTOR_H + 0.6, ROTOR_H + 1.8],
        [0, 0.9],
        M.panel,
        Placement(at),
    )
    p.neon.ring(6.2, 0.25, 8, N, Placement([at[0], ROTOR_H + 0.9, at[2]], math.pi / 8))


def _hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.ring(6.4, 1.2, 12, M.base, Placement([at[0], ROTOR_H - 0.4, at[2]]))
    p.neon.ring(6.4, 0.3, 12, N, Placement([at[0], ROTOR_H + 0.6, at[2]]))


def draw_wing(s: float) -> Any:
    """Return the drawing of the swing wing on side `s` (1: right), spread: its moving piece.

    A long tapered slab, a lit leading edge, flap lines along its trailing edge, a lamp at its tip
    and the barbette's pedestal under its gun (its stump stands on it).
    """

    def draw(p: Any) -> None:
        p.hull.bevel_slab(sided(WING, s), WING_Y, [0, 0.8], M.base, None, M.panel)
        strip(p.neon, [s * 33, -11], [s * 96, 2.4], 0.8, [WING_Y[2] - 0.5, WING_Y[2] + 0.1])
        for k in range(4):
            x0 = 38 + k * 15
            y0 = 15.6 - (x0 - 31) * 4 / 66
            p.bare.box([12, 0.3, 0.5], SOOT, Placement(boss_point(s * (x0 + 6), y0 - 4, WING_Y[2])))
            p.bare.box([0.4, 0.3, 4], SOOT, Placement(boss_point(s * x0, y0 - 2, WING_Y[2])))
        p.neon.box([2, 1, 3.5], N, Placement(boss_point(s * 98.5, 7, WING_Y[2] - 0.8)))
        pedestal = boss_point(s * WING_GUN_AT[0], WING_GUN_AT[1], WING_Y[2] - 0.2)
        p.hull.cylinder(
            3.8, WING_GUN_H - WING_Y[2] + 0.1, 8, M.panel, Placement(pedestal, math.pi / 8)
        )

    return draw


def titan_armour() -> Any:
    """Return the Swing-Wing Titan's armour drawings by region id (`drawing.armour`, D-254)."""
    return {
        "wing-right": {"whole": draw_wing(1)},
        "wing-left": {"whole": draw_wing(-1)},
        "glove-bay": {
            "whole": _bay_doors_seam,
            "pieces": [_bolts(1), _bolts(-1)],
            "frame": _bay_frame,
        },
        "tail-split": {
            "whole": _tail_seam,
            "pieces": [_tail_bolts(1), _tail_bolts(-1)],
            "frame": _tail_frame,
        },
        "rotor-hatch": {"whole": _hatch, "frame": _hatch_frame},
    }


def wing_barbette(p: Any, at: Vec3) -> None:
    """Add a wing gun's barbette (FB-SWING-WING-TITAN-03): an armoured drum on the wing, lit."""
    p.hull.bevel_slab(
        polygon(8, 6.2),
        [WING_Y[2] - 0.2, WING_GUN_H - 0.6, WING_GUN_H],
        [0, 0.6],
        M.panel,
        Placement([at[0], 0, at[2]], math.pi / 8),
        M.base,
    )
    p.neon.ring(6.25, 0.4, 8, N, Placement([at[0], WING_GUN_H - 1.6, at[2]], math.pi / 8))
    for k in range(2):
        a = math.pi * 0.8 + k * math.pi * 0.4
        q = [at[0] + math.sin(a) * 6.8, WING_Y[2], at[2] + math.cos(a) * 6.8]
        p.hull.box([3.2, 2, 0.9], M.base, Placement(q, a))


def tail_barbette(p: Any, at: Vec3) -> None:
    """Add a rear barbette (FB-SWING-WING-TITAN-03): an armoured drum on its engine pod's tail."""
    base = ENGINE_H + ENGINE_R
    p.hull.cylinder(
        5.6, BARBETTE_H - base, 10, M.panel, Placement([at[0], base, at[2]], math.pi / 10), 4.8
    )
    p.neon.ring(5.2, 0.4, 10, N, Placement([at[0], BARBETTE_H - 1.4, at[2]], math.pi / 10))
    p.bare.box([8, 0.6, 1], SOOT, Placement([at[0], BARBETTE_H - 0.3, at[2] - 3.4]))


def nose_radome(p: Any, at: Vec3) -> None:
    """Add the nose radome (FB-SWING-WING-TITAN-03): an armoured cupola, its laser turret's seat."""
    p.hull.bevel_slab(
        polygon(8, 5.4),
        [NOSE_H - 4, NOSE_H - 0.6, NOSE_H],
        [0, 0.7],
        M.panel,
        Placement([at[0], 0, at[2]], math.pi / 8),
        M.base,
    )
    p.neon.ring(5.4, 0.4, 8, N, Placement([at[0], NOSE_H - 1.6, at[2]], math.pi / 8))


def orb_collar(p: Any, at: Vec3) -> None:
    """Add the orb's collar on the rotor's hub (FB-SWING-WING-TITAN-11): an armoured lit ring."""
    p.hull.cylinder(
        4.6,
        ORB_POD[1] - ORB_POD[0],
        10,
        M.panel,
        Placement([at[0], ORB_POD[0], at[2]], math.pi / 10),
        3.8,
    )
    p.neon.ring(4.3, 0.4, 10, N, Placement([at[0], ORB_POD[1] - 0.8, at[2]], math.pi / 10))


def build_swing_wing_titan(scene: Any) -> Any:
    """FB-SWING-WING-TITAN-01, FB-SWING-WING-TITAN-04: the Swing-Wing Titan.

    A gigantic swing-wing bomber about 5.8 L across, its wings spread; rose light lines (shown
    yellow).
    """

    def core(p: Any) -> None:
        _fuselage(p)
        for s in SIDES:
            _glove(p, s)
            _engines(p, s)
        _tail(p)

    return build_boss_model(
        SWING_WING_TITAN,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "wing-left": wing_barbette,
                "wing-right": wing_barbette,
                "barbette-left": tail_barbette,
                "barbette-right": tail_barbette,
                "nose": nose_radome,
                "orb": orb_collar,
            },
            # FB-SWING-WING-TITAN-10, FB-SWING-WING-TITAN-11: the bays' doors and feed tubes, the
            # fairing's flaps and the tail's rotor.
            "rig": {"build": build_titan_rig, "triangles": titan_triangles},
            "armour": titan_armour(),
        },
    )

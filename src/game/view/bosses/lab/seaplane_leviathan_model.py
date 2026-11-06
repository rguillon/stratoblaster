# Copyright (c) 2026 Renaud Guillon
"""FB-SEAPLANE-LEVIATHAN-01 to -04: the Seaplane Leviathan, the Lab's L-17 final boss.

Logical pixels, nose +Z, Y up (towards the camera). A gigantic flying boat seen from above: a deep
boat hull, its V bottom narrowing under a flat deck, portholes and a lit chine down its sides, the
cockpit's glazing behind the bow; a streamlined pylon on its back carrying a high gull wing, its
inner panels rising to the kink, its outer panels flat out to rounded tips; three radial engines
on each outer panel (their propellers and the floats are its rig, `seaplane_leviathan_rig`); a
tall fin and its tailplane at the stern. Its bow doors, floats and hatch are armour. A machine,
not a creature: the Lab's fourth round builds gigantic airplanes (user request, 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.seaplane_leviathan import (
    BAY_FLOOR,
    BOW_END,
    DECK,
    DORSAL_AT,
    DORSAL_H,
    ENGINES,
    FIN,
    FIN_TOP,
    FIN_TOP_Y,
    HULL,
    HULL_CHINE,
    HULL_LOW,
    KINK,
    LASER_AT,
    LASER_H,
    LEADING,
    NACELLE,
    NACELLE_H,
    NACELLE_RADIUS,
    NOSE_AT,
    NOSE_H,
    PYLON,
    PYLON_TOP,
    ROTOR_AT,
    ROTOR_H,
    SEAPLANE_LEVIATHAN,
    TAIL_AT,
    TAIL_H,
    TAILPLANE,
    TAILPLANE_H,
    TAILPLANE_SPAN,
    TIP,
    TRAILING,
    WING_GUN_AT,
    WING_GUN_H,
    WING_TOP,
    WING_UNDER,
    WING_WAIST,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.seaplane_leviathan_rig import (
    build_seaplane_rig,
    draw_float_frame,
    draw_float_whole,
    rig_triangles,
)
from game.view.bosses.world_1_organic_kit import F, M, polygon
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["seaplane-leviathan"]
QUARTER = math.pi / 2


def flat(x: float, y: float) -> list[Any]:
    """Return the playfield point `(x, y)` as a model outline point `[x, z]`."""
    return [-x, -y]


def _mirrored(right: list[list[float]]) -> list[list[Any]]:
    """Return a whole outline (model XZ) from its right half (playfield, from the centre line)."""
    points = [flat(q[0], q[1]) for q in right]
    n = len(right)
    for k in range(n):
        q = right[n - 1 - k]
        if q[0] != 0:
            points.append(flat(-q[0], q[1]))
    return points


def _x_at(right: list[list[float]], y: float) -> float:
    for k in range(len(right) - 1):
        a = right[k]
        b = right[k + 1]
        if min(a[1], b[1]) <= y <= max(a[1], b[1]) and a[1] != b[1]:
            return a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1])
    return 0


def _aft(right: list[list[float]], y0: float) -> list[list[float]]:
    """Return the part of a right half outline aft of `y0` (cut straight across)."""
    result: list[list[float]] = [[0, y0], [_x_at(right, y0), y0]]
    result.extend([q for q in right if q[1] > y0 and q[0] != 0])
    result.append(right[len(right) - 1])
    return result


def leading_y(x: float) -> float:
    """Return the wing's leading edge's Y at `x` (from the root to the tip)."""
    return LEADING[0] + (LEADING[1] - LEADING[0]) * abs(x) / TIP


def trailing_y(x: float) -> float:
    """Return the wing's trailing edge's Y at `x`."""
    return TRAILING[0] + (TRAILING[1] - TRAILING[0]) * abs(x) / TIP


def strip(
    layer: Any, a: list[float], b: list[float], h: float, size: list[float], color: Any
) -> None:
    """Add a box from playfield `a` to `b` at height `h`, `size` `[width, thickness]` across it."""
    pa = boss_point(a[0], a[1], h)
    pb = boss_point(b[0], b[1], h)
    dx = pb[0] - pa[0]
    dz = pb[2] - pa[2]
    mid = [(pa[0] + pb[0]) / 2, h, (pa[2] + pb[2]) / 2]
    layer.box([size[0], size[1], math.hypot(dx, dz)], color, Placement(mid, math.atan2(dx, dz)))


def _hull(p: Any) -> None:
    """Draw the boat hull (FB-SEAPLANE-LEVIATHAN-02) aft of the bow doors, and the bow's floor.

    Its keel the whole length, a V bottom up to the hangar's floor; over it the upper hull from the
    bow doors to the stern, its flat deck; a lit chine and portholes down its sides, the cockpit's
    glazing across the deck behind the bow, the hangar's floor lit where the doors open, and the
    bulkhead at the back of the hangar with its lit doorframe.
    """
    p.hull.bevel_slab(_mirrored(HULL), [HULL_LOW, BAY_FLOOR - 0.5, BAY_FLOOR], [6, 0], M.base)
    upper = _aft(HULL, BOW_END)
    p.flesh.bevel_slab(
        _mirrored(upper), [BAY_FLOOR - 0.3, DECK - 0.8, DECK], [0, 0.8], F.graphite, None, F.slate
    )
    for side in [-1, 1]:
        strip(p.neon, [side * 13.6, -30], [side * 13.6, 20], HULL_CHINE, [0.4, 0.5], N)
        strip(p.neon, [side * 13.6, 20], [side * 11.1, 40], HULL_CHINE, [0.4, 0.5], N)
        for k in range(8):
            y = -36 + k * 9
            x = _x_at(HULL, y) + 0.05
            p.neon.box([0.4, 1, 1.2], N, Placement(boss_point(side * x, y, HULL_CHINE + 3.5)))
        # The cockpit's glazing: two lit panes across the deck's front, a frame between.
        p.bare.box([5.2, 0.8, 3.2], M.dark, Placement(boss_point(side * 4, BOW_END + 4.5, DECK)))
        p.neon.box([4.6, 0.3, 0.5], N, Placement(boss_point(side * 4, BOW_END + 3.1, DECK + 0.8)))
        # The hangar's floor lane lights, shown once the doors open.
        strip(p.neon, [side * 4.5, -74], [side * 4.5, BOW_END - 2], BAY_FLOOR, [0.5, 0.25], N)
    # The bulkhead at the hangar's back: a lit doorframe on the upper hull's front.
    front = boss_point(0, BOW_END - 0.2, BAY_FLOOR)
    p.bare.box([16, DECK - BAY_FLOOR - 3, 0.5], M.dark, Placement(front))
    p.neon.box([16.5, 0.5, 0.6], N, Placement([0, DECK - 3, front[2]]))
    for side in [-1, 1]:
        p.neon.box(
            [0.5, DECK - BAY_FLOOR - 3, 0.6], N, Placement([side * 8.2, BAY_FLOOR, front[2]])
        )
    # Deck walkways and the gun seats: the dorsal laser's, the stern rotor's well, the tail
    # turret's plinth.
    strip(p.bare, [0, BOW_END + 9], [0, 40], DECK, [2.2, 0.2], M.dark)
    laser = boss_point(LASER_AT[0], LASER_AT[1], DECK)
    p.hull.cylinder(3.8, LASER_H - DECK - 0.2, 8, M.base, Placement(laser))
    well = boss_point(ROTOR_AT[0], ROTOR_AT[1], DECK - 0.2)
    p.hull.cylinder(6.8, ROTOR_H - DECK, 8, M.base, Placement(well, math.pi / 8))
    tail = boss_point(TAIL_AT[0], TAIL_AT[1], DECK - 1)
    p.hull.cylinder(3.4, TAIL_H - DECK + 0.8, 8, M.base, Placement(tail))


def _pylon(p: Any) -> None:
    """Draw the pylon carrying the wing over the hull, the dorsal turret's seat on its top."""
    right: list[list[float]] = [
        [0, PYLON[0]],
        [3.5, PYLON[0] + 3],
        [6, PYLON[0] + 10],
        [6, PYLON[1] - 4],
        [0, PYLON[1]],
    ]
    p.flesh.bevel_slab(
        _mirrored(right), [DECK - 0.5, PYLON_TOP - 1, PYLON_TOP], [0, 1], F.graphite, None, F.slate
    )
    seat = boss_point(DORSAL_AT[0], DORSAL_AT[1], PYLON_TOP - 0.2)
    p.hull.cylinder(5.6, DORSAL_H - PYLON_TOP + 0.2, 10, M.base, Placement(seat))
    p.neon.ring(5.65, 0.35, 10, N, Placement([seat[0], DORSAL_H - 0.5, seat[2]]))


def _wing(p: Any) -> None:
    """Draw the gull wing (FB-SEAPLANE-LEVIATHAN-02).

    The inner panels rise from the pylon's top to the kink; the outer panels run flat from there
    to rounded tips, lit along their leading edges, dark aileron seams along their trailing edges;
    a plinth under each wing gun on the inner panel.
    """
    rise = WING_TOP - PYLON_TOP
    length = math.hypot(KINK, rise)
    roll = math.asin(rise / length)
    for side in [-1, 1]:
        s = -side
        local = [
            [0, -leading_y(0)],
            [s * length, -leading_y(KINK)],
            [s * length, -trailing_y(KINK)],
            [0, -trailing_y(0)],
        ]
        p.flesh.slab(
            local, [-3.5, 0], F.graphite, Placement([0, PYLON_TOP, 0], 0, 0, -side * roll), F.slate
        )
        outer = [
            [KINK, leading_y(KINK)],
            [TIP - 4, leading_y(TIP - 4)],
            [TIP - 1, leading_y(TIP) + 2.5],
            [TIP, (leading_y(TIP) + trailing_y(TIP)) / 2],
            [TIP - 1, trailing_y(TIP) - 2],
            [TIP - 4, trailing_y(TIP - 4)],
            [KINK, trailing_y(KINK)],
        ]
        p.flesh.bevel_slab(
            [flat(side * q[0], q[1]) for q in outer],
            [WING_UNDER, WING_WAIST, WING_TOP],
            [1, 0.6],
            F.graphite,
            None,
            F.slate,
        )
        strip(
            p.neon,
            [side * (KINK + 1), leading_y(KINK) - 0.2],
            [side * (TIP - 4), leading_y(TIP - 4) - 0.2],
            WING_WAIST - 0.4,
            [0.7, 0.8],
            N,
        )
        for x0, x1 in [[40, 50], [58, 68], [76, 88]]:
            strip(
                p.bare,
                [side * x0, trailing_y(x0) - 3.5],
                [side * x1, trailing_y(x1) - 3.5],
                WING_TOP,
                [0.4, 0.15],
                M.dark,
            )
        p.neon.box([1.6, 1.4, 2], N, Placement(boss_point(side * (TIP - 0.6), -4, WING_WAIST - 1)))
        plinth = boss_point(side * WING_GUN_AT[0], WING_GUN_AT[1], WING_GUN_H - 3.2)
        p.hull.cylinder(4, 3.2, 8, M.base, Placement(plinth, math.pi / 8))


def _engines(p: Any) -> None:
    """Draw the radial engines' nacelles (FB-SEAPLANE-LEVIATHAN-02), under their propellers.

    Each a tapered nacelle along the wing's chord, its round cowling at the front with a lit lip,
    the radial's cylinder heads in a ring inside it round the crankcase, an exhaust ring behind.
    """
    for side in [-1, 1]:
        for x in ENGINES:
            tail = boss_point(side * x, NACELLE[1], NACELLE_H)
            body = NACELLE[1] - NACELLE[0] - 6
            r = NACELLE_RADIUS - 0.3
            profile = [[1.2, 0], [r - 1, body * 0.3], [r, body * 0.65], [r, body]]
            p.hull.lathe(profile, 10, M.panel, Placement(tail, 0, QUARTER))
            cowl = boss_point(side * x, NACELLE[0] + 6, NACELLE_H)
            p.hull.cylinder(
                NACELLE_RADIUS - 0.4, 6, 10, M.base, Placement(cowl, 0, QUARTER), NACELLE_RADIUS
            )
            lip = boss_point(side * x, NACELLE[0] + 0.4, NACELLE_H)
            p.neon.ring(NACELLE_RADIUS + 0.05, 0.6, 10, N, Placement(lip, 0, QUARTER))
            p.bare.ring(
                NACELLE_RADIUS + 0.1,
                1.2,
                10,
                M.dark,
                Placement(boss_point(side * x, NACELLE[0] + 5, NACELLE_H), 0, QUARTER),
            )
            face = boss_point(side * x, NACELLE[0] + 1.2, NACELLE_H)
            p.bare.cylinder(NACELLE_RADIUS - 0.5, 0.6, 10, M.dark, Placement(face, 0, QUARTER))
            for k in range(7):
                a = k * 2 * math.pi / 7
                at = [face[0] - math.sin(a) * 1.4, face[1] + math.cos(a) * 1.4, face[2] + 0.3]
                p.hull.box([1.3, 2.4, 1.6], M.panel, Placement(at, 0, 0, a))


def _tail(p: Any) -> None:
    """Draw the tall tail (FB-SEAPLANE-LEVIATHAN-02): its fin and its tailplane.

    The fin a plate standing on the centre line, a lit stripe up its rudder; the tailplane across
    it high up, lit along its tips.
    """
    fin = [
        [DECK - 1, -FIN[0]],
        [DECK - 1, -FIN[1]],
        [FIN_TOP, -FIN_TOP_Y[1]],
        [FIN_TOP, -FIN_TOP_Y[0]],
    ]
    p.hull.slab(fin, [-1, 1], M.panel, Placement([0, 0, 0], 0, 0, QUARTER), M.base)
    p.neon.box([2.2, FIN_TOP - DECK - 4, 0.6], N, Placement([0, DECK + 2, -FIN[1] + 1.2]))
    p.neon.box(
        [2.3, 0.5, FIN_TOP_Y[1] - FIN_TOP_Y[0]],
        N,
        Placement([0, FIN_TOP - 0.3, -(FIN_TOP_Y[0] + FIN_TOP_Y[1]) / 2]),
    )
    right: list[list[float]] = [
        [0, TAILPLANE[0] - 2],
        [TAILPLANE_SPAN, TAILPLANE[0] + 3],
        [TAILPLANE_SPAN, TAILPLANE[1] - 1],
        [0, TAILPLANE[1]],
    ]
    p.hull.bevel_slab(
        _mirrored(right),
        [TAILPLANE_H - 1.2, TAILPLANE_H - 0.4, TAILPLANE_H + 0.6],
        [0, 0.4],
        M.panel,
    )
    for side in [-1, 1]:
        strip(
            p.neon,
            [side * (TAILPLANE_SPAN - 0.6), TAILPLANE[0] + 3.5],
            [side * (TAILPLANE_SPAN - 0.6), TAILPLANE[1] - 1.5],
            TAILPLANE_H + 0.6,
            [1, 0.3],
            N,
        )


def bow_door(side: float) -> Any:
    """Return the drawing of the bow door on `side` (1: right), shut: the bow's upper hull's half.

    A bevelled half bow from the keel line out, its deck and the stem; a lit seam along the keel
    line where it splits, portholes down its side, and its half of the nose turret's plinth.
    """

    def draw(p: Any) -> None:
        right = [q for q in HULL if q[1] < BOW_END]
        right.append([13.3, BOW_END])
        right.append([0, BOW_END])
        outline = [flat(side * q[0], q[1]) for q in right]
        p.flesh.bevel_slab(
            outline, [BAY_FLOOR, DECK - 0.8, DECK], [0, 0.8], F.graphite, None, F.slate
        )
        strip(p.neon, [side * 0.4, -78], [side * 0.4, BOW_END + 1], DECK, [0.4, 0.2], N)
        for y in [-68, -58, -48]:
            x = _x_at(HULL, y) + 0.05
            p.neon.box([0.4, 1, 1.2], N, Placement(boss_point(side * x, y, HULL_CHINE + 3.5)))
        plinth = boss_point(side * 2.6, NOSE_AT[1], DECK)
        p.hull.box([5, NOSE_H - DECK - 0.1, 9], M.base, Placement(plinth))

    return draw


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the stern rotor (BOSS-58): an octagonal cap, a lit seam round it."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.bevel_slab(
        polygon(8, 6.6),
        [ROTOR_H - 0.4, ROTOR_H + 0.3, ROTOR_H + 1.4],
        [0, 0.9],
        M.panel,
        Placement(at),
    )
    p.neon.ring(6.2, 0.25, 8, N, Placement([at[0], ROTOR_H + 0.7, at[2]], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.ring(6.9, 1.2, 12, M.base, Placement([at[0], ROTOR_H - 0.8, at[2]]))
    p.neon.ring(6.9, 0.3, 12, N, Placement([at[0], ROTOR_H + 0.2, at[2]]))


def _wing_gun(p: Any, at: Vec3) -> None:
    """Add a wing gun's blister (FB-SEAPLANE-LEVIATHAN-03): an armoured cupola on the gull panel.

    An octagonal ring round the turret, lit round its rim, two cheek plates ahead of it.
    """
    x = at[0]
    z = at[2]
    p.hull.bevel_slab(
        polygon(8, 6),
        [WING_GUN_H - 3, WING_GUN_H - 0.8, WING_GUN_H],
        [0, 0.6],
        M.panel,
        Placement([x, 0, z], math.pi / 8),
        M.base,
    )
    p.neon.ring(6.05, 0.4, 8, N, Placement([x, WING_GUN_H - 1.4, z], math.pi / 8))
    for dx in [-1, 1]:
        p.hull.box(
            [1.6, 2.2, 3.6], M.base, Placement([x + dx * 3.6, WING_GUN_H - 1.2, z + 5.4], dx * 0.3)
        )


def _nose_turret(p: Any, at: Vec3) -> None:
    """Add the nose turret (FB-SEAPLANE-LEVIATHAN-03): an armoured drum on the bow's deck.

    Lit round its rim, splinter plates round its front, a lit chevron on the deck ahead.
    """
    x = at[0]
    z = at[2]
    p.hull.cylinder(6, 1.6, 10, M.panel, Placement([x, NOSE_H - 1.6, z]), 5.4)
    p.neon.ring(6.05, 0.4, 10, N, Placement([x, NOSE_H - 1.1, z]))
    for k in range(3):
        a = -math.pi / 4 + k * math.pi / 4
        q = [x + math.sin(a) * 6.8, DECK, z + math.cos(a) * 6.8]
        p.hull.box([3.4, 2.2, 0.9], M.base, Placement(q, a))
    p.neon.box([4, 0.3, 0.6], N, Placement([x, DECK + 0.05, z + 10], 0))


def _tail_turret(p: Any, at: Vec3) -> None:
    """Add the tail turret (FB-SEAPLANE-LEVIATHAN-03): a turret ring on the stern's sponson."""
    x = at[0]
    z = at[2]
    p.hull.bevel_slab(
        polygon(8, 5.6),
        [DECK - 3, TAIL_H - 0.8, TAIL_H],
        [0.6, 0.5],
        M.panel,
        Placement([x, 0, z], math.pi / 8),
        M.base,
    )
    p.neon.ring(5.65, 0.4, 8, N, Placement([x, TAIL_H - 1.4, z], math.pi / 8))


def _dorsal_laser(p: Any, at: Vec3) -> None:
    """Add the dorsal laser's blister (FB-SEAPLANE-LEVIATHAN-03): a glazed dome on the deck.

    A low dome round the laser's turret, lit window bands round it.
    """
    x = at[0]
    z = at[2]
    p.hull.lathe(
        [[6, DECK - 0.2], [6, DECK + 1.2], [5, LASER_H - 0.6], [3.6, LASER_H]],
        10,
        M.panel,
        Placement([x, 0, z]),
    )
    p.neon.ring(5.75, 0.5, 10, N, Placement([x, DECK + 1.6, z]))


def build_seaplane_leviathan(scene: Any) -> Any:
    """FB-SEAPLANE-LEVIATHAN-01, FB-SEAPLANE-LEVIATHAN-04: the Seaplane Leviathan.

    A flying boat 5.5 L across its gull wing, six radial engines, wingtip floats, a tall tail; sea
    blue light lines (shown green).
    """

    def core(p: Any) -> None:
        _hull(p)
        _pylon(p)
        _wing(p)
        _engines(p)
        _tail(p)

    return build_boss_model(
        SEAPLANE_LEVIATHAN,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "wing-gun-left": _wing_gun,
                "wing-gun-right": _wing_gun,
                "nose-turret": _nose_turret,
                "tail-turret": _tail_turret,
                "dorsal-laser": _dorsal_laser,
            },
            # FB-SEAPLANE-LEVIATHAN-05, -09, -10: propellers, floats, spinners and launch deck.
            "rig": {"build": build_seaplane_rig, "triangles": rig_triangles},
            "armour": {
                "floats": {"whole": draw_float_whole, "pieces": [], "frame": draw_float_frame},
                "bow-door-right": {"whole": bow_door(1)},
                "bow-door-left": {"whole": bow_door(-1)},
                "rotor-hatch": {"whole": _draw_hatch, "frame": _draw_hatch_frame},
            },
        },
    )

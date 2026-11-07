# Copyright (c) 2026 Renaud Guillon
"""MB-ANVIL-BARGE-03 to MB-ANVIL-BARGE-05: the Anvil Barge's parts, horn halves and hatches.

Logical pixels, nose +Z, Y up (towards the camera). Its two lift jet banks and its forge (its
parts), the two halves of its horn (moving pieces, BOSS-45: drawn closed, they swing apart) and the
hatches over its face's late guns (BOSS-58). Riveted iron plate with glowing ember seams: a flying
bunker, not a creature (the Lab's fifth round, user request 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.anvil_barge import (
    CASEMATE_AT,
    CASEMATE_HATCH,
    FACE_TOP,
    FEET,
    FORGE,
    HORN,
    HORN_TIP,
    HORN_TOP,
    HORN_UNDER,
    JETS,
    ROTOR_AT,
    ROTOR_HATCH,
    STEP_FRONT,
    TURRET_AT,
    TURRET_HATCH,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.final_boss_greebles import studs
from game.view.bosses.world_1_organic_kit import M
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["anvil-barge"]
# Its shades: blackened iron for its hull, a paler hardened steel for its working face and horn,
# a darker iron for bands and the mechanism showing in its gaps.
IRON = [0.11, 0.105, 0.11]
STEEL = [0.2, 0.2, 0.215]
BAND = [0.07, 0.068, 0.072]
RIVET = [0.26, 0.25, 0.25]


def pt(x: float, y: float) -> list[float]:
    """Return a config point `(x, y)` as a slab outline point (model X, Z)."""
    return [-x, -y]


def outline_of(points: list[Any], side: float = 1) -> list[list[float]]:
    """Return config points (their X times `side`) as a slab outline (model X, Z)."""
    return [pt(side * q[0], q[1]) for q in points]


def rivets(p: Any, a: list[float], b: list[float], count: int, y: float) -> None:
    """Add a row of `count` rivets from config `a` to config `b`, at height `y`."""
    studs(p.hull, [pt(a[0], a[1]), pt(b[0], b[1])], [count, 0.7], y, RIVET)


def seam(p: Any, a: list[float], b: list[float], y: float, width: float = 0.5) -> None:
    """Add a glowing seam from config `a` to config `b` at height `y` (a thin neon bar)."""
    qa = boss_point(a[0], a[1], y)
    qb = boss_point(b[0], b[1], y)
    dx = qb[0] - qa[0]
    dz = qb[2] - qa[2]
    length = math.hypot(dx, dz)
    yaw = math.atan2(dx, dz)
    mid = [(qa[0] + qb[0]) / 2, y, (qa[2] + qb[2]) / 2]
    p.neon.box([width, 0.3, length], N, Placement(mid, yaw))


def jets(p: Any, at: Vec3) -> None:
    """Draw a lift jet bank (MB-ANVIL-BARGE-03): a long armoured nacelle along a foot's flank.

    Three intake fans in its top, lit rings round them; a heavy pylon onto the foot; its jet
    nozzles glowing under it; a lit stripe along its outer flank. It carries no gun.
    """
    x = at[0]
    z = at[2]
    w = JETS[0]
    h = JETS[1]
    out = 1 if x > 0 else -1
    outline = [
        [x - w, z - h + 3],
        [x - w + 2.5, z - h],
        [x + w - 2.5, z - h],
        [x + w, z - h + 3],
        [x + w, z + h - 3],
        [x + w - 2.5, z + h],
        [x - w + 2.5, z + h],
        [x - w, z + h - 3],
    ]
    p.hull.bevel_slab(outline, [JETS[2], 3, JETS[3]], [1.8, 1.2], IRON, None, STEEL)
    # The pylon onto the foot, and a band round the nacelle's middle.
    p.hull.box([4, 4, 14], BAND, Placement([x - out * (w + 0.6), FEET[4] - 3, z]))
    p.bare.box([2 * w + 0.4, 1.2, 2.2], BAND, Placement([x, JETS[3] - 0.9, z]))
    for k in [-1, 0, 1]:
        c = [x, JETS[3], z + k * 11.5]
        p.bare.cylinder(3.8, 0.25, 8, M.dark, Placement(c))
        p.neon.ring(4.1, 0.45, 8, N, Placement([c[0], c[1] - 0.1, c[2]]))
        p.hull.cylinder(1.3, 0.8, 6, M.panel, Placement(c))
        for j in range(3):
            yaw = j * math.pi / 3 + k * 0.4
            p.bare.box([0.7, 0.35, 6.4], M.base, Placement([c[0], c[1] + 0.2, c[2]], yaw))
        # The nozzle under it, glowing.
        p.neon.cylinder(2.4, 1.6, 6, N, Placement([c[0], JETS[2] - 1.5, c[2]]), 3)
    # A lit stripe along its outer flank, warning lights at its ends.
    p.neon.box([0.4, 1, 2 * h - 8], N, Placement([x + out * (w + 0.05), 0.5, z]))
    for s in [-1, 1]:
        p.neon.box([1.2, 1.2, 1.2], N, Placement([x, JETS[3] + 0.1, z + s * (h - 2)]))


def forge(p: Any, at: Vec3) -> None:
    """Draw the forge on the heel (MB-ANVIL-BARGE-03): a riveted furnace, its turret on its top.

    A glowing grate in its back, two stacks at its back corners with hot mouths, bands round it.
    Its turret's pedestal is the core's (it stays, under the stump, once the forge is gone).
    """
    x = at[0]
    z = at[2]
    hw = FORGE[0]
    hd = FORGE[1]
    top = FORGE[2]
    outline = [[x - hw, z - hd], [x + hw, z - hd], [x + hw, z + hd], [x - hw, z + hd]]
    p.hull.bevel_slab(outline, [FACE_TOP, top - 1.2, top], [0, 0.9], IRON, None, STEEL)
    p.bare.box([2 * hw + 0.4, 1, 2 * hd + 0.4], BAND, Placement([x, FACE_TOP + 1.6, z]))
    # The grate in its back (towards the screen's top): lit bars.
    for k in range(4):
        gx = x - 4.5 + k * 3
        p.neon.box([1.2, 2.6, 0.4], N, Placement([gx, FACE_TOP + 0.6, z - hd - 0.1]))
    for s in [-1, 1]:
        c = [x + s * (hw - 2.2), top, z - hd + 2.2]
        p.hull.cylinder(1.9, 6, 6, BAND, Placement(c), 1.6)
        p.neon.cylinder(1.5, 0.4, 6, N, Placement([c[0], top + 6, c[2]]))
    rivets(p, [-hw + 1, -(z + hd) + 1], [hw - 1, -(z + hd) + 1], 6, top)
    rivets(p, [-hw + 1, -(z - hd) - 1], [hw - 1, -(z - hd) - 1], 6, top)


def horn_half(side: float) -> Any:
    """Return the drawing of the horn's half on `side` (+1 the config's right), closed, as drawn.

    Hardened steel tapering to the tip, its top flat (a gatling stands on it once it has swung
    out), iron bands across it, a glowing seam along its outer edge and a lit cut face along the
    centre line that shows once the halves part (MB-ANVIL-BARGE-05).
    """

    def draw(p: Any) -> None:
        outline = outline_of(HORN, side)
        p.hull.bevel_slab(outline, [HORN_UNDER, HORN_TOP - 3, HORN_TOP], [2.5, 1.2], STEEL)
        for y in [-40, -51]:
            w = _horn_half_width(y)
            q = boss_point(side * w / 2, y, HORN_TOP - 0.2)
            p.bare.box([w + 0.6, 0.6, 1.6], BAND, Placement(q))
        for k in range(len(HORN) - 2):
            a = HORN[k + 1]
            b = HORN[k + 2]
            seam(p, [side * (a[0] - 1.6), a[1] - 0.6], [side * (b[0] - 1.2), b[1]], HORN_TOP + 0.05)
        cut = [[0, STEP_FRONT - 0.5], [side * 0.5, STEP_FRONT - 0.5], [side * 0.5, HORN_TIP + 3]]
        cut.append([0, HORN_TIP + 3])
        p.neon.slab(outline_of(cut), [HORN_UNDER + 3, HORN_TOP - 1.5], N)
        rivets(p, [side * 9.5, -35], [side * 4, -59], 6, HORN_TOP)

    return draw


def _horn_half_width(y: float) -> float:
    """Return the half horn's width at `y` (linear between its outline's outer corners)."""
    for k in range(1, len(HORN) - 1):
        a = HORN[k]
        b = HORN[k + 1]
        if b[1] <= y <= a[1]:
            return float(a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]))
    return 0.0


def turret_hatch(p: Any) -> None:
    """Draw the round plate over the face turret (BOSS-58): a riveted iron dome, a lit seam."""
    at = boss_point(TURRET_AT[0], TURRET_AT[1], 0)
    r = TURRET_HATCH
    profile = [
        [r, FACE_TOP],
        [r - 0.3, FACE_TOP + 0.9],
        [r * 0.6, FACE_TOP + 1.7],
        [0, FACE_TOP + 2],
    ]
    p.hull.lathe(profile, 8, IRON, Placement([at[0], 0, at[2]], math.pi / 8))
    p.neon.ring(r + 0.05, 0.3, 8, N, Placement([at[0], FACE_TOP + 0.2, at[2]], math.pi / 8))


def round_frame(p: Any) -> None:
    """Draw what the turret's plate leaves (BOSS-44): an iron collar round its well."""
    at = boss_point(TURRET_AT[0], TURRET_AT[1], 0)
    p.hull.ring(TURRET_HATCH, 0.8, 10, BAND, Placement([at[0], FACE_TOP - 0.2, at[2]]))
    p.bare.cylinder(TURRET_HATCH - 0.2, 0.2, 10, M.dark, Placement([at[0], FACE_TOP, at[2]]))
    p.neon.ring(TURRET_HATCH + 0.05, 0.3, 10, N, Placement([at[0], FACE_TOP + 0.5, at[2]]))


def _plate_hatch(at: list[Any], half: list[Any]) -> Any:
    """Return the drawing of a square hatch plate `half` big round config `at`."""

    def draw(p: Any) -> None:
        q = boss_point(at[0], at[1], FACE_TOP)
        outline = [
            pt(at[0] - half[0], at[1] - half[1]),
            pt(at[0] + half[0], at[1] - half[1]),
            pt(at[0] + half[0], at[1] + half[1]),
            pt(at[0] - half[0], at[1] + half[1]),
        ]
        p.hull.bevel_slab(outline, [FACE_TOP - 0.2, FACE_TOP + 0.6, FACE_TOP + 1.3], [0, 0.6], IRON)
        p.neon.box([2 * half[0] - 1.5, 0.3, 0.4], N, Placement([q[0], FACE_TOP + 1.3, q[2]]))
        p.neon.box([0.4, 0.3, 2 * half[1] - 1.5], N, Placement([q[0], FACE_TOP + 1.3, q[2]]))
        for sx in [-1, 1]:
            for sy in [-1, 1]:
                c = [q[0] + sx * (half[0] - 1), FACE_TOP + 1.3, q[2] + sy * (half[1] - 1)]
                p.hull.box([0.8, 0.3, 0.8], RIVET, Placement(c))

    return draw


def _plate_frame(at: list[Any], half: list[Any]) -> Any:
    """Return what a square hatch leaves (BOSS-44): an iron lip round its dark well."""

    def draw(p: Any) -> None:
        q = boss_point(at[0], at[1], FACE_TOP)
        for s in [-1, 1]:
            p.hull.box(
                [2 * half[0], 0.7, 0.8], BAND, Placement([q[0], FACE_TOP, q[2] + s * half[1]])
            )
            p.hull.box(
                [0.8, 0.7, 2 * half[1]], BAND, Placement([q[0] + s * half[0], FACE_TOP, q[2]])
            )
        p.bare.box([2 * half[0] - 0.6, 0.15, 2 * half[1] - 0.6], M.dark, Placement(q))
        p.neon.box([2 * half[0], 0.2, 0.3], N, Placement([q[0], FACE_TOP + 0.7, q[2] - half[1]]))

    return draw


def barge_armour() -> Any:
    """Return the Anvil Barge's armour drawings by region id (`drawing.armour`, D-254)."""
    left = [-CASEMATE_AT[0], CASEMATE_AT[1]]
    return {
        "horn-right": {"whole": horn_half(1)},
        "horn-left": {"whole": horn_half(-1)},
        "turret-hatch": {"whole": turret_hatch, "frame": round_frame},
        "rotor-hatch": {
            "whole": _plate_hatch(ROTOR_AT, [ROTOR_HATCH, ROTOR_HATCH]),
            "frame": _plate_frame(ROTOR_AT, [ROTOR_HATCH, ROTOR_HATCH]),
        },
        "casemate-hatch-left": {
            "whole": _plate_hatch(left, CASEMATE_HATCH),
            "frame": _plate_frame(left, CASEMATE_HATCH),
        },
        "casemate-hatch-right": {
            "whole": _plate_hatch(CASEMATE_AT, CASEMATE_HATCH),
            "frame": _plate_frame(CASEMATE_AT, CASEMATE_HATCH),
        },
    }

# Copyright (c) 2026 Renaud Guillon
"""FB-TWIN-PYLON-02, FB-TWIN-PYLON-03, FB-TWIN-PYLON-05: the Twin Pylon's pylons, parts and armour.

Its two lattice pylons with their cross-arms, its parts (the insulator stacks, the coil heads and
the transformer) and its armour regions (the end cowlings, the bus covers, the prow plate and the
capacitor's hatch). Logical pixels, nose +Z, Y up (towards the camera); shapes are given in config
coordinates (X right, Y up the screen) and turned into model space here.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.twin_pylon import (
    ARM_HEIGHT,
    ARM_REACH,
    CAP_ROTOR_AT,
    CAP_TOP,
    COIL_TOP,
    DECK_TOP,
    INSULATOR_TOP,
    PROW,
    PYLON_FOOT,
    PYLON_HEAD,
    PYLON_TOP,
    PYLON_X,
    TRANSFORMER_AT,
    TRANSFORMER_TOP,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.final_boss_greebles import SHADE, plate, rod
from game.view.bosses.final_boss_mechanism import armour
from game.view.bosses.final_boss_shapes import edge_strips
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["twin-pylon"]
# The lattice's levels: shares of the way up from the deck to the pylon's head.
LEVELS = [0, 0.3, 0.56, 0.8, 1]
LEG = 0.95
# The arc's jags from a coil head to the middle: `[across, up]` px off the straight line.
ARC_JAGS = [[2.2, 0.8], [-1.8, 1.6], [1.6, 0.6], [-2.4, 1.4], [1.2, 0.4], [0.0, 1.0]]
BRACE = 0.42


def pt(x: float, y: float, h: float) -> Vec3:
    """Return the config point `(x, y)` at height `h` in model space."""
    return boss_point(x, y, h)


def model_outline(outline: list[Any]) -> list[Any]:
    """Return a config outline as a model outline (`[x, z]` points)."""
    return [[-q[0], -q[1]] for q in outline]


def box_outline(x: list[Any], y: list[Any]) -> list[Any]:
    """Return the config rectangle from `x[0]` to `x[1]` across and `y[0]` to `y[1]` along."""
    return [[x[0], y[0]], [x[1], y[0]], [x[1], y[1]], [x[0], y[1]]]


def _corner(cx: float, level: float, i: int) -> Vec3:
    """Return the corner `i` (0 to 3, round) of the pylon at `cx` at `level` of its height."""
    half = PYLON_FOOT + (PYLON_HEAD - PYLON_FOOT) * level
    h = DECK_TOP + (PYLON_TOP - DECK_TOP) * level
    sx = 1 if i % 3 == 0 else -1
    sy = 1 if i < 2 else -1
    return pt(cx + sx * half, sy * half, h)


def draw_pylon(p: Any, cx: float) -> None:
    """Draw a lattice pylon centred at config X `cx` (FB-TWIN-PYLON-02).

    Four legs tapering from its footings to its head, a frame at each level, crossed braces on each
    face, a lit band round two levels, its cross-arm and the insulator strings under it.
    """
    for i in range(4):
        foot = _corner(cx, 0, i)
        p.hull.box([4.2, 2, 4.2], SHADE["mid"], Placement([foot[0], DECK_TOP - 0.6, foot[2]]))
        for k in range(len(LEVELS) - 1):
            rod(
                p.hull, _corner(cx, LEVELS[k], i), _corner(cx, LEVELS[k + 1], i), LEG, SHADE["base"]
            )
    for k in range(1, len(LEVELS)):
        for i in range(4):
            j = (i + 1) % 4
            rod(p.hull, _corner(cx, LEVELS[k], i), _corner(cx, LEVELS[k], j), BRACE, SHADE["mid"])
            a = _corner(cx, LEVELS[k - 1], i)
            b = _corner(cx, LEVELS[k], j)
            c = _corner(cx, LEVELS[k - 1], j)
            d = _corner(cx, LEVELS[k], i)
            rod(p.hull, a, b, BRACE * 0.8, SHADE["dark"])
            rod(p.hull, c, d, BRACE * 0.8, SHADE["dark"])
    for level in [0.3, 0.8]:
        half = PYLON_FOOT + (PYLON_HEAD - PYLON_FOOT) * level + 0.6
        h = DECK_TOP + (PYLON_TOP - DECK_TOP) * level
        p.neon.ring(half * 1.41, 0.5, 4, N, Placement(pt(cx, 0, h - 0.25), math.pi / 4))
    # The head: a block over the top frame the coil head stands on.
    p.hull.box(
        [PYLON_HEAD * 2 + 2, 2, PYLON_HEAD * 2 + 2],
        SHADE["mid"],
        Placement(pt(cx, 0, PYLON_TOP - 1)),
    )
    _arm(p, cx)


def _arm(p: Any, cx: float) -> None:
    """Draw a pylon's cross-arm (FB-TWIN-PYLON-02): a lattice beam across it near its head.

    Two chords and a zigzag between them, insulator strings hanging at both ends, a lit tip.
    """
    h = ARM_HEIGHT
    x0 = cx - ARM_REACH
    x1 = cx + ARM_REACH
    for y in [-2, 2]:
        rod(p.hull, pt(x0, y, h), pt(x1, y, h), 0.6, SHADE["base"])
    rod(p.hull, pt(x0, 0, h + 2.4), pt(x1, 0, h + 2.4), 0.5, SHADE["mid"])
    steps = 6
    for k in range(steps):
        xa = x0 + (x1 - x0) * k / steps
        xb = x0 + (x1 - x0) * (k + 1) / steps
        y = -2 if k % 2 == 0 else 2
        rod(p.hull, pt(xa, y, h), pt(xb, -y, h), 0.3, SHADE["dark"])
        rod(p.hull, pt(xb, -y, h), pt((xa + xb) / 2, 0, h + 2.4), 0.3, SHADE["dark"])
    for x in [x0 + 1, x1 - 1]:
        _string(p, pt(x, 0, h - 0.5), 4)
        p.neon.box([1.2, 0.8, 1.2], N, Placement(pt(x, 0, h - 5.6)))


def _string(p: Any, top: Vec3, count: int) -> None:
    """Add an insulator string hanging from `top`: `count` discs one under the other."""
    for k in range(count):
        at = [top[0], top[1] - 1.3 * (k + 1), top[2]]
        p.hull.cylinder(1.4, 0.6, 6, SHADE["light"], Placement(at))
    rod(p.hull, [top[0], top[1] - 1.3 * count - 0.4, top[2]], top, 0.3, SHADE["dark"])


def insulator(p: Any, at: Vec3) -> None:
    """Add an insulator stack (FB-TWIN-PYLON-03): a tall stack of ribbed discs on a lit base.

    Its laser emitter stands on its cap; a cable runs up from it to its pylon's arm.
    """
    x = at[0]
    z = at[2]
    p.hull.box([9, 2.2, 9], SHADE["mid"], Placement([x, DECK_TOP - 0.4, z]))
    p.neon.ring(4.8, 0.6, 8, N, Placement([x, DECK_TOP + 1, z], math.pi / 8))
    profile: list[Any] = [[2.4, DECK_TOP + 1.6]]
    h = DECK_TOP + 2.4
    while h < INSULATOR_TOP - 2.5:
        profile.append([2.4, h])
        profile.append([4.2, h + 0.5])
        profile.append([4.2, h + 0.9])
        profile.append([2.4, h + 1.4])
        h += 1.9
    profile.append([3, INSULATOR_TOP - 1.6])
    profile.append([4.6, INSULATOR_TOP - 1])
    profile.append([4.6, INSULATOR_TOP])
    profile.append([0, INSULATOR_TOP])
    p.hull.lathe(profile, 8, SHADE["light"], Placement([x, 0, z], math.pi / 8))
    p.neon.ring(4.7, 0.4, 8, N, Placement([x, INSULATOR_TOP - 0.7, z], math.pi / 8))
    # The cable to its pylon's arm tip.
    side = 1 if x < 0 else -1
    tip = pt(side * (PYLON_X + ARM_REACH - 1), 0, ARM_HEIGHT - 5.6)
    rod(p.neon, [x, INSULATOR_TOP - 1, z], tip, 0.35, N)


def coil_head(p: Any, at: Vec3) -> None:
    """Add a coil head (FB-TWIN-PYLON-03) on a pylon's head: a glowing toroid round a post.

    Its turret stands on the post's cap.
    """
    x = at[0]
    z = at[2]
    p.hull.cylinder(3, COIL_TOP - PYLON_TOP, 8, SHADE["base"], Placement([x, PYLON_TOP, z]))
    torus: list[Any] = [
        [3, PYLON_TOP + 0.6],
        [6.6, PYLON_TOP + 0.8],
        [8.2, PYLON_TOP + 1.8],
        [6.6, PYLON_TOP + 2.8],
        [3, PYLON_TOP + 3],
    ]
    p.hull.lathe(torus, 10, SHADE["mid"], Placement([x, 0, z]))
    p.neon.ring(8.3, 0.5, 10, N, Placement([x, PYLON_TOP + 1.55, z]))
    # Coil windings showing as lit rings up its post.
    for k in range(2):
        p.neon.ring(3.1, 0.3, 8, N, Placement([x, PYLON_TOP + 3.6 + k * 0.9, z]))
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        p.hull.box(
            [1.6, 1.6, 1.6],
            SHADE["light"],
            Placement([x + math.cos(a) * 7.4, PYLON_TOP + 2.4, z + math.sin(a) * 7.4], a),
        )
    # Its half of the arc crackling between the two coil heads, over the conduit.
    steps = len(ARC_JAGS)
    inward = -1 if x > 0 else 1
    last = [x + inward * 7, PYLON_TOP + 2, z]
    for k in range(steps):
        t = (k + 1) / steps
        jag: list[Any] = ARC_JAGS[k]
        q = [x + inward * (7 + (abs(x) - 7) * t), PYLON_TOP + 2 + jag[1], z + jag[0]]
        rod(p.neon, last, q, 0.3, N)
        last = q


def transformer(p: Any, at: Vec3) -> None:
    """Add the transformer (FB-TWIN-PYLON-03): a finned box with three bushings, its rotor on top.

    Cooling fins along its flanks, lit seams, three insulated bushings at its back.
    """
    x = at[0]
    z = at[2]
    base = DECK_TOP - 0.5
    p.hull.bevel_slab(
        model_outline(box_outline([-11, 11], [TRANSFORMER_AT[1] - 8, TRANSFORMER_AT[1] + 8])),
        [base, TRANSFORMER_TOP - 1, TRANSFORMER_TOP],
        [0, 1],
        SHADE["base"],
        None,
        SHADE["mid"],
    )
    for s in [-1, 1]:
        for k in range(5):
            fz = z - 6 + k * 3
            p.hull.box(
                [3, TRANSFORMER_TOP - base - 2, 0.7],
                SHADE["dark"],
                Placement([x + s * 12, base, fz]),
            )
        edge_strips(
            p.neon,
            [[x + s * 10.4, z - 7], [x + s * 10.4, z + 7]],
            0.5,
            [TRANSFORMER_TOP + 0.02, TRANSFORMER_TOP + 0.12],
            N,
        )
    for k in range(3):
        bx = x + (k - 1) * 6
        bz = z - 6.2
        p.hull.cylinder(
            1.3, 4.5, 6, SHADE["light"], Placement([bx, TRANSFORMER_TOP - 0.2, bz]), 0.8
        )
        p.neon.box([1, 0.8, 1], N, Placement([bx, TRANSFORMER_TOP + 4.3, bz]))


def _cowl(p: Any, s: float) -> None:
    """Draw the end cowling on the config side `s`: a ribbed hood over the platform's end."""
    outline = (
        box_outline([s * 60, s * 79], [1, 17.5])
        if s > 0
        else box_outline([s * 79, s * 60], [1, 17.5])
    )
    armour(p.hull, model_outline(outline), [DECK_TOP - 0.5, 12], SHADE["mid"], 2.4, SHADE["panel"])
    for k in range(4):
        x = s * (63 + k * 4.5)
        rod(p.hull, pt(x, 2, 11.6), pt(x, 16.5, 11.6), 0.45, SHADE["dark"])
    edge_strips(p.neon, [[-s * 61, -9], [-s * 78, -9]], 0.6, [12, 12.2], N)


def draw_cowls(p: Any) -> None:
    """Draw both end cowlings (the `end-cowls` region, FB-TWIN-PYLON-05)."""
    _cowl(p, 1)
    _cowl(p, -1)


def draw_bus_covers(p: Any) -> None:
    """Draw both bus covers (the `bus-covers` region): ribbed plates over the bus bars."""
    for s in [-1, 1]:
        xs = [s * 13.5, s * 29.5] if s > 0 else [s * 29.5, s * 13.5]
        outline = box_outline(xs, [-18.5, -1.5])
        armour(
            p.hull, model_outline(outline), [DECK_TOP - 0.5, 11], SHADE["base"], 1.6, SHADE["panel"]
        )
        for k in range(3):
            y = -15 + k * 5.5
            p.hull.box([12, 0.6, 1.2], SHADE["dark"], Placement(pt(s * 21.5, y, 11)))
        edge_strips(p.neon, [[-s * 14.5, 1.8], [-s * 28.5, 1.8]], 0.5, [11, 11.2], N)


def draw_prow_plate(p: Any) -> None:
    """Draw the prow plate (the `prow-plate` region): a wedge of armour over the platform's prow."""
    outline = [[-PROW[0], -19], [PROW[0], -19], [PROW[0] - 3, PROW[1]], [-PROW[0] + 3, PROW[1]]]
    armour(p.hull, model_outline(outline), [DECK_TOP - 1.5, 11], SHADE["mid"], 2, SHADE["panel"])
    edge_strips(
        p.neon,
        [[-PROW[0] + 3.5, -PROW[1] - 0.6], [PROW[0] - 3.5, -PROW[1] - 0.6]],
        0.6,
        [9.6, 10],
        N,
    )
    plate(p.hull, model_outline(box_outline([-5, 5], [-28, -22])), 11, SHADE["light"], 0.4)


def draw_hatch(p: Any) -> None:
    """Draw the hatch over the capacitor's rotor (BOSS-58): an octagonal cap, a lit seam."""
    at = pt(CAP_ROTOR_AT[0], CAP_ROTOR_AT[1], 0)
    cap = [
        [
            5.8 * math.cos(math.pi / 8 + k * math.pi / 4),
            5.8 * math.sin(math.pi / 8 + k * math.pi / 4),
        ]
        for k in range(8)
    ]
    p.hull.bevel_slab(
        cap, [CAP_TOP - 0.4, CAP_TOP + 0.6, CAP_TOP + 1.4], [0, 0.6], SHADE["panel"], Placement(at)
    )
    p.neon.ring(5.6, 0.3, 8, N, Placement([at[0], CAP_TOP + 0.7, at[2]], math.pi / 8))


def draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a lit collar round the opening the rotor rises from."""
    p.neon.ring(5.5, 0.4, 12, N, Placement(pt(CAP_ROTOR_AT[0], CAP_ROTOR_AT[1], CAP_TOP)))


def pylon_armour() -> Any:
    """Return the Twin Pylon's armour drawings by region id (`drawing.armour`, D-254)."""
    return {
        "end-cowls": {"whole": draw_cowls},
        "bus-covers": {"whole": draw_bus_covers},
        "prow-plate": {"whole": draw_prow_plate},
        "rotor-hatch": {"whole": draw_hatch, "frame": draw_hatch_frame},
    }

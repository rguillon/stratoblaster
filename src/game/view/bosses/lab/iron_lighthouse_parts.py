# Copyright (c) 2026 Renaud Guillon
"""MB-IRON-LIGHTHOUSE-03 to MB-IRON-LIGHTHOUSE-05: the Iron Lighthouse's parts and armour.

Logical pixels, nose +Z, Y up (towards the camera); shapes are given in config coordinates (X
right, Y up the screen) and turned into model space here. Its buttresses and its dynamo house (its
parts), its two deck leaves (moving pieces, BOSS-45: drawn flat, they drop open), the cottages'
roofs, the landing stage's hatch and the lantern's dome (hatches over its late guns, BOSS-58).
Riveted iron, painted bands and lamp-yellow light lines: a machine, not a creature (the Lab's fifth
round, user request 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.iron_lighthouse import (
    BOW_AT,
    BOW_TOP,
    CASEMATE_AT,
    CASEMATE_TOP,
    COTTAGE_AT,
    COTTAGE_HALF,
    COTTAGE_RIDGE,
    COTTAGE_WALL,
    DECK,
    DECK_LOW,
    DOME_R,
    DYNAMO_AT,
    LANTERN_TOP,
    LEAF_X,
    LEAF_Y,
    PLATFORM_R,
    TOWER_AT,
    leaf_outline,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.final_boss_greebles import SHADE, rect
from game.view.bosses.final_boss_shapes import edge_strips
from game.view.enemies.enemy_shapes import decal
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["iron-lighthouse"]
# Its paint: the tower's pale bands and its dark ones, the cottages' whitewash, the roofs' slate.
PALE = SHADE["pale"]
BAND = [0.13, 0.12, 0.12]
WASH = [0.24, 0.235, 0.22]
SLATE = [0.07, 0.075, 0.09]
IRON = SHADE["base"]
RIVET = SHADE["light"]
# The deck plates' top: dark, oiled iron.
DECK_TOP = [0.085, 0.085, 0.095]


def pt(x: float, y: float) -> list[float]:
    """Return the config point `(x, y)` as a model outline point `[x, z]`."""
    return [-x, -y]


def model_outline(outline: list[Any]) -> list[list[float]]:
    """Return a config outline as a model outline."""
    return [pt(q[0], q[1]) for q in outline]


def beam(p: Any, a: list[Any], b: list[Any], size: list[Any], color: Any) -> None:
    """Add a box beam from the config point `a` to `b` (seen from above): `[width, low, high]`."""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    length = math.hypot(dx, dy)
    yaw = math.atan2(-dx, -dy)
    mid = boss_point((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, size[1])
    p.hull.box([size[0], size[2] - size[1], length], color, Placement(mid, yaw), SHADE["panel"])


def rivet_row(p: Any, a: list[Any], b: list[Any], count: int, y: float) -> None:
    """Add `count` rivets from the config point `a` to `b`, at height `y`."""
    for k in range(count):
        t = (k + 0.5) / count
        q = pt(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        decal(p.bare, rect(q, [0.7, 0.7], 0.785), y, RIVET)


def both_faces(builder: Any, corners: list[Any], color: Any) -> None:
    """Add a flat polygon seen from both sides (its corners either way round)."""
    builder.face(corners, color)
    builder.face([corners[len(corners) - 1 - k] for k in range(len(corners))], color)


def strut(p: Any, a: Vec3, b: Vec3, width: float, color: Any) -> None:
    """Add a square strut from the model point `a` to `b`, `width` thick."""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dz = b[2] - a[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    yaw = math.atan2(dx, dz)
    pitch = math.acos(max(-1, min(1, dy / max(length, 0.001))))
    p.hull.box([width, length, width], color, Placement(a, yaw, pitch))


def buttress(p: Any, at: Vec3) -> None:
    """Draw a buttress (MB-IRON-LIGHTHOUSE-03): a riveted iron pier on the deck leaf.

    Its casemate's armoured housing at its outer foot (its fixed row of three on top, BOSS-58), a
    flying arch of girders from it up to the tower's flank, lit seams and a warning lamp.
    """
    s = 1 if at[0] < 0 else -1
    cx = s * CASEMATE_AT[0]
    cy = CASEMATE_AT[1]
    # The casemate's housing: an iron block, bevelled, a darker armour skirt round its foot.
    outline = model_outline([
        [cx - 5, cy - 6],
        [cx + 5, cy - 6],
        [cx + 5, cy + 7],
        [cx - 5, cy + 7],
    ])
    p.flesh.bevel_slab(outline, [DECK, CASEMATE_TOP - 1.2, CASEMATE_TOP], [0, 0.9], IRON)
    p.hull.box([11.2, 1.2, 14.2], SHADE["dark"], Placement(boss_point(cx, cy + 0.5, DECK)))
    edge_strips(
        p.neon,
        [pt(cx - 4, cy - 6.05), pt(cx + 4, cy - 6.05)],
        0.5,
        [CASEMATE_TOP - 2.6, CASEMATE_TOP - 2],
        N,
    )
    rivet_row(p, [cx - 4, cy + 6.2], [cx + 4, cy + 6.2], 5, CASEMATE_TOP)
    # The flying arch: two girders from the housing's top up to the tower's flank, braced.
    for dy in [-3.5, 3.5]:
        a = boss_point(cx - s * 3, cy + 0.5 + dy, CASEMATE_TOP - 0.5)
        b = boss_point(s * 8.6, TOWER_AT[1] + dy * 0.6, 23)
        strut(p, a, b, 1.7, SHADE["mid"])
        mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 2.5, (a[2] + b[2]) / 2]
        strut(p, mid, [mid[0], DECK, mid[2]], 1.0, SHADE["dark"])
    lamp = boss_point(cx + s * 3.5, cy + 5, CASEMATE_TOP)
    p.hull.cylinder(0.9, 1.4, 6, SHADE["panel"], Placement(lamp))
    p.charge.cylinder(0.6, 0.8, 6, N, Placement([lamp[0], lamp[1] + 1.4, lamp[2]]))


def dynamo(p: Any, _at: Vec3) -> None:
    """Draw the dynamo house (MB-IRON-LIGHTHOUSE-03, no gun): the engine that lights the lamp.

    A riveted engine house, its big flywheel turning in a slot in its roof, two smoke stacks and a
    lit conduit to the tower's foot; lit windows down its flanks.
    """
    x = DYNAMO_AT[0]
    y = DYNAMO_AT[1]
    outline = model_outline([[x - 8, y - 6], [x + 8, y - 6], [x + 8, y + 7], [x - 8, y + 7]])
    p.flesh.bevel_slab(outline, [DECK, 14, 15.5], [0, 1.2], IRON)
    p.hull.box([17, 1.2, 14], SHADE["dark"], Placement(boss_point(x, y + 0.5, DECK)))
    # The flywheel: a dark disc on its edge, across the house, in a lit slot.
    wheel = boss_point(x - 2, y + 0.5, 15)
    p.bare.box([3.4, 0.2, 11], SHADE["dark"], Placement([wheel[0], 15.45, wheel[2]]))
    p.hull.cylinder(5.5, 1.6, 12, SHADE["light"], Placement(wheel, 0, 0, math.pi / 2))
    p.neon.ring(
        5.55, 0.4, 12, N, Placement([wheel[0] - 0.6, wheel[1], wheel[2]], 0, 0, math.pi / 2)
    )
    p.hull.cylinder(
        1.4,
        2.4,
        6,
        SHADE["panel"],
        Placement([wheel[0] - 1.2, wheel[1], wheel[2]], 0, 0, math.pi / 2),
    )
    # Two smoke stacks on its back corner, lit bands round their tops.
    for dx in [4.5, 6.8]:
        q = boss_point(x + dx, y + 4, 15.5)
        p.hull.cylinder(1.3, 7, 8, SHADE["mid"], Placement(q), 1.1)
        p.neon.ring(1.15, 0.4, 8, N, Placement([q[0], q[1] + 6.2, q[2]]))
        p.bare.cylinder(0.8, 0.1, 8, SHADE["dark"], Placement([q[0], q[1] + 7, q[2]]))
    # Lit windows down its flanks, a vent grille on its roof, the conduit to the tower.
    for side in [-1, 1]:
        for k in range(3):
            w = boss_point(x + side * 8.05, y - 3 + k * 4, 10)
            p.neon.box([0.3, 1.8, 1.6], N, Placement(w))
    for k in range(4):
        decal(p.bare, rect(pt(x + 4.5, y - 4 + k * 1.2), [5, 0.5]), 15.55, SHADE["light"])
    beam(p, [0, y - 6], [0, TOWER_AT[1] + 8], [2.2, DECK, DECK + 1.6], SHADE["mid"])
    p.neon.box([0.5, 0.3, 6], N, Placement(boss_point(0, y - 9.5, DECK + 1.6)))


def _leaf(side: float) -> Any:
    """Return the drawing of the deck leaf on `side` (+1 the config's right), flat, as drawn.

    Riveted deck plating, a rim band with its rivets and a lit line along the rim, the hinge's
    barrel along its inner edge and ribs underneath (seen as it drops open).
    """

    def draw(p: Any) -> None:
        outline = [[side * q[0], q[1]] for q in leaf_outline()]
        p.flesh.slab(model_outline(outline), [DECK_LOW, DECK], IRON, None, DECK_TOP)
        # Plate seams across it, rivets along them.
        for y in [-3, 7]:
            a = [side * (LEAF_X + 0.5), y]
            b = [side * (math.sqrt(PLATFORM_R * PLATFORM_R - y * y) - 0.5), y]
            decal(
                p.bare,
                rect(pt((a[0] + b[0]) / 2, y), [abs(b[0] - a[0]), 0.35]),
                DECK + 0.02,
                SHADE["dark"],
            )
            rivet_row(p, [a[0], y + 0.8], [b[0], y + 0.8], 6, DECK + 0.03)
        # The rim band: a lit line along the arc.
        arc = [pt(side * q[0] * 0.985, q[1] * 0.985) for q in leaf_outline()[1:8]]
        edge_strips(p.neon, arc, 0.55, [DECK, DECK + 0.25], N)
        edge_strips(
            p.hull,
            [pt(side * q[0], q[1]) for q in leaf_outline()[1:8]],
            1.2,
            [DECK_LOW - 0.6, DECK - 0.4],
            SHADE["dark"],
        )
        # The casemate's plinth (its buttress stands on it; its stump stays on it).
        plinth = boss_point(side * CASEMATE_AT[0], CASEMATE_AT[1] + 0.5, DECK)
        p.hull.box([8.4, CASEMATE_TOP - DECK - 0.2, 11.4], SHADE["dark"], Placement(plinth))
        # The hinge's barrel along its inner edge, and its knuckles.
        hinge = boss_point(side * LEAF_X, (LEAF_Y[0] + LEAF_Y[1]) / 2, DECK - 1.6)
        length = LEAF_Y[1] - LEAF_Y[0] - 2
        p.hull.cylinder(
            1.1,
            length,
            8,
            SHADE["mid"],
            Placement([hinge[0], hinge[1], hinge[2] + length / 2], 0, math.pi / 2),
        )
        for k in range(3):
            ky = LEAF_Y[0] + 3 + k * (length - 4) / 2
            q = boss_point(side * (LEAF_X + 1.2), ky, DECK)
            p.neon.box([0.8, 0.25, 1.4], N, Placement(q))
        # Ribs underneath, from the hinge out to the rim.
        for y in [-8, 4, 15]:
            a = [side * (LEAF_X + 1), y]
            b = [side * (math.sqrt(PLATFORM_R * PLATFORM_R - y * y) - 1.5), y]
            beam(p, a, b, [1.2, DECK_LOW - 1.2, DECK_LOW], SHADE["dark"])

    return draw


def _roof(side: float) -> Any:
    """Return the drawing of the cottage roof on `side`: a slate gable over the whitewashed walls.

    A chimney on its back slope, a lit ridge; it bursts off as the cottage's turret comes into use
    (BOSS-58).
    """

    def draw(p: Any) -> None:
        x = side * COTTAGE_AT[0]
        y = COTTAGE_AT[1]
        hx = COTTAGE_HALF[0] + 0.8
        hy = COTTAGE_HALF[1] + 0.8
        w = COTTAGE_WALL
        r = COTTAGE_RIDGE
        # Model corners: the ridge runs across the boss (config X).
        a = boss_point(x - hx, y - hy, w)
        b = boss_point(x + hx, y - hy, w)
        c = boss_point(x + hx, y, r)
        d = boss_point(x - hx, y, r)
        e = boss_point(x - hx, y + hy, w)
        f = boss_point(x + hx, y + hy, w)
        both_faces(p.hull, [a, d, c, b], SLATE)
        both_faces(p.hull, [f, c, d, e], SLATE)
        both_faces(p.hull, [b, c, f], WASH)
        both_faces(p.hull, [e, d, a], WASH)
        p.neon.box([2 * hx, 0.3, 0.5], N, Placement([c[0] + (d[0] - c[0]) / 2, r - 0.1, c[2]]))
        chimney = boss_point(x + side * 2.5, y + 2.2, w + 1)
        p.hull.box([1.8, 4.6, 1.8], BAND, Placement(chimney))
        p.neon.box([1.2, 0.3, 1.2], N, Placement([chimney[0], chimney[1] + 4.6, chimney[2]]))

    return draw


def _bow_hatch(p: Any) -> None:
    """Draw the landing stage's hatch (BOSS-58): an armoured octagonal lid, lit round its rim."""
    at = boss_point(BOW_AT[0], BOW_AT[1], 0)
    p.hull.lathe(
        [[5.4, DECK], [5.4, BOW_TOP + 0.6], [4.4, BOW_TOP + 1.6], [0, BOW_TOP + 1.9]],
        8,
        SHADE["mid"],
        Placement(at, math.pi / 8),
    )
    p.neon.ring(5.45, 0.35, 8, N, Placement([at[0], BOW_TOP, at[2]], math.pi / 8))
    p.hull.box([1.2, 0.8, 6], SHADE["dark"], Placement([at[0], BOW_TOP + 1.5, at[2]]))


def _dome(p: Any) -> None:
    """Draw the lantern's dome (BOSS-58): a ribbed cupola, a ventilator ball and a lit finial.

    It bursts off as the lantern's rotor comes into use, its last stage.
    """
    at = boss_point(TOWER_AT[0], TOWER_AT[1], 0)
    base = LANTERN_TOP
    p.hull.lathe(
        [
            [DOME_R, base],
            [DOME_R - 0.4, base + 1.2],
            [DOME_R - 1.8, base + 3.2],
            [2.2, base + 4.6],
            [1.4, base + 5],
        ],
        12,
        BAND,
        Placement([at[0], 0, at[2]]),
    )
    for k in range(6):
        a = k * math.pi / 3
        foot = [
            at[0] + math.cos(a) * (DOME_R - 0.1),
            base + 0.4,
            at[2] + math.sin(a) * (DOME_R - 0.1),
        ]
        top = [at[0] + math.cos(a) * 2.4, base + 4.5, at[2] + math.sin(a) * 2.4]
        both_faces(
            p.neon,
            [foot, top, [top[0], top[1] + 0.3, top[2]], [foot[0], foot[1] + 0.3, foot[2]]],
            N,
        )
    p.hull.lathe(
        [[0, base + 5], [1.4, base + 5.8], [1.4, base + 6.8], [0, base + 7.6]],
        8,
        SHADE["mid"],
        Placement([at[0], 0, at[2]]),
    )
    p.neon.cylinder(0.35, 2.4, 4, N, Placement([at[0], base + 7.5, at[2]]))


def _dome_frame(p: Any) -> None:
    """Draw what the dome leaves (BOSS-44): an iron collar round the lantern's open roof."""
    at = boss_point(TOWER_AT[0], TOWER_AT[1], 0)
    p.hull.ring(DOME_R, 0.9, 12, SHADE["dark"], Placement([at[0], LANTERN_TOP - 0.2, at[2]]))
    p.neon.ring(DOME_R + 0.05, 0.3, 12, N, Placement([at[0], LANTERN_TOP + 0.4, at[2]]))


def lighthouse_armour() -> Any:
    """Return the Iron Lighthouse's armour drawings by region id (`drawing.armour`, D-254)."""
    return {
        "leaf-right": {"whole": _leaf(1)},
        "leaf-left": {"whole": _leaf(-1)},
        "roof-left": {"whole": _roof(-1)},
        "roof-right": {"whole": _roof(1)},
        "bow-hatch": {"whole": _bow_hatch},
        "dome": {"whole": _dome, "frame": _dome_frame},
    }

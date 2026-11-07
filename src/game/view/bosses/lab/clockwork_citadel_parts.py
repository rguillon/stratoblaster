# Copyright (c) 2026 Renaud Guillon
"""FB-CLOCKWORK-CITADEL-03 to FB-CLOCKWORK-CITADEL-07: the Clockwork Citadel's parts and armour.

Logical pixels, nose +Z, Y up (towards the camera). Its parts: the front belfries (a brass crown
of four bell lanterns round each front tower's turret), the gear trains on their flank shelves, the
pendulum's bob (its rod a limb on its joint, BOSS-33) and the minute hand (it orbits, BOSS-34). Its
armour: the great wheels and the clock face's halves (moving pieces, BOSS-45), the cuckoo house,
the back towers' roofs and the rotor's hatch (hatches, BOSS-58). Stone, steel and brass with warm
light lines: a clock-tower fortress, not a creature (the Lab's fifth round, user request
2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.clockwork_citadel import (
    CENTRE,
    CUCKOO_AT,
    CUCKOO_HOUSE,
    FACE_RADIUS,
    FACE_TOP,
    HAND_LENGTH,
    PENDULUM_PIVOT,
    ROOF,
    ROOF_RADIUS,
    ROTOR_AT,
    ROTOR_HATCH,
    SHELF_TOP,
    TOWER_AT,
    TOWER_RADIUS,
    TOWER_TOP,
    WHEEL_AT,
    WHEEL_HEIGHTS,
    WHEEL_RADIUS,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.world_1_organic_kit import M
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["clockwork-citadel"]
# Its materials' shades: dressed stone, a darker course, brass, the dial's dark enamel.
STONE = [0.13, 0.125, 0.12]
COURSE = [0.09, 0.087, 0.083]
BRASS = [0.22, 0.18, 0.11]
ENAMEL = [0.06, 0.06, 0.07]
# The rod's height over the shelf it swings over, and the bob's lens.
ROD_HEIGHT = 11
BOB_PROFILE = [[6, 7.5], [9.6, 9.4], [10, 10.6], [9.2, 11.8], [5, 13], [0, 13.4]]


def pt(x: float, y: float) -> list[float]:
    """Return a config point `(x, y)` as a slab outline point (model X, Z)."""
    return [-x, -y]


def gear(p: Any, at: Vec3, radius: float, teeth: int, heights: list[Any], color: Any) -> None:
    """Add a flat gear wheel at `at` (model, its foot ignored) between `heights`.

    Its toothed rim (one slab, `teeth` teeth), a dark recess, three spokes and a lit hub.
    """
    h0 = heights[0]
    h1 = heights[1]
    star: list[list[float]] = []
    for k in range(2 * teeth):
        a = math.pi * k / teeth
        r = radius + 0.9 if k % 2 == 0 else radius
        star.append([at[0] + math.cos(a) * r, at[2] + math.sin(a) * r])
    p.hull.slab(star, [h0, h1], color)
    p.bare.cylinder(radius - 1.4, 0.12, teeth, M.dark, Placement([at[0], h1, at[2]]))
    for k in range(3):
        p.hull.box(
            [0.8, 0.4, 2 * radius - 2.4],
            color,
            Placement([at[0], h1, at[2]], k * math.pi / 3),
        )
    p.hull.cylinder(radius * 0.25 + 0.6, 0.6, 8, M.panel, Placement([at[0], h1, at[2]]))
    p.neon.cylinder(radius * 0.18 + 0.3, 0.3, 6, N, Placement([at[0], h1 + 0.6, at[2]]))


def belfry(p: Any, at: Vec3) -> None:
    """Draw a front belfry (FB-CLOCKWORK-CITADEL-04): a brass crown on its tower, four lanterns.

    A brass ring round the drum's top, a bell lantern at four points round it (posts, a domed cap,
    the bell hanging inside, lit), its twin turret in the middle (BOSS-58).
    """
    x = at[0]
    z = at[2]
    r = TOWER_RADIUS
    p.hull.lathe(
        [[r + 0.8, TOWER_TOP - 1.5], [r + 0.8, TOWER_TOP + 0.8], [r - 1.2, TOWER_TOP + 1.2]],
        12,
        BRASS,
        Placement([x, 0, z]),
        False,
    )
    p.neon.ring(r + 0.85, 0.35, 12, N, Placement([x, TOWER_TOP - 0.4, z]))
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        c = [x + math.cos(a) * (r - 1.6), TOWER_TOP + 1.2, z + math.sin(a) * (r - 1.6)]
        for j in range(4):
            b = j * math.pi / 2 + math.pi / 4
            p.hull.box(
                [0.6, 4.2, 0.6],
                M.base,
                Placement([c[0] + math.cos(b) * 1.8, c[1], c[2] + math.sin(b) * 1.8]),
            )
        p.hull.lathe(
            [[2.9, c[1] + 4.2], [2.6, c[1] + 5], [1.2, c[1] + 6.4], [0, c[1] + 7.2]],
            8,
            BRASS,
            Placement([c[0], 0, c[2]]),
        )
        p.hull.lathe(
            [[1.5, c[1] + 0.8], [1.2, c[1] + 2.4], [0, c[1] + 4]],
            8,
            BRASS,
            Placement([c[0], 0, c[2]]),
        )
        p.charge.box([0.6, 0.6, 0.6], N, Placement([c[0], c[1] + 7.2, c[2]]))


def gear_train(p: Any, at: Vec3) -> None:
    """Draw a gear train on its flank shelf (FB-CLOCKWORK-CITADEL-06): no gun.

    A great brass wheel and two pinions meshing round it, their arbors in a steel bridge across.
    """
    x = at[0]
    z = at[2]
    out = 1 if x < 0 else -1
    h = [SHELF_TOP, SHELF_TOP + 1.6]
    gear(p, [x, 0, z], 7.5, 14, h, BRASS)
    gear(p, [x + out * 2.5, 0, z + 10.5], 3.6, 8, [h[0] + 1.4, h[1] + 1.4], BRASS)
    gear(p, [x - out * 6.5, 0, z - 9], 4.2, 9, [h[0] + 0.8, h[1] + 0.8], BRASS)
    p.hull.box([3, 1, 24], M.panel, Placement([x - out * 1.5, h[1] + 2.4, z], -out * 0.25), M.base)
    for dz in [-9, 0, 9]:
        p.hull.cylinder(
            0.7, 4.2, 6, M.base, Placement([x - out * 1.5 + out * 0.25 * dz, h[0], z + dz])
        )
    p.neon.box([0.4, 0.4, 20], N, Placement([x - out * 1.5, h[1] + 3.4, z], -out * 0.25))


def bob(p: Any, at: Vec3) -> None:
    """Draw the pendulum's bob (FB-CLOCKWORK-CITADEL-07): a brass lens, a lit rosette, its clamp."""
    x = at[0]
    z = at[2]
    p.hull.lathe(BOB_PROFILE, 16, BRASS, Placement([x, 0, z]))
    p.neon.ring(10.05, 0.4, 16, N, Placement([x, 10.2, z]))
    for k in range(6):
        a = k * math.pi / 3
        q = [x + math.cos(a) * 3.2, 12.9, z + math.sin(a) * 3.2]
        p.neon.box([0.5, 0.3, 2.6], N, Placement(q, -a + math.pi / 2))
    p.hull.box([3.4, 2.2, 4], M.panel, Placement([x, 12.6, z + 8.6]), M.base)


def _rod(p: Any) -> None:
    """Draw the pendulum's rod (a limb on its joint): steel, lit, from its pivot to the bob."""
    a = boss_point(PENDULUM_PIVOT[0], PENDULUM_PIVOT[1], ROD_HEIGHT)
    length = 76 - 9 - PENDULUM_PIVOT[1]
    p.hull.box([1.6, 1.2, length], M.panel, Placement([a[0], ROD_HEIGHT, a[2] - length / 2]))
    p.neon.box([0.4, 0.3, length - 2], N, Placement([a[0], ROD_HEIGHT + 1.2, a[2] - length / 2]))
    p.hull.cylinder(2.2, 2.4, 8, M.base, Placement([a[0], ROD_HEIGHT - 0.6, a[2]]))


def pendulum_limbs() -> Any:
    """Return the pendulum's rod, a limb on its joint that goes with the bob (BOSS-33)."""
    return {"pendulum": {"draw": _rod, "part": "pendulum"}}


def minute_hand(p: Any, _at: Vec3) -> None:
    """Draw the minute hand (FB-CLOCKWORK-CITADEL-03): an ornate blued-steel hand, no gun.

    A ring round the centre boss, a counterweight tail, a long tapered blade with a pierced lozenge
    and a spade tip, a lit line along it; drawn pointing at six o'clock (it orbits).
    """
    h0 = CENTRE[1]
    h1 = CENTRE[1] + 0.9
    p.hull.lathe([[4.6, h0], [4.6, h1]], 10, M.panel, Placement([0, 0, 0]), False)
    p.hull.lathe([[3.2, h1], [4.6, h1]], 10, M.panel, Placement([0, 0, 0]), False)
    blade = [
        pt(-1.6, -4),
        pt(-2.6, -12),
        pt(-1.2, -21),
        pt(-3.4, -25),
        pt(0, -HAND_LENGTH),
        pt(3.4, -25),
        pt(1.2, -21),
        pt(2.6, -12),
        pt(1.6, -4),
    ]
    p.hull.slab(blade, [h0, h1], M.panel, None, M.base)
    tail = [pt(-1.5, 4), pt(-3.6, 9), pt(0, 12.5), pt(3.6, 9), pt(1.5, 4)]
    p.hull.slab(tail, [h0, h1], M.panel, None, M.base)
    p.neon.box([0.5, 0.3, HAND_LENGTH - 9], N, Placement(boss_point(0, -(HAND_LENGTH + 5) / 2, h1)))
    p.charge.box([1.6, 0.4, 1.6], N, Placement(boss_point(0, -25, h1), math.pi / 4))
    p.bare.box([1.4, 0.2, 3.2], ENAMEL, Placement(boss_point(0, -15, h1)))


# The armour: drawings of its moving pieces and hatches.


def wheel(side: float) -> Any:
    """Return the drawing of the great wheel on `side` (+1 the config's right), as drawn."""

    def draw(p: Any) -> None:
        at = boss_point(side * WHEEL_AT[0], WHEEL_AT[1], 0)
        gear(p, at, WHEEL_RADIUS - 0.6, 18, WHEEL_HEIGHTS, BRASS)
        p.neon.ring(
            WHEEL_RADIUS - 2.4, 0.3, 18, N, Placement([at[0], WHEEL_HEIGHTS[1] + 0.05, at[2]])
        )

    return draw


def face(side: float) -> Any:
    """Return the drawing of the clock face's half on `side` (+1 the config's right), as drawn.

    Dark enamel in a brass bezel, lit hour bars (doubled at twelve, three, six and nine), minute
    a brass dot between them, a brass chapter ring, the latch bars along its cut edge.
    """

    def draw(p: Any) -> None:
        r = FACE_RADIUS
        n = 12
        disc: list[list[float]] = []
        bezel: list[list[float]] = []
        inner: list[list[float]] = []
        for k in range(n + 1):
            a = -math.pi / 2 + math.pi * k / n
            disc.append(pt(side * r * math.cos(a), r * math.sin(a)))
            bezel.append(pt(side * (r + 0.6) * math.cos(a), (r + 0.6) * math.sin(a)))
            inner.append(pt(side * (r - 2.2) * math.cos(a), (r - 2.2) * math.sin(a)))
        p.hull.slab(disc, [ROOF, FACE_TOP], M.base, None, ENAMEL)
        ring = list(bezel)
        ring.extend([inner[n - k] for k in range(n + 1)])
        p.hull.slab(ring, [FACE_TOP - 0.6, FACE_TOP + 0.9], BRASS)
        for hour in range(7):
            a = hour * math.pi / 6
            c = math.sin(a) * side
            s = math.cos(a)
            yaw = math.atan2(-c, -s)
            bars = [-0.9, 0.9] if hour % 3 == 0 else [0]
            for b in bars:
                q = boss_point(c * 26.5 - s * b, s * 26.5 + c * b, FACE_TOP)
                p.neon.box([0.7, 0.25, 5], N, Placement(q, yaw))
            if hour < 6:
                am = a + math.pi / 12
                q = boss_point(side * math.sin(am) * 30.5, math.cos(am) * 30.5, FACE_TOP)
                p.hull.box([0.8, 0.2, 0.8], BRASS, Placement(q, -am * side))
        chapter: list[list[float]] = []
        for k in range(n + 1):
            a = -math.pi / 2 + math.pi * k / n
            chapter.append(pt(side * 21 * math.cos(a), 21 * math.sin(a)))
        for k in range(n):
            u = chapter[k]
            v = chapter[k + 1]
            dx = v[0] - u[0]
            dz = v[1] - u[1]
            p.hull.box(
                [0.5, 0.25, math.sqrt(dx * dx + dz * dz)],
                BRASS,
                Placement([(u[0] + v[0]) / 2, FACE_TOP, (u[1] + v[1]) / 2], math.atan2(dx, dz)),
            )
        for y in [-27, -15, 15, 27]:
            q = boss_point(side * 0.8, y, FACE_TOP)
            p.hull.box([1.6, 0.7, 3], M.panel, Placement(q))

    return draw


def _octagon_hatch_frame(at_cfg: list[Any], radius: float, height: float) -> Any:
    def draw(p: Any) -> None:
        at = boss_point(at_cfg[0], at_cfg[1], 0)
        p.hull.ring(radius, 0.9, 12, M.base, Placement([at[0], height, at[2]]))
        p.neon.ring(radius, 0.3, 12, N, Placement([at[0], height + 0.9, at[2]]))

    return draw


def tower_roof(side: float) -> Any:
    """Return the drawing of a back tower's roof on `side`: a slate cone over a bell, a finial.

    It bursts as the turret under it first comes into use (BOSS-58).
    """

    def draw(p: Any) -> None:
        at = boss_point(side * TOWER_AT[0], -TOWER_AT[1], 0)
        r = ROOF_RADIUS
        place = Placement([at[0], 0, at[2]], math.pi / 8)
        p.hull.lathe(
            [
                [r + 1, TOWER_TOP],
                [r + 1, TOWER_TOP + 1.2],
                [r * 0.5, TOWER_TOP + 7],
                [0, TOWER_TOP + 12],
            ],
            8,
            COURSE,
            place,
        )
        for k in range(4):
            a = k * math.pi / 2 + math.pi / 8
            foot = [at[0] + math.cos(a) * r, TOWER_TOP + 1.3, at[2] + math.sin(a) * r]
            mid = [at[0] + math.cos(a) * r * 0.5, TOWER_TOP + 7.1, at[2] + math.sin(a) * r * 0.5]
            p.neon.face(
                [foot, mid, [mid[0], mid[1] + 0.4, mid[2]], [foot[0], foot[1] + 0.4, foot[2]]], N
            )
        p.hull.cylinder(0.4, 3, 4, BRASS, Placement([at[0], TOWER_TOP + 11.5, at[2]]))
        p.neon.box([0.8, 0.8, 0.8], N, Placement([at[0], TOWER_TOP + 14.4, at[2]]))

    return draw


def cuckoo_house(p: Any) -> None:
    """Draw the cuckoo house over the gate (BOSS-58): a gabled brass-trimmed house, its round door.

    It bursts as the cuckoo gun under it first comes into use.
    """
    at = boss_point(CUCKOO_AT[0], CUCKOO_AT[1], ROOF)
    w = CUCKOO_HOUSE[0]
    d = CUCKOO_HOUSE[1]
    eave = CUCKOO_HOUSE[2] - 4
    p.flesh.box([2 * w, eave - ROOF, 2 * d], STONE, Placement(at), COURSE)
    for s in [-1, 1]:
        p.hull.face(
            [
                [at[0] + s * (w + 0.8), eave, at[2] - d - 0.6],
                [at[0] + s * (w + 0.8), eave, at[2] + d + 0.6],
                [at[0], CUCKOO_HOUSE[2], at[2] + d + 0.6],
                [at[0], CUCKOO_HOUSE[2], at[2] - d - 0.6],
            ]
            if s > 0
            else [
                [at[0], CUCKOO_HOUSE[2], at[2] - d - 0.6],
                [at[0], CUCKOO_HOUSE[2], at[2] + d + 0.6],
                [at[0] + s * (w + 0.8), eave, at[2] + d + 0.6],
                [at[0] + s * (w + 0.8), eave, at[2] - d - 0.6],
            ],
            BRASS,
        )
    door = [at[0], ROOF + 2.5, at[2] + d + 0.05]
    p.bare.cylinder(2, 0.2, 10, M.dark, Placement(door, 0, math.pi / 2))
    p.neon.ring(2.1, 0.3, 10, N, Placement(door, 0, math.pi / 2))
    p.neon.box([0.4, 0.4, 2 * d + 1.2], N, Placement([at[0], CUCKOO_HOUSE[2], at[2]]))


def _rotor_hatch(p: Any) -> None:
    """Draw the hatch over the rotor (BOSS-58): a domed brass lid on the roof's back, lit seam."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    r = ROTOR_HATCH
    p.hull.lathe(
        [[r, ROOF], [r, ROOF + 1], [r * 0.6, ROOF + 2.4], [0, ROOF + 2.8]],
        8,
        BRASS,
        Placement([at[0], 0, at[2]], math.pi / 8),
    )
    p.neon.ring(r + 0.05, 0.3, 8, N, Placement([at[0], ROOF + 0.4, at[2]], math.pi / 8))


def citadel_armour() -> Any:
    """Return the Clockwork Citadel's armour drawings by region id (`drawing.armour`, D-254)."""
    back = [TOWER_AT[0], -TOWER_AT[1]]
    return {
        "wheel-right": {"whole": wheel(1)},
        "wheel-left": {"whole": wheel(-1)},
        "face-right": {"whole": face(1)},
        "face-left": {"whole": face(-1)},
        "cuckoo-house": {
            "whole": cuckoo_house,
            "frame": _octagon_hatch_frame(CUCKOO_AT, CUCKOO_HOUSE[0], ROOF),
        },
        "roof-left": {
            "whole": tower_roof(-1),
            "frame": _octagon_hatch_frame([-back[0], back[1]], ROOF_RADIUS, TOWER_TOP),
        },
        "roof-right": {
            "whole": tower_roof(1),
            "frame": _octagon_hatch_frame(back, ROOF_RADIUS, TOWER_TOP),
        },
        "rotor-hatch": {
            "whole": _rotor_hatch,
            "frame": _octagon_hatch_frame(ROTOR_AT, ROTOR_HATCH, ROOF),
        },
    }

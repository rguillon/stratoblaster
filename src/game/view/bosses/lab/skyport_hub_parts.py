# Copyright (c) 2026 Renaud Guillon
"""FB-SKYPORT-HUB-03 to FB-SKYPORT-HUB-05: the Skyport Hub's parts, runways and armour.

Logical pixels, nose +Z, Y up (towards the camera); shapes are given in config coordinates (X
right, Y up the screen) and turned into model space here. Its runway-end batteries, fuel depots
and radar mast (its parts), its runways (the rear ones are moving pieces, BOSS-45), its terminal's
roof halves (moving pieces) and the hatches over its late guns (BOSS-58). Dark metal decks, pale
runway markings and aqua light lines: a machine, not a creature (the Lab's fifth round, user
request 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.skyport_hub import (
    BATTERY_TOP,
    DECK,
    DECK_LOW,
    FAN_OUT,
    FAN_R,
    ROOF,
    RUNWAY_END,
    RUNWAY_HALF,
    RUNWAY_ROOT,
    TERMINAL,
    roof_outline,
    runway_outline,
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


N = BOSS_LOOK.neon["skyport-hub"]
DEG = math.pi / 180
# Its paint: the runways' dark tarmac and their pale markings, the tanks' pale skins.
TARMAC = [0.075, 0.08, 0.085]
MARK = SHADE["pale"]
TANK = [0.2, 0.21, 0.22]


def pt(x: float, y: float) -> list[float]:
    """Return the config point `(x, y)` as a model outline point `[x, z]`."""
    return [-x, -y]


def mpt(q: list[Any]) -> list[float]:
    """Return the config point `q` as a model outline point."""
    return pt(q[0], q[1])


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


def runway(p: Any, deg: float) -> None:
    """Draw the runway heading `deg` (FB-SKYPORT-HUB-02), with the lift fan under its end.

    Dark tarmac on a metal deck, a dashed pale centre line, threshold stripes and a number block at
    its end, lit edge lights down both sides, a dark girder keel under it; the lift fan's duct
    (its lit lip; the blades spin on the rig) past its end (FB-SKYPORT-HUB-06).
    """
    c = math.cos(deg * DEG)
    s = math.sin(deg * DEG)
    nx = -s
    ny = c

    def at(out: float, side: float) -> list[float]:
        return [out * c + side * nx, out * s + side * ny]

    yaw = math.atan2(c, s)
    p.flesh.slab(model_outline(runway_outline(deg)), [DECK_LOW, DECK], SHADE["base"], None, TARMAC)
    # The keel under it.
    beam(
        p, at(RUNWAY_ROOT + 2, 0), at(RUNWAY_END - 2, 0), [5, DECK_LOW - 3, DECK_LOW], SHADE["dark"]
    )
    # Centre line dashes, threshold stripes, edge lights.
    for k in range(6):
        q = at(RUNWAY_ROOT + 10 + k * 8, 0)
        decal(p.bare, rect(pt(q[0], q[1]), [0.6, 4], yaw), DECK + 0.03, MARK)
    for k in range(4):
        q = at(RUNWAY_END - 3, (k - 1.5) * 3.2)
        decal(p.bare, rect(pt(q[0], q[1]), [1.4, 5], yaw), DECK + 0.03, MARK)
    q = at(RUNWAY_END - 10, 0)
    decal(p.bare, rect(pt(q[0], q[1]), [4, 2.4], yaw), DECK + 0.03, MARK)
    for side in [-1, 1]:
        for k in range(8):
            q = at(RUNWAY_ROOT + 6 + k * 8.5, side * (RUNWAY_HALF - 0.8))
            decal(p.neon, rect(pt(q[0], q[1]), [0.8, 0.8], yaw), DECK + 0.05, N)
        edge_strips(
            p.hull,
            [mpt(at(RUNWAY_ROOT, side * RUNWAY_HALF)), mpt(at(RUNWAY_END, side * RUNWAY_HALF))],
            0.9,
            [DECK - 1, DECK + 0.35],
            SHADE["mid"],
        )
    # The lift fan's duct past its end.
    f = at(FAN_OUT, 0)
    fan = boss_point(f[0], f[1], 0)
    lip = DECK - 0.5
    p.hull.lathe(
        [
            [FAN_R, DECK_LOW - 3],
            [FAN_R + 1.6, DECK_LOW - 2.4],
            [FAN_R + 1.6, lip - 0.6],
            [FAN_R + 0.6, lip],
            [FAN_R, lip - 0.4],
        ],
        14,
        SHADE["base"],
        Placement([fan[0], 0, fan[2]]),
        False,
    )
    p.neon.ring(FAN_R + 0.9, 0.3, 14, N, Placement([fan[0], lip, fan[2]]))
    for k in range(3):
        b = k * math.pi * 2 / 3 + yaw
        mid = [fan[0] + math.cos(b) * FAN_R / 2, DECK_LOW - 2.6, fan[2] + math.sin(b) * FAN_R / 2]
        p.hull.box([1, 1, FAN_R], SHADE["dark"], Placement(mid, math.pi / 2 - b))
    p.hull.cylinder(2, 3.5, 8, SHADE["panel"], Placement([fan[0], DECK_LOW - 3.5, fan[2]]), 1.4)


def battery(p: Any, at: Vec3) -> None:
    """Draw a runway-end battery (FB-SKYPORT-HUB-03): an armoured emplacement over the threshold.

    A bevelled blast wall wrapped round its back and sides, ammunition lockers, a lit band; its
    fixed row of three barrels stands on the plinth in it (BOSS-58), pointing down the runway.
    """
    x = -at[0]
    y = -at[2]
    s = 1 if x > 0 else -1
    yaw = math.atan2(-s * 1, 1)
    ring = []
    for k in range(9):
        a = (k * 30 - 120) * DEG
        ring.append([math.cos(a) * 8.5, math.sin(a) * 8.5])
    for k in range(9):
        a = (120 - k * 30) * DEG
        ring.append([math.cos(a) * 5.8, math.sin(a) * 5.8])
    # Turn it so its open side faces out along the runway (the gun's way).
    out = math.atan2(-1, s) - math.pi
    ca = math.cos(out)
    sa = math.sin(out)
    wall = [[x + q[0] * ca - q[1] * sa, y + q[0] * sa + q[1] * ca] for q in ring]
    p.flesh.bevel_slab(
        model_outline(wall), [DECK, BATTERY_TOP + 1.2, BATTERY_TOP + 2.4], [0, 0.8], SHADE["mid"]
    )
    edge_strips(p.neon, model_outline(wall[1:8]), 0.5, [BATTERY_TOP + 2.4, BATTERY_TOP + 2.6], N)
    for k in [2, 6]:
        q = wall[k + 9]
        p.hull.box(
            [2.2, 2.4, 1.6],
            SHADE["panel"],
            Placement(boss_point(q[0] * 0.5 + x * 0.5, q[1] * 0.5 + y * 0.5, DECK), yaw),
        )
    p.hull.cylinder(5.2, BATTERY_TOP - DECK, 10, SHADE["base"], Placement(boss_point(x, y, DECK)))
    p.neon.ring(5.25, 0.35, 10, N, Placement(boss_point(x, y, BATTERY_TOP - 1)))


def depot(p: Any, at: Vec3) -> None:
    """Draw a fuel depot (FB-SKYPORT-HUB-03, no gun): three round tanks in a bunded yard.

    Pale tanks with domed tops and lit bands, a low bund wall round them, a pipe rack to the apron.
    """
    x = -at[0]
    y = -at[2]
    s = 1 if x > 0 else -1
    yard = model_outline([[x - 10, y - 8], [x + 10, y - 8], [x + 10, y + 8], [x - 10, y + 8]])
    p.flesh.bevel_slab(yard, [DECK, DECK + 1.6, DECK + 2.2], [0, 0.6], SHADE["mid"])
    spots = [[x - 4.5, y - 3.5, 4.4], [x + 4.5, y - 3, 4], [x + s * 1, y + 4, 4.4]]
    for t in spots:
        q = boss_point(t[0], t[1], DECK + 2.2)
        r = t[2]
        p.hull.lathe(
            [[r, 0], [r, 6], [r * 0.8, 7.4], [r * 0.4, 8.1], [0, 8.3]],
            12,
            TANK,
            Placement(q),
        )
        p.neon.ring(r + 0.05, 0.4, 12, N, Placement([q[0], q[1] + 4.2, q[2]]))
        p.hull.box([1, 1.2, 1], SHADE["dark"], Placement([q[0], q[1] + 8, q[2]]))
    beam(p, [x - s * 10, y + 1], [x - s * 19, y + 1], [1.6, DECK + 2, DECK + 3.4], SHADE["light"])
    for k in range(3):
        q = boss_point(x - s * (11 + k * 3), y + 1, DECK)
        p.hull.box([0.6, 2, 0.6], SHADE["dark"], Placement(q))
    decal(p.neon, rect(pt(x, y - 8.2), [16, 0.5]), DECK + 2.25, N)


def radar(p: Any, at: Vec3) -> None:
    """Draw the radar mast (FB-SKYPORT-HUB-03, no gun): a lattice tower on the back pier.

    A square plinth, four legs braced up to a platform with its lit rail; the dish turns on top of
    it (the rig).
    """
    x = -at[0]
    y = -at[2]
    base = boss_point(x, y, DECK)
    p.flesh.box([14, 2.2, 14], SHADE["mid"], Placement(base))
    top = 14
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            foot = [base[0] + sx * 5.5, DECK + 2.2, base[2] + sy * 5.5]
            head = [base[0] + sx * 3, top, base[2] + sy * 3]
            _strut(p, foot, head, 1.1, SHADE["light"])
    p.hull.cylinder(5, 1.2, 8, SHADE["panel"], Placement([base[0], top, base[2]], math.pi / 8))
    p.neon.ring(5.05, 0.35, 8, N, Placement([base[0], top + 0.9, base[2]], math.pi / 8))
    p.hull.cylinder(1.6, 3, 8, SHADE["dark"], Placement([base[0], top + 1.2, base[2]]))
    p.charge.box([1.2, 1.2, 1.2], N, Placement([base[0] + 4.2, top + 1.2, base[2] + 4.2]))


def _strut(p: Any, a: Vec3, b: Vec3, width: float, color: Any) -> None:
    """Add a square strut from the model point `a` to `b`, `width` thick."""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dz = b[2] - a[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    yaw = math.atan2(dx, dz)
    pitch = math.acos(max(-1, min(1, dy / max(length, 0.001))))
    p.hull.box([width, length, width], color, Placement(a, yaw, pitch))


def _rear_runway(side: float) -> Any:
    """Return the drawing of the rear runway on `side` (+1 the config's right), at rest."""

    def draw(p: Any) -> None:
        runway(p, 90 - side * 45)

    return draw


def _roof(side: float) -> Any:
    """Return the drawing of the terminal's roof half on `side`, closed, as drawn.

    A bevelled metal shell, glazed skylight strips lit along it, ribs across it and its slide
    shoes under its outer edge (FB-SKYPORT-HUB-11).
    """

    def draw(p: Any) -> None:
        outline = [[side * q[0], q[1]] for q in roof_outline()]
        p.flesh.bevel_slab(
            model_outline(outline),
            [ROOF[0], ROOF[1] - 1, ROOF[1]],
            [0, 1.4],
            SHADE["mid"],
            None,
            SHADE["panel"],
        )
        for k in range(3):
            x = side * (3.5 + k * 4)
            decal(
                p.bare,
                rect(pt(x, 0), [1.6, 2 * TERMINAL - 10 - k * 4]),
                ROOF[1] + 0.02,
                [0.05, 0.09, 0.1],
            )
            decal(p.neon, rect(pt(x, 0), [0.4, 2 * TERMINAL - 11 - k * 4]), ROOF[1] + 0.04, N)
        for dy in [-9, 9]:
            q = boss_point(side * (TERMINAL - 3), dy, ROOF[0] - 1.2)
            p.hull.box([4, 1.2, 2.4], SHADE["dark"], Placement(q))
        # The seam lit along its inner edge (where it splits).
        edge_strips(
            p.neon,
            [pt(side * 0.3, -TERMINAL + 2), pt(side * 0.3, TERMINAL - 2)],
            0.5,
            [ROOF[1] - 0.6, ROOF[1] + 0.05],
            N,
        )

    return draw


def _roof_frame(side: float) -> Any:
    """Return what the right (`side` +1) roof half leaves (BOSS-44): the terminal's open hall.

    A dark floor at the deck's height inside the walls, a lit edge, girders across it.
    """

    def draw(p: Any) -> None:
        outline = [[side * q[0], q[1]] for q in roof_outline()]
        p.bare.slab(model_outline(outline), [DECK, DECK + 0.3], SHADE["dark"])
        for dy in [-10, 10]:
            beam(
                p,
                [side * 1, dy],
                [side * (TERMINAL - 1), dy],
                [1, DECK + 0.3, DECK + 1.3],
                SHADE["base"],
            )
        decal(p.neon, rect(pt(side * (TERMINAL - 1.2), 0), [0.5, 12]), DECK + 0.35, N)

    return draw


def _lid(at: list[Any], radius: float, frame_shell: bool) -> Any:
    """Return the drawing of a hatch's lid round the config point `at` (BOSS-58).

    An armoured octagonal lid on the deck, a seam of light round it, a hazard bar across it.
    """

    def draw(p: Any) -> None:
        q = boss_point(at[0], at[1], 0)
        top = DECK + (1.8 if frame_shell else 1.4)
        p.hull.lathe(
            [
                [radius / math.cos(math.pi / 8), DECK - 0.2],
                [radius / math.cos(math.pi / 8), top - 0.6],
                [radius * 0.8, top],
                [0, top],
            ],
            8,
            SHADE["mid"],
            Placement([q[0], 0, q[2]], math.pi / 8),
        )
        p.neon.ring(
            radius / math.cos(math.pi / 8) + 0.05,
            0.3,
            8,
            N,
            Placement([q[0], DECK + 0.3, q[2]], math.pi / 8),
        )
        p.hull.box([radius * 1.4, 0.5, 1], SHADE["light"], Placement([q[0], top - 0.1, q[2]]))

    return draw


def hub_armour(hatches: list[Any]) -> Any:
    """Return the Skyport Hub's armour drawings by region id (`drawing.armour`, D-254).

    `hatches`: `[region id, at, radius]` of each hatch over a late gun.
    """
    result: Any = {
        "rear-runway-right": {"whole": _rear_runway(1)},
        "rear-runway-left": {"whole": _rear_runway(-1)},
        "roof-right": {"whole": _roof(1), "frame": _roof_frame(1)},
        "roof-left": {"whole": _roof(-1), "frame": _roof_frame(-1)},
    }
    for h in hatches:
        result[h[0]] = {"whole": _lid(h[1], h[2], h[0].startswith("silo"))}
    return result

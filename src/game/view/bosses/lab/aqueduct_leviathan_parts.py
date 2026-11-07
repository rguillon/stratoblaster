# Copyright (c) 2026 Renaud Guillon
"""FB-AQUEDUCT-LEVIATHAN-03, -10, -11: the Aqueduct Leviathan's parts and armour drawings.

Logical pixels, nose +Z, Y up (towards the camera). Its parts (the gun housings hung under its
middle arches, its lift engines' ducts, its gate towers), and its armour: the sluice houses that
slide back, the channel's middle sections that swing forward, the keep's front cutwater, and the
hatches over its late guns.
"""

from game.config.bosses.lab.aqueduct_leviathan import (
    ABUTMENT,
    ABUTMENT_HALF,
    ARCH_GUN_H,
    CAP_HALF,
    CHANNEL_HALF,
    CHANNEL_TOP,
    CUT_GUN_AT,
    CUTWATER,
    CUTWATER_LOW,
    KEEP_LASER_AT,
    KEEP_LASER_H,
    LEAF,
    MISSILE_AT,
    OUTER_GUN_AT,
    PIER_TOP,
    PIER_TURRET_AT,
    ROTOR_AT,
    SHROUD_HALF,
    SHUTTER_HALF,
    SLUICE,
    SLUICE_TOP,
    SPRING,
    TOWER_TOP,
)
from game.view.bosses.lab.aqueduct_leviathan_kit import (
    COURSE,
    QUARTER,
    STONE,
    N,
    block,
    box_outline,
    channel,
    flat,
    hatch,
    hatch_frame,
    pt,
)
from game.view.bosses.world_1_organic_kit import M
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


# The lift engines' ducts: their radius, their band's foot and height.
DUCT_RADIUS = 8.5
DUCT_FOOT = 2.5
DUCT_HIGH = 3.5
ENGINE_Y = -40


def gun_housing(p: Any, x: float, crown: float) -> None:
    """Add the housing a fixed gun hangs from under an arch at `x`, up to the rib's `crown`.

    A squat armoured block, its gun on its top, a hanger up to the rib, lit seams.
    """
    block(p.hull, [x - 4.5, x + 4.5, -23.5, -16], [ARCH_GUN_H - 4.5, ARCH_GUN_H], M.panel)
    block(p.hull, [x - 2.5, x + 2.5, -17, -13.5], [ARCH_GUN_H - 1, crown], M.base)
    p.neon.box([8.4, 0.4, 0.4], N, Placement(pt(x, -23.4, ARCH_GUN_H - 1)))
    p.bare.cylinder(4.2, 0.5, 8, M.dark, Placement(pt(x, -20, ARCH_GUN_H - 0.3)))


def arch_gun(p: Any, at: Vec3) -> None:
    """Add a middle arch's gun housing (FB-AQUEDUCT-LEVIATHAN-03), the part, under its rib."""
    x = -at[0]
    gun_housing(p, x, SPRING + 12 - 0.5)


def engine(p: Any, at: Vec3) -> None:
    """Add a lift engine (FB-AQUEDUCT-LEVIATHAN-02): a ducted lift fan slung before a pier.

    A deep duct ring, a lit lip, two struts across it to the hub (its blades are the rig's), and a
    pylon back to the pier's cutwater.
    """
    x = -at[0]
    centre = pt(x, ENGINE_Y, DUCT_FOOT)
    p.hull.ring(DUCT_RADIUS, DUCT_HIGH, 12, M.panel, Placement(centre))
    p.hull.ring(DUCT_RADIUS + 1.2, DUCT_HIGH - 1, 12, M.base, Placement(centre))
    p.neon.ring(
        DUCT_RADIUS + 0.1, 0.5, 12, N, Placement([centre[0], DUCT_FOOT + DUCT_HIGH, centre[2]])
    )
    for k in [0, 1]:
        p.bare.box(
            [2 * DUCT_RADIUS, 0.8, 0.8],
            M.dark,
            Placement([centre[0], DUCT_FOOT + 1, centre[2]], k * QUARTER),
        )
    p.hull.cylinder(1.8, 3, 8, M.base, Placement([centre[0], DUCT_FOOT, centre[2]]))
    block(p.hull, [x - 2.5, x + 2.5, ENGINE_Y + DUCT_RADIUS - 0.5, -29], [DUCT_FOOT, 9], M.panel)
    p.neon.box([0.5, 0.4, 2], N, Placement(pt(x, -31, 9)))


def tower(p: Any, at: Vec3) -> None:
    """Add a gate tower (FB-AQUEDUCT-LEVIATHAN-02) on its abutment: crenellated, a beacon.

    A tall square tower, a lit band round it, merlons round its roof, a dark gate where the channel
    runs in, lit arrow slits and a beacon on its roof.
    """
    x = -at[0]
    side = 1 if x > 0 else -1
    x0 = ABUTMENT[0] + 2
    x1 = ABUTMENT[1] - 2
    b = [side * x0, side * x1] if side > 0 else [side * x1, side * x0]
    half = ABUTMENT_HALF - 2
    outline = box_outline([b[0], b[1], -half, half])
    p.hull.bevel_slab(
        outline, [PIER_TOP, TOWER_TOP - 1.5, TOWER_TOP], [0, 1.2], STONE, None, M.panel
    )
    for y in [-half, half]:
        p.neon.box([b[1] - b[0] - 2, 0.6, 0.4], N, Placement(pt(x, y, TOWER_TOP - 6)))
    merlon = [TOWER_TOP, TOWER_TOP + 2.5]
    for k in range(4):
        u = -half + 2 + k * (2 * half - 4) / 3
        v = b[0] + 2 + k * (b[1] - b[0] - 4) / 3
        for ym in [-half + 0.8, half - 0.8]:
            block(p.hull, [v - 1.2, v + 1.2, ym - 0.8, ym + 0.8], merlon, STONE)
        for xx in [b[0] + 0.8, b[1] - 0.8]:
            block(p.hull, [xx - 0.8, xx + 0.8, u - 1.2, u + 1.2], merlon, STONE)
    inner = side * x0
    block(
        p.bare,
        [inner - 0.6, inner + 0.6, -CHANNEL_HALF, CHANNEL_HALF],
        [PIER_TOP, CHANNEL_TOP + 3],
        M.dark,
    )
    for y in [-5, 0, 5]:
        p.neon.box([0.4, 3, 0.6], N, Placement(pt(side * x1 + side * 0.1, y, TOWER_TOP - 14)))
    beacon = pt(x, 0, TOWER_TOP)
    p.hull.cylinder(2.4, 2, 8, M.base, Placement(beacon))
    p.neon.cylinder(1.4, 3.5, 8, N, Placement([beacon[0], TOWER_TOP + 2, beacon[2]]), 0.5)


def _sluice(side: float) -> Any:
    """Return the drawing of the sluice house over the inner pier on `side`, as it rests.

    A gatehouse straddling the channel: stone walls, an iron roof with a ridge, a lit band, the
    great wheel of its gate on its front, dark slots where the channel runs through.
    """

    def draw(p: Any) -> None:
        b = [SLUICE[0], SLUICE[1]] if side > 0 else [-SLUICE[1], -SLUICE[0]]
        box = [b[0], b[1], SLUICE[2], SLUICE[3]]
        p.hull.bevel_slab(
            box_outline(box),
            [PIER_TOP, SLUICE_TOP - 2.5, SLUICE_TOP - 1.5],
            [0, 0.6],
            STONE,
            None,
            COURSE,
        )
        roof = [b[0] + 0.8, b[1] - 0.8, SLUICE[2] + 0.8, SLUICE[3] - 0.8]
        p.hull.bevel_slab(
            box_outline(roof),
            [SLUICE_TOP - 1.6, SLUICE_TOP - 0.8, SLUICE_TOP],
            [0, 2.5],
            M.panel,
            None,
            M.base,
        )
        xm = (b[0] + b[1]) / 2
        p.neon.box(
            [0.6, 0.4, SLUICE[3] - SLUICE[2] - 3],
            N,
            Placement(pt(xm, (SLUICE[2] + SLUICE[3]) / 2, SLUICE_TOP)),
        )
        p.neon.box(
            [b[1] - b[0] - 0.6, 0.6, 0.4], N, Placement(pt(xm, SLUICE[2] - 0.1, SLUICE_TOP - 6))
        )
        wheel = pt(xm, SLUICE[2], SLUICE_TOP - 9)
        p.hull.cylinder(3.2, 1, 10, M.panel, Placement(wheel, 0, -QUARTER))
        p.neon.ring(3.25, 0.5, 10, N, Placement([wheel[0], wheel[1], wheel[2] + 0.3], 0, -QUARTER))
        for x in [b[0] - 0.1, b[1] + 0.1]:
            block(
                p.bare,
                [x - 0.2, x + 0.2, -CHANNEL_HALF + 0.5, CHANNEL_HALF - 0.5],
                [PIER_TOP + 0.5, CHANNEL_TOP],
                M.dark,
            )

    return draw


def _leaf(side: float) -> Any:
    """Return the drawing of the channel's middle section on `side` (it swings forward).

    A stretch of the channel, its hinge pin at its outer front corner, a lit break at its keep end.
    """

    def draw(p: Any) -> None:
        x0 = LEAF[0] if side > 0 else -LEAF[1]
        x1 = LEAF[1] if side > 0 else -LEAF[0]
        channel(p, x0, x1)
        hinge = pt(side * LEAF[1], LEAF[2], 16.8)
        p.hull.cylinder(1.3, CHANNEL_TOP + 1 - 16.8, 8, M.panel, Placement(hinge))
        end = side * (LEAF[0] + 0.4)
        p.neon.box([0.5, 0.5, 2 * CHANNEL_HALF], N, Placement(pt(end, 0, CHANNEL_TOP - 0.2)))

    return draw


def _cutwater(p: Any) -> None:
    """Draw the keep pier's front cutwater (FB-AQUEDUCT-LEVIATHAN-11): a pointed stone cap.

    It bursts off as the channel breaks, baring the orb's well. A lit seam up its point.
    """
    outline = [flat(q[0], q[1]) for q in CUTWATER]
    p.hull.bevel_slab(
        outline, [CUTWATER_LOW, PIER_TOP - 1, PIER_TOP], [0, 0.8], STONE, None, COURSE
    )
    p.neon.box([0.6, 0.4, 5], N, Placement(pt(0, -27, PIER_TOP)))


def _add_pair(result: Any, base: str, at: list[Any], half: list[Any], heights: list[Any]) -> None:
    """Add the drawings of the hatches `base`-hatch-left/-right over mounts at `±at[0]`."""
    left = [-at[0], at[1]]
    result[base + "-hatch-left"] = {
        "whole": hatch(left, half, heights),
        "frame": hatch_frame(left, half, heights[0] + 0.3),
    }
    result[base + "-hatch-right"] = {
        "whole": hatch(at, half, heights),
        "frame": hatch_frame(at, half, heights[0] + 0.3),
    }


def aqueduct_armour() -> Any:
    """Return the drawings of its armour regions (FB-AQUEDUCT-LEVIATHAN-10, -11, BOSS-58)."""
    caps = [PIER_TOP - 0.3, PIER_TOP + 2.5]
    result: Any = {
        "sluice-right": {"whole": _sluice(1)},
        "sluice-left": {"whole": _sluice(-1)},
        "leaf-right": {"whole": _leaf(1)},
        "leaf-left": {"whole": _leaf(-1)},
        "cutwater": {"whole": _cutwater},
        "keep-shutter": {
            "whole": hatch(KEEP_LASER_AT, SHUTTER_HALF, [KEEP_LASER_H - 0.3, KEEP_LASER_H + 3.5]),
            "frame": hatch_frame(KEEP_LASER_AT, SHUTTER_HALF, KEEP_LASER_H),
        },
        "rotor-hatch": {
            "whole": hatch(ROTOR_AT, CAP_HALF, caps),
            "frame": hatch_frame(ROTOR_AT, CAP_HALF, PIER_TOP),
        },
    }
    _add_pair(result, "outer-gun", OUTER_GUN_AT, SHROUD_HALF, [ARCH_GUN_H - 0.3, ARCH_GUN_H + 3])
    _add_pair(result, "pier-turret", PIER_TURRET_AT, CAP_HALF, caps)
    _add_pair(result, "missile", MISSILE_AT, CAP_HALF, caps)
    _add_pair(result, "cut-gun", CUT_GUN_AT, CAP_HALF, caps)
    return result

# Copyright (c) 2026 Renaud Guillon
"""FB-SKY-ARSENAL-03, FB-SKY-ARSENAL-05, FB-SKY-ARSENAL-10, FB-SKY-ARSENAL-11: its pieces.

The Sky Arsenal's moving pieces (its top tier on its turntable, its four corner petals), its parts
(the gun decks' cowls, the bastions' cupolas, the ammunition crane) and the hatches it sheds.
Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.sky_arsenal import (
    BASTION_GUN_HEIGHT,
    CRANE_HEIGHT,
    DECK_GUN_HEIGHT,
    LOW_HALF,
    LOW_TOP,
    MID_TOP,
    MORTAR_AT,
    ORB_AT,
    PETAL_CUT,
    PETAL_Y,
    ROTOR_AT,
    TOP_HALF,
    TOP_TOP,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.final_boss_greebles import dish, rod
from game.view.bosses.world_1_organic_kit import M, polygon
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["sky-arsenal"]
# Plating a shade lighter than the panels, for the armour plates on the tiers.
PLATE = [0.2, 0.2, 0.235]


def xz(x: float, y: float) -> list[float]:
    """Return a config point `[x, y]` as a model outline point (XZ)."""
    return [-x, -y]


def _square(half: float) -> list[list[float]]:
    return [[-half, -half], [half, -half], [half, half], [-half, half]]


def _draw_top_tier(p: Any) -> None:
    """Draw the top tier (FB-SKY-ARSENAL-02), square on at rest: it turns on its turntable.

    A plated block with a lit band round it, a parapet, a pinnacle tower on each corner (they show
    its turn), embrasures in its walls and the seats of its gun decks' cowls.
    """
    h = TOP_HALF
    p.hull.bevel_slab(
        _square(h), [MID_TOP, MID_TOP + 3, TOP_TOP], [1.5, 1.2], M.base, None, M.panel
    )
    p.neon.box([h * 2 - 2.4, 0.6, h * 2 - 2.4], N, Placement([0, MID_TOP + 4.5, 0]))
    for k in range(4):
        yaw = k * math.pi / 2
        c = math.cos(yaw)
        s = math.sin(yaw)
        # The parapet along each edge, embrasures under it.
        q = [-(h - 1.6) * c, TOP_TOP - 0.2, (h - 1.6) * s]
        p.hull.box([1.4, 1.4, h * 2 - 6], M.panel, Placement(q, yaw), PLATE)
        for u in [-12, -4, 4, 12]:
            w = [-(h - 0.2) * c + u * s, MID_TOP + 6.5, (h - 0.2) * s + u * c]
            p.bare.box([0.6, 1.6, 2.4], M.dark, Placement(w, yaw))
    for sx in [-1, 1]:
        for sz in [-1, 1]:
            _pinnacle(p, [sx * (h - 3), TOP_TOP - 0.5, sz * (h - 3)], sx * sz > 0)
    # The rotor's well in the middle and lit strips out to the gun decks' seats.
    p.bare.cylinder(7.4, 0.5, 8, M.dark, Placement([0, TOP_TOP - 0.3, 0]))
    for sx in [-1, 1]:
        seat = boss_point(sx * 12, -11, 0)
        p.hull.cylinder(
            6.8,
            DECK_GUN_HEIGHT - TOP_TOP + 0.3,
            10,
            M.base,
            Placement([seat[0], TOP_TOP - 0.3, seat[2]]),
        )
        p.neon.box([0.5, 0.3, 9], N, Placement([seat[0], TOP_TOP, seat[2] - 11]))


def _pinnacle(p: Any, at: Vec3, flag: bool) -> None:
    """Add a pinnacle tower on a corner of the top tier: a lit ring, a spire, maybe a pennant.

    The pennants stream back along two of them, so the tier's turn shows (FB-SKY-ARSENAL-05).
    """
    x = at[0]
    y = at[1]
    z = at[2]
    p.hull.cylinder(4.2, 6, 8, M.panel, Placement(at, math.pi / 8), 3.4)
    p.neon.ring(3.75, 0.5, 8, N, Placement([x, y + 3.4, z], math.pi / 8))
    p.hull.cylinder(3.6, 4.5, 8, M.base, Placement([x, y + 6, z], math.pi / 8), 0.4)
    if not flag:
        dish(p, [x, y + 10.4, z], 3.6, [0.6, math.atan2(x, z)])
    if flag:
        p.hull.cylinder(0.35, 7, 4, M.dark, Placement([x, y + 9, z]))
        p.hull.slab([[x, z], [x + 6.5, z - 1.2], [x, z - 3]], [y + 15, y + 15.4], M.panel)
        p.neon.box([0.4, 0.5, 2.6], N, Placement([x + 0.6, y + 15, z - 1.5]))


def _petal(front: bool, s: float) -> Any:
    """Return the drawing of a corner petal: `front` or back, on side `s` (model X sign).

    A thick plated wedge in the lower tier's corner, armour plates on its top, a lit chevron along
    its inner edge, a bed for what rides it.
    """
    c = PETAL_CUT - LOW_HALF
    v = -1 if front else 1
    tri = [[c, v * LOW_HALF], [LOW_HALF, v * LOW_HALF], [LOW_HALF, v * c]]
    outline = [[s * q[0], -q[1]] for q in tri]
    y0 = PETAL_Y[0]
    y1 = PETAL_Y[1]

    def at(x: float, y: float, h: float) -> Vec3:
        return [s * x, h, -v * y]

    def draw(p: Any) -> None:
        p.hull.bevel_slab(outline, [y0, y1 - 3, y1], [4, 1.2], M.base, None, M.panel)
        inner = [[c + 4, LOW_HALF - 2], [LOW_HALF - 2, LOW_HALF - 2], [LOW_HALF - 2, c + 4]]
        p.hull.bevel_slab(
            [[s * q[0], -v * q[1]] for q in inner], [y1 - 0.2, y1 - 0.2, y1 + 0.8], [0, 0.6], PLATE
        )
        rod(p.neon, at(c + 2, LOW_HALF - 1, y1 + 0.1), at(LOW_HALF - 1, c + 2, y1 + 0.1), 0.35, N)
        # Rivet rows along its outer edges, and a ring bolted where its bastion or rack stands.
        for k in range(5):
            u = c + 6 + k * 6
            p.bare.box([0.8, 0.4, 0.8], M.panel, Placement(at(u, LOW_HALF - 0.8, y1 - 0.4)))
            p.bare.box([0.8, 0.4, 0.8], M.panel, Placement(at(LOW_HALF - 0.8, u, y1 - 0.4)))
        p.neon.ring(7.6, 0.4, 10, N, Placement(at(39, 39, y1 + 0.5)))
        if front:
            # The bastion's pedestal (what its gun leaves once destroyed stands on it).
            p.hull.cylinder(
                5.4, BASTION_GUN_HEIGHT - y1 + 0.2, 8, M.panel, Placement(at(39, 39, y1 - 0.2))
            )
        # Dark seams across its top plate, a lit wall face along its outer edges.
        for u in [26, 36]:
            p.bare.box([0.5, 0.3, 0.5], M.dark, Placement(at(u, LOW_HALF - 3, y1 + 0.8)))
        p.neon.box(
            [0.4, 0.6, LOW_HALF - c - 6],
            N,
            Placement(at(LOW_HALF + 0.05, (LOW_HALF + c) / 2, y1 - 2.4)),
        )
        p.neon.box(
            [LOW_HALF - c - 6, 0.6, 0.4],
            N,
            Placement(at((LOW_HALF + c) / 2, LOW_HALF + 0.05, y1 - 2.4)),
        )

    return draw


def petal_armour() -> dict[str, Any]:
    """Return the moving pieces' drawings by region id (`drawing.armour`); config right is -X."""
    return {
        "top-tier": {"whole": _draw_top_tier},
        "petal-front-right": {"whole": _petal(True, -1)},
        "petal-front-left": {"whole": _petal(True, 1)},
        "petal-back-right": {"whole": _petal(False, -1)},
        "petal-back-left": {"whole": _petal(False, 1)},
        "mortar-hatch": {"whole": _draw_mortar_hatches},
        "stern-hatch": {"whole": _draw_stern_hatch},
        "rotor-hatch": {"whole": _draw_rotor_hatch, "frame": _draw_rotor_frame},
    }


def _draw_mortar_hatches(p: Any) -> None:
    """Draw the mortars' hatches on the middle deck (FB-SKY-ARSENAL-10): split armoured lids."""
    for s in [-1, 1]:
        at = boss_point(s * MORTAR_AT[0], MORTAR_AT[1], 0)
        lid = [[at[0] + q[0], at[2] + q[1]] for q in _square(6.6)]
        p.hull.bevel_slab(lid, [MID_TOP, MID_TOP + 0.6, MID_TOP + 1.5], [0, 0.6], M.panel)
        p.neon.box([13, 0.3, 0.4], N, Placement([at[0], MID_TOP + 1.4, at[2]], math.pi / 4))
        p.bare.box([0.4, 0.3, 13], M.dark, Placement([at[0], MID_TOP + 1.4, at[2]], math.pi / 4))


def _draw_stern_hatch(p: Any) -> None:
    """Draw the stern plating over the orb's bay (FB-SKY-ARSENAL-11): a riveted double lid."""
    at = boss_point(ORB_AT[0], ORB_AT[1], 0)
    for s in [-1, 1]:
        lid = [[at[0] + s * q[0], at[2] + q[1]] for q in [[0.3, -7], [9.6, -7], [9.6, 8], [0.3, 8]]]
        p.hull.bevel_slab(lid, [LOW_TOP, LOW_TOP + 0.4, LOW_TOP + 1.4], [0, 0.6], PLATE)
        for k in range(3):
            p.bare.box(
                [0.8, 0.4, 0.8],
                M.panel,
                Placement([at[0] + s * 8, LOW_TOP + 1.2, at[2] - 4 + 4 * k]),
            )
    p.neon.box([0.5, 0.3, 14], N, Placement([at[0], LOW_TOP + 1.3, at[2] + 0.5]))


def _draw_rotor_hatch(p: Any) -> None:
    """Draw the hatch over the top rotor (BOSS-58): an armoured octagonal cap, lit round it."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.bevel_slab(
        polygon(8, 6.8),
        [TOP_TOP - 0.2, TOP_TOP + 0.3, TOP_TOP + 1.4],
        [0, 0.8],
        M.panel,
        Placement(at),
    )
    p.hull.bevel_slab(
        polygon(8, 4.4),
        [TOP_TOP + 1.4, TOP_TOP + 1.4, TOP_TOP + 2.4],
        [0, 0.6],
        M.base,
        Placement(at),
    )
    p.neon.ring(6.6, 0.25, 8, N, Placement([at[0], TOP_TOP + 1, at[2]], math.pi / 8))


def _draw_rotor_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the well the rotor rises out of."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.ring(6.2, 1.2, 16, M.base, Placement([at[0], TOP_TOP - 0.3, at[2]]))
    p.neon.ring(6.2, 0.3, 16, N, Placement([at[0], TOP_TOP + 0.7, at[2]]))


def deck_gun(p: Any, at: Vec3) -> None:
    """Add a gun deck's cowl (FB-SKY-ARSENAL-03): an armoured ring on the top tier, lit."""
    x = at[0]
    z = at[2]
    p.hull.bevel_slab(
        polygon(8, 7),
        [TOP_TOP - 0.3, TOP_TOP + 0.6, DECK_GUN_HEIGHT],
        [0, 0.6],
        M.panel,
        Placement([x, 0, z], math.pi / 8),
        M.base,
    )
    p.neon.ring(7.05, 0.4, 8, N, Placement([x, DECK_GUN_HEIGHT - 0.8, z], math.pi / 8))
    for dx in [-5, 5]:
        p.hull.box([1.4, 1.6, 3.4], M.base, Placement([x + dx, DECK_GUN_HEIGHT - 0.6, z]))


def bastion(p: Any, at: Vec3) -> None:
    """Add a bastion (FB-SKY-ARSENAL-03): an octagonal armoured cupola on its front petal, lit."""
    x = at[0]
    z = at[2]
    top = BASTION_GUN_HEIGHT
    y1 = PETAL_Y[1]
    p.hull.lathe(
        [[8.6, y1 - 0.4], [8.6, y1 + 1.2], [7.4, top - 1.2], [6.4, top]],
        8,
        M.panel,
        Placement([x, 0, z], math.pi / 8),
    )
    p.neon.ring(8.1, 0.5, 8, N, Placement([x, y1 + 1.6, z], math.pi / 8))
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        p.bare.box(
            [1, 1.6, 2.6],
            M.dark,
            Placement([x + 7.7 * math.sin(a), y1 + 3, z + 7.7 * math.cos(a)], a),
        )


def crane(p: Any, at: Vec3) -> None:
    """Add the ammunition crane (FB-SKY-ARSENAL-03): its turntable, cab, jib and hanging crate.

    On the middle tier's back left corner, its lattice jib reaching out over the lower tier, a
    shell crate on its cable; its laser turret on the cab's roof.
    """
    x = at[0]
    z = at[2]
    p.hull.cylinder(8.4, 1.4, 10, M.panel, Placement([x, MID_TOP - 0.2, z]))
    p.neon.ring(8.45, 0.4, 10, N, Placement([x, MID_TOP + 0.6, z]))
    # The cab: a plated box under the laser's turret.
    p.hull.bevel_slab(
        _square(5.6),
        [MID_TOP + 1.2, MID_TOP + 3, CRANE_HEIGHT],
        [0, 0.8],
        M.base,
        Placement([x, 0, z]),
        M.panel,
    )
    p.neon.box([0.4, 0.6, 7], N, Placement([x + 5.65, MID_TOP + 3.6, z]))
    # The jib out over the stern (model -Z), its counterweight the other way.
    out = [0, -1]
    root = [x + out[0] * 4, CRANE_HEIGHT - 2, z + out[1] * 4]
    tip = [x + out[0] * 22, CRANE_HEIGHT + 3, z + out[1] * 22]
    for side in [-1, 1]:
        dx = -out[1] * 1.4 * side
        dz = out[0] * 1.4 * side
        rod(
            p.hull,
            [root[0] + dx, root[1], root[2] + dz],
            [tip[0] + dx, tip[1], tip[2] + dz],
            0.6,
            M.panel,
        )
    rod(p.hull, [root[0], root[1] + 2.4, root[2]], tip, 0.5, M.panel)
    for k in range(1, 5):
        t = k / 5
        q = [
            root[0] + (tip[0] - root[0]) * t,
            root[1] + (tip[1] - root[1]) * t,
            root[2] + (tip[2] - root[2]) * t,
        ]
        rod(
            p.hull,
            [q[0] + out[1] * 1.4, q[1], q[2] - out[0] * 1.4],
            [q[0] - out[1] * 1.4, q[1] + 1.6, q[2] + out[0] * 1.4],
            0.35,
            M.base,
        )
    p.neon.box([1.2, 1.2, 1.2], N, Placement([tip[0], tip[1] + 0.6, tip[2]]))
    back = [x - out[0] * 8, MID_TOP + 1.2, z - out[1] * 8]
    p.hull.box([5, 3.4, 5], M.panel, Placement(back, math.pi / 4), M.base)
    # The cable and the shell crate hanging under the jib's tip, over the lower deck.
    crate = [tip[0], MID_TOP - 2, tip[2]]
    rod(p.hull, [tip[0], tip[1], tip[2]], [crate[0], crate[1] + 4, crate[2]], 0.3, M.dark)
    p.hull.box([5, 4, 5], M.base, Placement(crate, math.pi / 4), PLATE)
    p.neon.box([5.2, 0.4, 0.4], N, Placement([crate[0], crate[1] + 2.4, crate[2]], math.pi / 4))

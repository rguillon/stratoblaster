# Copyright (c) 2026 Renaud Guillon
"""MB-MANGROVE-CROC-01 to MB-MANGROVE-CROC-06, 3-1: the Mangrove Croc.

Logical pixels, nose +Z, Y up (towards the camera). A long, low hover-gunboat shaped like a
crocodile: a scaly armoured back, a broad head with raised green neon eyes, jaws that open and
close around the jaw cannon, and two side pontoons. Its back plating (the carapace over its keel
from behind the dome to the snout, with the head and the back's growth on it) is the armour it
sheds (MB-MANGROVE-CROC-13, D-254): `draw_plating`.
"""

from game.config.bosses.world_3.mangrove_croc import CROC_DOME, MANGROVE_CROC
from game.config.record import record
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.mini_boss_greebles import vent
from game.view.bosses.mini_boss_shapes import (
    SHADE,
    WHITE,
    H,
    offset,
)
from game.view.bosses.world_3.jungle_flesh import JUNGLE_FLESH, F, gland, spine, table
from game.view.bosses.world_3.mangrove_croc_jungle import SWAMP, moss, scutes, stone, vine
from game.view.bosses.world_3.mangrove_croc_parts import (
    CROC_GREEN,
    CROC_JAWS,
    jaw_cannon,
    pontoon,
)
from game.view.enemies.enemy_shapes import SIDES, decal, side_stripe
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import ROUND_SECTION, SHELL_SECTION, organ
from render.geometry.solids import LoftOptions, Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import TYPE_CHECKING, Any

from game.view.enemies.enemy_mesh import EnemyParts

if TYPE_CHECKING:
    from render.geometry.outline import OutlinePoint
type Vec3 = list[float]
# __pragma__ ("noskip")


# The hull's shape (loft stations, tail to snout: z, half width, bottom, top): long, low and broad.
# Its back from `PLATING_FROM` to the snout is the plating (MB-MANGROVE-CROC-13); `top_at` reads it.
HULL = table([
    [-50, 2.5, 1.5, 4],
    [-42, 7, 0, 6.5],
    [-28, 13, -2.5, 9],
    [-8, 17, -3, 10.5],
    [10, 15, -2.5, 10],
    [22, 11, -1.5, 8.5],
    [30, 7.5, -0.5, 6],
])
# Where the plating starts (z), just ahead of the dome's hump.
PLATING_FROM = -8
# The keel: the body as drawn (the core), full up to the dome's hump, then flattened to `KEEL_TOP`
# under the plating, which sits `PLATING_SINK` into it.
KEEL_TOP = 3.3
PLATING_SINK = 0.3
KEEL = table([
    [-50, 2.5, 1.5, 4],
    [-42, 7, 0, 6.5],
    [-28, 13, -2.5, 9],
    [-11, 16.5, -3, 10.3],
    [PLATING_FROM, 17, -3, KEEL_TOP],
    [10, 15, -2.5, KEEL_TOP],
    [22, 11, -1.5, KEEL_TOP],
    [30, 7.5, -0.5, KEEL_TOP],
])
# The plating's loft stations: the hull's back over the keel, from `PLATING_FROM` to the snout.
PLATING = table([
    [st[0], st[1], KEEL_TOP - PLATING_SINK, st[3]] for st in HULL if st[0] >= PLATING_FROM
])
# The hover skirt under the hull, seen from above.
SKIRT = table([
    [0, -44],
    [13, -30],
    [18, -6],
    [15, 14],
    [9, 28],
    [-9, 28],
    [-15, 14],
    [-18, -6],
    [-13, -30],
])
# The eyes on the head: where each sits (x across, z along) and the bump's radius and height.
EYE = record({"x": 7, "z": 17, "radius": 3.6, "height": 10.4})
# Rows of scutes either side of the spine (x, from z, to z, step).
SCUTE_ROWS = table([
    [4, -40, 6, 7],
    [-4, -40, 6, 7],
    [10, -28, -2, 8],
    [-10, -28, -2, 8],
])
# The ring dome on its back (a lathe profile around the dome's axis).
DOME = table([[6.5, 0], [6.5, 1.5], [5, 4], [2.4, 5.2], [0, 5.4]])


def top_at(z: float) -> float:
    """Return the hull's height at `z` (the top of its loft there), for things laid on it."""
    for i in range(1, len(HULL)):
        a = HULL[i - 1]
        b = HULL[i]
        if z > b[0]:
            continue
        height: float = a[3] + ((b[3] - a[3]) * (z - a[0])) / (b[0] - a[0])
        return height
    last: float = HULL[len(HULL) - 1][3]
    return last


def _chines(p: EnemyParts, section: Any, stations: Any) -> None:
    """Draw the green neon chines along both flanks of a loft of `section` over `stations`."""
    for side in [1, 6]:
        p.neon.loft(
            side_stripe(table(section), side, [0.2, 0.45], 1.03),
            stations,
            CROC_GREEN,
            None,
            LoftOptions(True),
        )


def draw_hull(p: EnemyParts) -> None:
    """Draw the keel, its skirt, its green neon chines and the pontoons' pylons.

    The keel is the body up to the dome's hump, flattened under the plating (`draw_plating`).
    """
    hull = p.hull
    flesh = p.flesh
    # MB-MANGROVE-CROC-02: a living croc's swollen, moss-skinned body; its hover skirt a grafted
    # metal belly.
    flesh.loft(ROUND_SECTION, KEEL, JUNGLE_FLESH)
    hull.bevel_slab(SKIRT, [-4.5, -3.5, -2.5], [0.5, 0.5], H.dark, None, SWAMP.mud)
    path: list[Vec3] = [[0, st[3] + 0.4, st[0]] for st in KEEL[1:4]]
    spine(p, path, {"at": [-30, -18], "halfWidth": 9, "y": 4, "height": 6.2}, CROC_GREEN)
    _chines(p, ROUND_SECTION, KEEL[1:4])
    for s in SIDES:
        for z in [-14, 2]:
            hull.box([16, 2.4, 4], H.dark, Placement([s * 20, 3, z]), H.panel)
            # The pylon stands from the keel's widest flank (BOSS-52).
            hull.box([2, 6, 3], SHADE["edge"], Placement([s * 15, 0, z]))
        vine(hull, [s * 15, 5, -14], [s * 23, 4.5, 2], 4.5)


def draw_head(p: EnemyParts) -> None:
    """Draw the head, on the plating.

    Its two raised eyes with green neon slits, nostrils at the snout, a brow ridge.
    """
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    for s in SIDES:
        at: Vec3 = [s * EYE.x, top_at(EYE.z) - 1, EYE.z]
        # MB-MANGROVE-CROC-02: a bulging flesh eye socket, its eye a gland under the neon slit.
        organ(
            flesh,
            EYE.radius,
            6,
            F.sinew,
            Placement(at),
            (EYE.height - at[1]) / (EYE.radius * 2),
        )
        gland(p, [s * EYE.x, EYE.height - 1.6, EYE.z], 1.6, CROC_GREEN)
        slit: list[OutlinePoint] = [
            [s * (EYE.x - 2.4), EYE.z - 0.6],
            [s * (EYE.x + 2.2), EYE.z - 1.6],
            [s * (EYE.x + 2.2), EYE.z + 0.4],
            [s * (EYE.x - 2.4), EYE.z + 1.2],
        ]
        decal(neon, table(slit), EYE.height + 0.05, CROC_GREEN)
        hull.box([4, 1.2, 1.4], H.dark, Placement([s * 3.2, top_at(27) - 0.4, 27]))
    hull.box([12, 1.4, 3], SHADE["edge"], Placement([0, top_at(13), 13]))
    charge.box([5, 0.4, 2], WHITE, Placement([0, top_at(22) + 0.05, 22]))


def _draw_scutes(p: EnemyParts, on_plating: bool) -> None:
    """Draw the rows of scutes on the plating (`on_plating`) or on the tail."""
    for row in SCUTE_ROWS:
        x = row[0]
        z_from = row[1]
        z_to = row[2]
        step = row[3]
        points: list[Vec3] = []
        z = z_from
        while z <= z_to:
            if (z >= PLATING_FROM) == on_plating:
                points.append([x, top_at(z) - 0.3, z])
            z += step
        # The narrow rows (|x| < 6, the TS literal) get smaller scutes.
        scutes(p.hull, points, 2.2 if abs(x) < 6 else 1.8)


def draw_back(p: EnemyParts) -> None:
    """Draw the scaly back of the plating (MB-MANGROVE-CROC-05).

    Rows of scutes, moss in the hollows, a river stone and a vent.
    """
    hull = p.hull
    _draw_scutes(p, True)
    moss(hull, [[6, -2], [13, 0], [11, 8], [5, 6]], top_at(3) - 0.2)
    stone(hull, [-11, top_at(6) - 0.8, 6], 2.6, 0.4)
    vent(hull, [0, top_at(-2) + 0.1, 1], [8, 5], 3)


def draw_tail(p: EnemyParts) -> None:
    """Draw the tail's growth (MB-MANGROVE-CROC-05): scutes, moss and a river stone."""
    hull = p.hull
    _draw_scutes(p, False)
    moss(hull, [[-3, -36], [3, -34], [2, -22], [-2, -24]], top_at(-30) + 0.1)
    stone(hull, [9, top_at(-34) - 0.6, -34], 2, 1.2)


def draw_dome(p: EnemyParts) -> None:
    """Draw the ring dome on the hump of its back, the core's rings leaving from its top."""
    if len(CROC_DOME) == 0:
        return
    top = boss_point(CROC_DOME[0][0], CROC_DOME[0][1], CROC_DOME[0][2])
    base: Vec3 = [top[0], top_at(top[2]) - 0.5, top[2]]
    scale = (top[1] - base[1] - 0.6) / 5.4
    p.hull.lathe(
        [[r, y * scale] for r, y in DOME],
        8,
        H.panel,
        Placement(base),
    )
    p.neon.ring(6.7, 0.7, 8, CROC_GREEN, Placement(offset(base, 0, 0.6, 0)))
    p.charge.cylinder(1.5, 0.6, 6, WHITE, Placement(offset(top, 0, -0.6, 0)), 0.8)
    p.muzzle(top, "ring")


def draw_plating(p: EnemyParts) -> None:
    """Draw the back plating (MB-MANGROVE-CROC-13): the armour it sheds at its transformation.

    A ridged carapace over the flattened keel, from just under the keel's top up to the hull's
    back, from ahead of the dome to the snout; the head, the chines, the spine's end and the back's
    growth on it. The gatlings lie folded under it.
    """
    p.flesh.loft(SHELL_SECTION, PLATING, JUNGLE_FLESH)
    _chines(p, SHELL_SECTION, PLATING[0:3])
    path: list[Vec3] = [[0, st[3] + 0.4, st[0]] for st in PLATING]
    spine(p, path, {"at": [-6], "halfWidth": 9, "y": 4, "height": 6.2}, CROC_GREEN)
    draw_head(p)
    draw_back(p)


def mangrove_croc_core(p: EnemyParts) -> None:
    """Add the core of the Mangrove Croc: its keel, tail, dome and reactors (no plating)."""
    draw_hull(p)
    draw_tail(p)
    draw_dome(p)
    for s in SIDES:
        reactor_sac(p, table([s * 4, 3, -45]), 2.2, CROC_GREEN, F.sinew, None)


def build_mangrove_croc(scene: Any) -> Any:
    """MB-MANGROVE-CROC-01, MB-MANGROVE-CROC-06: the Mangrove Croc, a long, low hover-gunboat.

    Green neon: a crocodile's scaly armoured hull on a hover skirt, raised neon eyes, jaws opening
    and closing around the jaw cannon in its throat, two side pontoons with fan guns, moss and vines
    from the delta. Its back plating is the armour it sheds (MB-MANGROVE-CROC-13).
    """
    parts: dict[str, Any] = {
        "jaw-cannon": jaw_cannon,
        "pontoon-left": pontoon,
        "pontoon-right": pontoon,
    }
    return build_boss_model(
        MANGROVE_CROC,
        scene,
        CROC_GREEN,
        {
            "core": mangrove_croc_core,
            "parts": parts,
            "limbs": CROC_JAWS,
            "armour": {"back": {"whole": draw_plating}},
        },
    )

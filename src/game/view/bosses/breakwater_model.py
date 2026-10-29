"""P07-R05, P16-R05, 1-2: the Breakwater, ported from `bosses/breakwater-model.ts`. Logical pixels,
nose +Z, Y up (towards the camera).
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.bosses.mini_bosses import BREAKWATER  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.mini_boss_greebles import lamps, mast  # noqa: E402
from game.view.bosses.mini_boss_shapes import (  # noqa: E402
    neon_band,
    offset,
    radius_of,
    sign_of,
    socket,
    turret,
)
from game.view.bosses.world_1_organic_kit import (  # noqa: E402
    F,
    M,
    barbs,
    gland,
    graft,
    growth,
    hide,
    mantle,
    polygon,
    rib_cage,
    sac,
    scale_outline,
    spine,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES  # noqa: E402
from game.view.enemies.organic_parts import eyes, reactor_sac  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[Any]
__pragma__("noskip")

ORANGE = BOSS_LOOK.neon["breakwater"]

# The barge's hull seen from above: a long, square-cut hull, bulging where the mortars sit.
BARGE_HULL = [
    [-24, 27],
    [24, 27],
    [31, 20],
    [31, 6],
    [39, 0],
    [39, -24],
    [31, -30],
    [31, -34],
    [24, -40],
    [-24, -40],
    [-31, -34],
    [-31, -30],
    [-39, -24],
    [-39, 0],
    [-31, 6],
    [-31, 20],
]
# Heights of the shell's rim: its belly, its widest line, its top.
HULL_Y = [-5, -1, 4]
# The ram plate around its centre: a V of chamfered armour over the bow.
PLATE = [
    [0, 17],
    [20, 5],
    [21, -5],
    [15, -10],
    [-15, -10],
    [-21, -5],
    [-20, 5],
]


def _draw_body(p: Any) -> None:
    """The crab's body (P16-R05): a wide mantle under a domed, plated shell, ribs over its back, an
    orange vein along its spine, eyes on stalks at its front over its mouth (the bow gun)."""
    deck = HULL_Y[2]
    mantle(p, BARGE_HULL, [HULL_Y[0], deck], F.sinew, ORANGE)
    neon_band(p.neon, BARGE_HULL, [-1.4, -0.4], [1.02, 1.02], ORANGE)
    hide(
        p,
        {
            "tail": -41,
            "nose": 13,
            "width": 27,
            "bottom": deck - 1,
            "top": 16,
            "segments": 4,
            "shell": [F.crimson, F.membrane],
            "belly": F.purple,
        },
    )
    rib_cage(p, [-30, -20, -10, 0], {"halfWidth": 22, "y": deck, "height": 10, "thickness": 1.1})
    spine(p, [0, 16, -34], [0, 16.5, 6], {"color": ORANGE, "width": 1.4})
    for s in SIDES:
        tentacle(p, [s * 4, deck + 3, 12], [s * 6, deck + 9, 19], [0, 1, 0], [0.9, 0.5], F.sinew, 3)
        eyes(p, [s * 6, deck + 9, 19], {"count": 1, "size": 1.3}, ORANGE)
        gland(p, [s * 16, deck + 8, -28], 2, ORANGE)
        for z in [-24, -10]:
            vein_line(p, [s * 10, 14, z], [s * 26, deck + 1, z - 4], [s * 2, 3, 0], 1, ORANGE)


def _draw_legs(p: Any) -> None:
    """The crab's walking legs, three each side, folded under its rim (bone, jointed)."""
    for s in SIDES:
        for z in [-8, -20, -32]:
            knee = [s * 36, HULL_Y[2] + 4, z - 2]
            tentacle(p, [s * 24, HULL_Y[2], z], knee, [0, 2, 0], [2.4, 1.6], F.sinew, 4)
            tentacle(p, knee, [s * 40, HULL_Y[0], z - 6], [s, 0, 0], [1.6, 0.2], F.bone, 4)


def _draw_grafts(p: Any) -> None:
    """Grafts: a riveted back plate, armour bands on the flanks, exhausts, running lights."""
    graft(p, polygon(6, 8, [1.2, 1]), [15, 16.6], [0, 0, -14])
    graft(p, polygon(4, 6, [1.3, 0.7]), [13.6, 15], [0, 0, 2], {"color": M.base})
    for s in SIDES:
        graft(p, polygon(5, 5, [0.8, 1.6]), [9, 10.4], [s * 18, 0, -16], {"color": M.base})
        lamps(
            p.neon,
            [[s * 27, HULL_Y[2] + 0.4, z] for z in [16, 2, -29]],
            1.2,
            ORANGE,
        )
    mast(p, [11, 15, -22], 8, ORANGE)


def _bow_gun(p: Any, at: Vec3) -> None:
    """The bow gun in the hold (the core's fans, bursts and rings), turning on the hold's floor."""
    gun = {"radius": 7, "barrels": 2, "gap": 3, "bore": 1.2, "length": 6, "neon": ORANGE}
    turret(p, offset(at, 0, HULL_Y[2] + 0.4, 0), gun)


def _ram_plate(p: Any, at: Vec3) -> None:
    """The ram plate (P07-R05, P16-R05): no weapon, the crab's thick bony brow shield, a V of
    grafted armour on it, orange veins along its edge."""
    top = 9
    p.flesh.bevel_slab(PLATE, [-3, 1, top - 1.5], [1.5, 4], F.bone, Placement(at), F.sinew)
    neon_band(p.neon, PLATE, [0.6, 1.8], [1.02, 1.02], ORANGE, Placement(at))
    for side in SIDES:
        edge = offset(at, side * 16, top - 1.6, 3.5)
        vein_line(p, offset(at, side, top - 1.2, 12.5), edge, [0, 0.8, 0], 1, ORANGE)
    graft(p, scale_outline(PLATE, 0.55, 0, 2), [top - 1.6, top], at)
    barbs(p, offset(at, 0, 2, 15), {"count": 3, "spacing": 7, "size": 4, "dir": [0, 0.2, 1]})


def _mortar(p: Any, at: Vec3) -> None:
    """A mortar (P07-R05, P16-R05): a swollen barnacle growth on the flank under its turret, a spawn
    sac beside it."""
    r = radius_of(BREAKWATER.stats.parts, 1, 13)
    growth(p, offset(at, 0, HULL_Y[2] - 2, 0), r, ORANGE, {"flesh": F.purple, "height": 0.4})
    sac(p, offset(at, sign_of(at[0]) * 8, HULL_Y[2], 6), 3.5, F.crimson, {"stretch": 0.7})


def _mortar_turret(p: Any, at: Vec3) -> None:
    """A mortar's turret: a squat dome and a short, fat, raised barrel."""
    r = radius_of(BREAKWATER.stats.parts, 1, 13)
    turret(
        p,
        offset(at, 0, HULL_Y[2] + 3, 0),
        {
            "radius": r,
            "barrels": 1,
            "gap": 0,
            "bore": 3.6,
            "length": 3,
            "elevation": 0.6,
            "neon": ORANGE,
            "hatch": sign_of(at[0]),
        },
    )


def build_breakwater(scene: Any) -> Any:
    """P07-R05, P16-R05: the Breakwater, a huge armoured shore crab with orange veins: a wide plated
    shell over jointed legs, a bony V-shaped ram plate over its snout, a gun in its mouth and two
    barnacle mortars on its flanks."""

    def core(p: Any) -> None:
        _draw_body(p)
        _draw_legs(p)
        _draw_grafts(p)
        for s in SIDES:
            socket(p.hull, [s * 34, HULL_Y[2], -12], 8, 1)
            # The ram plate's grafted brackets on the snout.
            p.hull.box([4, 3, 8], M.dark, Placement([s * 13, HULL_Y[2] - 1, 24]))
            reactor_sac(p, [s * 16, -0.5, -40], 3.4, ORANGE)
        p.reactor([0, -0.5, -40], 3.8)

    return build_boss_model(
        BREAKWATER,
        scene,
        ORANGE,
        {
            "core": core,
            "parts": {"ram-plate": _ram_plate, "mortar-left": _mortar, "mortar-right": _mortar},
            "turrets": {
                "core": _bow_gun,
                "mortar-left": _mortar_turret,
                "mortar-right": _mortar_turret,
            },
        },
    )

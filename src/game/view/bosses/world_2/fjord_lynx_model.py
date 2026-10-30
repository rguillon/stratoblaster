"""P08-R10, 2-2: the Fjord Lynx, ported from `bosses/world-2/fjord-lynx-model.ts`.

Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_2.fjord_lynx import FJORD_LYNX
from game.view.enemies.enemy_shapes import (  # noqa: E402
    FIGHTER_SECTION,
    POD_SECTION,
    SIDES,
    angry_eyes,
    canopy_paint,
    decal,
    side_stripe,
)
from game.view.enemies.organic_parts import reactor_sac  # noqa: E402
from render.geometry.organic import RibSpec, ribs  # noqa: E402
from render.geometry.solids import LoftOptions, Placement, place_at  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import BuiltEnemyModel, EnemyParts  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.mini_boss_greebles import plate  # noqa: E402
from game.view.bosses.mini_boss_shapes import (  # noqa: E402
    SHADE,
    H,
    offset,
    scaled,
    socket,
)
from game.view.bosses.world_2.fjord_lynx_frost import (  # noqa: E402
    RIME,
    icicles,
    snow_cap,
    spread,
)
from game.view.bosses.world_2.fjord_lynx_parts import (  # noqa: E402
    CYAN,
    WHITE_NEON,
    chin_turret,
    paw,
    paw_centre,
    paw_turret,
    radar_mast,
)
from game.view.bosses.world_2.w2_organic import (  # noqa: E402
    ICE_FLESH,
    crystals,
    gland,
    glow_vein,
    sinew,
    spine_row,
)

# The low hull seen from above: a crouched body, broad at the shoulders, narrow at the haunches.
BODY = [  # type: list[list[float]]
    [0.0, 46.0],
    [8.0, 42.0],
    [15.0, 30.0],
    [20.0, 14.0],
    [22.0, 0.0],
    [20.0, -18.0],
    [15.0, -34.0],
    [9.0, -46.0],
    [-9.0, -46.0],
    [-15.0, -34.0],
    [-20.0, -18.0],
    [-22.0, 0.0],
    [-20.0, 14.0],
    [-15.0, 30.0],
    [-8.0, 42.0],
]
# Heights of the hull: its belly, its rim, its deck.
HULL = [-3.0, 0.0, 5.0]
# The head and back along the centre line (loft stations: z, half width, bottom, top).
BACK = [  # type: list[list[float]]
    [-44.0, 5.0, 4.0, 7.5],
    [-30.0, 9.0, 4.0, 10.0],
    [-6.0, 11.0, 4.0, 12.0],
    [10.0, 10.0, 4.0, 12.5],
    [20.0, 6.0, 4.0, 9.0],
    [24.0, 2.0, 4.0, 5.5],
]
# The right haunch's armour (mirrored on the left), raised over the rear of the hull.
HAUNCH = [  # type: list[list[float]]
    [6.0, -16.0],
    [16.0, -12.0],
    [19.0, -22.0],
    [14.0, -38.0],
    [7.0, -40.0],
]
# The foreleg from the shoulder out to the paw (the right one; mirrored on the left).
FORELEG = [  # type: list[list[float]]
    [14.0, 8.0],
    [20.0, 26.0],
    [27.0, 20.0],
    [21.0, 2.0],
]
# The sponson on the left flank carrying the radar mast (around the mast's centre).
SPONSON = [  # type: list[list[float]]
    [-8.0, 10.0],
    [8.0, 7.0],
    [9.0, -7.0],
    [-8.0, -9.0],
]
# Snow packed on the rear deck, either side of the back.
REAR_SNOW = [  # type: list[list[float]]
    [-12.0, -30.0],
    [12.0, -30.0],
    [9.0, -42.0],
    [-9.0, -42.0],
]
# The bobtail: a short stub behind the back (loft stations).
TAIL = [  # type: list[list[float]]
    [-54.0, 0.0, 6.0, 6.0],
    [-50.0, 3.0, 3.5, 8.0],
    [-42.0, 4.0, 3.0, 8.0],
]


def tip(length: float, place: Placement) -> Vec3:
    """The point `length` along the +Y axis of a solid placed by `place` (its tip)."""
    at: Vec3 = place.at if place.at is not None else [0.0, 0.0, 0.0]
    y1 = length * math.cos(place.pitch)
    z1 = length * math.sin(place.pitch)
    return offset(at, -y1 * math.sin(place.roll), y1 * math.cos(place.roll), z1)


def draw_body(p: EnemyParts) -> None:
    """The hull, the back and head, the haunches and the forelegs out to the paws."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R05: a crouched, muscled cat of cold flesh; metal only on its haunches' armour.
    flesh.bevel_slab(BODY, HULL, [2.0, 2.5], ICE_FLESH.teal, None, ICE_FLESH.rime)
    flesh.loft(
        FIGHTER_SECTION,
        BACK,
        ICE_FLESH.purple,
        None,
        LoftOptions(False, canopy_paint([3, 4], ICE_FLESH.seam)),
    )
    ribs(
        flesh,
        [-30.0, -22.0, -14.0, -6.0],
        RibSpec(10.0, 6.0, 6.0, 0.8),
        ICE_FLESH.bone,
    )
    spine_row(flesh, [0.0, 12.0, -2.0], [0.0, 10.0, -34.0], 5, 3)
    for side in [1, 6]:
        stripe = side_stripe(FIGHTER_SECTION, side, [0.3, 0.75])
        neon.loft(stripe, BACK[1:5], CYAN, None, LoftOptions(True))
    neon.box([0.8, 0.5, 22.0], WHITE_NEON, Placement([0.0, 12.1, -18.0]))
    for s in SIDES:
        haunch = [[s * p0[0], p0[1]] for p0 in HAUNCH]
        hull.bevel_slab(haunch, [4.0, 5.0, 8.0], [0.5, 1.4], H.panel, None, RIME)
        snow_cap(hull, scaled(haunch, 0.7, s * 3.5, -8.5), 8)
        leg = [[s * p0[0], p0[1]] for p0 in FORELEG]
        flesh.bevel_slab(leg, [-2.0, 0.0, 3.5], [0.6, 1.0], ICE_FLESH.sinew, None, ICE_FLESH.rime)
        sinew(flesh, [s * 16.0, 4.0, 8.0], offset(paw_centre(s), -s * 7.0, 2.5, -8.0), 1.6)
        glow_vein(p, [s * 8.0, 11.0, -4.0], [s * 15.0, 6.0, 20.0], 0.8, CYAN)
        neon.box([0.8, 0.5, 18.0], CYAN, Placement([s * 20.6, 0.4, -6.0], s * -0.05))
    flesh.loft(POD_SECTION, TAIL, ICE_FLESH.sinew)
    crystals(flesh, [0.0, 8.0, -50.0], 3, 3)


def draw_ears(p: EnemyParts) -> None:
    """The tufted antennas: an ear on each side of the head, a whip with a light on its tip."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    for s in SIDES:
        ear = Placement([s * 6.0, 10.0, 14.0], 0.0, -0.25, -s * 0.35)
        flesh.cylinder(
            3.4, 8, 3, ICE_FLESH.sinew, Placement(ear.at, s * 0.5, ear.pitch, ear.roll), 0
        )
        top = tip(7.0, ear)
        whip = Placement(top, 0.0, -0.55, -s * 0.5)
        hull.cylinder(0.4, 9, 4, H.dark, whip, 0.25)
        end = tip(9.0, whip)
        neon.lathe(
            [[0.0, 0.0], [1.0, 1.2], [0.0, 3.4]],
            4,
            WHITE_NEON,
            place_at(whip, end),
        )
        neon.box(
            [0.6, 0.4, 3.0],
            CYAN,
            Placement(offset(ear.at, s * 1.2, 3.4, 0.6), 0.0, 0.0, -s * 0.35),
        )


def draw_deck(p: EnemyParts) -> None:
    """Deck details: vents, seams, the sponson for the radar mast, frost and icicles, the eyes."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    mast = FJORD_LYNX.stats.parts[2]
    # `mast?.x ?? -25` and `mast?.y ?? 22`.
    mast_x = -25.0 if mast == None or mast.x == None else mast.x  # noqa: E711
    mast_y = 22.0 if mast == None or mast.y == None else mast.y  # noqa: E711
    at: Vec3 = [-mast_x, 0.0, -mast_y]
    sponson = [[x + at[0], z + at[2]] for x, z in SPONSON]
    flesh.bevel_slab(sponson, [-2.0, 0.0, 2.5], [0.6, 1.0], ICE_FLESH.purple, None, ICE_FLESH.rime)
    socket(hull, offset(at, 0.0, 2.5, 0.0), 6, 0.6)
    for s in SIDES:
        gland(p, [s * 13.0, HULL[2] + 0.3, 20.0], 1.2, CYAN)
        crystals(flesh, [s * 14.0, HULL[2], -26.0], 3)
        icicles(flesh, spread([s * 20.5, -0.5, 8.0], [s * 19.0, -0.5, -22.0], 5), 4)
        icicles(flesh, spread([s * 13.0, -0.5, -38.0], [s * 5.0, -0.5, -45.0], 3), 3)
    plate(hull, scaled(SPONSON, 0.5, at[0] + 1.0, at[2] - 1.0), [2.5, 0.4], SHADE["patch"])
    snow_cap(flesh, REAR_SNOW, HULL[2])
    for eye in angry_eyes((0.0, 41.5), 2.4, [5.0, 1.2], 0.35):
        decal(neon, eye, 5.05, CYAN)


def draw_core(p: EnemyParts) -> None:
    """The core: the body, the ears, the deck and the reactor sacs."""
    draw_body(p)
    draw_ears(p)
    draw_deck(p)
    for s in SIDES:
        reactor_sac(p, [s * 7.0, 2.5, -46.0], 3, CYAN, ICE_FLESH.purple)


def boss_drawing(core: Any, parts: Any, turrets: Any, limbs: Any, ring: Any) -> Any:
    """What `build_boss_model` draws a boss from (`BossDrawing` in the TypeScript): a plain
    object, with `ring` and `limbs` None when absent."""
    drawing: Any = None
    __pragma__(
        "js",
        "{}",
        """
    drawing = {core: core, parts: parts, turrets: turrets, limbs: limbs, ring: ring};
    """,
    )
    return drawing


def build_fjord_lynx(scene: Any) -> BuiltEnemyModel:
    """P08-R10: the Fjord Lynx, a fast, low gunship crouched like a lynx: two forward paws with
    cannons, tufted antennas over its head, a radar mast on its left flank, white and cyan neon,
    snow on its back. P16-R05: now a living cyber-lynx of cold flesh, ribs and ice spines down
    its back, sinews to its paws, metal plates on its haunches and grafted guns."""
    model: BuiltEnemyModel = build_boss_model(
        FJORD_LYNX,
        scene,
        CYAN,
        boss_drawing(
            draw_core,
            {"paw-left": paw, "paw-right": paw, "radar-mast": radar_mast},
            {"core": chin_turret, "paw-left": paw_turret, "paw-right": paw_turret},
            None,
            None,
        ),
    )
    return model

"""P08-R10, 2-4: the Avalanche, ported from `bosses/world-2/avalanche-model.ts`.

Logical pixels, nose +Z, Y up (towards the camera).
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_2.avalanche import (
    AVALANCHE,
    AVALANCHE_ARM,
    AVALANCHE_CHUTE,
    AVALANCHE_CORE_GUNS,
)
from game.config.record import merge  # noqa: E402
from game.view.enemies.enemy_shapes import (  # noqa: E402
    FIGHTER_SECTION,
    SIDES,
    angry_eyes,
    canopy_paint,
    decal,
    side_stripe,
)
from game.view.enemies.organic_parts import reactor_sac  # noqa: E402
from render.geometry.organic import RibSpec, SegmentedBody, ribs, segmented_body  # noqa: E402
from render.geometry.solids import LoftOptions, Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import BuiltEnemyModel, EnemyParts  # noqa: E402
from render.geometry.outline import OutlinePoint  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.mini_boss_greebles import lamps, plate, rect  # noqa: E402
from game.view.bosses.mini_boss_mechanism import GEAR  # noqa: E402
from game.view.bosses.mini_boss_shapes import (  # noqa: E402
    SHADE,
    WHITE,
    H,
    neon_band,
    offset,
    socket,
)
from game.view.bosses.world_2.avalanche_arms import (  # noqa: E402
    AVALANCHE_YELLOW,
    arm_limbs,
    drill,
)
from game.view.bosses.world_2.avalanche_frost import (  # noqa: E402
    FROST,
    PACKED,
    barrel_to,
    icicles,
    snow_cap,
)
from game.view.bosses.world_2.w2_organic import (  # noqa: E402
    ICE_FLESH,
    crystals,
    gland,
    glow_vein,
    shell,
    sinew,
    spine_row,
)

# Yellow neon of the Avalanche.
YELLOW = AVALANCHE_YELLOW

# The chassis seen from above: a heavy, blunt-nosed hull between its two tracks.
CHASSIS = [  # type: list[list[float]]
    [0.0, 33.0],
    [16.0, 31.0],
    [24.0, 23.0],
    [26.0, -8.0],
    [22.0, -30.0],
    [12.0, -36.0],
    [-12.0, -36.0],
    [-22.0, -30.0],
    [-26.0, -8.0],
    [-24.0, 23.0],
    [-16.0, 31.0],
]
# Heights of the chassis: its bottom, its waist, its deck.
DECK = [-4.0, 0.0, 7.0]
# The cab at the front (loft stations: z, half width, bottom, top).
CAB = [  # type: list[list[float]]
    [4.0, 11.0, 6.0, 13.0],
    [12.0, 12.0, 6.0, 17.0],
    [20.0, 12.0, 6.0, 17.5],
    [27.0, 10.0, 6.0, 15.0],
    [32.0, 6.0, 6.0, 11.0],
]
# A track on each side: its centre across, and its centre and length along Z.
TRACK_X = 31.0
TRACK_Z = -6.0
TRACK_LENGTH = 58.0
# The rock hopper's bin around its centre, and its heights (bottom, rim's foot, rim).
BIN = [  # type: list[list[float]]
    [-15.0, -15.0],
    [15.0, -15.0],
    [13.0, 14.0],
    [-13.0, 14.0],
]
BIN_Y = [5.0, 8.0, 20.0]
# Rocks heaped in the bin: x, z, size, turn, and whether snow covers them.
ROCKS = [
    (-7.0, -6.0, 7.0, 0.3, True),
    (5.0, -8.0, 6.0, 1.1, False),
    (8.0, 4.0, 7.5, 0.6, True),
    (-6.0, 6.0, 6.5, 1.4, False),
    (0.0, -1.0, 8.0, 0.9, False),
]
# Snow caps on the deck and the cab's roof: outline, height, depth.
SNOW = [
    (
        [
            [9.0, 2.0],
            [20.0, 0.0],
            [22.0, -14.0],
            [14.0, -18.0],
            [10.0, -10.0],
        ],
        DECK[2],
        1.0,
    ),
    (
        [
            [-12.0, -22.0],
            [-4.0, -20.0],
            [-2.0, -30.0],
            [-14.0, -32.0],
        ],
        DECK[2],
        0.8,
    ),
    (
        [
            [-4.0, 13.0],
            [6.0, 12.0],
            [8.0, 20.0],
            [-2.0, 21.0],
        ],
        17.3,
        0.8,
    ),
]
# A weathered patch welded on the deck's right.
PATCH = [  # type: list[list[float]]
    [-22.0, -6.0],
    [-15.0, -6.0],
    [-15.0, 4.0],
    [-21.0, 6.0],
]


def unit_girth(t: float) -> float:
    """A body of even girth from tail to nose (`girth: () => 1`)."""
    return 1.0


def draw_body(p: EnemyParts) -> None:
    """The chassis, its tracks, the cab and the engine deck."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R05: a burrowing beast, a squat body of flesh under a ridged shell, its head in front.
    flesh.bevel_slab(CHASSIS, DECK, [2.0, 2.2], ICE_FLESH.sinew, None, ICE_FLESH.purple)
    neon_band(neon, CHASSIS, [-2.2, -0.6], [0.985, 1.02], YELLOW)
    shell(flesh, SegmentedBody(-36.0, 6.0, 4, 21.0, 4.0, 13.0))
    flesh.loft(
        FIGHTER_SECTION,
        CAB,
        ICE_FLESH.purple,
        None,
        LoftOptions(False, canopy_paint([1, 2], ICE_FLESH.seam)),
    )
    plate(hull, rect(10.0, 8.0), [17.0, 0.8], H.panel, Placement([0.0, 0.0, 16.0]))
    for side in [1, 6]:
        stripe = side_stripe(FIGHTER_SECTION, side, [0.3, 0.75])
        neon.loft(stripe, CAB[0:3], YELLOW, None, LoftOptions(True))
    for eye in angry_eyes((0.0, 30.5), 3.0, [5.0, 1.3], 0.3):
        decal(neon, eye, 11.2, YELLOW)
    for s in SIDES:
        draw_track(p, s)
    # Spiracles breathing out of the shell, metal valves sooted at their tops.
    ribs(
        flesh,
        [-24.0, -16.0, -8.0],
        RibSpec(14.0, 8.0, 7.0, 1.0),
        ICE_FLESH.bone,
    )
    for s in SIDES:
        flesh.cylinder(
            2.6, 13.0, 5, ICE_FLESH.sinew, Placement([s * 10.0, DECK[2] + 4.0, -15.0]), 1.8
        )
        glow_vein(p, [s * 4.0, 16.0, 10.0], [s * 16.0, 10.0, -26.0], 0.9, YELLOW)
        hull.cylinder(2.1, 1.5, 6, SHADE["soot"], Placement([s * 10.0, DECK[2] + 17.0, -15.0]))
        lamps(neon, [[s * 13.5, DECK[2] + 6.0, -2.0]], 1.4, YELLOW)


def draw_track(p: EnemyParts, s: float) -> None:
    """A track on side `s`: its belt, fender, road wheels and the packed snow in its treads."""
    hull = p.hull
    flesh = p.flesh
    x = s * TRACK_X
    # P16-R05: a crawling flank of swollen segments where the track was, a metal fender over it.
    segmented_body(
        flesh,
        SegmentedBody(
            TRACK_Z - TRACK_LENGTH / 2,
            TRACK_Z + TRACK_LENGTH / 2,
            5,
            5.0,
            -10.0,
            0.0,
            0.25,
            unit_girth,
            [False, False],
        ),
        ICE_FLESH.teal,
        Placement([x, 0.0, 0.0]),
    )
    hull.bevel_slab(
        [
            [x - 5.5, TRACK_Z - TRACK_LENGTH / 2 + 3.0],
            [x + 5.5, TRACK_Z - TRACK_LENGTH / 2 + 3.0],
            [x + 5.5, TRACK_Z + TRACK_LENGTH / 2 - 2.0],
            [x - 5.5, TRACK_Z + TRACK_LENGTH / 2 - 2.0],
        ],
        [3.5, 4.5, 6.5],
        [0.4, 1.0],
        H.base,
        None,
        H.panel,
    )
    # Snow drifted on the fender's rear half, packed into the treads at the front.
    snow_cap(
        hull,
        [
            [x - 4.5, TRACK_Z - 24.0],
            [x + 4.5, TRACK_Z - 22.0],
            [x + 4.0, TRACK_Z - 4.0],
            [x - 4.0, TRACK_Z - 9.0],
        ],
        6.5,
        0.8,
    )
    # Short clawed legs under each segment, digging.
    for i in range(4):
        z = TRACK_Z - 21.0 + i * 14.0
        sinew(
            flesh,
            [x + s * 4.0, -3.0, z],
            [x + s * 8.0, -7.0, z + 3.0],
            1.3,
            ICE_FLESH.bone,
            [0.0, 2.0, 0.0],
        )


def draw_frost(p: EnemyParts) -> None:
    """Frost over the deck, icicles under the nose and along the flanks, hazard paint, sockets."""
    hull = p.hull
    flesh = p.flesh
    for item in SNOW:
        snow_cap(flesh, item[0], item[1], item[2])
    nose: list[Vec3] = [
        [x, DECK[0] + 0.5, 31.5 - abs(x) * 0.12] for x in [-14.0, -8.0, -2.0, 4.0, 10.0, 15.0]
    ]
    icicles(flesh, nose, 4.5)
    for s in SIDES:
        flank: list[Vec3] = [
            [s * 24.0, DECK[0] + 0.5, 12.0],
            [s * 25.0, DECK[0] + 0.5, 0.0],
        ]
        icicles(flesh, flank, 3.5)
        shoulder = AVALANCHE_ARM.shoulder
        socket(hull, boss_point(s * shoulder[0], shoulder[1], DECK[2]), 6, 1.5)
        crystals(flesh, [s * 14.0, 12.0, -28.0], 4)
        gland(p, [s * 18.0, DECK[2], -6.0], 1.5, YELLOW)
    spine_row(flesh, [0.0, 15.0, -4.0], [0.0, 13.0, -30.0], 4, 4)
    plate(hull, PATCH, [DECK[2], 0.6], SHADE["patch"])


def draw_guns(p: EnemyParts) -> None:
    """The core's twin guns under the cab's chin, on a mount."""
    p.hull.box([18.0, 4.0, 7.0], H.dark, Placement([0.0, 3.0, 28.0]), H.panel)
    for tip in AVALANCHE_CORE_GUNS:
        barrel_to(p, tip, [1.7, 9.0])
    p.charge.box([8.0, 0.6, 2.0], WHITE, Placement([0.0, 17.6, 15.0]))


def draw_core(p: EnemyParts) -> None:
    """The core: the body, the frost, the guns and the reactor sacs."""
    draw_body(p)
    draw_frost(p)
    draw_guns(p)
    for s in SIDES:
        reactor_sac(p, [s * 16.0, 2.0, -36.5], 3.4, YELLOW, ICE_FLESH.purple)


def hopper(p: EnemyParts, at: Vec3) -> None:
    """The rock hopper (P08-R10): a bin on struts, heaped with rocks and snow, a yellow band round
    its rim and a chute at its front, where its rocks drop from."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    # P16-R05: a crop sac of flesh, its mouth gaping with rocks and ice, a metal rim grafted on.
    bin_at: list[OutlinePoint] = [[x + at[0], z + at[2]] for x, z in BIN]
    flesh.bevel_slab(bin_at, BIN_Y, [2.5, 0.8], ICE_FLESH.membrane, None, ICE_FLESH.purple)
    flesh.box([22.0, 1.0, 22.0], ICE_FLESH.seam, Placement(offset(at, 0.0, BIN_Y[2] - 1.0, 0.0)))
    glow_vein(
        p,
        offset(at, -13.0, BIN_Y[0] + 2.0, -10.0),
        offset(at, -12.0, BIN_Y[2] - 3.0, 10.0),
        0.8,
        YELLOW,
    )
    neon_band(
        neon,
        BIN,
        [BIN_Y[2] - 2.5, BIN_Y[2] - 1.2],
        [1.01, 1.02],
        YELLOW,
        Placement(at),
    )
    for rock in ROCKS:
        snowy = rock[4]
        hull.box(
            [rock[2], rock[2] * 0.6, rock[2] * 0.8],
            FROST if snowy else PACKED,
            Placement(offset(at, rock[0], BIN_Y[2] - 1.5, rock[1]), rock[3], 0.0, rock[3] * 0.3),
            FROST if snowy else H.panel,
        )
    if len(AVALANCHE_CHUTE) > 0:
        chute = AVALANCHE_CHUTE[0]
        lip = boss_point(chute[0], chute[1], chute[2])
        hull.box(
            [9.0, 2.0, 5.0],
            H.dark,
            Placement(offset(lip, 0.0, -1.5, -2.5), 0.0, -0.3),
            GEAR,
        )
        charge.box([6.0, 0.5, 1.2], WHITE, Placement(offset(lip, 0.0, -0.5, -0.8)))
        p.muzzle(lip)
    for s in SIDES:
        sinew(flesh, offset(at, s * 10.0, 0.0, 6.0), offset(at, s * 12.0, BIN_Y[1], 10.0), 1.2)
    icicles(
        flesh,
        [
            offset(at, -11.0, BIN_Y[0], -13.0),
            offset(at, 0.0, BIN_Y[0], -13.5),
            offset(at, 10.0, BIN_Y[0], -13.0),
        ],
        4,
    )


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


def build_avalanche(scene: Any) -> BuiltEnemyModel:
    """P08-R10: the Avalanche, a heavy drilling machine 3.5 L across, yellow neon: a tracked chassis
    crusted with snow and icicles, a cab at its nose, two drill arms swinging in front of it and a
    rock hopper heaped with ice and stone on its back. P16-R05: now a burrowing beast of flesh
    under a ridged shell, crawling on segmented flanks, a crop sac of rock and ice on its back and
    fleshy arms ending in grafted drills."""
    limbs = merge(arm_limbs("left"), arm_limbs("right"))
    model: BuiltEnemyModel = build_boss_model(
        AVALANCHE,
        scene,
        YELLOW,
        boss_drawing(
            draw_core,
            {"drill-left": drill, "drill-right": drill, "hopper": hopper},
            None,
            limbs,
            None,
        ),
    )
    return model

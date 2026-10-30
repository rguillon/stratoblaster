"""The Narwhal (P08-R10, 2-1), ported from `bosses/world-2/narwhal-model.ts`.

The final boss of the Ice floes level. Logical pixels, nose +Z, Y up (towards the camera). A long
flying submarine: a round hull with a sail on its back, cruciform tail planes and a shrouded
propeller, teal neon along its back; its spiral horn, torpedo tubes and ballast pods are its parts.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.world_2.narwhal import NARWHAL, NARWHAL_EMITTER
from game.config.enemy_look import ENEMY_LOOK
from game.config.record import record
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.final_boss_shapes import edge_strips, shift, turret
from game.view.bosses.mini_boss_greebles import plate, rect
from game.view.bosses.world_2.floe_breaker_frost import FROST  # noqa: E402
from game.view.bosses.world_2.narwhal_details import (  # noqa: E402
    deck_dressing,
    hull_dressing,
)
from game.view.bosses.world_2.narwhal_parts import (  # noqa: E402
    SUB_SECTION,
    ballast_pod,
    horn_lance,
    torpedo_tube,
)
from game.view.bosses.world_2.w2_organic import (  # noqa: E402
    ICE_FLESH,
    crystals,
    gland,
    glow_vein,
    spine_row,
)
from game.view.enemies.enemy_shapes import SIDES, flip_x, side_stripe
from render.geometry.organic import RibSpec, organ, ribs
from render.geometry.solids import LoftOptions, Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import BuiltEnemyModel, EnemyParts  # noqa: E402

__pragma__("noskip")

H = ENEMY_LOOK.hull
N = BOSS_LOOK.neon.narwhal
if N == None:  # noqa: E711
    N = [0.05, 0.95, 0.75]
WHITE = [1, 1, 1]
QUARTER = math.pi / 2

# The pressure hull (loft stations, tail to nose): round, its widest just behind the sail.
HULL = [  # type: list[list[float]]
    [-66, 4, 2, 9],
    [-56, 9, -2, 12],
    [-40, 14, -5, 15],
    [-16, 17, -7, 17],
    [10, 18, -7, 17.5],
    [30, 16.5, -6, 16.5],
    [42, 13, -4, 14],
    [50, 8, -1, 10],
    [56, 0, 4.5, 4.5],
]
# The flat back of `SUB_SECTION`, and its shoulders either side.
BACK = 4
# The sail (conning tower) on its back (loft stations, aft to front).
SAIL = [  # type: list[list[float]]
    [-8, 3, 15, 22],
    [-2, 5, 15, 27],
    [16, 5, 15, 27],
    [22, 3, 15, 23],
]
# The right sail plane (the screen's left: +X is the model's left side, mirrored for the other).
SAIL_PLANE = [  # type: list[list[float]]
    [4.5, 15],
    [14, 11],
    [14, 8],
    [4.5, 7],
]
# The right stern plane, and the upper and lower rudders (in their own plane, rolled upright).
STERN_PLANE = [  # type: list[list[float]]
    [6, -50],
    [24, -59],
    [25, -65],
    [5, -63],
]
RUDDER = [  # type: list[list[float]]
    [0, -48],
    [13, -58],
    [13, -64],
    [0, -64],
]
# The propeller shroud: a lathe profile out along its outer wall and back along its inner one.
SHROUD = [  # type: list[list[float]]
    [6.4, 0],
    [7, 0.5],
    [7, 6],
    [6.2, 6],
    [6.2, 0.5],
]
# The emitter on the sail's top: a lathe profile (the core's spiral gun).
EMITTER = [  # type: list[list[float]]
    [3, 0],
    [3.2, 1.2],
    [2, 2.6],
    [0, 3],
]


def hull_paint(side: int, band: int) -> Any:
    """Snow lies in patches along its back, between the neon lines."""
    if side == BACK and band % 2 == 1:
        return ICE_FLESH.rime
    if band == 0:
        return ICE_FLESH.bone
    return None


def sail_paint(side: int, band: int) -> Any:
    """The sail's flat top under its snow cap."""
    if side == BACK:
        return ICE_FLESH.rime
    return None


def draw_hull(p: EnemyParts) -> None:
    """The pressure hull, its teal neon along the back, and the ballast pods' pylons."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R06: a whale's body of cold teal flesh, ribbed, metal bands grafted round it.
    flesh.loft(SUB_SECTION, HULL, ICE_FLESH.teal, None, LoftOptions(False, hull_paint))
    ribs(
        flesh,
        [-36, -28, 28, 36],
        RibSpec(15.5, 3, 13, 0.8),
        ICE_FLESH.bone,
    )
    for side in [BACK - 1, BACK + 1]:
        stripe = side_stripe(SUB_SECTION, side, [0.1, 0.35], 1.03)
        neon.loft(stripe, HULL[1:7], N, None, LoftOptions(True))
    # A neon line under its chin and along its keel lamps.
    neon.box([1, 0.5, 30], N, Placement([0, -7.2, 0]))
    for s in SIDES:
        pylon = [
            [s * 15, -28],
            [s * 33, -24],
            [s * 33, -12],
            [s * 15, -6],
        ]
        flesh.bevel_slab(pylon, [3, 5, 7], [0.5, 1], ICE_FLESH.sinew, None, ICE_FLESH.rime)
        hull.ring(17.8, 1.4, 8, H.panel, Placement([0, 5, s * 6 - 10], 0, QUARTER))


def draw_sail(p: EnemyParts) -> None:
    """The sail, its planes and the spiral emitter on its top."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    # The dorsal hump where the sail was, its planes now fins.
    flesh.loft(SUB_SECTION, SAIL, ICE_FLESH.purple, None, LoftOptions(False, sail_paint))
    edge_strips(
        neon,
        [
            [0, -7.6],
            [0, 21.6],
        ],
        0.8,
        [26.9, 27.5],
        N,
    )
    for s in SIDES:
        plane = SAIL_PLANE if s > 0 else flip_x(SAIL_PLANE)
        flesh.bevel_slab(
            plane, [21, 22, 23], [0.3, 0.6], ICE_FLESH.membrane, None, ICE_FLESH.purple
        )
        crystals(flesh, [s * 12, 22, 9], 2.6, 2)
        # Feelers on the hump, of different heights.
        flesh.cylinder(0.8, 4 + s * 1.5, 4, ICE_FLESH.sinew, Placement([s * 2.2, 27, 2]), 0.2)
    hull.lathe(EMITTER, 8, H.dark, Placement([0, 27, 10]))
    neon.ring(3.3, 0.5, 8, N, Placement([0, 27.4, 10]))
    charge.cylinder(1.3, 1.6, 6, WHITE, Placement([0, 29.4, 10]), 0.4)
    for at in NARWHAL_EMITTER:
        p.muzzle(boss_point(at[0], at[1], at[2]), "ring")


def draw_tail(p: EnemyParts) -> None:
    """The cruciform tail: stern planes, rudders, the propeller shroud and its reactor."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    for s in SIDES:
        # The tail flukes, flesh where the stern planes were.
        plane = STERN_PLANE if s > 0 else flip_x(STERN_PLANE)
        flesh.bevel_slab(plane, [4, 5, 6.5], [0.4, 0.8], ICE_FLESH.teal, None, ICE_FLESH.rime)
        edge_strips(
            neon,
            STERN_PLANE[0:2] if s > 0 else flip_x(STERN_PLANE[0:2]),
            0.8,
            [5.6, 6.6],
            N,
        )
        crystals(flesh, [s * 22, 6, -60], 3, 2)
    flesh.bevel_slab(
        RUDDER,
        [-0.8, 0, 0.8],
        [0.2, 0.4],
        ICE_FLESH.sinew,
        Placement([0, 9, 0], 0, 0, QUARTER),
    )
    flesh.bevel_slab(
        RUDDER,
        [-0.8, 0, 0.8],
        [0.2, 0.4],
        ICE_FLESH.sinew,
        Placement([0, 1, 0], 0, 0, -QUARTER),
    )
    organ(flesh, 6.5, 7, ICE_FLESH.purple, Placement([0, 5, -72], 0, QUARTER), 0.6)
    hull.lathe(SHROUD, 8, H.dark, Placement([0, 5, -73], 0, QUARTER), False)
    neon.ring(7.2, 0.8, 8, N, Placement([0, 5, -70], 0, QUARTER))
    p.reactor([0, 5, -67], 3.6)
    glow_vein(p, [0, 10, -66], [0, 14, -44], 1.2, N)


def draw_deck(p: EnemyParts) -> None:
    """Deck details: hatches, vents, frost, ice chunks, hazard paint."""
    hull = p.hull
    flesh = p.flesh
    plate(hull, rect(5, 7), [17.6, 0.5], FROST.panel, Placement([0, 0, -18]))
    plate(hull, rect(4, 4), [15.6, 0.5], H.panel, Placement([0, 0, -38]))
    gland(p, [0, 17, -26], 1.6, N)
    spine_row(flesh, [0, 16, -50], [0, 17, -30], 4, 3.5)
    crystals(flesh, [6, 16.6, -32], 3.4)
    crystals(flesh, [-7, 16.6, 24], 2.6)
    crystals(flesh, [-9, 12, -48], 3)
    for s in SIDES:
        glow_vein(p, [s * 5, 17, 20], [s * 14, 10, 44], 1, N)
        glow_vein(p, [s * 5, 16, -14], [s * 15, 8, -48], 1, N)


def deck_gun(p: EnemyParts, at: list[float]) -> None:
    """The deck gun on the forward deck (the core's turret), around its pivot `at`."""
    p.hull.cylinder(6.5, 2, 8, H.dark, Placement(shift(at, [0, 15, 0])))
    turret(p, shift(at, [0, 16.5, 0]), 7, [2, N])


def draw_core(p: EnemyParts) -> None:
    """The core body: hull, sail, tail, deck, and the hull and deck dressing."""
    draw_hull(p)
    draw_sail(p)
    draw_tail(p)
    draw_deck(p)
    hull_dressing(p, N)
    deck_dressing(p, N)


def draw_lance(p: EnemyParts, at: list[float]) -> None:
    """The horn lance, a part."""
    horn_lance(p, at, N)


def draw_tube(p: EnemyParts, at: list[float]) -> None:
    """A torpedo tube on a flank, a part (both flanks)."""
    torpedo_tube(p, at, N)


def draw_pod(p: EnemyParts, at: list[float]) -> None:
    """A ballast pod on its pylon, a part (both sides)."""
    ballast_pod(p, at, N)


def boss_drawing(core: Any, parts: Any, turrets: Any, limbs: Any, ring: Any) -> Any:
    """The `BossDrawing` of a boss model (`boss-model.ts`): what the model is drawn from."""
    return record({"core": core, "parts": parts, "turrets": turrets, "limbs": limbs, "ring": ring})


def build_narwhal(scene: Any) -> BuiltEnemyModel:
    """P08-R10: the Narwhal, a long flying submarine 5 L from its tail to the tip of its spiral
    horn, teal neon along its back; its horn lance, two torpedo tubes on its flanks and two
    ballast pods on pylons are its parts, its deck gun and the emitter on its sail the core's
    guns.
    P16-R06: now a living cyber-narwhal, a whale of cold flesh, ribbed, with fins and flukes, its
    horn of bone; its torpedo tubes and ballast sacs swell from its flanks, metal grafted on.
    """
    parts = record(
        {
            "lance": draw_lance,
            "tube-left": draw_tube,
            "tube-right": draw_tube,
            "pod-left": draw_pod,
            "pod-right": draw_pod,
        }
    )
    turrets = record({"core": deck_gun})
    return build_boss_model(
        NARWHAL,
        scene,
        N,
        boss_drawing(draw_core, parts, turrets, None, None),
    )

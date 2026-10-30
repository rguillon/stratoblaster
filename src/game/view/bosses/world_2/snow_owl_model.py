"""The Snow Owl (P08-R10, 2-3)

Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_2.snow_owl import OWL_CHIN_GUNS, OWL_CROWN, SNOW_OWL
from game.config.record import record
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.mini_boss_greebles import lamps, seam
from game.view.bosses.mini_boss_shapes import QUARTER, SHADE, WHITE, H, scaled
from game.view.bosses.world_2.snow_owl_parts import (  # noqa: E402
    OWL_WHITE,
    eye,
    icicles,
    radar_pod,
)
from game.view.bosses.world_2.w2_organic import (  # noqa: E402
    ICE_FLESH,
    crystals,
    gland,
    sinew,
    spine_row,
)
from game.view.enemies.enemy_shapes import FIGHTER_SECTION, SIDES, canopy_paint
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import RibSpec, ribs
from render.geometry.solids import LoftOptions, Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import BuiltEnemyModel, EnemyParts  # noqa: E402

__pragma__("noskip")

# Navigation lights: red to port (+X, the screen's left), green to starboard.
PORT_RED = [1, 0.1, 0.12]
STARBOARD_GREEN = [0.2, 1, 0.35]

# The right wing seen from above, from the leading edge's root out to the tip and back.
HALF_WING = [  # type: list[list[float]]
    [0, 15],
    [14, 14],
    [28, 10],
    [40, 5],
    [48, 1],
    [51, -3],
    [49, -7],
    [45, -8],
    [42, -6],
    [39, -10],
    [35, -8],
    [31, -12],
    [27, -10],
    [22, -14],
    [14, -14],
    [6, -17],
    [0, -18],
]
# Both wings: an owl's broad, rounded wing, its trailing edge cut into feathers. The left half
# is the right one mirrored and walked back from the tip to the root (without its end points).
WING = [point for point in HALF_WING]
for j in range(len(HALF_WING) - 2):
    i = len(HALF_WING) - 2 - j
    WING.append([-HALF_WING[i][0], HALF_WING[i][1]])
# The leading edge's neon, root to tip (one wing; mirrored for the other).
LEADING_EDGE = [  # type: list[list[float]]
    [5, 13.6],
    [14, 12.8],
    [28, 8.8],
    [40, 3.8],
    [47, 0.4],
]
# The body along the centre line (loft stations: z, half width, bottom, top).
BODY = [  # type: list[list[float]]
    [-27, 5, -1, 6],
    [-18, 10, -3, 10],
    [-4, 13, -4, 12],
    [10, 12, -3, 11],
    [20, 9, -2, 8],
    [24, 5, 0, 5],
]
# Where the trailing edge's icicles hang (one wing; mirrored for the other).
WING_ICICLES = [  # type: list[list[float]]
    [43, -1, -6.5],
    [37, -1, -8],
    [29, -1, -10],
    [20, -1, -12.5],
]


def draw_wings(p: EnemyParts) -> None:
    """The wings: dark metal under a crust of snow, white neon along their leading edges."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R05: broad membrane wings on bone struts, rime on their fronts; too big to flutter.
    flesh.bevel_slab(
        WING,
        [-1.2, 0, 1.6],
        [0.8, 1.2],
        ICE_FLESH.membrane,
        None,
        ICE_FLESH.purple,
    )
    flesh.bevel_slab(
        scaled(WING, 0.86, 0, 2),
        [1.5, 1.7, 2.1],
        [0, 0.5],
        ICE_FLESH.teal,
        None,
        ICE_FLESH.rime,
    )
    for s in SIDES:
        for i in range(len(LEADING_EDGE) - 1):
            a = LEADING_EDGE[i]
            b = LEADING_EDGE[i + 1]
            seam(neon, [s * a[0], a[1]], [s * b[0], b[1]], [1.6, 0.8, 0.7], OWL_WHITE)
        # Feather lines across the trailing edge.
        for pt in [[45, -3], [38, -5], [30, -7], [21, -9]]:
            sinew(
                flesh,
                [s * 6, 2.4, 2],
                [s * (pt[0] - 2), 2, pt[1] - 3],
                0.7,
                ICE_FLESH.bone,
                [0, 0.6, 4],
            )
        sinew(flesh, [s * 5, 2.4, 10], [s * 50, 1.8, -2], 1.1, ICE_FLESH.bone, [0, 1, 6])
        icicles(flesh, WING_ICICLES, s)
        hull.ring(8, 1, 8, H.panel, Placement([s * 38, 1.6, 2]))
    lamps(neon, [[50.5, 0.4, -3]], 1.4, PORT_RED)
    lamps(neon, [[-50.5, 0.4, -3]], 1.4, STARBOARD_GREEN)


def draw_body(p: EnemyParts) -> None:
    """The body: a rounded fuselage, snow on its back, ear tufts, vents and twin reactors."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R05: a plump body of cold flesh, ribbed, a sinewy neck holding the great eye.
    hull.ring(6.4, 1.2, 8, H.panel, Placement([0, 5, 21], 0, QUARTER))
    flesh.loft(
        FIGHTER_SECTION,
        BODY,
        ICE_FLESH.teal,
        None,
        LoftOptions(False, canopy_paint([1, 2], ICE_FLESH.rime)),
    )
    ribs(
        flesh,
        [-16, -8, 0],
        RibSpec(11, 4, 7, 0.7),
        ICE_FLESH.bone,
    )
    flesh.cylinder(6, 5, 7, ICE_FLESH.sinew, Placement([0, 5, 23], math.pi / 8, QUARTER))
    for s in SIDES:
        # Ear tufts, swept back over the head, a white light on each tip.
        flesh.box(
            [2.4, 9, 4],
            ICE_FLESH.purple,
            Placement([s * 6.5, 8, 15], 0, -0.5, -s * 0.45),
            ICE_FLESH.rime,
        )
        neon.box([1.2, 1.2, 1.2], OWL_WHITE, Placement([s * 9.9, 14.6, 10.7]))
        gland(p, [s * 7, 9.4, -10], 1.2, OWL_WHITE)
        crystals(flesh, [s * 5, 9, -20], 2.6)
        neon.box([0.6, 0.4, 14], OWL_WHITE, Placement([s * 10.6, 6.2, -8], s * 0.05))
        reactor_sac(p, [s * 4, 2.5, -27.2], 2.6, OWL_WHITE, ICE_FLESH.purple)
    spine_row(flesh, [0, 12, 4], [0, 9, -18], 4, 2.6)


def draw_guns(p: EnemyParts) -> None:
    """The crown emitter on the back (its rings) and the chin guns either side of the eye."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    crowns = [boss_point(m[0], m[1], m[2]) for m in OWL_CROWN]
    if len(crowns) > 0:
        crown = crowns[0]
        hull.cylinder(3.4, 1.5, 8, H.base, Placement([crown[0], crown[1] - 2, crown[2]]))
        neon.ring(3.5, 0.4, 8, OWL_WHITE, Placement([crown[0], crown[1] - 1.2, crown[2]]))
        charge.cylinder(2, 0.5, 8, WHITE, Placement([crown[0], crown[1] - 0.5, crown[2]]))
        muzzle(crown, "ring")
    for m in OWL_CHIN_GUNS:
        tip = boss_point(m[0], m[1], m[2])
        x = tip[0]
        y = tip[1]
        z = tip[2]
        hull.box([5, 4.5, 9], H.base, Placement([x, y - 2.6, z - 12]), H.panel)
        hull.cylinder(1.3, 9.4, 6, H.dark, Placement([x, y, z - 10], 0, QUARTER))
        charge.cylinder(1.35, 0.6, 6, WHITE, Placement([x, y, z - 0.6], 0, QUARTER))
        muzzle(tip, "gun")


def draw_core(p: EnemyParts) -> None:
    """The core body: wings, body, the guns, and the sensor's hood."""
    draw_wings(p)
    draw_body(p)
    draw_guns(p)
    p.hull.box([12, 0.4, 3], SHADE["edge"], Placement([0, 11.5, 2]))


def boss_drawing(core: Any, parts: Any, turrets: Any, limbs: Any, ring: Any) -> Any:
    """The `BossDrawing` of a boss model: what the model is drawn from."""
    return record({"core": core, "parts": parts, "turrets": turrets, "limbs": limbs, "ring": ring})


def build_snow_owl(scene: Any) -> BuiltEnemyModel:
    """P08-R10: the Snow Owl, a wide-winged recon drone with white neon: snow on its broad wings,
    two radar pods with turning antennas on them and a big round sensor eye at its front.
    P16-R05: now a living owl of cold flesh with membrane wings on bone, its radomes grafted on
    swollen nacelles, its eye a real eye in a lid of flesh.
    """
    parts = record({"pod-left": radar_pod, "pod-right": radar_pod, "eye": eye})
    return build_boss_model(
        SNOW_OWL,
        scene,
        OWL_WHITE,
        boss_drawing(draw_core, parts, None, None, None),
    )

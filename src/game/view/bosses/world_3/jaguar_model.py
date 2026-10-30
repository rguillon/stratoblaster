"""P09-R09, 3-5: the Jaguar, the mini boss of the canopy city. Model space: logical pixels, nose +Z
(down the screen),
Y up towards the camera; +X is the screen's left."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_3.jaguar import JAGUAR, JAGUAR_EYE, JAGUAR_FANGS, JAGUAR_PARTS
from game.config.enemy_look import ENEMY_LOOK
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.mini_boss_greebles import vent
from game.view.bosses.overlord_city import (
    edge_lights,
    symmetric,
)
from game.view.bosses.world_3.jaguar_parts import (
    AMBER,
    COAT,
    claw_mount,
    claw_turret,
    rosette,
    tail_mount,
    tail_turret,
)
from game.view.bosses.world_3.jungle_flesh import F, sinew, spine, table, vein_to
from game.view.enemies.enemy_shapes import (
    SIDES,
    angry_eyes,
    canopy_paint,
    decal,
    side_stripe,
)
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import ROUND_SECTION
from render.geometry.solids import LoftOptions, Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

H = ENEMY_LOOK.hull
WHITE = [1, 1, 1]
QUARTER = math.pi / 2

# The stealth delta seen from above (right half, nose to tail): a long nose, the wings swept back
# from the claw roots, a sawtooth trailing edge.
WING = symmetric(
    [
        [5, 54],
        [10, 40],
        [15, 26],
        [22, 14],
        [40, -2],
        [57, -18],
        [56, -26],
        [44, -26],
        [36, -36],
        [26, -32],
        [18, -44],
        [8, -46],
    ],
    60,
)
# Heights of the wing: belly, edge, top.
WING_Y = [-3, 0, 3]
# Its leading edges, lit amber (edges of WING, from point i to the next).
LEADING = [3, 4, 5, 19, 20, 21]
# The fuselage along the centre line, tail to nose (loft stations), the cockpit painted dark.
FUSELAGE = table(
    [
        [-50, 6, 1, 6],
        [-36, 10, 1, 9],
        [-10, 12, 1, 11],
        [14, 11, 1, 11],
        [32, 8, 1, 9],
        [46, 6, 1, 7],
        [56, 3, 1, 4.5],
        [61, 0, 2.5, 2.5],
    ]
)
# The rosettes on the wings (right half, mirrored): where and how big.
SPOTS = table(
    [
        [24, 4, 3.2],
        [35, -9, 3],
        [48, -18, 2.3],
        [26, -20, 3.2],
        [19, -33, 2.5],
        [39, -27, 2],
        [16, 18, 2.4],
    ]
)
# The tail curling from the fuselage's end out to the cannon's pod (points along it).
TAIL = table(
    [
        [0, 2.5, -48],
        [8, 2.5, -56],
        [20, 2.5, -56],
        boss_point(JAGUAR_PARTS.tail[0], JAGUAR_PARTS.tail[1], 1.5),
    ]
)


def segment(p: EnemyParts, ends: list[Vec3], radius: float, end: float) -> None:
    """A cylinder lying from `ends[0]` to `ends[1]`."""
    a = ends[0]
    b = ends[1]
    dx = b[0] - a[0]
    dz = b[2] - a[2]
    place = Placement(a, math.atan2(dx, dz), QUARTER)
    p.flesh.cylinder(radius, math.hypot(dx, dz), 6, COAT, place, end)
    p.neon.ring(radius + 0.2, 0.7, 6, AMBER, place)


def draw_sinews(p: EnemyParts) -> None:
    """P16-R05: its bone spine, the sinews and veins under its pelt."""
    path: list[Vec3] = []
    for st in FUSELAGE[1:5]:
        path.append([0, st[3] + 0.3, st[0]])
    spine(
        p,
        path,
        {"at": [-30, -18, -6, 6], "halfWidth": 11, "y": 2, "height": 9.6},
        AMBER,
    )
    for s in SIDES:
        sinew(
            p,
            [[s * 9, 4, 16], [s * 40, 2.4, -14]],
            [0, 1.4, 4],
            1.4,
            F.sinew,
        )
        vein_to(
            p,
            [[s * 10, 3.4, 4], [s * 36, 3.4, -30]],
            [0, 0, 6],
            AMBER,
        )


def draw_body(p: EnemyParts) -> None:
    """The wings and the fuselage, the cockpit dark, rosettes on the wings, lit leading edges."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R05: a living big cat: a spotted pelt stretched over its delta like a flying squirrel's,
    # a muscular body with a bone spine, metal fins and nozzles grafted on.
    flesh.bevel_slab(WING, WING_Y, [1.5, 2], F.sinew, None, COAT)
    edge_lights(neon, WING, LEADING, [-1.4, -0.3], AMBER)
    flesh.loft(
        ROUND_SECTION,
        FUSELAGE,
        COAT,
        None,
        LoftOptions(False, table(canopy_paint([3, 4], F.crimson))),
    )
    draw_sinews(p)
    for side in [1, 6]:
        neon.loft(
            side_stripe(table(ROUND_SECTION), side, [0.3, 0.75]),
            FUSELAGE[1:6],
            AMBER,
            None,
            LoftOptions(True),
        )
    for s in SIDES:
        for spot in SPOTS:
            rosette(hull, [s * spot[0], spot[1]], spot[2], WING_Y[2] + 0.05)
        vent(hull, [s * 14, WING_Y[2] - 0.1, -22], [4, 9], 3, s * 0.2)
        # Canted fins, like a stealth fighter's, near the tail.
        hull.box([1, 8, 12], H.panel, Placement([s * 13, 4, -34], 0, 0, s * 0.5), COAT)
        neon.box([0.5, 0.5, 10], AMBER, Placement([s * 16.5, 10.6, -34], 0, 0, s * 0.5))
    for i in range(len(TAIL) - 1):
        segment(p, [TAIL[i], TAIL[i + 1]], 2.8 - i * 0.3, 2.5 - i * 0.3)


def draw_head(p: EnemyParts) -> None:
    """The cat's head: ears on the fuselage, angry amber eyes, fang guns under the nose."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    for s in SIDES:
        flesh.lathe(
            [[3.2, 0], [0, 5.5]],
            3,
            COAT,
            Placement([s * 6, 8, 36], s * 0.4),
        )
    for eye in angry_eyes(table([0, 45]), 3, [5.5, 1.6], 0.35):
        decal(neon, eye, 7.5, AMBER)
    for m in JAGUAR_FANGS:
        tip = boss_point(m[0], m[1], m[2])
        hull.cylinder(
            1.2,
            tip[2] - 2 - 46,
            6,
            H.dark,
            Placement([tip[0], tip[1], 46], 0, QUARTER),
            1,
        )
        charge.cylinder(
            1.3,
            2,
            6,
            WHITE,
            Placement([tip[0], tip[1], tip[2] - 2], 0, QUARTER),
            0.8,
        )
        muzzle(tip)
    # The spiral emitter: a lit eye on the back behind the cockpit.
    eye_at = boss_point(JAGUAR_EYE[0], JAGUAR_EYE[1], JAGUAR_EYE[2])
    hull.cylinder(
        4,
        1.6,
        8,
        H.dark,
        Placement([eye_at[0], eye_at[1] - 3, eye_at[2]]),
        3.4,
    )
    charge.lathe(
        [[2.6, 0], [1.8, 1.2], [0, 1.4]],
        6,
        WHITE,
        Placement([eye_at[0], eye_at[1] - 1.4, eye_at[2]]),
    )
    neon.ring(4.1, 0.6, 8, AMBER, Placement([eye_at[0], eye_at[1] - 2.6, eye_at[2]]))
    muzzle(eye_at, "ring")


def jaguar_core(p: EnemyParts) -> None:
    """The core of the Jaguar: its body, head and the reactors at its tail."""
    draw_body(p)
    draw_head(p)
    for s in SIDES:
        reactor_sac(p, table([s * 6, 3.5, -50]), 3.5, AMBER, F.sinew, None)


def build_jaguar(scene: Any) -> Any:
    """P09-R09: the Jaguar, a sleek stealth interceptor with spotted armour and amber neon: a cat's
    head with ears and fang guns, claw guns reaching forward from its wing roots, and a tail
    curling out to a cannon held high over its left wing."""
    parts: dict[str, Any] = {
        "claw-left": claw_mount,
        "claw-right": claw_mount,
        "tail-cannon": tail_mount,
    }
    turrets: dict[str, Any] = {
        "claw-left": claw_turret,
        "claw-right": claw_turret,
        "tail-cannon": tail_turret,
    }
    return build_boss_model(
        JAGUAR,
        scene,
        AMBER,
        {"core": jaguar_core, "parts": parts, "turrets": turrets},
    )

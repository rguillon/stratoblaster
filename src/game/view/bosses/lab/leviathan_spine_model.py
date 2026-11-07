# Copyright (c) 2026 Renaud Guillon
"""FB-LEVIATHAN-SPINE-01 to FB-LEVIATHAN-SPINE-05: the Leviathan Spine, the Lab's L-3 final boss.

Logical pixels, nose +Z, Y up (towards the camera). A very long sea-serpent: a wedge-shaped skull
with glowing eyes, fangs and gill slits, a segmented armoured body tapering to a tail fluke
(`leviathan_spine_body`); its parts are its pectoral fins, the gun nodes along its spine and its
tail fluke.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.leviathan_spine import LEVIATHAN_SPINE
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.leviathan_spine_body import SKULL_TOP, draw_body, spine_armour, top_at
from game.view.bosses.world_1_organic_kit import (
    F,
    M,
    barbs,
    graft,
    growth,
    polygon,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.organic import organ
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["leviathan-spine"]

# Its skull seen from above (model x, z): wide behind its eyes, a long wedge to its snout.
SKULL = [
    [0, 98],
    [5, 96],
    [9, 88],
    [13, 78],
    [14, 70],
    [13, 62],
    [9, 58],
    [-9, 58],
    [-13, 62],
    [-14, 70],
    [-13, 78],
    [-9, 88],
    [-5, 96],
]
# The right pectoral fin (config +X, model -X) seen from above, model (x, z): from the body's
# flank out to its tip, where its laser emitter sits.
FIN = [
    [-11, 36],
    [-22, 35],
    [-31, 32],
    [-35, 28],
    [-33, 23],
    [-24, 17],
    [-11, 14],
]
# The tail fluke seen from above, model (x, z).
FLUKE = [
    [0, -70],
    [10, -77],
    [22, -88],
    [26, -97],
    [18, -95],
    [8, -91],
    [0, -96],
    [-8, -91],
    [-18, -95],
    [-26, -97],
    [-22, -88],
    [-10, -77],
]


def _draw_head(p: Any) -> None:
    """Draw its head: a wedge skull, its brow and snout plates, glowing eyes, fangs, gills.

    The crown plate between brow and snout is its armour (`crown`); the crest turret's collar at the
    back of its skull.
    """
    p.flesh.bevel_slab(SKULL, [-3, 2, SKULL_TOP], [1.5, 1.4], F.slate, None, F.graphite)
    # Brow ridge behind the crown and the snout plate before it.
    p.flesh.bevel_slab(
        [[-12, 70], [12, 70], [11, 60], [-11, 60]], [SKULL_TOP - 0.4, 8, 9], [0, 1], F.bone
    )
    p.flesh.bevel_slab(
        [[-8, 96], [8, 96], [10, 88], [-10, 88]], [SKULL_TOP - 0.4, 7.6, 8.4], [0, 1.4], F.bone
    )
    graft(p, polygon(8, 6.4), [9, 11], [0, 0, 63], {"color": M.base})
    for s in SIDES:
        organ(p.vein, 2.6, 6, N, Placement([s * 11.6, 3.4, 80]), 0.8)
        # The bone spur each fin grows on, out to the pad under its emitter (its stump stays on
        # it once the fin is gone).
        tentacle(p, [s * 11, 2.6, 30], [s * 29, 2.4, 28], [0, 0.8, 1], [2.2, 1.4], F.bone)
        organ(p.flesh, 3.6, 7, F.slate, Placement([s * 31, 1.6, 28]), 0.6)
        barbs(p, [s * 4, 0.5, 96], {"count": 2, "spacing": 3, "size": 5, "dir": [0, -0.5, 0.9]})
        barbs(p, [s * 12, 0, 66], {"count": 1, "spacing": 0, "size": 6, "dir": [s, 0.4, -0.6]})
        for k in range(3):
            z = 55 - k * 3.6
            vein_line(p, [s * 13.2, 4, z], [s * 14.2, 7.6, z - 1.6], [s * 0.6, 0, 0], 0.9, N)


def _fin(p: Any, at: Vec3) -> None:
    """Add a pectoral fin (FB-LEVIATHAN-SPINE-03): a membrane on bone rays from its flank.

    Its laser emitter's pod at its tip, a neon vein along its leading edge.
    """
    s = 1 if at[0] > 0 else -1
    outline = [[-s * q[0], q[1]] for q in FIN]
    p.flesh.bevel_slab(outline, [1.6, 2.6, 3.8], [0.8, 1.2], F.membrane, None, F.slate)
    for ray in [[34, 29], [30, 22], [24, 18]]:
        tentacle(p, [s * 11, 3, 26], [s * ray[0], 3.6, ray[1]], [0, 0.6, 0], [1.4, 0.3], F.bone)
    for k in range(len(outline) - 4):
        a = outline[k]
        b = outline[k + 1]
        vein_line(p, [a[0], 3.9, a[1]], [b[0], 3.9, b[1]], [0, 0.2, 0], 1, N)
    tip = [s * 31, 0, 28]
    organ(p.flesh, 4.6, 8, F.slate, Placement([tip[0], 2, tip[2]]), 0.45)
    p.hull.cylinder(3.4, 1.6, 8, M.base, Placement([tip[0], 4.6, tip[2]]))


def _node(height: float, spikes: int) -> Any:
    """Return the drawing of a dorsal gun node: an armoured growth on its spine, bone spikes round.

    Its gun mount (BOSS-58) on top, at `height`.
    """

    def draw(p: Any, at: Vec3) -> None:
        r = 8.6
        base = height - r * 2 * 0.45
        growth(p, [at[0], base, at[2]], r, N, {"flesh": F.graphite, "height": 0.45})
        for k in range(spikes):
            a = (k + 0.5) * 2 * math.pi / spikes
            foot = [at[0] + math.sin(a) * r * 0.85, base + 2, at[2] + math.cos(a) * r * 0.85]
            tip = [math.sin(a) * 4, 3, math.cos(a) * 4]
            barbs(p, foot, {"count": 1, "spacing": 0, "size": 1, "dir": tip})
        p.hull.cylinder(4.4, 1, 10, M.panel, Placement([at[0], height - 0.8, at[2]]))

    return draw


def _fluke(p: Any, at: Vec3) -> None:
    """Add the tail fluke (FB-LEVIATHAN-SPINE-03): a crescent of membrane on bone rays.

    Its missile ports' block grafted on its root (BOSS-58).
    """
    p.flesh.bevel_slab(FLUKE, [0, 1.6, 3.4], [0.8, 1.2], F.membrane, None, F.slate)
    for s in SIDES:
        tentacle(p, [s * 3, 3, -76], [s * 24, 3.2, -94], [0, 0.6, s * 2], [1.6, 0.3], F.bone)
        vein_line(p, [s * 2, 3.5, -71], [s * 22, 3.5, -88], [0, 0.2, s * 1.5], 1, N)
    graft(p, polygon(4, 8.6, [1, 0.9]), [3.4, 7], [at[0], 0, at[2]], {"color": M.panel})


def build_leviathan_spine(scene: Any) -> Any:
    """FB-LEVIATHAN-SPINE-01, FB-LEVIATHAN-SPINE-04: the Leviathan Spine.

    A sea-serpent 5.5 L long with deep blue veins (shown green): two pectoral fins, three gun nodes
    along its spine and a tail fluke; its shed plating drawn as pieces of their own.
    """

    def core(p: Any) -> None:
        draw_body(p)
        _draw_head(p)
        # The stalks its gun nodes grow on (their stumps stay on them once a node is gone).
        stalks: list[list[float]] = [[42, 17], [-11, 17.5], [-47, 15.5]]
        for stalk in stalks:
            low = top_at(stalk[0]) - 1.5
            p.hull.cylinder(2.8, stalk[1] - low, 8, M.base, Placement([0, low, stalk[0]]), 2.2)

    return build_boss_model(
        LEVIATHAN_SPINE,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "fin-left": _fin,
                "fin-right": _fin,
                "node-front": _node(17, 6),
                "node-mid": _node(17.5, 5),
                "node-rear": _node(15.5, 6),
                "tail-fluke": _fluke,
            },
            "armour": spine_armour(),
        },
    )

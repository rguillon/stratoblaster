# Copyright (c) 2026 Renaud Guillon
"""The lighter veteran kinds, the Wasp and the Phantom (specs/enemies/wasp.md, phantom.md).

Logical pixels, nose +Z, Y up (to the camera).
"""

import math

from game.config.enemies_veteran import VETERAN_NEON as N
from game.config.enemy_look import ENEMY_LOOK
from game.sim.enemies.phantom import Phantom
from game.view.enemies.enemy_mesh import BuiltEnemyModel, build_enemy_model
from game.view.enemies.enemy_shapes import POD_SECTION, SIDES, flip_x
from game.view.enemies.organic_parts import eyes
from game.view.enemies.vetelite_organic import LEAN_SECTION, mandibles, membrane_pair, sinew
from game.view.enemies.veteran_shapes import back_band, edge_strip, nose_gun
from render.babylon import child_meshes
from render.geometry.organic import (
    SegmentedBody,
    carapace,
    curve,
    organ,
    segment_stations,
    segmented_body,
)
from render.geometry.organic import (
    vein as vein_tube,
)
from render.geometry.solids import Placement

# isort: split
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
F = ENEMY_LOOK.flesh
QUARTER = math.pi / 2


def _phantom_girth(t: float) -> float:
    return 0.5 + 0.5 * math.sin(math.pi * min(1, t * 1.3))


# ENM-WASP-01: the Wasp's narrow, swollen abdomen (tail to waist), striped with neon.
WASP_ABDOMEN = SegmentedBody(-9, -0.8, 3, 2.4, -0.9, 1.8, 0.25)
# Its plated thorax and head, waist to jaws.
WASP_THORAX = SegmentedBody(-1.2, 7.4, 2, 2.3, -0.9, 1.8)
# Its two pairs of thin swept wings (right side), the front pair the bigger (ENM-WASP-05).
WASP_WINGS = [
    {
        "root": [1.2, 3.4],
        "tips": [[9.6, 0.4], [9.3, -0.9]],
        "y": 1.4,
        "thickness": 0.25,
        "strut": 0.35,
    },
    {
        "root": [1.2, 1.4],
        "tips": [[7.4, -3.2], [6.8, -4.2]],
        "y": 1.3,
        "thickness": 0.25,
        "strut": 0.3,
    },
]


def build_wasp(scene: Any) -> Any:
    """Return a small, wasp-like insect (ENM-WASP-01, ENM-WASP-02).

    It has a swollen abdomen striped with yellow neon bands and a yellow neon sting (ENM-WASP-03),
    two pairs of fluttering membrane wings with reactors under them (ENM-WASP-05), and bone
    mandibles round a gun grafted in its jaws, within the veteran triangle budget (ENM-WASP-06).
    """

    def draw(p: Any) -> None:
        hull = p.hull
        flesh = p.flesh
        neon = p.neon
        segmented_body(flesh, WASP_ABDOMEN, F.sinew, None, LEAN_SECTION)
        carapace(flesh, WASP_THORAX, [F.slate, F.membrane])
        # The head, a bulb between the eyes, capped with a metal plate.
        organ(flesh, 1.6, 6, F.slate, Placement([0, 0.3, 7.2], 0, QUARTER), 0.9)
        hull.box([2.2, 0.4, 2.2], H.panel, Placement([0, 1.75, 4.2]))
        stations = segment_stations(WASP_ABDOMEN)
        for band in [[-7.2, -6.4], [-5.4, -4.6], [-3.6, -2.8]]:
            back_band(neon, stations, band, N.wasp)
        for wing in WASP_WINGS:
            membrane_pair(p, wing, 9)
        # The sting, out of the tail.
        neon.cylinder(0.45, 2, 6, N.wasp, Placement([0, 0.3, -8.8], 0, -QUARTER), 0)
        eyes(p, [0, 1.3, 8.3], {"count": 2, "size": 0.5, "spacing": 2.2}, N.wasp)
        mandibles(flesh, [0, 0.5, 8.2], [2.4, 2.6, 0.35])
        for s in SIDES:
            p.reactor([s * 2.6, 0.2, 0.6], 0.6)
        nose_gun(p, [0, 0.8, 7.6], 2, 0.45)

    return build_enemy_model("wasp", scene, N.wasp, draw)


# ENM-PHANTOM-01: the Phantom's flying wing, seen from above (nose +Z).
PHANTOM_WING = [
    [0, 14],
    [17, -6],
    [16, -9],
    [8, -6],
    [0, -11],
    [-8, -6],
    [-16, -9],
    [-17, -6],
]
# Its metal nose cap, grafted over the gun.
PHANTOM_NOSE = [  # type: list[list[float]]
    [7, 1.6, -0.6, 1.6],
    [10.5, 1.2, -0.4, 1.2],
    [12.5, 0, 0.3, 0.3],
]
# Its body, a low ridged shell blended into the wing, tail to nose.
PHANTOM_BODY = SegmentedBody(-10, 13.5, 3, 6, -1.2, 2.4, None, _phantom_girth)
# The bone struts holding the wing out: from the shoulder to the nose and to each tip (right).
PHANTOM_STRUTS = [
    [[3, 0.9, 2], [17, 0.4, -6.5]],
    [[3, 0.9, -2], [9, 0.5, -6.5]],
]


def phantom_edges() -> list[list[list[float]]]:
    """Return the wing's edges lit in neon: from the nose to each tip, and across each tip.

    ENM-PHANTOM-03.
    """
    nose = PHANTOM_WING[0]
    tip = PHANTOM_WING[1]
    tail = PHANTOM_WING[2]
    result: list[list[list[float]]] = []
    for strip in [edge_strip(nose, tip, 0.6), edge_strip(tip, tail, 0.6)]:
        result.append(strip)
        result.append(flip_x(strip))
    return result


def mirror_point(s: float, q: list[float]) -> list[float]:
    """`q` mirrored by `s` across the centre line (x times `s`)."""
    return [s * q[0], q[1], q[2]]


def build_phantom(scene: Any) -> Any:
    """ENM-PHANTOM-01: a sleek flying wing with a faceted hull and pale violet neon edges.

    Two reactors sit at the back of its body (ENM-PHANTOM-05), within the veteran triangle budget
    (ENM-PHANTOM-07). It fades out and in with the Phantom (ENM-PHANTOM-06): every mesh is as
    visible as the Phantom is (`Phantom.opacity`).
    """

    def draw(p: Any) -> None:
        hull = p.hull
        flesh = p.flesh
        neon = p.neon
        vein = p.vein
        # ENM-PHANTOM-02: a membrane wing on bone struts, a shell of a body, a metal nose cap
        # and gun.
        flesh.bevel_slab(PHANTOM_WING, [-0.6, 0, 0.6], [0.5, 1.2], F.membrane, None, F.graphite)
        carapace(flesh, PHANTOM_BODY, [F.graphite, F.membrane])
        for strip in phantom_edges():
            neon.slab(strip, [-0.15, 0.3], N.phantom, None)
        for s in SIDES:
            for strut in PHANTOM_STRUTS:
                start = mirror_point(s, strut[0])
                end = mirror_point(s, strut[1])
                sinew(flesh, start, end, [0.7, 0.2], F.bone, [0, 0.5, 0])
            vein_tube(
                vein,
                curve([s * 2.2, 2.3, 3], [s * 2.2, 2, -5], [s * 0.6, 0.4, 0], 2),
                0.6,
                N.phantom,
            )
            p.reactor([s * 2.4, 0.2, -10], 1.2)
        eyes(p, [0, 1.6, 9], {"count": 2, "size": 0.5, "spacing": 1.6}, N.phantom)
        hull.loft(POD_SECTION, PHANTOM_NOSE, H.panel, None, None)
        nose_gun(p, [0, 0.6, 8], 5.8)

    model = build_enemy_model("phantom", scene, N.phantom, draw)

    def sync(enemy: Any, dt: float) -> None:
        model.sync(enemy, dt)
        opacity = enemy.opacity if isinstance(enemy, Phantom) else 1
        # Listed on each sync, not at build: the edge trim meshes (ENM-PHANTOM-06, GFX-TRIM-06) are
        # added to the model after this builder returns, and they fade with it too.
        for mesh in child_meshes(model.root, False):
            mesh.visibility = opacity
            mesh.isVisible = opacity > 0

    return BuiltEnemyModel(model.root, sync)

# Copyright (c) 2026 Renaud Guillon
"""The lighter veteran kinds, the Wasp and the Phantom (specs/enemies/wasp.md, phantom.md).

Logical pixels, nose +Z, Y up (to the camera).
"""

import math

from game.config.enemies_veteran import VETERAN_CONFIG
from game.config.enemies_veteran import VETERAN_NEON as N
from game.config.enemy_look import ENEMY_LOOK
from game.sim.enemies.phantom import Phantom
from game.view.enemies.basic_parts import config_barrels
from game.view.enemies.enemy_mesh import BuiltEnemyModel, build_enemy_model
from game.view.enemies.enemy_shapes import POD_SECTION, SIDES, flip_x
from game.view.enemies.organic_parts import eyes
from game.view.enemies.vetelite_organic import sinew
from game.view.enemies.veteran_shapes import edge_strip
from render.babylon import child_meshes
from render.geometry.organic import (
    SegmentedBody,
    carapace,
    curve,
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


# ENM-WASP-01: the Wasp, an unmanned drone round a single ducted fan. The duct's inner and outer
# radius, its bottom and top, and the fan in it (a spinning rotor, ENM-42).
WASP_DUCT = [5.9, 7.4]  # type: list[float]
WASP_DUCT_HEIGHT = [-0.8, 1.4]  # type: list[float]
WASP_FAN = 5.6
WASP_DUCT_SIDES = 12
# Its sensor and gun pod bolted to the front of the duct, its avionics box at the back (`[w, h, d]`
# boxes standing on their base, and their centres).
WASP_POD = [3.2, 1.8, 4]  # type: list[float]
WASP_POD_AT = [0, -0.4, 8.6]  # type: list[float]
WASP_AVIONICS = [2.6, 1.3, 3.2]  # type: list[float]
WASP_AVIONICS_AT = [0, -0.4, -8.4]  # type: list[float]
# The tail fin standing on the avionics box (`[z, y]`, side view), and the sensor's lens.
WASP_FIN = [[-7.4, 0.9], [-10.4, 0.9], [-10.6, 2.6], [-9.2, 2.6]]  # type: list[list[float]]
WASP_LENS = [[0, -0.4], [0.7, 0], [0, 0.45]]  # type: list[list[float]]


# A docked Wasp's still fan: its blades (`[x, z]` per unit of radius, as the rotors') and count.
WASP_BLADE = [[-0.12, 0.3], [0.12, 0.3], [0.22, 0.92], [-0.08, 0.95]]  # type: list[list[float]]
WASP_BLADES = 5


def docked_wasp(parts: Any, at: list[float]) -> None:
    """Draw a Wasp waiting in a bay at `at`, nose +Z, its fan still (a carrier's piece: no rotor).

    Its duct with the lit lip, the fan's blades, the sensor pod and the avionics box with its fin.
    """
    x = at[0]
    y = at[1]
    z = at[2]
    inner = WASP_DUCT[0]
    outer = WASP_DUCT[1]
    bottom = WASP_DUCT_HEIGHT[0]
    top = WASP_DUCT_HEIGHT[1]
    duct = [[outer, bottom], [outer, top - 0.3], [outer - 0.4, top], [inner, top], [inner, bottom]]
    parts.hull.lathe(duct, WASP_DUCT_SIDES, H.panel, Placement([x, y, z]), False)
    lip = [[outer - 0.55, top + 0.03], [inner + 0.35, top + 0.03]]
    parts.neon.lathe(lip, WASP_DUCT_SIDES, N.wasp, Placement([x, y, z]), False)
    blade = [[pt[0] * WASP_FAN, pt[1] * WASP_FAN] for pt in WASP_BLADE]
    for k in range(WASP_BLADES):
        turn = (2 * math.pi * k) / WASP_BLADES
        parts.hull.slab(blade, [y + 0.12, y + 0.28], H.panel, Placement([x, 0, z], turn))
    pod = WASP_POD_AT
    parts.hull.box(WASP_POD, H.base, Placement([x + pod[0], y + pod[1], z + pod[2]]), H.panel)
    box = WASP_AVIONICS_AT
    parts.hull.box(WASP_AVIONICS, H.base, Placement([x + box[0], y + box[1], z + box[2]]), H.panel)
    fin = [[pt[1] + y, pt[0] + z] for pt in WASP_FIN]
    # Rolled a quarter turn to stand up: the slab's height becomes -X.
    parts.hull.slab(fin, [-x - 0.15, -x + 0.15], H.panel, Placement([0, 0, 0], 0, 0, QUARTER))


def build_wasp(scene: Any) -> Any:
    """Return a small unmanned drone (ENM-WASP-01, ENM-WASP-02).

    A single fan spins in its round duct, its core; four stator struts hold the fan's hub. A
    sensor pod at the nose carries its three guns and a lens that charges up through its pause
    (ENM-WASP-04), an avionics box and a tail fin sit at the back, and a yellow light runs round
    the duct's lip (ENM-WASP-03).
    """

    def draw(p: Any) -> None:
        hull = p.hull
        neon = p.neon
        inner = WASP_DUCT[0]
        outer = WASP_DUCT[1]
        bottom = WASP_DUCT_HEIGHT[0]
        top = WASP_DUCT_HEIGHT[1]
        # The duct: its outer wall up and its lip in, trimmed; its inner wall down round the fan
        # drawn bare, as the struts, so no highlight runs round the inside.
        wall = [[outer, bottom], [outer, top - 0.3], [outer - 0.4, top], [inner, top]]
        hull.lathe(wall, WASP_DUCT_SIDES, H.panel, None, False)
        p.bare.lathe([[inner, top], [inner, bottom]], WASP_DUCT_SIDES, H.panel, None, False)
        lip = [[outer - 0.55, top + 0.03], [inner + 0.35, top + 0.03]]
        neon.lathe(lip, WASP_DUCT_SIDES, N.wasp, None, False)
        # The stator struts across the duct under the fan, and the fan itself.
        for k in range(2):
            strut = Placement([0, -0.6, 0], QUARTER / 2 + k * QUARTER)
            p.bare.box([0.5, 0.4, 2 * inner + 0.4], H.dark, strut)
        p.rotor([0, 0.2, 0], WASP_FAN)
        # The sensor and gun pod at the nose, its lens charging up through the pause.
        hull.box(WASP_POD, H.base, Placement(WASP_POD_AT), H.panel)
        lens_at = [0, WASP_POD_AT[1] + WASP_POD[1], WASP_POD_AT[2] + 0.6]
        p.charge.lathe(WASP_LENS, 6, [1, 1, 1], Placement(lens_at))
        config_barrels(p, VETERAN_CONFIG.wasp.muzzles, 2, 0.45)
        # The avionics box at the back, a tail fin on it and a light along its back.
        hull.box(WASP_AVIONICS, H.base, Placement(WASP_AVIONICS_AT), H.panel)
        fin = [[pt[1], pt[0]] for pt in WASP_FIN]
        hull.slab(fin, [-0.15, 0.15], H.panel, Placement([0, 0, 0], 0, 0, QUARTER))
        neon.box([0.4, 0.2, 2.4], N.wasp, Placement([0, 0.9, -8.4]))

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
        config_barrels(p, VETERAN_CONFIG.phantom.muzzles, 5.8, 0.4)

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

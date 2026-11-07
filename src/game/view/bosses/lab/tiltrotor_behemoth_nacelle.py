# Copyright (c) 2026 Renaud Guillon
"""FB-TILTROTOR-BEHEMOTH-05: the Tiltrotor Behemoth's rotor nacelles, drawn in their own frame.

Logical pixels. A nacelle's frame: its pivot (in its wingtip cradle) at the origin, its axis up
local +Y (standing, as a rotor) out to `NACELLE_LENGTH`, its hub ring just past it. Its rotor's
three blades hinge on the hub ring, each folding back along the nacelle; its spinner is four
petals that close into a pyramid over the hub and open like a flower. The view rig
(`tiltrotor_behemoth_rig`) poses them on nodes; the cannon parts it turns into draw the same
nacelle tilted forward, its blades folded (`docked_triangles`), so the swap reads as one object.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.tiltrotor_behemoth import (
    NACELLE_LENGTH,
    NACELLE_RADIUS,
    ROTOR_RADIUS,
)
from game.view.bosses.world_1_organic_kit import M
from game.view.enemies.enemy_mesh import collect_parts
from render.geometry.mesh_triangles import Vertex, triangles
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["tiltrotor-behemoth"]
QUARTER = math.pi / 2
LAYERS = ["hull", "bare", "neon"]
# The hub ring the blades hinge on: its radius, its foot and its height over the nacelle's end.
HUB_RADIUS = 7.4
HUB_Y = NACELLE_LENGTH
HUB_HEIGHT = 1.5
# The blades: their roots on the hub ring (from the axis), their turn about the axis each, their
# width, and how far they fold back (radians).
BLADE_ROOT = HUB_RADIUS
BLADE_TURNS = [0, 2 * math.pi / 3, 4 * math.pi / 3]
BLADE_WIDTH = 4
BLADE_FOLD = math.pi / 2 + 0.06
# The spinner: four petals on the hub ring's top, `PETAL_BASE` out from the axis, closing into a
# pyramid `PETAL_HEIGHT` high (leaning in by `PETAL_LEAN`), opening out to `PETAL_OPEN`.
NOSE_Y = HUB_Y + HUB_HEIGHT
PETAL_BASE = 6.6
PETAL_HEIGHT = 8
PETAL_LEAN = math.atan2(PETAL_BASE, PETAL_HEIGHT)
PETAL_LENGTH = math.sqrt(PETAL_BASE * PETAL_BASE + PETAL_HEIGHT * PETAL_HEIGHT)
PETAL_OPEN = 1.95
PETAL_TURNS = [math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4]


def draw_body(p: Any) -> None:
    """Draw a nacelle's body up local Y from its pivot.

    A rounded cowling with a lit intake ring and lit exhaust vents, a pivot shaft across its root
    (into the cradle's cheeks), the hub ring the blades hinge on at its end.
    """
    r = NACELLE_RADIUS
    length = NACELLE_LENGTH
    p.hull.lathe(
        [
            [2.5, -2.5],
            [r * 0.9, -0.5],
            [r, 2],
            [r, length - 4],
            [r + 0.5, length - 1.5],
            [r + 0.5, length],
        ],
        10,
        M.panel,
        Placement([0, 0, 0]),
    )
    p.neon.ring(r + 0.55, 0.6, 10, N, Placement([0, length - 3.4, 0]))
    p.neon.ring(r + 0.05, 0.5, 10, N, Placement([0, 6, 0]))
    for k in range(4):
        a = k * QUARTER + math.pi / 4
        p.bare.box([1.6, 5, 0.5], M.dark, Placement([math.sin(a) * r, 9, math.cos(a) * r], a))
    p.hull.cylinder(2.2, r * 2 + 3.4, 8, M.base, Placement([r + 1.7, 0, 0], 0, 0, QUARTER))
    p.hull.cylinder(HUB_RADIUS, HUB_HEIGHT, 12, M.base, Placement([0, HUB_Y, 0]))
    p.neon.ring(HUB_RADIUS + 0.05, 0.45, 12, N, Placement([0, HUB_Y + 0.5, 0]))


def draw_blade(p: Any) -> None:
    """Draw a blade along local +Z from its root (its hinge on the hub ring): a lit tip."""
    reach = ROTOR_RADIUS - BLADE_ROOT
    w = BLADE_WIDTH
    p.hull.box([w, 0.7, reach - 2], M.panel, Placement([0, -0.35, reach / 2 - 1]))
    p.hull.box([w * 0.7, 0.7, 2], M.base, Placement([0, -0.35, reach - 1]))
    p.neon.box([w * 0.72, 0.75, 1.6], N, Placement([0, -0.37, reach - 1.1]))
    p.neon.box([0.5, 0.75, reach - 6], N, Placement([w * 0.3, -0.37, reach / 2]))
    p.hull.cylinder(1.3, 2.6, 6, M.base, Placement([0, 0, -0.6], 0, QUARTER))


def draw_petal(p: Any) -> None:
    """Draw a spinner petal up local Y from its hinge (its base along local X): lit down its middle.

    A flat triangle plate, both faces; its hinge node leans it in or opens it out.
    """
    w = PETAL_BASE
    h = PETAL_LENGTH
    p.hull.face([[-w, 0, 0], [w, 0, 0], [0, h, 0]], M.panel)
    p.hull.face([[w, 0, -0.4], [-w, 0, -0.4], [0, h, -0.4]], M.base)
    p.neon.box([0.6, h * 0.7, 0.3], N, Placement([0, 0.6, 0.1]))


def drawn(draw: Any) -> list[Any]:
    """Return the triangles `draw` draws, layer by layer: `[layer, triangles]` pairs."""
    parts = collect_parts(draw)["parts"]
    return [[layer, triangles(getattr(parts, layer).geometry)] for layer in LAYERS]


def turned(v: Vec3, rot: Vec3) -> Vec3:
    """`v` turned as a Babylon node turns it: about Z, then X, then Y (`rot` `[x, y, z]`)."""
    cz = math.cos(rot[2])
    sz = math.sin(rot[2])
    x = v[0] * cz - v[1] * sz
    y = v[0] * sz + v[1] * cz
    z = v[2]
    cx = math.cos(rot[0])
    sx = math.sin(rot[0])
    y2 = y * cx - z * sx
    z2 = y * sx + z * cx
    cy = math.cos(rot[1])
    sy = math.sin(rot[1])
    return [x * cy + z2 * sy, y2, -x * sy + z2 * cy]


def posed(layers: list[Any], at: Vec3, rot: Vec3) -> list[Any]:
    """`layers` (see `drawn`) turned by `rot` (as a node) and moved to `at`."""
    result: list[Any] = []
    for pair in layers:
        tris: list[Any] = []
        for tri in pair[1]:
            placed: list[Any] = []
            for v in tri:
                q = turned(v.position, rot)
                placed.append(Vertex([q[0] + at[0], q[1] + at[1], q[2] + at[2]], v.color))
            tris.append(placed)
        result.append([pair[0], tris])
    return result


def flat(layers: list[Any]) -> list[Any]:
    """Return the triangles of `layers` (see `drawn`), all layers together."""
    result: list[Any] = []
    for pair in layers:
        result.extend(pair[1])
    return result


def joined(a: list[Any], b: list[Any]) -> list[Any]:
    """Return `a` and `b` (see `drawn`) as one, layer by layer."""
    result: list[Any] = []
    for i in range(len(a)):
        tris = list(a[i][1])
        tris.extend(b[i][1])
        result.append([a[i][0], tris])
    return result


def blade_layers(k: int, fold: float, spin: float) -> list[Any]:
    """Return blade `k` in the nacelle's frame, folded back `fold`, the hub turned `spin`."""
    blade = posed(drawn(draw_blade), [0, 0, BLADE_ROOT], [fold, 0, 0])
    return posed(blade, [0, HUB_Y + HUB_HEIGHT / 2, 0], [0, BLADE_TURNS[k] + spin, 0])


def petal_layers(open_: float, spin: float) -> list[Any]:
    """Return the four petals in the nacelle's frame, `open_` of the way open."""
    lean = -PETAL_LEAN + (PETAL_OPEN + PETAL_LEAN) * open_
    result = posed(drawn(draw_petal), [0, 0, PETAL_BASE], [lean, 0, 0])
    one = posed(result, [0, NOSE_Y, 0], [0, PETAL_TURNS[0] + spin, 0])
    for k in range(1, len(PETAL_TURNS)):
        one = joined(one, posed(result, [0, NOSE_Y, 0], [0, PETAL_TURNS[k] + spin, 0]))
    return one


def nacelle_layers(fold: float) -> list[Any]:
    """Return a nacelle's body and its blades (folded `fold` of the way), in its own frame."""
    result = drawn(draw_body)
    for k in range(len(BLADE_TURNS)):
        result = joined(result, blade_layers(k, fold * BLADE_FOLD, 0))
    return result


def docked_layers() -> list[Any]:
    """Return a nacelle tilted forward, its blades folded back (a cannon part's body).

    In its own frame turned a quarter turn about X: its pivot at the origin, its axis along +Z.
    """
    return posed(nacelle_layers(1), [0, 0, 0], [QUARTER, 0, 0])

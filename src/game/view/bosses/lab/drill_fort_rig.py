# Copyright (c) 2026 Renaud Guillon
"""MB-DRILL-FORT-05: the Drill Fort's view rig.

Logical pixels, nose +Z, Y up (towards the camera). Its drill head's spiral flutes, turning about
the drill's axis all the time (faster as it strains through its transformation, MB-DRILL-FORT-10),
gone with the drill head once it is destroyed; and the lumps of ore riding its conveyor belt back
from the drill's intake. Visual only: the sim knows nothing of them (no part, no muzzle).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.drill_fort import BELT_TOP, CONE_BASE, CONE_TIP, DRILL_AXIS, FLUTES
from game.view.bosses.boss_limbs import boss_point
from game.view.enemies.enemy_mesh import build_enemy_model, collect_parts
from render.babylon import new_transform_node, set_enabled
from render.geometry.mesh_triangles import Vertex, triangles
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["drill-fort"]
LAYERS = ["hull", "bare", "neon", "vein", "charge"]
# The flutes: how many segments each, how many turns they wind round the cone, and the spin
# (radians a second; `STRAIN` times faster while it transforms).
SEGMENTS = 8
TURNS = 1.25
SPIN = 5.0
STRAIN = 2.6
# The ore on the belt: lumps `GAP` px apart from `FIRST`, riding back at `BELT_SPEED` px a second.
LUMPS = 5
FIRST = -21
GAP = 7
BELT_SPEED = 9
ROCK = [0.13, 0.12, 0.11]


def cone_radius(z: float) -> float:
    """Return the cone's radius `z` px from its base towards its tip."""
    length = CONE_BASE[0] - CONE_TIP
    k = min(1, max(0, z / length))
    return float(CONE_BASE[1] * (1 - k) + 0.8 * k)


def draw_flutes(p: Any) -> None:
    """Draw the spiral flutes round the drill's axis (local +Z from its base to its tip).

    Each a winding row of hardened blade segments standing out of the cone, every other one with
    a lit cutting edge.
    """
    length = CONE_BASE[0] - CONE_TIP
    step = (length - 4) / SEGMENTS
    for f in range(FLUTES):
        for j in range(SEGMENTS):
            z = 1.5 + (j + 0.5) * step
            a = 2 * math.pi * f / FLUTES + 2 * math.pi * TURNS * z / length
            r = cone_radius(z) - 0.6
            c = math.cos(a)
            s = math.sin(a)
            size = max(0.9, 1.6 * r / CONE_BASE[1] + 0.6)
            place = Placement([r * c, r * s, z], 0, 0, a - math.pi / 2)
            p.hull.box([size * 1.6, size * 1.5, step * 1.15], [0.2, 0.2, 0.23], place)
            if j % 2 == 0:
                edge = Placement(
                    [(r + size * 1.4) * c, (r + size * 1.4) * s, z], 0, 0, a - math.pi / 2
                )
                p.neon.box([size * 0.5, 0.4, step], N, edge)


def draw_lumps(p: Any) -> None:
    """Draw the ore lumps on the belt (local: along -Z from the first, sitting on the belt)."""
    for k in range(LUMPS):
        size = 2.2 if k % 2 == 0 else 1.7
        p.bare.box([size + 0.4, size, size], ROCK, Placement([0, 0, -GAP * k], k * 0.9))
    p.neon.box([0.7, 0.4, 0.7], N, Placement([0.4, 2.2, -GAP * 2]))


def drill_axis() -> Vec3:
    """Return the drill's axis at its base (model space)."""
    return boss_point(0, CONE_BASE[0], DRILL_AXIS)


def lump_start() -> Vec3:
    """Return where the first lump sits at rest (model space)."""
    return boss_point(0, FIRST, BELT_TOP)


def _drill_broken(boss: Any) -> bool:
    """Whether `boss`'s drill head is destroyed (None: the model on its own)."""
    if boss == None:
        return False
    for piece in boss.parts:
        if piece.spec.id == "drill":
            return bool(piece.broken)
    return False


class DrillRig:
    """The drill's flutes on a node turning about its axis, and the belt's lumps on theirs."""

    def __init__(self, drill: Any, belt: Any, models: list[Any]) -> None:
        self.drill = drill
        self.belt = belt
        self.models = models
        self.turn = 0.0
        self.ride = 0.0

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Spin the drill, run the belt, and sync their models."""
        rate = SPIN
        if boss != None and boss.transforming_into != 0:
            rate = SPIN * STRAIN
        self.turn = (self.turn + rate * dt) % (2 * math.pi)
        self.ride = (self.ride + BELT_SPEED * dt) % GAP
        set_enabled(self.drill, not _drill_broken(boss))
        self.drill.rotation.z = self.turn
        start = lump_start()
        self.belt.position.set(start[0], start[1], start[2] - self.ride)
        for model in self.models:
            model.sync(lit, dt)


def _hang(name: str, root: Any, at: Vec3, draw: Any, neon: Any, breath: Any) -> list[Any]:
    """Return `[node, model]`: a node on `root` at `at` carrying the model `draw` draws."""
    node = new_transform_node(name, root.getScene())
    node.parent = root
    node.position.set(at[0], at[1], at[2])
    model = build_enemy_model(name, root.getScene(), neon, draw, breath)
    model.root.parent = node
    return [node, model]


def build_drill_rig(root: Any, neon: Any, breath: Any) -> DrillRig:
    """Return the drill's flutes and the belt's lumps on `root` (the boss model's)."""
    drill = _hang("drill-fort-flutes", root, drill_axis(), draw_flutes, neon, breath)
    belt = _hang("drill-fort-ore", root, lump_start(), draw_lumps, neon, breath)
    return DrillRig(drill[0], belt[0], [drill[1], belt[1]])


def _drawn(draw: Any) -> list[Any]:
    parts = collect_parts(draw)["parts"]
    result: list[Any] = []
    for layer in LAYERS:
        result.extend(triangles(getattr(parts, layer).geometry))
    return result


def _moved(tris: list[Any], at: Vec3) -> list[Any]:
    return [
        [
            Vertex([v.position[0] + at[0], v.position[1] + at[1], v.position[2] + at[2]], v.color)
            for v in tri
        ]
        for tri in tris
    ]


def drill_rig_triangles(_unfold: float) -> list[Any]:
    """Return the rig's triangles (model space): the flutes and the lumps, at rest."""
    result = _moved(_drawn(draw_flutes), drill_axis())
    result.extend(_moved(_drawn(draw_lumps), lump_start()))
    return result

# Copyright (c) 2026 Renaud Guillon
"""FB-AQUEDUCT-LEVIATHAN-05: the Aqueduct Leviathan's view rig.

Logical pixels, nose +Z, Y up (towards the camera). The blades of its two lift fans, spinning in
their ducts (the lift engines, its parts) all the time, faster as it strains through a
transformation, gone with their engine once it is destroyed. Visual only: the sim knows nothing of
them (no part, no muzzle).
"""

import math

from game.config.bosses.lab.aqueduct_leviathan import PIERS
from game.view.bosses.lab.aqueduct_leviathan_kit import N, pt
from game.view.bosses.lab.aqueduct_leviathan_parts import DUCT_FOOT, DUCT_RADIUS, ENGINE_Y
from game.view.bosses.world_1_organic_kit import M
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


LAYERS = ["hull", "bare", "neon", "vein", "charge"]
BLADES = 5
SPIN = 9.0
STRAIN = 2.2
# Which engine each fan is in, and its side.
ENGINES = ["engine-right", "engine-left"]
SIDES = [1, -1]


def draw_blades(p: Any) -> None:
    """Draw a fan's blades round its hub (local: spinning about Y), lit tips."""
    for k in range(BLADES):
        a = 2 * math.pi * k / BLADES
        reach = DUCT_RADIUS - 0.6
        mid = reach / 2 + 0.8
        place = Placement([math.sin(a) * mid, 0, math.cos(a) * mid], a, 0, 0.35)
        p.hull.box([2.2, 0.4, reach - 1.2], [0.2, 0.2, 0.23], place)
        tip = Placement([math.sin(a) * (reach - 0.6), 0.1, math.cos(a) * (reach - 0.6)], a)
        p.neon.box([2, 0.45, 0.8], N, tip)
    p.hull.cylinder(1.4, 1, 8, M.panel, Placement([0, -0.3, 0]))


def fan_at(side: float) -> Vec3:
    """Return the hub of the fan on `side` (model space)."""
    return pt(side * PIERS[4], ENGINE_Y, DUCT_FOOT + 1.6)


def _broken(boss: Any, part_id: str) -> bool:
    """Whether `boss`'s part `part_id` is destroyed (None: the model on its own)."""
    if boss == None:
        return False
    for piece in boss.parts:
        if piece.spec.id == part_id:
            return bool(piece.broken)
    return False


class FanRig:
    """The two fans' blades, each on a node spinning about its hub."""

    def __init__(self, fans: list[Any], models: list[Any]) -> None:
        self.fans = fans
        self.models = models
        self.turn = 0.0

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Spin the fans (faster while it transforms), hide a destroyed engine's, sync them."""
        rate = SPIN
        if boss != None and boss.transforming_into != 0:
            rate = SPIN * STRAIN
        self.turn = (self.turn + rate * dt) % (2 * math.pi)
        for i in range(len(self.fans)):
            fan = self.fans[i]
            set_enabled(fan, not _broken(boss, ENGINES[i]))
            fan.rotation.y = self.turn if i == 0 else -self.turn
        for model in self.models:
            model.sync(lit, dt)


def build_fan_rig(root: Any, neon: Any, breath: Any) -> FanRig:
    """Return the lift fans' blades on `root` (the boss model's)."""
    fans: list[Any] = []
    models: list[Any] = []
    for i in range(len(SIDES)):
        name = "aqueduct-leviathan-fan-" + str(i)
        node = new_transform_node(name, root.getScene())
        node.parent = root
        at = fan_at(SIDES[i])
        node.position.set(at[0], at[1], at[2])
        model = build_enemy_model(name, root.getScene(), neon, draw_blades, breath)
        model.root.parent = node
        fans.append(node)
        models.append(model)
    return FanRig(fans, models)


def fan_triangles(_unfold: float) -> list[Any]:
    """Return the rig's triangles (model space): both fans' blades at rest."""
    parts = collect_parts(draw_blades)["parts"]
    drawn: list[Any] = []
    for layer in LAYERS:
        drawn.extend(triangles(getattr(parts, layer).geometry))
    result: list[Any] = []
    for side in SIDES:
        at = fan_at(side)
        result.extend([
            [
                Vertex(
                    [v.position[0] + at[0], v.position[1] + at[1], v.position[2] + at[2]],
                    v.color,
                )
                for v in tri
            ]
            for tri in drawn
        ])
    return result

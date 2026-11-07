# Copyright (c) 2026 Renaud Guillon
"""MB-ANVIL-BARGE-05: the Anvil Barge's rig, what moves that the fight does not need.

Logical pixels, nose +Z, Y up. Two hydraulic rams in the forge throat push the horn's halves apart
as it splits: each a cylinder on its seat by the step and a lit piston rod telescoping out to its
half's inner side, following it as it swings (D-228's custom rigs, BOSS-46). Nothing here is hit
or fires: the halves themselves are moving pieces of the design (BOSS-45).
"""

import math

from game.config.bosses.lab.anvil_barge import ANVIL_BARGE, STEP_FRONT
from game.config.bosses.moving_regions import motion_value, move_point
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.lab.anvil_barge_parts import BAND, N
from game.view.bosses.region_motion import progress
from game.view.bosses.world_1_organic_kit import M
from game.view.enemies.enemy_mesh import build_enemy_model
from render.babylon import new_transform_node
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


# A ram's seat (config, the right one) and where its rod meets the half's inner side, as drawn;
# its height; its cylinder's length and its rod's (drawn along +Y, scaled to its reach).
SEAT = [3.5, STEP_FRONT - 1.5]
GRIP = [1.5, -49]
RAM_HEIGHT = 8.5
BARREL = 7
ROD = 10


def _region(region_id: str) -> Any:
    for region in ANVIL_BARGE.armour:
        if region.id == region_id:
            return region
    raise ValueError('The Anvil Barge has no region "' + region_id + '"')


def _model(name: str, root: Any, draw: Any, neon: Any, breath: Any) -> list[Any]:
    """Return `[node, model]`: a model drawn by `draw` (model space) on a node of `root`."""
    scene = root.getScene()
    node = new_transform_node(name, scene)
    node.parent = root
    model = build_enemy_model(name, scene, neon, draw, breath)
    model.root.parent = node
    return [node, model]


def _draw_barrel(p: Any) -> None:
    """Draw a ram's cylinder along +Y from the origin: dark iron, lit bands."""
    p.hull.cylinder(1.3, BARREL, 6, BAND, Placement([0, 0, 0]))
    p.neon.ring(1.35, 0.4, 6, N, Placement([0, BARREL - 1, 0]))


def _draw_rod(p: Any) -> None:
    """Draw a ram's piston rod along +Y from the origin, `ROD` long: bright steel, a lit tip."""
    p.hull.cylinder(0.65, ROD, 6, M.panel, Placement([0, 0, 0]))
    p.neon.box([1.4, 0.8, 1.4], N, Placement([0, ROD - 0.8, 0]))


def _aim(node: Any, start: Vec3, end: Vec3) -> float:
    """Put `node` at `start` (model) pointing its +Y at `end`; return the distance between them."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    node.position.set(start[0], start[1], start[2])
    node.rotation.y = math.atan2(dx, dz)
    node.rotation.x = math.acos(max(-1, min(1, dy / max(length, 0.001))))
    return length


class BargeRig:
    """The Anvil Barge's rams (see the module)."""

    def __init__(self, rams: list[list[Any]]) -> None:
        # Per ram: `[barrel node, barrel model, rod node, rod model, region, side]`.
        self.rams = rams

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Push the rams out with the horn's halves for `boss` (None: at rest)."""
        for ram in self.rams:
            region = ram[4]
            side = ram[5]
            motion = region.motion
            value = motion_value(motion, progress(region, boss))
            grip = move_point(motion, value, [side * GRIP[0], GRIP[1], RAM_HEIGHT])
            start = boss_point(side * SEAT[0], SEAT[1], RAM_HEIGHT)
            end = boss_point(grip[0], grip[1], grip[2])
            _aim(ram[0], start, end)
            length = _aim(ram[2], start, end)
            ram[2].scaling.set(1, max(length - 1, 0.5) / ROD, 1)
            ram[1].sync(lit, dt)
            ram[3].sync(lit, dt)


def build_barge_rig(root: Any, neon: Any, breath: Any) -> BargeRig:
    """Return the Anvil Barge's rig on `root` (the boss model's)."""
    rams: list[list[Any]] = []
    for side in [1, -1]:
        name = "right" if side > 0 else "left"
        barrel = _model("anvil-barge-ram-" + name, root, _draw_barrel, neon, breath)
        rod = _model("anvil-barge-rod-" + name, root, _draw_rod, neon, breath)
        rams.append([barrel[0], barrel[1], rod[0], rod[1], _region("horn-" + name), side])
    return BargeRig(rams)


def rig_triangles(_unfold: float) -> list[Any]:
    """Return the rig's triangles for the wholeness check (BOSS-52): none.

    Its rams lie in the throat, from their seats by the step to the horn's halves.
    """
    return []

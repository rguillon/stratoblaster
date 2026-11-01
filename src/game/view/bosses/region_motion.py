"""How a moving region's piece is posed in a boss model (D-230; see
`game/config/bosses/moving_regions.py`): its node's place and turn, its triangles moved, and where
it is as the boss transforms.

Model space of a boss: logical pixels, +Y up (towards the camera), its nose at +Z; a point `(x, y,
z)` of the config (X right, Y up the screen, Z height) is model `(-x, z, -y)`
(`boss_limbs.boss_point`). Babylon turns about X, Y and Z (its left-handed rotation matrices):
`y' = y cos a - z sin a, z' = y sin a + z cos a` about X; `x' = x cos a + z sin a,
z' = -x sin a + z cos a` about Y; `x' = x cos a - y sin a, y' = x sin a + y cos a` about Z.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.moving_regions import (
    inverse_value,
    is_moving,
    motion_value,
    move_point,
)
from game.view.bosses.boss_reveal import HIDDEN, SHOWN, ease, reveal_phase, share
from render.geometry.shatter import Vertex

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

Vec3 = list[float]
__pragma__("noskip")

DEG = math.pi / 180


def to_config(p: Vec3) -> Vec3:
    """A model-space point in the config's axes."""
    return [-p[0], -p[2], p[1]]


def to_model(p: Vec3) -> Vec3:
    """A config point in model space."""
    return [-p[0], p[2], -p[1]]


def moved_triangles(tris: list[Any], motion: Any, value: Any) -> list[Any]:
    """`tris` (model space) moved by `value` of `motion` from the pose as drawn."""
    result: list[Any] = []
    for tri in tris:
        result.append(
            [
                Vertex(to_model(move_point(motion, value, to_config(v.position))), v.color)
                for v in tri
            ]
        )
    return result


def node_pose(motion: Any, value: Any) -> list[Vec3]:
    """`[position, rotation]` (model space, Babylon's turns about X, Y and Z in radians) of a node
    holding what is drawn in model space, moved by `value` of `motion`."""
    position = to_model(move_point(motion, value, [0, 0, 0]))
    if motion.kind == "slide":
        return [position, [0, 0, 0]]
    a = value * DEG
    if motion.axis == "up":
        return [position, [0, -a, 0]]
    if motion.axis == "along":
        return [position, [0, 0, a]]
    return [position, [a, 0, 0]]


def relative_value(motion: Any, value: Any) -> Any:
    """`value` of `motion` from its end pose rather than from the pose as drawn (for what rides
    the piece, drawn where it ends up)."""
    end = inverse_value(motion, motion_value(motion, 1))
    if motion.kind == "slide":
        return [value[0] + end[0], value[1] + end[1], value[2] + end[2]]
    return value + end


def progress(region: Any, boss: Any) -> float:
    """How far `region`'s piece has moved for `boss` (None: at rest), from its rest pose (0) to its
    end pose (1): during its transformation, from the armour's burst on (`BOSS_LOOK.reveal.move`),
    eased."""
    if boss == None:  # noqa: E711
        return 0
    phase = reveal_phase(region.form, boss.form, boss.transforming_into)
    if phase == HIDDEN:
        return 0
    if phase == SHOWN:
        return 1
    return ease(share(boss.transform, BOSS_LOOK.reveal.move))


def posed(tris: list[Any], region: Any, form: int) -> list[Any]:
    """`tris` of `region`'s piece as the boss is after transformation `form`: at rest before its
    own, moved after it; unmoved for a region that does not move."""
    if not is_moving(region):
        return tris
    k = 1 if form >= region.form else 0
    return moved_triangles(tris, region.motion, motion_value(region.motion, k))

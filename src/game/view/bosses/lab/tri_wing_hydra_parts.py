# Copyright (c) 2026 Renaud Guillon
"""FB-TRI-WING-HYDRA-02, FB-TRI-WING-HYDRA-03: the Tri-Wing Hydra's necks, heads and shoulders.

Each neck a limb on its swaying joint (BOSS-33), each head a part on the same joint, its turret on
its crown (its mount, BOSS-58); the shoulder plates are parts on the body's flanks. Logical pixels,
nose +Z, Y up (towards the camera).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.tri_wing_hydra import (
    HEAD_CENTRE,
    HEAD_LEFT,
    NECK_CENTRE,
    NECK_LEFT,
    SHOULDER_TOP,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.world_1_organic_kit import (
    F,
    M,
    gland,
    graft,
    polygon,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.organic_parts import eyes
from render.geometry.organic import ROUND_SECTION
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


LIME = BOSS_LOOK.neon["tri-wing-hydra"]

# A head along its own +Z (loft stations: z, half width, bottom, top), its crown at its centre.
SKULL = [
    [-10, 0, 6.5, 6.5],
    [-7.5, 6.2, 3.2, 9.4],
    [-2, 8.6, 2.2, 11.2],
    [4, 7.4, 2.6, 10.4],
    [10, 5, 3.6, 8],
    [15, 2.4, 4.8, 6.6],
]
# Its lower jaw, hanging open under the snout.
JAW = [
    [-3, 6, 0.6, 3.6],
    [6, 5, 1, 3.4],
    [13.5, 2, 2, 3.2],
]
# The neck's thickness at its root and at the head, and its height there.
NECK_RADII = [5.6, 3.8]
NECK_ROOT_Y = 5.5
NECK_HEAD_Y = 7
# A shoulder plate (pauldron) around its centre: a broad, rounded plate over the flank.
PAULDRON: list[Any] = [
    [-11, -9],
    [-4, -12.5],
    [6, -11],
    [12, -4],
    [12, 5],
    [6, 11],
    [-4, 12],
    [-11, 7],
]


def _model(spot: list[Any], height: float = 0) -> Vec3:
    """Return a config point `[x, y]` as a model point at `height`."""
    return boss_point(spot[0], spot[1], height)


def _toward(start: Vec3, end: Vec3) -> float:
    """Return the yaw from `start` to `end` (model space)."""
    return math.atan2(end[0] - start[0], end[2] - start[2])


def _toward_by(start: Vec3, end: Vec3, k: float, height: float) -> Vec3:
    """Return the point `k` of the way from `start` to `end`, at `height`."""
    return [start[0] + (end[0] - start[0]) * k, height, start[2] + (end[2] - start[2]) * k]


def neck_drawing(root_spot: list[Any], head_spot: list[Any]) -> Any:
    """Return the drawing of a neck (FB-TRI-WING-HYDRA-02) from its root to its head.

    A thick sinew bowed up, bone vertebra plates down its back, a lime vein along each side.
    """
    root = _model(root_spot, NECK_ROOT_Y)
    head = _model(head_spot, NECK_HEAD_Y)
    end = _toward_by(root, head, 0.86, NECK_HEAD_Y)
    yaw = _toward(root, head)

    def draw(p: Any) -> None:
        tentacle(p, root, end, [0, 3, 0], NECK_RADII, F.sinew, 6)
        for k in range(4):
            u = 0.12 + k * 0.22
            spot = _toward_by(root, end, u, 0)
            lift = NECK_ROOT_Y + (NECK_HEAD_Y - NECK_ROOT_Y) * u + 3 * math.sin(math.pi * u)
            radius = NECK_RADII[0] + (NECK_RADII[1] - NECK_RADII[0]) * u
            graft(
                p,
                polygon(4, radius * 0.75, [1.1, 0.8]),
                [lift + radius * 0.55, lift + radius * 0.85],
                spot,
                {"yaw": yaw, "color": M.panel},
            )
        across = [math.cos(yaw), 0, -math.sin(yaw)]
        for s in SIDES:
            off = 3.4 * s
            vein_line(
                p,
                [root[0] + across[0] * off, root[1] + 2.2, root[2] + across[2] * off],
                [end[0] + across[0] * off * 0.7, end[1] + 1.6, end[2] + across[2] * off * 0.7],
                [0, 3, 0],
                0.7,
                LIME,
            )

    return draw


def neck_limbs() -> Any:
    """Return the necks, each a limb on its joint (BOSS-33): they stay when their head is gone."""
    right_head = [-HEAD_LEFT[0], HEAD_LEFT[1]]
    right_root = [-NECK_LEFT[0], NECK_LEFT[1]]
    return {
        "neck-left": {"draw": neck_drawing(NECK_LEFT, HEAD_LEFT)},
        "neck-right": {"draw": neck_drawing(right_root, right_head)},
        "neck-centre": {"draw": neck_drawing(NECK_CENTRE, HEAD_CENTRE)},
    }


def head_drawing(root_spot: list[Any]) -> Any:
    """Return the drawing of a head on the neck from `root_spot` (FB-TRI-WING-HYDRA-03).

    A long armoured skull looking along its neck, its jaw hanging open over bone teeth, eyes along
    its brow, swept-back bone horns, a riveted crest behind its crown turret (its mount, BOSS-58)
    and lime veins along its cheeks.
    """
    root = _model(root_spot)

    def draw(p: Any, at: Vec3) -> None:
        yaw = _toward(root, at)
        place = Placement([at[0], 0, at[2]], yaw)
        p.flesh.loft(ROUND_SECTION, SKULL, F.slate, place)
        p.flesh.loft(ROUND_SECTION, JAW, F.sinew, place)
        cos = math.cos(yaw)
        sin = math.sin(yaw)

        def turn(x: float, y: float, z: float) -> Vec3:
            return [at[0] + x * cos + z * sin, y, at[2] - x * sin + z * cos]

        # Bone teeth: fangs down from the snout, tusks up from the jaw.
        for x in [-2.6, 0, 2.6]:
            tentacle(p, turn(x, 5.6, 11.5), turn(x, 3.4, 13.5), [0, 0, 0], [0.7, 0], F.bone, 3)
        for s in SIDES:
            tentacle(
                p, turn(s * 3, 2.8, 9), turn(s * 3.4, 5.4, 10.5), [0, 0, 0], [0.7, 0], F.bone, 3
            )

        for s in SIDES:
            eyes(p, turn(s * 6.6, 8.6, 4.5), {"count": 2, "size": 0.9, "spacing": 1.6}, LIME)
            tentacle(
                p, turn(s * 4, 9.5, -4), turn(s * 8.5, 11, -15), [0, 2, 0], [1.4, 0.2], F.bone, 4
            )
            vein_line(p, turn(s * 7.4, 6, 8), turn(s * 8, 6.5, -6), [0, 1, 0], 0.7, LIME)
        graft(p, polygon(5, 3.4, [0.9, 1.4]), [9.2, 10.4], turn(0, 0, -6), {"yaw": yaw})

    return draw


def _pauldron(p: Any, at: Vec3, mirror: float) -> None:
    """Add a shoulder plate: a broad bone pauldron over the flank, riveted plates on it."""
    outline = [[q[0] * mirror, q[1]] for q in PAULDRON]
    p.flesh.bevel_slab(outline, [3, 8, SHOULDER_TOP], [1.5, 2.2], F.bone, Placement(at), F.slate)
    p.vein.ring(11.4, 0.6, 8, LIME, Placement([at[0], 8.4, at[2]], math.pi / 8))
    for k in range(3):
        a = mirror * (0.9 + k * 0.7)
        tentacle(
            p,
            [at[0] + math.sin(a) * 9, SHOULDER_TOP - 0.5, at[2] + math.cos(a) * 9],
            [at[0] + math.sin(a) * 15, SHOULDER_TOP - 3.5, at[2] + math.cos(a) * 15],
            [0, 1.5, 0],
            [1.4, 0],
            F.bone,
            3,
        )


def missile_shoulder(p: Any, at: Vec3) -> None:
    """Add the left shoulder plate: its missile block grafted on its top (its mount, BOSS-58)."""
    _pauldron(p, at, -1 if at[0] > 0 else 1)
    graft(p, polygon(4, 9.6, [1, 1]), [SHOULDER_TOP - 1, SHOULDER_TOP], [at[0], 0, at[2] - 2])
    gland(p, [at[0] - 6, SHOULDER_TOP - 2.5, at[2] - 9], 1.3, LIME)


def laser_shoulder(p: Any, at: Vec3) -> None:
    """Add the right shoulder plate: a gland of light behind its laser (its mount, BOSS-58)."""
    _pauldron(p, at, -1 if at[0] > 0 else 1)
    graft(p, polygon(6, 5.6), [SHOULDER_TOP - 1, SHOULDER_TOP], [at[0], 0, at[2] + 4])
    gland(p, [at[0], SHOULDER_TOP - 0.6, at[2] - 4], 2.2, LIME, F.graphite)

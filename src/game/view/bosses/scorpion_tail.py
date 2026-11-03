# Copyright (c) 2026 Renaud Guillon
"""The Scorpion's tail (MB-SCORPION-04, D-228): a chain of shelled beads arched over its back.

Its stinger hanging from the tip in front of the head. As the Scorpion turns round (its
transformation, MB-SCORPION-11), the tail unfolds straight out behind it, now towards the player, a
little longer, its new cannon at the end.

Model space: logical pixels, nose +Z, Y up. A tail point is `(z, y)`.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.boss_reveal import ease, share
from game.view.bosses.mini_boss_shapes import QUARTER
from game.view.bosses.scorpion_look import YELLOW
from game.view.bosses.world_1_organic_kit import F
from game.view.enemies.enemy_mesh import build_enemy_model, collect_parts
from render.babylon import new_transform_node
from render.geometry.mesh_triangles import Vertex, triangles
from render.geometry.organic import SegmentedBody, carapace
from render.geometry.outline import hypot2
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# The tail's spine, from its root on the abdomen (z, y), up and back, then over the body, its last
# joint above the head, where the stinger hangs: each pair of points is a segment.
TAIL = [
    [-18, 6],
    [-28, 13],
    [-27, 22],
    [-15, 28],
    [2, 29],
    [16, 26],
    [24, 21],
]
# Half widths of the segments, root to tip.
TAIL_WIDTH = [7, 6.5, 6, 5.5, 5, 4.5]
# Unfolded: every segment straight out behind (along -Z), this much longer.
STRETCH = 1.1
LAYERS = ["hull", "flesh", "neon", "vein", "charge"]


def segment_count() -> int:
    """Return the number of segments in the tail (one fewer than its joints)."""
    return len(TAIL) - 1


def _length(i: int) -> float:
    a = TAIL[i]
    b = TAIL[i + 1]
    return hypot2(b[0] - a[0], b[1] - a[1])


def _rest_angle(i: int) -> float:
    """Return the direction of segment `i` at rest, in the (z, y) plane.

    It is atan2(dy, dz), at most pi.
    """
    a = TAIL[i]
    b = TAIL[i + 1]
    angle = math.atan2(b[1] - a[1], b[0] - a[0])
    return angle if angle <= math.pi else angle - 2 * math.pi


def tail_pose(unfold: float) -> list[list[float]]:
    """Each segment `[z, y, angle, stretch]`.

    `unfold` of the way from arched to straight out behind: it swings back over the top, each
    segment turning towards pi.
    """
    e = ease(unfold)
    result: list[list[float]] = []
    z: float = TAIL[0][0]
    y: float = TAIL[0][1]
    stretch = 1 + (STRETCH - 1) * e
    for i in range(segment_count()):
        angle = _rest_angle(i) + (math.pi - _rest_angle(i)) * e
        result.append([z, y, angle, stretch])
        length = _length(i) * stretch
        z += math.cos(angle) * length
        y += math.sin(angle) * length
    return result


def _width(i: int) -> float:
    return TAIL_WIDTH[i] if i < len(TAIL_WIDTH) else 4


def segment_drawing(i: int) -> Any:
    """Segment `i` drawn along +Z from its root: a ridged bead of shell, a sinew ring at its root.

    Yellow lights along its back and belly (it turns over as it unfolds).
    """
    length = _length(i)
    w = _width(i)

    def draw(p: Any) -> None:
        body = SegmentedBody(
            length * 0.14 - w * 0.4, length * 0.86 + w * 0.4, 1, w, -w * 0.9, w * 0.9
        )
        carapace(p.flesh, body, [F.slate, F.membrane], Placement([0, 0, 0]))
        ring = w * 0.8
        p.flesh.cylinder(ring, ring * 2, 6, F.sinew, Placement([ring, 0, 0], 0, 0, QUARTER))
        p.vein.cylinder(ring * 1.04, 0.8, 6, YELLOW, Placement([0.4, 0, 0], 0, 0, QUARTER))
        for side in [1, -1]:
            p.neon.box(
                [1, 0.4, length * 0.5],
                YELLOW,
                Placement([0, side * w * 0.9 - (0.4 if side < 0 else 0), length * 0.25]),
            )

    return draw


def _placed(tris: list[Any], pose: list[float]) -> list[Any]:
    """`tris` of a segment drawn along +Z, placed by `pose` (`tail_pose`)."""
    z0 = pose[0]
    y0 = pose[1]
    pitch = -pose[2]
    k = pose[3]
    c = math.cos(pitch)
    s = math.sin(pitch)
    result: list[Any] = []
    for tri in tris:
        placed: list[Any] = []
        for v in tri:
            x, y, z = v.position[0], v.position[1], v.position[2] * k
            placed.append(Vertex([x, y * c - z * s + y0, y * s + z * c + z0], v.color))
        result.append(placed)
    return result


def tail_triangles(unfold: float) -> list[Any]:
    """Return the tail's triangles (model space), `unfold` of the way out."""
    pose = tail_pose(unfold)
    result: list[Any] = []
    for i in range(segment_count()):
        parts = collect_parts(segment_drawing(i))["parts"]
        tris: list[Any] = []
        for layer in LAYERS:
            tris.extend(triangles(getattr(parts, layer).geometry))
        result.extend(_placed(tris, pose[i]))
    return result


def unfolding(boss: Any) -> float:
    """How far the tail has unfolded for `boss` (None: at rest).

    From the burst of its armour to its weapons swinging up (`BOSS_LOOK.reveal`), then out for good.
    """
    if boss == None:
        return 0
    if boss.form >= 1:
        return 1
    if boss.transforming_into != 1:
        return 0
    look = BOSS_LOOK.reveal
    return share(boss.transform, [look.burst, look.swing[1]])


class TailRig:
    """The tail's segments, each a model on a node placed by `tail_pose`."""

    def __init__(self, nodes: list[Any], models: list[Any]) -> None:
        self.nodes = nodes
        self.models = models

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Pose the tail's nodes for the boss and sync its models."""
        pose = tail_pose(unfolding(boss))
        for i in range(len(self.nodes)):
            node = self.nodes[i]
            node.position.set(0, pose[i][1], pose[i][0])
            node.rotation.x = -pose[i][2]
            node.scaling.set(1, 1, pose[i][3])
            self.models[i].sync(lit, dt)


def build_tail_rig(root: Any, neon: Any, breath: Any) -> TailRig:
    """Return the tail on `root` (the boss model's)."""
    scene = root.getScene()
    nodes: list[Any] = []
    models: list[Any] = []
    for i in range(segment_count()):
        node = new_transform_node("scorpion-tail-" + str(i), scene)
        node.parent = root
        model = build_enemy_model(
            "scorpion-tail-" + str(i), scene, neon, segment_drawing(i), breath
        )
        model.root.parent = node
        nodes.append(node)
        models.append(model)
    return TailRig(nodes, models)

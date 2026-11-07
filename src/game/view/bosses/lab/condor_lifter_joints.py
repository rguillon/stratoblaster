# Copyright (c) 2026 Renaud Guillon
"""Jointed pieces for the L-16 Lab bosses' view rigs (Condor Lifter, Stratoliner Colossus).

Model space of a boss: logical pixels, nose +Z, Y up. A piece is a model hung at the end of a
chain of nodes, each placed by a `Joint` (its position, its turn about one or more axes and its
scaling, as Babylon applies them: scaling, then the turn about Z, then X, then Y, then the
position). The same joints pose the live nodes and the piece's triangles (for the wholeness and
budget checks), so both always agree.
"""

import math

from game.view.bosses.boss_reveal import ease, share
from game.view.enemies.enemy_mesh import build_enemy_model, collect_parts
from render.babylon import new_transform_node, set_enabled
from render.geometry.mesh_triangles import Vertex, append_triangles, triangles

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


LAYERS = ["hull", "bare", "neon", "vein", "charge"]


class Joint:
    """Where a node of a chain goes: `at`, turned `turn` ([x, y, z] radians), scaled `scale`."""

    def __init__(self, at: Vec3, turn: Any = None, scale: Any = None) -> None:
        self.at = at
        self.turn = turn if turn != None else [0, 0, 0]
        self.scale = scale if scale != None else [1, 1, 1]


def joint_point(v: Vec3, joint: Joint) -> Vec3:
    """Return the point `v` of a node's frame in its parent's frame, as Babylon places it."""
    x = v[0] * joint.scale[0]
    y = v[1] * joint.scale[1]
    z = v[2] * joint.scale[2]
    rz = joint.turn[2]
    if rz != 0:
        c = math.cos(rz)
        s = math.sin(rz)
        x, y = x * c - y * s, x * s + y * c
    rx = joint.turn[0]
    if rx != 0:
        c = math.cos(rx)
        s = math.sin(rx)
        y, z = y * c - z * s, y * s + z * c
    ry = joint.turn[1]
    if ry != 0:
        c = math.cos(ry)
        s = math.sin(ry)
        x, z = x * c + z * s, -x * s + z * c
    return [x + joint.at[0], y + joint.at[1], z + joint.at[2]]


def chain_point(v: Vec3, joints: list[Joint]) -> Vec3:
    """Return the point `v` of a chain's last node in the boss's frame (`joints` root first)."""
    p = v
    for k in range(len(joints)):
        p = joint_point(p, joints[len(joints) - 1 - k])
    return p


def drawn(draw: Any) -> list[Any]:
    """Return the triangles `draw(p)` draws, every layer."""
    parts = collect_parts(draw)["parts"]
    result: list[Any] = []
    for layer in LAYERS:
        result.extend(triangles(getattr(parts, layer).geometry))
    return result


def posed(tris: list[Any], joints: list[Joint]) -> list[Any]:
    """Return `tris` (drawn in a chain's last frame) in the boss's frame."""
    return [[Vertex(chain_point(v.position, joints), v.color) for v in tri] for tri in tris]


def paint_posed(p: Any, draw: Any, joints: list[Joint]) -> None:
    """Add to `p` (a drawing's parts) what `draw` draws in a chain's last frame, posed by `joints`.

    Layer by layer, so a piece drawn at rest in a whole (an armour region's) matches the rig's.
    """
    parts = collect_parts(draw)["parts"]
    for layer in LAYERS:
        tris = triangles(getattr(parts, layer).geometry)
        append_triangles(getattr(p, layer).geometry, posed(tris, joints))


def place(node: Any, joint: Joint) -> None:
    """Place a live node as `joint` says."""
    node.position.set(joint.at[0], joint.at[1], joint.at[2])
    node.rotation.set(joint.turn[0], joint.turn[1], joint.turn[2])
    node.scaling.set(joint.scale[0], joint.scale[1], joint.scale[2])


class Piece:
    """A model at the end of a chain of `nodes` (root first)."""

    def __init__(self, nodes: list[Any], model: Any, draw: Any) -> None:
        self.nodes = nodes
        self.model = model
        self.draw = draw

    def pose(self, joints: list[Joint]) -> None:
        """Place its nodes."""
        for k in range(len(self.nodes)):
            place(self.nodes[k], joints[k])

    def show(self, on: bool, lit: Any, dt: float) -> None:
        """Show or hide it, and sync its model when shown."""
        set_enabled(self.nodes[0], on)
        if on:
            self.model.sync(lit, dt)


def build_piece(name: str, root: Any, neon: Any, draw: Any, breath: Any, depth: int) -> Piece:
    """Return a piece drawn by `draw` at the end of a chain of `depth` nodes on `root`."""
    scene = root.getScene()
    nodes: list[Any] = []
    parent = root
    for k in range(depth):
        node = new_transform_node(name + "-joint-" + str(k), scene)
        node.parent = parent
        nodes.append(node)
        parent = node
    model = build_enemy_model(name, scene, neon, draw, breath)
    model.root.parent = parent
    return Piece(nodes, model, draw)


def stage(boss: Any, form: int, span: list[float]) -> float:
    """How far a move of transformation `form` over `span` (shares of it) is, 0 to 1, eased.

    1 once the boss has done that transformation, 0 before it starts (`boss` None: at rest).
    """
    if boss == None:
        return 0
    if boss.form >= form:
        return 1
    if boss.transforming_into != form:
        return 0
    return ease(share(boss.transform, span))


def during(boss: Any, form: int, start: float, end: float) -> bool:
    """Whether transformation `form` is going on and between `start` and `end` of it."""
    if boss == None or boss.form >= form or boss.transforming_into != form:
        return False
    inside: bool = start <= boss.transform < end
    return inside


def after(boss: Any, form: int, start: float) -> bool:
    """Whether transformation `form` is done, or going on past `start` of it."""
    if boss == None:
        return False
    if boss.form >= form:
        return True
    going: bool = boss.transforming_into == form and boss.transform >= start
    return going


def offset(at: Vec3, dx: float, dy: float, dz: float) -> Vec3:
    """Return `at` moved by `(dx, dy, dz)`."""
    return [at[0] + dx, at[1] + dy, at[2] + dz]

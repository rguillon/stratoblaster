# Copyright (c) 2026 Renaud Guillon
"""MB-MORTAR-RAFT-05: the Mortar Raft's rig, the lashings of its stern outriggers.

Logical pixels, nose +Z, Y up. Ropes run from cleats on the barge's stern quarters over to each
outrigger's bow. As it transforms they strain (shuddering), snap as the armour would burst, and
only their frayed ends are left, hanging from the barge's cleats, while the outriggers swing out
(moving pieces of the design, BOSS-45). Nothing here is hit or fires.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.mortar_raft import DECK, OUTRIGGER_TOP
from game.view.bosses.lab.mortar_raft_parts import ROPE, N, pt, rope
from game.view.bosses.world_1_organic_kit import M
from game.view.enemies.enemy_mesh import build_enemy_model
from render.babylon import new_transform_node, set_enabled
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# The lashings: from the barge's cleats `[x, y]` (right side; mirrored) to the outrigger's.
LASHINGS = [[[13.6, 24], [20.2, 26.4]], [[14.4, 28], [20.2, 30.6]], [[13.2, 33], [20.2, 26.4]]]
CLEAT_H = DECK + 0.4


def _draw_lashings(p: Any) -> None:
    """Draw the taut lashings on both sides, and the cleats they run from."""
    for s in [-1, 1]:
        for lash in LASHINGS:
            a = pt(s * lash[0][0], lash[0][1], CLEAT_H)
            b = pt(s * lash[1][0], lash[1][1], OUTRIGGER_TOP - 0.2)
            rope(p.bare, a, b, 0.55, ROPE)
        p.neon.box([0.5, 0.4, 0.5], N, Placement(pt(s * 17, 28, OUTRIGGER_TOP)))


def _draw_ends(p: Any) -> None:
    """Draw the frayed ends left hanging from the barge's cleats once the lashings have snapped."""
    for s in [-1, 1]:
        for lash in LASHINGS:
            a = pt(s * lash[0][0], lash[0][1], CLEAT_H)
            b = pt(s * (lash[0][0] + 2.2), lash[0][1] + 1.2, DECK - 3.5)
            rope(p.bare, a, b, 0.55, ROPE)
            p.hull.box([1.4, 0.8, 1], M.dark, Placement(a))


def _model(name: str, root: Any, draw: Any, neon: Any, breath: Any) -> list[Any]:
    """Return `[node, model]`: a model drawn by `draw` (model space) on a node of `root`."""
    scene = root.getScene()
    node = new_transform_node(name, scene)
    node.parent = root
    model = build_enemy_model(name, scene, neon, draw, breath)
    model.root.parent = node
    return [node, model]


class RaftRig:
    """The Mortar Raft's lashings: taut, straining, then snapped (see the module)."""

    def __init__(self, taut: list[Any], ends: list[Any]) -> None:
        self.taut = taut
        self.ends = ends

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Show the lashings for `boss` (None: at rest)."""
        snapped = False
        shake = 0.0
        if boss != None:
            if boss.form >= 1:
                snapped = True
            elif boss.transforming_into == 1:
                burst = BOSS_LOOK.reveal.burst
                snapped = boss.transform >= burst
                shake = 0.35 * math.sin(boss.age * 90)
        set_enabled(self.taut[0], not snapped)
        set_enabled(self.ends[0], snapped)
        self.taut[0].position.set(shake, 0, 0)
        if snapped:
            self.ends[1].sync(lit, dt)
        else:
            self.taut[1].sync(lit, dt)


def build_raft_rig(root: Any, neon: Any, breath: Any) -> RaftRig:
    """Return the Mortar Raft's rig on `root` (the boss model's)."""
    taut = _model("mortar-raft-lashings", root, _draw_lashings, neon, breath)
    ends = _model("mortar-raft-lashing-ends", root, _draw_ends, neon, breath)
    set_enabled(ends[0], False)
    return RaftRig(taut, ends)


def raft_triangles(_unfold: float) -> list[Any]:
    """Return the rig's triangles for the wholeness check (BOSS-52): none.

    The lashings hang between the barge's cleats and the outriggers, their
    ends from the cleats.
    """
    return []

# Copyright (c) 2026 Renaud Guillon
"""FB-STAR-FORT-02, FB-STAR-FORT-11: the Star Fort's rig, what moves that the fight does not need.

Logical pixels, nose +Z, Y up. The energy running round its moat (lit dashes circling, faster
after each transformation) and the rock pinnacle its keep rises on: a rough column of rock hidden
in the fort's slab at rest, pushed up under the keep as the keep slides up (a moving piece of the
design, BOSS-45), so the risen keep stands on its rock. Nothing here is hit or fires.
"""

import math

from game.config.bosses.lab.star_fort import (
    KEEP_AT,
    KEEP_R,
    KEEP_RISE,
    MOAT,
    MOAT_H,
    PARADE,
    STAR_FORT,
)
from game.view.bosses.lab.star_fort_parts import SCARP, N, pt
from game.view.bosses.region_motion import progress
from game.view.enemies.enemy_mesh import build_enemy_model, collect_parts
from render.babylon import new_transform_node
from render.geometry.mesh_triangles import Vertex, triangles
from render.geometry.rough import Roughness, rough_lathe
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# The pinnacle: its profile `[radius, height]` from its foot, drawn with its top at the parade
# ground (hidden at rest), `KEEP_RISE` px up at the end.
PINNACLE = [[KEEP_R - 2.5, 0], [KEEP_R - 0.6, KEEP_RISE * 0.55], [KEEP_R + 0.4, KEEP_RISE + 0.6]]
# The moat's energy: this many dashes, turning this fast (radians a second) at each form.
DASHES = 18
SPIN = [0.35, 0.7, 1.2]


def _region(region_id: str) -> Any:
    for region in STAR_FORT.armour:
        if region.id == region_id:
            return region
    raise ValueError('The Star Fort has no region "' + region_id + '"')


def _draw_pinnacle(p: Any) -> None:
    """Draw the rock pinnacle with its top at height 0 (model space, its node's origin)."""
    rough_lathe(
        p.flesh,
        PINNACLE,
        9,
        SCARP,
        Roughness(0.12, 0.14, 0.3, 5),
        Placement([0, -KEEP_RISE - 0.6, 0]),
    )


def _draw_dashes(p: Any) -> None:
    """Draw the lit dashes over the moat, round the origin."""
    r = (MOAT[0] + MOAT[1]) / 2
    for k in range(DASHES):
        a = 2 * math.pi * k / DASHES
        p.neon.box(
            [1.6, 0.4, 5], N, Placement([r * math.cos(a), MOAT_H + 0.2, r * math.sin(a)], -a)
        )


def _model(name: str, root: Any, draw: Any, neon: Any, breath: Any) -> list[Any]:
    """Return `[node, model]`: a model drawn by `draw` (model space) on a node of `root`."""
    scene = root.getScene()
    node = new_transform_node(name, scene)
    node.parent = root
    model = build_enemy_model(name, scene, neon, draw, breath)
    model.root.parent = node
    return [node, model]


class FortRig:
    """The Star Fort's moat energy and keep pinnacle (see the module)."""

    def __init__(self, pinnacle: list[Any], dashes: list[Any]) -> None:
        self.pinnacle = pinnacle
        self.dashes = dashes
        self.keep = _region("keep")
        self.clock = 0.0
        self.turn = 0.0

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Rise the pinnacle with the keep and turn the moat's energy for `boss` (None: at rest)."""
        self.clock += dt
        form = boss.form if boss != None else 0
        self.turn += SPIN[min(form, len(SPIN) - 1)] * dt
        self.dashes[0].rotation.y = self.turn
        self.dashes[1].sync(lit, dt)
        k = progress(self.keep, boss)
        base = pt(KEEP_AT[0], KEEP_AT[1], PARADE)
        self.pinnacle[0].position.set(base[0], PARADE + k * KEEP_RISE, base[2])
        self.pinnacle[1].sync(lit, dt)


def build_fort_rig(root: Any, neon: Any, breath: Any) -> FortRig:
    """Return the Star Fort's rig on `root` (the boss model's)."""
    pinnacle = _model("star-fort-pinnacle", root, _draw_pinnacle, neon, breath)
    base = pt(KEEP_AT[0], KEEP_AT[1], PARADE)
    pinnacle[0].position.set(base[0], PARADE, base[2])
    dashes = _model("star-fort-moat", root, _draw_dashes, neon, breath)
    return FortRig(pinnacle, dashes)


def _lifted(tris: list[Any], base: list[Any], lift: float) -> list[Any]:
    """Return `tris` moved over `base` (model space) and `lift` up."""
    return [
        [
            Vertex(
                [v.position[0] + base[0], v.position[1] + lift, v.position[2] + base[2]], v.color
            )
            for v in tri
        ]
        for tri in tris
    ]


def fort_triangles(unfold: float) -> list[Any]:
    """Return the rig's triangles for the wholeness check (BOSS-52): the pinnacle.

    Pushed up under the risen keep (`unfold` 1; at the first transformation it still stands in the
    keep), the moat's dashes left out (they lie on the moat).
    """
    parts = collect_parts(_draw_pinnacle)["parts"]
    base = pt(KEEP_AT[0], KEEP_AT[1], PARADE)
    lift = PARADE + (KEEP_RISE if unfold >= 1 else 0)
    result: list[Any] = []
    for layer in ["hull", "flesh", "bare", "bare_flesh"]:
        result.extend(_lifted(triangles(getattr(parts, layer).geometry), base, lift))
    return result

# Copyright (c) 2026 Renaud Guillon
"""MB-BELL-KEEP-04, MB-BELL-KEEP-05: the Bell Keep's rig, what moves that the fight does not need.

Logical pixels, nose +Z, Y up. Its bell swings in its tower's frame, tolling (harder once it has
transformed), and is gone with the tower; a portcullis behind each gate rises as its drawbridge
lowers, and the drawbridges' chains pay out from the winches over the gates to the bridges' tips
(D-228's custom rigs, BOSS-46). Nothing here is hit or fires: the bridges themselves are moving
pieces of the design (BOSS-45).
"""

import math

from game.config.bosses.lab.bell_keep import (
    BELL_AT,
    BELL_BEAM,
    BELL_KEEP,
    BRIDGE_LENGTH,
    FLOOR,
    GATE,
    GATE_FRONT,
    GATE_OPEN,
    GATE_TOP,
)
from game.config.bosses.moving_regions import motion_value, move_point
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.lab.bell_keep_parts import TIMBER, N
from game.view.bosses.region_motion import progress
from game.view.bosses.world_1_organic_kit import M
from game.view.enemies.enemy_mesh import build_enemy_model
from render.babylon import new_transform_node, set_enabled
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


# The bell (MB-BELL-KEEP-04): its profile `[radius, height over its lip]`, its swing (radians either
# way) and its period (a toll at each end), calm and once it has transformed.
BELL_PROFILE = [[4.3, 0], [4.2, 0.7], [3.4, 2], [3, 4.4], [2.5, 6.4], [1.3, 7.3], [0, 7.5]]
BELL_HANG = 8.2
SWING = [0.45, 0.8]
PERIOD = [6.0, 3.0]
# A portcullis: its bars' pitch, how far behind the gate's mouth it hangs, how high it rises.
BAR_PITCH = 2.7
PORTCULLIS_IN = 2.6
RISE = GATE_OPEN - FLOOR + 1
# A chain as drawn: this long along +Y, its links this long; scaled to its length.
CHAIN = 10
LINK = 2.5


def _region(region_id: str) -> Any:
    for region in BELL_KEEP.armour:
        if region.id == region_id:
            return region
    raise ValueError('The Bell Keep has no region "' + region_id + '"')


def _part_index(part_id: str) -> int:
    parts = BELL_KEEP.stats.parts
    for i in range(len(parts)):
        if parts[i].id == part_id:
            return i
    return -1


def _draw_bell(p: Any, pivot: Vec3) -> None:
    """Draw the bell hanging from its axle at `pivot` (model): bronze, lit bands, a yoke."""
    lip = pivot[1] - BELL_HANG
    p.hull.lathe(BELL_PROFILE, 10, M.panel, Placement([pivot[0], lip, pivot[2]]))
    p.neon.ring(4.25, 0.35, 10, N, Placement([pivot[0], lip + 0.25, pivot[2]]))
    p.neon.ring(2.75, 0.3, 10, N, Placement([pivot[0], lip + 5.2, pivot[2]]))
    p.hull.box([3.6, 1.6, 1.4], TIMBER, Placement([pivot[0], lip + 7.2, pivot[2]]))


def _draw_portcullis(p: Any, side: float) -> None:
    """Draw the portcullis of the gate on `side` (+1 the config's right), down: an iron grille."""
    x0 = side * GATE[0]
    x1 = side * GATE[1]
    y = GATE_FRONT + PORTCULLIS_IN
    width = GATE[1] - GATE[0]
    bars = math.floor(width / BAR_PITCH)
    for k in range(bars + 1):
        x = x0 + (x1 - x0) * k / bars
        q = boss_point(x, y, FLOOR - 0.3)
        p.hull.box([0.6, GATE_OPEN - FLOOR + 0.8, 0.6], M.base, Placement(q))
        p.neon.box([0.3, 0.6, 0.3], N, Placement([q[0], FLOOR - 0.6, q[2] - 0.35]))
    for h in [FLOOR + 2.5, FLOOR + 5.5]:
        q = boss_point((x0 + x1) / 2, y, h)
        p.hull.box([width + 0.4, 0.6, 0.5], M.base, Placement(q))


def _portcullis(side: float) -> Any:
    """Return the drawing of the portcullis on `side` (see `_draw_portcullis`)."""

    def draw(p: Any) -> None:
        _draw_portcullis(p, side)

    return draw


def _draw_chain(p: Any) -> None:
    """Draw a chain from the origin up +Y, `CHAIN` long: links turned a quarter each in turn."""
    count = math.floor(CHAIN / LINK)
    for k in range(count):
        size = [0.35, LINK * 1.1, 0.9] if k % 2 == 0 else [0.9, LINK * 1.1, 0.35]
        p.bare.box(size, M.base, Placement([0, k * LINK, 0]))


def _model(name: str, root: Any, draw: Any, neon: Any, breath: Any) -> list[Any]:
    """Return `[node, model]`: a model drawn by `draw` (model space) on a node of `root`."""
    scene = root.getScene()
    node = new_transform_node(name, scene)
    node.parent = root
    model = build_enemy_model(name, scene, neon, draw, breath)
    model.root.parent = node
    return [node, model]


class KeepRig:
    """The Bell Keep's bell, portcullises and drawbridge chains (see the module)."""

    def __init__(
        self,
        bell: list[Any],
        pivot: Vec3,
        gates: list[list[Any]],
        chains: list[list[Any]],
    ) -> None:
        self.bell = bell
        self.pivot = pivot
        # Per gate: `[node, model, region, side]`; per chain: `[node, model, region, anchor, x]`.
        self.gates = gates
        self.chains = chains
        self.belfry = _part_index("belfry")
        self.clock = 0.0

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Swing the bell, raise the portcullises, pay out the chains for `boss` (None: at rest)."""
        self.clock += dt
        self._show_bell(boss, lit, dt)
        for gate in self.gates:
            k = progress(gate[2], boss)
            gate[0].position.set(0, k * RISE, 0)
            gate[1].sync(lit, dt)
        for chain in self.chains:
            self._show_chain(chain, boss, lit, dt)

    def _show_bell(self, boss: Any, lit: Any, dt: float) -> None:
        node = self.bell[0]
        standing = True
        angry = False
        t = self.clock
        if boss != None:
            t = boss.age
            angry = boss.form >= 1
            if self.belfry >= 0 and self.belfry < len(boss.parts):
                part = boss.parts[self.belfry]
                standing = not part.destroyed and not part.hidden
        set_enabled(node, standing)
        if not standing:
            return
        k = 1 if angry else 0
        node.rotation.x = SWING[k] * math.sin(2 * math.pi * t / PERIOD[k])
        self.bell[1].sync(lit, dt)

    def _show_chain(self, chain: Any, boss: Any, lit: Any, dt: float) -> None:
        region = chain[2]
        motion = region.motion
        value = motion_value(motion, progress(region, boss))
        tip = move_point(motion, value, [chain[4], GATE_FRONT - BRIDGE_LENGTH + 0.8, FLOOR])
        end = boss_point(tip[0], tip[1], tip[2])
        start = chain[3]
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dz = end[2] - start[2]
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        node = chain[0]
        node.position.set(start[0], start[1], start[2])
        node.rotation.y = math.atan2(dx, dz)
        node.rotation.x = math.acos(max(-1, min(1, dy / max(length, 0.001))))
        node.scaling.set(1, max(length, 0.1) / CHAIN, 1)
        chain[1].sync(lit, dt)


def build_keep_rig(root: Any, neon: Any, breath: Any) -> KeepRig:
    """Return the Bell Keep's rig on `root` (the boss model's)."""
    pivot = boss_point(BELL_AT[0], BELL_AT[1], BELL_BEAM - 1.4)

    def bell(p: Any) -> None:
        _draw_bell(p, [0, 0, 0])

    bell_view = _model("bell-keep-bell", root, bell, neon, breath)
    bell_view[0].position.set(pivot[0], pivot[1], pivot[2])
    gates: list[list[Any]] = []
    chains: list[list[Any]] = []
    for side in [1, -1]:
        name = "right" if side > 0 else "left"
        region = _region("bridge-" + name)

        view = _model("bell-keep-portcullis-" + name, root, _portcullis(side), neon, breath)
        gates.append([view[0], view[1], region, side])
        for x in [GATE[0] + 1.2, GATE[1] - 1.2]:
            anchor = boss_point(side * x, GATE_FRONT + 1.2, GATE_TOP + 1)
            link = _model("bell-keep-chain-" + name + str(x), root, _draw_chain, neon, breath)
            chains.append([link[0], link[1], region, anchor, side * x])
    return KeepRig(bell_view, pivot, gates, chains)


def rig_triangles(_unfold: float) -> list[Any]:
    """Return the rig's triangles for the wholeness check (BOSS-52): none.

    Its pieces hang on the core's: the bell from its axle, the portcullises in their gates, the
    chains from the winches to the bridges' tips.
    """
    return []

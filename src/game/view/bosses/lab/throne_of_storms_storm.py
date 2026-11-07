# Copyright (c) 2026 Renaud Guillon
"""FB-THRONE-OF-STORMS-12: the lightning crackling round the Throne of Storms' spire (its rig).

Visual only (it fires nothing and cannot be hit). From the start, short sparks crackle round the
spire's tip; as its second transformation strains it, and from then on, forked bolts leap from the
tip down to its four towers' tops, slid out by then. Each bolt has two zigzag shapes it flickers
between (and off), on its own beat, so the storm crackles. Logical pixels, nose +Z, Y up.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.throne_of_storms import (
    SLIDE_OUT,
    SPIRE_AT,
    SPIRE_TOP,
    TOWER_AT,
    TOWER_TOP,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.final_boss_greebles import rod
from game.view.enemies.enemy_mesh import build_enemy_model
from render.babylon import new_transform_node, set_enabled

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["throne-of-storms"]
# The bolts' zigzag: how many legs, how far a kink strays (a share of the bolt's length), a bolt's
# radius; the sparks' length; how many times a second each bolt changes shape.
LEGS = 6
STRAY = 0.09
RADIUS = 0.45
SPARK = 7
FLICKER = 13
# Where the bolts leap to: the towers' tops, out on their rails (config, and height).
TOWERS: list[Any] = [[1, 1], [-1, 1], [1, -1], [-1, -1]]
# Fixed kinks for each shape (a share of `STRAY` either side), so the bolts are drawn once.
KINKS: list[Any] = [
    [0.6, -1, 0.8, -0.4, 1],
    [-0.8, 0.5, -1, 0.9, -0.3],
]


def _tip() -> Vec3:
    return boss_point(SPIRE_AT[0], SPIRE_AT[1], SPIRE_TOP)


def _zigzag(p: Any, a: Vec3, b: Vec3, kinks: list[Any], radius: float) -> None:
    """Draw a lit zigzag from `a` to `b`, its kinks strayed sideways (and up) by `kinks`."""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dz = b[2] - a[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz) or 1
    flat = math.sqrt(dx * dx + dz * dz) or 1
    # Sideways, flat (across the bolt), and up.
    side = [-dz / flat, 0, dx / flat]
    last = a
    for k in range(1, LEGS + 1):
        t = k / LEGS
        stray = kinks[(k - 1) % len(kinks)] * STRAY * length if k < LEGS else 0
        point = [
            a[0] + dx * t + side[0] * stray,
            a[1] + dy * t + stray * 0.4,
            a[2] + dz * t + side[2] * stray,
        ]
        rod(p.neon, last, point, radius, N)
        last = point


def _bolt(target: Vec3, shape: int) -> Any:
    def draw(p: Any) -> None:
        _zigzag(p, _tip(), target, KINKS[shape], RADIUS)

    return draw


def _sparks(shape: int) -> Any:
    """Return the drawing of the tip's sparks in shape `shape`: three short forks round it."""

    def draw(p: Any) -> None:
        tip = _tip()
        for k in range(3):
            a = (k * 2 + shape) * math.pi / 3 + 0.4
            end = [
                tip[0] + math.cos(a) * SPARK,
                tip[1] - 2 - shape * 2,
                tip[2] + math.sin(a) * SPARK,
            ]
            _zigzag(p, tip, end, KINKS[(k + shape) % 2], RADIUS * 0.7)

    return draw


def _towers() -> list[Vec3]:
    out = TOWER_AT + SLIDE_OUT
    return [boss_point(c[0] * out, c[1] * out, TOWER_TOP + 1) for c in TOWERS]


class StormRig:
    """The spire's lightning: the tip's sparks and the bolts to the towers, `[node, model]` each.

    `sparks` (two shapes) and `bolts` (per tower, two shapes).
    """

    def __init__(self, sparks: list[Any], bolts: list[Any]) -> None:
        self.sparks = sparks
        self.bolts = bolts
        self.age = 0.0

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Flicker the sparks always, and the bolts once its second transformation strains it."""
        self.age += dt
        beat = math.floor(self.age * FLICKER)
        storm = False
        if boss != None:
            storm = boss.form >= 2 or (boss.transforming_into == 2 and boss.transform > 0.1)
        for k in range(len(self.sparks)):
            on = beat % 3 == k
            set_enabled(self.sparks[k][0], on)
            if on:
                self.sparks[k][1].sync(lit, dt)
        for i in range(len(self.bolts)):
            pair = self.bolts[i]
            step = (beat + i * 2) % (4 + i % 2)
            for k in range(len(pair)):
                on = storm and step == k
                set_enabled(pair[k][0], on)
                if on:
                    pair[k][1].sync(lit, dt)


def _model(name: str, root: Any, draw: Any, neon: Any, breath: Any) -> list[Any]:
    """Return `[node, model]`: a model drawn by `draw` on a node of `root`."""
    scene = root.getScene()
    node = new_transform_node(name, scene)
    node.parent = root
    model = build_enemy_model(name, scene, neon, draw, breath)
    model.root.parent = node
    set_enabled(node, False)
    return [node, model]


def _name(i: int, k: int) -> str:
    return "throne-bolt-" + str(i) + "-" + str(k)


def build_storm_rig(root: Any, neon: Any, breath: Any) -> StormRig:
    """Return the spire's lightning on `root` (the boss model's)."""
    sparks = [_model("throne-spark-" + str(k), root, _sparks(k), neon, breath) for k in range(2)]
    towers = _towers()
    bolts = [
        [_model(_name(i, k), root, _bolt(towers[i], k), neon, breath) for k in range(2)]
        for i in range(len(towers))
    ]
    return StormRig(sparks, bolts)


def storm_triangles(_unfold: float) -> list[Any]:
    """Return the rig's triangles for the wholeness check: none (light, standing on nothing)."""
    return []

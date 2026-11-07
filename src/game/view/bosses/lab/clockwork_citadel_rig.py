# Copyright (c) 2026 Renaud Guillon
"""FB-CLOCKWORK-CITADEL-02, FB-CLOCKWORK-CITADEL-10: the Clockwork Citadel's rig.

Logical pixels, nose +Z, Y up. What moves that the fight does not need to know about: the hour
hand turning on the arbor's top (a twelfth as fast as the minute hand, which is a part, BOSS-34),
the exposed gear trains on the roof turning with the clock. The pinions meshing the great wheels
stop once the wheels unmesh (the first transformation); the back train keeps time to the end.
Nothing here is hit or fires.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.clockwork_citadel import ARBOR, ROOF, SPIN
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.lab.clockwork_citadel_parts import BRASS, gear, pt
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


N = BOSS_LOOK.neon["clockwork-citadel"]
# The hour hand: its length, its turn at rest (radians, pointing at four o'clock), its rate as a
# share of the minute hand's.
HOUR_LENGTH = 19
HOUR_REST = -2.1
HOUR_RATE = 1 / 12
# The roof's gear trains: `[x, y, radius, teeth, flank]` (the right ones; mirrored), `flank` 1 for
# the pinions meshing the great wheels (they stop once those unmesh). Each turns the other way to
# its neighbour, at a rate set by its size.
TRAINS = [  # type: list[list[float]]
    [40.5, 18, 4.6, 10, 1],
    [41, 7.5, 3.2, 8, 1],
    [15.5, 41.5, 4.6, 10, 0],
    [25.5, 40.5, 3.6, 8, 0],
]
TRAIN_HEIGHTS = [ROOF, ROOF + 1.4]
# Radians a second the gears turn at, for a radius of 1.
TRAIN_RATE = 2.2


def _model(name: str, root: Any, draw: Any, neon: Any, breath: Any) -> list[Any]:
    """Return `[node, model]`: a model drawn by `draw` (model space) on a node of `root`."""
    scene = root.getScene()
    node = new_transform_node(name, scene)
    node.parent = root
    model = build_enemy_model(name, scene, neon, draw, breath)
    model.root.parent = node
    return [node, model]


def _draw_hour_hand(p: Any) -> None:
    """Draw the hour hand at the origin, pointing at six o'clock: a broad blade, a lit line."""
    h0 = ARBOR[1]
    h1 = ARBOR[1] + 0.8
    blade = [pt(-1.4, 2), pt(-3, -6), pt(-1.2, -13), pt(-3.6, -16), pt(0, -HOUR_LENGTH)]
    blade.extend([pt(3.6, -16), pt(1.2, -13), pt(3, -6), pt(1.4, 2)])
    p.hull.slab(blade, [h0, h1], M.panel, None, M.base)
    p.hull.cylinder(3, 1.2, 8, BRASS, Placement([0, h0 - 0.2, 0]))
    p.neon.box([0.5, 0.3, HOUR_LENGTH - 6], N, Placement(boss_point(0, -(HOUR_LENGTH - 2) / 2, h1)))
    p.neon.cylinder(0.9, 0.4, 8, N, Placement([0, h0 + 1, 0]))


def _gear_drawing(radius: float, teeth: int) -> Any:
    def draw(p: Any) -> None:
        gear(p, [0, 0, 0], radius, teeth, TRAIN_HEIGHTS, BRASS)

    return draw


class CitadelRig:
    """The Clockwork Citadel's hour hand and roof gear trains (see the module)."""

    def __init__(self, hour: list[Any], gears: list[list[Any]]) -> None:
        # Per gear: `[node, model, rate, flank]`.
        self.hour = hour
        self.gears = gears
        self.clock = 0.0
        self.stopped_at = -1.0

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Turn the hour hand and the gears for `boss` (None: on the clock of the viewer)."""
        self.clock += dt
        t = self.clock
        spin = SPIN * t
        unmeshed = False
        if boss != None:
            t = boss.age
            spin = boss.spin
            unmeshed = boss.form >= 1 or boss.transforming_into == 1
        if unmeshed and self.stopped_at < 0:
            self.stopped_at = t
        if not unmeshed:
            self.stopped_at = -1.0
        self.hour[0].rotation.y = HOUR_REST + spin * HOUR_RATE
        self.hour[1].sync(lit, dt)
        for g in self.gears:
            run = t
            if g[3] > 0 and self.stopped_at >= 0:
                run = self.stopped_at
            g[0].rotation.y = g[2] * run
            g[1].sync(lit, dt)


def build_citadel_rig(root: Any, neon: Any, breath: Any) -> CitadelRig:
    """Return the Clockwork Citadel's rig on `root` (the boss model's)."""
    hour = _model("clockwork-citadel-hour-hand", root, _draw_hour_hand, neon, breath)
    gears: list[list[Any]] = []
    for side in [1, -1]:
        for k in range(len(TRAINS)):
            g = TRAINS[k]
            name = "clockwork-citadel-gear-" + str(k) + ("r" if side > 0 else "l")
            view = _model(name, root, _gear_drawing(g[2], math.floor(g[3])), neon, breath)
            at = boss_point(side * g[0], g[1], 0)
            view[0].position.set(at[0], 0, at[2])
            way = 1 if k % 2 == 0 else -1
            gears.append([view[0], view[1], side * way * TRAIN_RATE / g[2], g[4]])
    return CitadelRig(hour, gears)


def rig_triangles(_unfold: float) -> list[Any]:
    """Return the rig's triangles for the wholeness check (BOSS-52): none.

    Its pieces lie on the core's: the hour hand on the arbor's top, the gears on the roof.
    """
    return []

# Copyright (c) 2026 Renaud Guillon
"""FB-STORM-PETREL-10: the struts holding the Storm Petrel's gun batteries to its body.

Logical pixels, nose +Z, Y up. Each battery slides straight out of its body's flank to its spot
on an outer wing (`slideFrom`, `boss_reveal`). Its strut never turns: a bracket against the deck's
inner side moves out with it, and an arm and a brace from the body's flank stretch out to the
bracket as it goes.
"""

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.final_bosses import STORM_PETREL
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_reveal import HIDDEN, SHOWN, ease, reveal_phase, share
from game.view.bosses.final_boss_greebles import rod
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


N = BOSS_LOOK.neon["storm-petrel"]
BATTERIES = ["battery-left", "battery-right"]

# The strut: where it meets the body's flank (x from the centre line), its bracket against the deck
# (a gap from the deck's side, its thickness, height and depth), its arm (its height at the body
# and at the bracket, its radius) and its brace (from low on the body, further back, up to the
# bracket's foot). It runs a little behind the battery's centre (towards the tail), clear of the
# sweepers that come out behind the wing roots (FB-STORM-PETREL-11). Shorter than `shortest` of
# its full length, the arm is hidden (still inside the body).
STRUT: dict[str, Any] = {
    "bodyX": 12,
    "gap": 0.6,
    "bracket": [2.2, 8, 9],
    "bracketBase": 7.5,
    "arm": [12, 13.5],
    "armRadius": 1.4,
    "armZ": -1,
    "brace": [5, 9],
    "braceRadius": 1.0,
    "braceZ": [-9, -3],
    "shortest": 0.03,
}


def _battery(part_id: str) -> Any:
    for spec in STORM_PETREL.stats.parts:
        if spec.id == part_id:
            return spec
    raise ValueError('The Storm Petrel has no part "' + part_id + '"')


class StrutShape:
    """Where the strut of battery `part_id` goes (model space).

    `side` (+1 or -1, its model X), `at` (the battery's centre), `inner` (X of the bracket's inner
    face once out), `pivot` (X where the arm leaves the body) and `start` (how far along X the
    battery starts, from `at`, inside the body).
    """

    def __init__(self, part_id: str) -> None:
        spec = _battery(part_id)
        look = STORM_PETREL.weapons[part_id]
        self.at = boss_point(spec.x, spec.y)
        self.side = 1 if self.at[0] > 0 else -1
        size = STRUT["bracket"]
        self.centre = self.at[0] - self.side * (look.radius + STRUT["gap"] + size[0] / 2)
        self.inner = self.centre - self.side * size[0] / 2
        self.pivot = self.side * STRUT["bodyX"]
        out = boss_point(look.slideFrom[0], look.slideFrom[1])
        self.start = out[0] - self.at[0]

    def bracket(self, p: Any) -> None:
        """Draw the bracket, flat against the deck's inner side, a neon line down its face."""
        size = STRUT["bracket"]
        bottom = STRUT["bracketBase"]
        z = self.at[2]
        # A box stands on its base.
        p.hull.box(size, M.base, Placement([self.centre, bottom, z]))
        line = size[1] * 0.7
        p.neon.box([0.4, line, 0.6], N, Placement([self.inner, bottom + (size[1] - line) / 2, z]))

    def arm(self, p: Any) -> None:
        """Draw the arm and the brace, from the body's flank (at X 0: the pivot) to the bracket."""
        k = STRUT
        reach = self.inner - self.pivot
        z = self.at[2] + k["armZ"]
        start = [0, k["arm"][0], z]
        end = [reach, k["arm"][1], z]
        rod(p.hull, start, end, k["armRadius"], M.base)
        lift = k["armRadius"] * 0.9
        rod(p.neon, [0, start[1] + lift, z], [reach, end[1] + lift, z], 0.3, N)
        brace = k["brace"]
        bz = k["braceZ"]
        low = [0, brace[0], self.at[2] + bz[0]]
        high = [reach, brace[1], self.at[2] + bz[1]]
        rod(p.hull, low, high, k["braceRadius"], M.base)


def _out(boss: Any) -> float:
    """How far out the batteries are for `boss` (0: inside the body, 1: in place), -1 if hidden."""
    if boss == None:
        return -1
    reveal = _battery(BATTERIES[0]).reveal
    phase = reveal_phase(reveal, boss.form, boss.transforming_into)
    if phase == HIDDEN:
        return -1
    if phase == SHOWN:
        return 1
    look = BOSS_LOOK.reveal
    if boss.transform < look.swing[0]:
        return -1
    return ease(share(boss.transform, look.swing))


class StrutRig:
    """The battery struts, each a model on a node of the boss model.

    For each, its arm (stretching out) and its bracket (moving out).
    """

    def __init__(self, shapes: list[StrutShape], arms: list[Any], brackets: list[Any]) -> None:
        self.shapes = shapes
        self.arms = arms
        self.brackets = brackets

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Move the struts out with the batteries (hidden until they come out) and sync them."""
        out = _out(boss)
        for i in range(len(self.shapes)):
            shape = self.shapes[i]
            arm = self.arms[i]
            bracket = self.brackets[i]
            back = (1 - max(out, 0)) * shape.start
            full = shape.inner - shape.pivot
            share_out = (full + back) / full
            set_enabled(bracket[0], out >= 0)
            set_enabled(arm[0], out >= 0 and share_out > STRUT["shortest"])
            bracket[0].position.set(back, 0, 0)
            arm[0].scaling.set(max(share_out, STRUT["shortest"]), 1, 1)
            arm[1].sync(lit, dt)
            bracket[1].sync(lit, dt)


def _model(name: str, root: Any, at: Vec3, draw: Any, neon: Any, breath: Any) -> list[Any]:
    """Return `[node, model]`: a model drawn by `draw` on a node of `root` at `at`."""
    scene = root.getScene()
    node = new_transform_node(name, scene)
    node.parent = root
    node.position.set(at[0], at[1], at[2])
    model = build_enemy_model(name, scene, neon, draw, breath)
    model.root.parent = node
    return [node, model]


def build_strut_rig(root: Any, neon: Any, breath: Any) -> StrutRig:
    """Return the battery struts on `root` (the boss model's)."""
    shapes: list[StrutShape] = []
    arms: list[Any] = []
    brackets: list[Any] = []
    for part_id in BATTERIES:
        shape = StrutShape(part_id)
        name = "storm-petrel-strut-" + part_id
        shapes.append(shape)
        arms.append(_model(name + "-arm", root, [shape.pivot, 0, 0], shape.arm, neon, breath))
        brackets.append(_model(name + "-bracket", root, [0, 0, 0], shape.bracket, neon, breath))
    return StrutRig(shapes, arms, brackets)

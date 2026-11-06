# Copyright (c) 2026 Renaud Guillon
"""MB-ROCKET-INTERCEPTOR-02, MB-ROCKET-INTERCEPTOR-05: the Rocket Interceptor's view rig.

Logical pixels, nose +Z, Y up (towards the camera). The morph of its one transformation, staged
on the reveal timeline (`BOSS_LOOK.reveal`):
- its boosters' casings (their pylons, back saddles and nozzles; their nose cones are its parts):
  as it strains their pylons' bolts flash, then each booster rolls outward off its pylons and
  falls away behind and below it, still burning, out of sight by its end (they are jettisoned);
- the middle section of each wing: it telescopes out of the stub wing half as far as the outer
  section (a moving piece, drawn with the armour), so the wing comes out in two stages;
- the two doors over each new wingtip: they open up like a clamshell, fore and aft, as the lance
  under them rises (its pod, drawn by the boss model, rides the outer section).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.rocket_interceptor import (
    BOOSTER_AXIS,
    BOOSTER_CASING,
    BOOSTER_EXIT,
    BOOSTER_R,
    BOOSTER_TOP,
    BOOSTER_X,
    EXT_IN,
    EXT_Y,
    MID,
    MID_IN,
    WING,
    WING_Y,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_reveal import ease, share
from game.view.bosses.world_1_organic_kit import F, M
from game.view.enemies.enemy_mesh import build_enemy_model, collect_parts
from render.babylon import new_transform_node, set_enabled
from render.geometry.mesh_triangles import Vertex, triangles
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["rocket-interceptor"]
QUARTER = math.pi / 2
LAYERS = ["hull", "bare", "flesh", "neon", "vein", "charge"]
SIDES = [1, -1]
# Booster paint: pale bands round the dark casing (shown in the body shades).
BAND = [0.24, 0.24, 0.26]
# The jettison (shares of the transformation): the bolts flash until `BOLTS`; the boosters roll
# outward `ROLL` radians and drift `DRIFT` px out, back and down over `FALL`.
BOLTS = 0.15
FALL = [0.12, 1.0]
ROLL = 1.25
DRIFT = [45, 80, 110]
# The doors over each wingtip: their span `[x0, x1]`, their hinges' Y (front, back) and the Y
# they meet at, their height, and how far they open (radians) over `OPEN`.
DOOR_X = [38, 49.5]
DOOR_Y = [11, 23, 17]
DOOR_H = EXT_Y[1]
DOOR_OPEN = 2.6
OPEN = [0.36, 0.56]


def pt(x: float, y: float, h: float) -> Vec3:
    """Return the playfield point `(x, y)` at height `h` in model space."""
    return boss_point(x, y, h)


def flat(x: float, y: float) -> list[Any]:
    """Return the playfield point `(x, y)` as a model outline point `[x, z]`."""
    return [-x, -y]


def pivot(side: float) -> Vec3:
    """Return the booster's roll pivot (model space): along its outer foot."""
    return pt(side * (BOOSTER_X + BOOSTER_R), 0, BOOSTER_AXIS - BOOSTER_R)


def draw_booster(side: float) -> Any:
    """Return the drawing of the booster casing on `side`, in its pivot's frame.

    A long cylinder of dark plating with pale bands, a dark bulkhead at its front (where its nose
    cone, a part, sits), the saddle on its back the missile block stands on, its bell nozzle and
    flame at the back, two pylons to the wingtip, their bolts lit.
    """
    o = pivot(side)

    def at(x: float, y: float, h: float) -> Vec3:
        q = pt(side * x, y, h)
        return [q[0] - o[0], q[1] - o[1], q[2] - o[2]]

    def draw(p: Any) -> None:
        y0 = BOOSTER_CASING[0]
        y1 = BOOSTER_CASING[1]
        lay = Placement(at(BOOSTER_X, y1, BOOSTER_AXIS), 0, QUARTER)
        p.hull.cylinder(BOOSTER_R, y1 - y0, 10, M.base, lay)
        for y in [-24, -2, 20]:
            p.bare.ring(
                BOOSTER_R + 0.15,
                2.4,
                10,
                BAND,
                Placement(at(BOOSTER_X, y + 1.2, BOOSTER_AXIS), 0, QUARTER),
            )
        p.neon.ring(
            BOOSTER_R + 0.2, 0.6, 10, N, Placement(at(BOOSTER_X, 9, BOOSTER_AXIS), 0, QUARTER)
        )
        p.bare.cylinder(
            BOOSTER_R - 1, 0.6, 10, M.dark, Placement(at(BOOSTER_X, y0, BOOSTER_AXIS), 0, QUARTER)
        )
        # The saddle on its back: a flat armoured deck the missile block stands on.
        p.hull.bevel_slab(
            [
                flat(side * (BOOSTER_X - 6.5), -24),
                flat(side * (BOOSTER_X + 6.5), -24),
                flat(side * (BOOSTER_X + 6.5), -5),
                flat(side * (BOOSTER_X - 6.5), -5),
            ],
            [BOOSTER_TOP - 3, BOOSTER_TOP - 0.6, BOOSTER_TOP],
            [0, 0.6],
            M.panel,
            Placement([-o[0], -o[1], -o[2]]),
            M.base,
        )
        # A stringer down its back and a light along each flank.
        p.hull.box(
            [2.4, 1.2, 34], M.panel, Placement(at(BOOSTER_X, 13, BOOSTER_AXIS + BOOSTER_R - 0.6))
        )
        for k in [-1, 1]:
            p.neon.box(
                [0.5, 0.5, 40],
                N,
                Placement(at(BOOSTER_X + k * (BOOSTER_R - 0.2), 4, BOOSTER_AXIS + 3)),
            )
        # The bell nozzle, its flame.
        p.hull.lathe(
            [[5.5, 0], [6.5, 3.5], [8.4, BOOSTER_EXIT - y1]],
            10,
            M.panel,
            Placement(at(BOOSTER_X, y1, BOOSTER_AXIS), 0, -QUARTER),
            False,
        )
        p.bare.cylinder(
            6.2,
            1,
            10,
            M.dark,
            Placement(at(BOOSTER_X, BOOSTER_EXIT - 1.5, BOOSTER_AXIS), 0, -QUARTER),
        )
        p.reactor(at(BOOSTER_X, BOOSTER_EXIT - 1, BOOSTER_AXIS), 5.6)
        # Its pylons to the wingtip, a bolt lit on each.
        tip = WING[1][0]
        for y in [3, 19]:
            mid_x = (tip - 1 + BOOSTER_X - BOOSTER_R + 1.5) / 2
            width = BOOSTER_X - BOOSTER_R + 1.5 - tip + 1
            p.hull.box([width, 4.5, 6], M.panel, Placement(at(mid_x, y, WING_Y[1])))
            p.neon.box([1.6, 0.4, 1.6], N, Placement(at(tip + 1.5, y, WING_Y[1] + 4.5)))

    return draw


def draw_middle(side: float) -> Any:
    """Return the drawing of the middle section of the wing on `side`, as drawn once out.

    A plated slab a little thinner than the stub wing, a light along its leading edge, two seams.
    """

    def draw(p: Any) -> None:
        x0 = side * MID[0]
        x1 = side * MID[1]
        outline = [flat(x0, MID[2]), flat(x1, MID[2]), flat(x1, MID[3]), flat(x0, MID[3])]
        p.flesh.bevel_slab(outline, [3, 5, 5.9], [0.3, 0.6], F.graphite, None, F.slate)
        p.neon.box([MID[1] - MID[0] - 2, 0.4, 0.5], N, Placement(pt(side * 28, MID[2] + 0.6, 5.8)))
        for x in [26, 32]:
            p.bare.box([0.5, 0.3, MID[3] - MID[2] - 3], M.dark, Placement(pt(side * x, 17, 5.85)))

    return draw


def draw_door(side: float, back: bool) -> Any:
    """Return the drawing of a door over the wingtip on `side`, in its hinge's frame.

    A thin plate from its hinge to the middle of the tip, ribbed, its free edge lit.
    """
    length = DOOR_Y[2] - DOOR_Y[0]
    sign = 1 if back else -1

    def draw(p: Any) -> None:
        width = DOOR_X[1] - DOOR_X[0]
        x = -side * (DOOR_X[0] + DOOR_X[1]) / 2
        p.hull.box([width, 0.8, length - 0.2], M.panel, Placement([x, 0, sign * length / 2]))
        p.neon.box([width - 1.5, 0.5, 0.5], N, Placement([x, 0.5, sign * (length - 0.6)]))
        p.bare.box([width - 3, 0.3, 0.8], M.dark, Placement([x, 0.8, sign * length * 0.4]))

    return draw


def door_hinge(back: bool) -> Vec3:
    """Return a door's hinge (model space, the outer section out), at its span's middle."""
    return pt(0, DOOR_Y[1] if back else DOOR_Y[0], DOOR_H)


def slid(boss: Any) -> float:
    """How far the wing's sections have slid out for `boss` (None: in), 0 to 1."""
    if boss == None:
        return 0
    if boss.form >= 1:
        return 1
    if boss.transforming_into != 1:
        return 0
    return ease(share(boss.transform, BOSS_LOOK.reveal.move))


def opened(boss: Any) -> float:
    """How far the doors over the wingtips have opened, 0 to 1."""
    if boss == None:
        return 0
    if boss.form >= 1:
        return 1
    if boss.transforming_into != 1:
        return 0
    return ease(share(boss.transform, OPEN))


def jettison(boss: Any) -> float:
    """How far the boosters have fallen away (-1: gone; 0: on their pylons)."""
    if boss == None:
        return 0
    if boss.form >= 1:
        return -1
    if boss.transforming_into != 1:
        return 0
    return ease(share(boss.transform, FALL))


class InterceptorRig:
    """The boosters on their pivots, the middle sections and the doors on their hinges."""

    def __init__(
        self, boosters: list[Any], middles: list[Any], doors: list[Any], models: list[Any]
    ) -> None:
        self.boosters = boosters
        self.middles = middles
        self.doors = doors
        self.models = models

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Pose its pieces for the boss's transformation, and sync their models."""
        fall = jettison(boss)
        k = slid(boss)
        a = opened(boss) * DOOR_OPEN
        for i in range(2):
            side = SIDES[i]
            booster = self.boosters[i]
            set_enabled(booster, fall >= 0)
            if fall >= 0:
                p = pivot(side)
                jolt = 0.0
                if boss != None and boss.transforming_into == 1 and boss.transform < BOLTS:
                    jolt = math.sin(boss.transform * 90) * 0.6
                booster.position.set(
                    p[0] - side * DRIFT[0] * fall + jolt,
                    p[1] - DRIFT[2] * fall * fall,
                    p[2] - DRIFT[1] * fall * fall,
                )
                booster.rotation.z = side * ROLL * fall
                booster.rotation.y = -side * 0.35 * fall
            self.middles[i].position.set(side * MID_IN * (1 - k), 0, 0)
            for j in range(2):
                back = j == 1
                door = self.doors[i * 2 + j]
                hinge = door_hinge(back)
                door.position.set(hinge[0] + side * EXT_IN * (1 - k), hinge[1], hinge[2])
                door.rotation.x = -a if back else a
        for model in self.models:
            model.sync(lit, dt)


def _node(name: str, root: Any, at: Vec3) -> Any:
    node = new_transform_node(name, root.getScene())
    node.parent = root
    node.position.set(at[0], at[1], at[2])
    return node


def _hang(name: str, root: Any, at: Vec3, draw: Any, neon: Any, breath: Any) -> list[Any]:
    """Return `[node, model]`: a node on `root` at `at` carrying the model `draw` draws."""
    node = _node(name, root, at)
    model = build_enemy_model(name, root.getScene(), neon, draw, breath)
    model.root.parent = node
    return [node, model]


def build_interceptor_rig(root: Any, neon: Any, breath: Any) -> InterceptorRig:
    """Return the boosters, middle sections and doors on `root` (the boss model's)."""
    models: list[Any] = []
    boosters: list[Any] = []
    middles: list[Any] = []
    doors: list[Any] = []
    for side in SIDES:
        name = "rocket-interceptor-" + ("right" if side > 0 else "left")
        booster = _hang(name + "-booster", root, pivot(side), draw_booster(side), neon, breath)
        boosters.append(booster[0])
        models.append(booster[1])
        middle = _hang(name + "-middle", root, [0, 0, 0], draw_middle(side), neon, breath)
        middles.append(middle[0])
        models.append(middle[1])
        for back in [False, True]:
            door = _hang(
                name + "-door-" + ("back" if back else "front"),
                root,
                door_hinge(back),
                draw_door(side, back),
                neon,
                breath,
            )
            doors.append(door[0])
            models.append(door[1])
    return InterceptorRig(boosters, middles, doors, models)


def _drawn(draw: Any) -> list[Any]:
    parts = collect_parts(draw)["parts"]
    result: list[Any] = []
    for layer in LAYERS:
        result.extend(triangles(getattr(parts, layer).geometry))
    return result


def _moved(tris: list[Any], at: Vec3, turn: float) -> list[Any]:
    """`tris` turned `turn` about X (as Babylon's `rotation.x`), then moved to `at`."""
    c = math.cos(turn)
    s = math.sin(turn)
    result: list[Any] = []
    for tri in tris:
        placed: list[Any] = []
        for v in tri:
            x = v.position[0]
            y = v.position[1]
            z = v.position[2]
            placed.append(
                Vertex([x + at[0], y * c - z * s + at[1], y * s + z * c + at[2]], v.color)
            )
        result.append(placed)
    return result


def interceptor_triangles(unfold: float) -> list[Any]:
    """Return the rig's triangles (model space): its boosters on, or its wings out and open."""
    result: list[Any] = []
    out = unfold >= 1
    for side in SIDES:
        if not out:
            result.extend(_moved(_drawn(draw_booster(side)), pivot(side), 0))
        result.extend(_moved(_drawn(draw_middle(side)), [0 if out else side * MID_IN, 0, 0], 0))
        for back in [False, True]:
            hinge = door_hinge(back)
            at = [hinge[0] + (0 if out else side * EXT_IN), hinge[1], hinge[2]]
            turn = DOOR_OPEN if out else 0
            result.extend(_moved(_drawn(draw_door(side, back)), at, -turn if back else turn))
    return result

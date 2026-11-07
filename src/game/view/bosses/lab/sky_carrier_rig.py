# Copyright (c) 2026 Renaud Guillon
"""FB-SKY-CARRIER-05, FB-SKY-CARRIER-11: the Sky Carrier's view rig.

Logical pixels, nose +Z, Y up. Its lift engines' rotors, spinning in their ducts all the time
(visual only), and the beam cannon's boom: hinged at the bow's tip, stowed lying aft along the
deck's centre line between the catapults; at the second transformation it swings up and over the
bow, half a turn about its hinge, to point straight ahead, the beam cannon (a part, drawn with the
boss's parts) rising onto its end.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.sky_carrier import BOOM_HINGE, BOOM_LENGTH, FAN_H, FAN_RADIUS, LIFT_FANS
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_reveal import ease, share
from game.view.bosses.world_1_organic_kit import M
from game.view.enemies.enemy_mesh import build_enemy_model, collect_parts
from render.babylon import new_transform_node
from render.geometry.mesh_triangles import Vertex, triangles
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["sky-carrier"]
QUARTER = math.pi / 2
LAYERS = ["hull", "bare", "neon", "vein", "charge"]
# The boom's half width and half height round its axis, and the share of the transformation it
# swings over in (from the armour's burst to the weapons' swing's end).
BOOM_HALF = [3, 1.4]
SWING = [0.15, 0.75]
# The lift rotors' spin (radians a second) and blades.
FAN_SPIN = 9
FAN_BLADES = 4


def hinge() -> Vec3:
    """Return the boom's hinge (model space): at the bow's tip, on the boom's axis."""
    return boss_point(0, BOOM_HINGE[0], BOOM_HINGE[1])


def draw_boom(p: Any) -> None:
    """Draw the boom in its hinge's frame, stowed: lying along -Z from the hinge, its axis at 0.

    A box girder, the same above and below its axis (it turns over as it swings), lit rails down
    its sides, braces across, a heavy knuckle at the hinge and a cradle at its end.
    """
    w = BOOM_HALF[0]
    h = BOOM_HALF[1]
    length = BOOM_LENGTH
    p.hull.box([w * 2, h * 2, length - 2], M.base, Placement([0, -h, -length / 2 - 1]))
    for side in [-1, 1]:
        p.hull.box(
            [0.9, h * 2 + 0.6, length - 3],
            M.panel,
            Placement([side * (w + 0.2), -h - 0.3, -length / 2 - 1]),
        )
        p.neon.box([0.4, 0.6, length - 6], N, Placement([side * (w + 0.7), -0.3, -length / 2 - 1]))
    for k in range(4):
        z = -4 - k * (length - 6) / 3
        p.bare.box([w * 2 + 0.4, h * 2 + 0.4, 1], M.dark, Placement([0, -h - 0.2, z]))
    p.hull.cylinder(h + 1.4, w * 2 + 3, 8, M.panel, Placement([-(w + 1.5), 0, 0], QUARTER, QUARTER))
    p.hull.box([w * 2 + 2, h * 2 + 1.2, 3], M.panel, Placement([0, -h - 0.6, -length + 1.5]))


def draw_fan(p: Any) -> None:
    """Draw a lift rotor's blades round its hub (in the hub's frame, spinning about Y)."""
    for k in range(FAN_BLADES):
        a = k * 2 * math.pi / FAN_BLADES
        reach = FAN_RADIUS - 0.8
        p.bare.box(
            [1.8, 0.4, reach],
            M.panel,
            Placement([math.sin(a) * reach / 2, 0, math.cos(a) * reach / 2], a),
        )
    p.bare.cylinder(1.6, 1.2, 8, M.base, Placement([0, -0.2, 0]), 1)
    p.neon.cylinder(0.8, 0.3, 6, N, Placement([0, 1, 0]))


def unfolding(boss: Any) -> float:
    """How far the boom has swung for `boss` (None: stowed), 0 to 1."""
    if boss == None:
        return 0
    if boss.form >= 2:
        return 1
    if boss.transforming_into != 2:
        return 0
    return ease(share(boss.transform, SWING))


def fan_points() -> list[Vec3]:
    """Return each lift rotor's hub (model space), in its duct."""
    return [boss_point(q[0], q[1], FAN_H + 1.2) for q in LIFT_FANS]


class CarrierRig:
    """The boom on its hinge node, and the lift rotors on their hub nodes."""

    def __init__(self, boom: Any, fans: list[Any], models: list[Any]) -> None:
        self.boom = boom
        self.fans = fans
        self.models = models
        self.turn = 0.0

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Swing the boom and spin the rotors for the boss, and sync their models."""
        self.boom.rotation.x = unfolding(boss) * math.pi
        self.turn = (self.turn + FAN_SPIN * dt) % (2 * math.pi)
        for i in range(len(self.fans)):
            self.fans[i].rotation.y = self.turn if i % 2 == 0 else -self.turn
        for model in self.models:
            model.sync(lit, dt)


def _node(name: str, root: Any, at: Vec3) -> Any:
    node = new_transform_node(name, root.getScene())
    node.parent = root
    node.position.set(at[0], at[1], at[2])
    return node


def build_carrier_rig(root: Any, neon: Any, breath: Any) -> CarrierRig:
    """Return the boom and the lift rotors on `root` (the boss model's)."""
    scene = root.getScene()
    models: list[Any] = []
    boom = _node("sky-carrier-boom", root, hinge())
    model = build_enemy_model("sky-carrier-boom", scene, neon, draw_boom, breath)
    model.root.parent = boom
    models.append(model)
    fans: list[Any] = []
    points = fan_points()
    for i in range(len(points)):
        name = "sky-carrier-fan-" + str(i)
        hub = _node(name, root, points[i])
        blades = build_enemy_model(name, scene, neon, draw_fan, breath)
        blades.root.parent = hub
        fans.append(hub)
        models.append(blades)
    return CarrierRig(boom, fans, models)


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


def carrier_triangles(unfold: float) -> list[Any]:
    """Return the rig's triangles (model space), the boom `unfold` of the way over the bow."""
    result = _moved(_drawn(draw_boom), hinge(), unfold * math.pi)
    fan = _drawn(draw_fan)
    for at in fan_points():
        result.extend(_moved(fan, at, 0))
    return result

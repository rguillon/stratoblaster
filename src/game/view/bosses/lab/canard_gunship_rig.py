# Copyright (c) 2026 Renaud Guillon
"""MB-CANARD-GUNSHIP-05: the Canard Gunship's view rig.

Logical pixels, nose +Z, Y up. Its pusher propellers, spinning behind its engines all the time;
and, down its right flank, what turns its cargo doors into a gun gallery as it transforms
(MB-CANARD-GUNSHIP-10): two struts under each door, telescoping from the roof's edge to the door
as it folds down; an ammunition rack in each bay that swings out about its foot onto the open
platform, beside the gatling; and a railing along each platform's outer edge that rises once the
door is down. Visual only: the sim knows nothing of them (no part, no muzzle).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.canard_gunship import (
    CANARD_GUNSHIP,
    DOOR_REACH,
    DOOR_SWING,
    DOORS,
    ENGINE_H,
    ENGINE_X,
    FLOOR,
    HALF,
    PROP_RADIUS,
    PROP_Y,
    ROOF,
)
from game.config.bosses.moving_regions import motion_value
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_reveal import ease, share
from game.view.bosses.region_motion import progress
from game.view.bosses.world_1_organic_kit import M
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


N = BOSS_LOOK.neon["canard-gunship"]
QUARTER = math.pi / 2
DEG = math.pi / 180
LAYERS = ["hull", "bare", "neon", "vein", "charge"]
SPIN = 18
BLADES = 4
# Of the transformation: the racks' swing out and the railings' rise.
RACK = [0.42, 0.66]
RAIL = [0.62, 0.86]
# The racks' length and the struts' spots along each door (from its ends), and how far out on the
# door they push it.
RACK_LENGTH = 11.5
STRUT_IN = 3.5
STRUT_REACH = 10
# The sleeve each strut's rod runs out of.
SLEEVE = 3


def door_region(k: int) -> Any:
    """Return door `k`'s moving region (the design's)."""
    name = "door-fore" if k == 0 else "door-aft"
    for region in CANARD_GUNSHIP.armour:
        if region.id == name:
            return region
    return None


def door_angle(region: Any, boss: Any) -> float:
    """Return the door's turn about its hinge for `boss` (radians: -pi/2 closed, 0 open)."""
    value: float = motion_value(DOOR_SWING, progress(region, boss))
    return value * DEG


def stage_of(boss: Any, span: list[float]) -> float:
    """How far a step of the transformation over `span` has gone for `boss` (None: not), 0 to 1."""
    if boss == None:
        return 0
    if boss.form >= 1:
        return 1
    if boss.transforming_into != 1:
        return 0
    return ease(share(boss.transform, span))


def strut_ends(k: int, j: int, angle: float) -> list[Vec3]:
    """Return strut `j` of door `k`'s ends (model space): on the roof's edge, and on the door."""
    door = DOORS[k]
    y = door[0] + STRUT_IN if j == 0 else door[1] - STRUT_IN
    top = boss_point(HALF - 0.6, y, ROOF - 1.4)
    out = boss_point(HALF + STRUT_REACH * math.cos(angle), y, FLOOR - STRUT_REACH * math.sin(angle))
    return [top, out]


def rack_pivot(k: int) -> Vec3:
    """Return door `k`'s rack's pivot (model space): its foot at the bay's aft end, on the floor."""
    return boss_point(HALF - 1.2, DOORS[k][1] - 1.8, FLOOR)


def rail_hinge(k: int) -> Vec3:
    """Return door `k`'s railing's hinge (model space): on the open platform's outer edge."""
    door = DOORS[k]
    return boss_point(HALF + DOOR_REACH - 1.2, (door[0] + door[1]) / 2, FLOOR)


def rail_length(k: int) -> float:
    """Return door `k`'s railing's length."""
    return DOORS[k][1] - DOORS[k][0] - 3


def draw_blades(p: Any) -> None:
    """Draw a propeller round its hub (spinning about local Z): lit tips, a spinner ahead of it."""
    for k in range(BLADES):
        a = k * 2 * math.pi / BLADES
        c = math.cos(a)
        s = math.sin(a)
        reach = PROP_RADIUS - 0.4
        mid = reach / 2
        p.hull.box([reach, 0.5, 2.6], M.panel, Placement([c * mid, s * mid - 0.25, 0], 0, 0, a))
        p.neon.box(
            [1.8, 0.55, 2.7],
            N,
            Placement([c * (reach - 0.9), s * (reach - 0.9) - 0.27, 0], 0, 0, a),
        )
    p.hull.cylinder(0.6, 4.5, 8, M.base, Placement([0, 0, -1.2], 0, QUARTER), 2.0)
    p.neon.ring(1.9, 0.4, 8, N, Placement([0, 0, 1.4], 0, QUARTER))


def draw_rod(p: Any) -> None:
    """Draw a strut's rod: 1 px long up local Y (stretched to length), lit."""
    p.hull.cylinder(0.4, 1, 5, M.panel, Placement([0, 0, 0]))


def draw_sleeve(p: Any) -> None:
    """Draw a strut's sleeve up local Y from its anchor."""
    p.hull.cylinder(0.75, SLEEVE, 6, M.base, Placement([0, 0, 0]))
    p.neon.ring(0.8, 0.3, 6, N, Placement([0, SLEEVE - 0.6, 0]))


def draw_rack(p: Any) -> None:
    """Draw an ammunition rack lying along local -X from its foot.

    A frame with three drum magazines in it, lit along its top, a foot bearing at its root.
    """
    length = RACK_LENGTH
    p.hull.box([length, 0.8, 2.6], M.base, Placement([-length / 2, 0, 0]))
    for side in [-1, 1]:
        p.bare.box([length, 1.8, 0.4], M.dark, Placement([-length / 2, 0.8, side * 1.1]))
    for j in range(3):
        x = -2.4 - j * 3.6
        p.hull.cylinder(1.3, 1.8, 8, M.panel, Placement([x, 0.8, 0]))
        p.neon.ring(1.35, 0.35, 8, N, Placement([x, 2.1, 0]))
    p.neon.box([length - 1, 0.3, 0.4], N, Placement([-length / 2, 2.6, 1.1]))
    p.hull.cylinder(1.5, 2.6, 8, M.panel, Placement([0, 0, 0]))


def _rail_drawing(length: float) -> Any:
    def draw(p: Any) -> None:
        """Draw a railing standing up local Y along local Z: posts, a lit bar on top."""
        for j in range(4):
            z = -length / 2 + j * length / 3
            p.hull.box([0.5, 3, 0.5], M.panel, Placement([0, 0, z]))
        p.neon.box([0.5, 0.5, length + 0.5], N, Placement([0, 2.8, 0]))
        p.bare.box([0.4, 0.4, length], M.dark, Placement([0, 1.4, 0]))

    return draw


def point_at(node: Any, start: Vec3, end: Vec3) -> float:
    """Turn `node` (at `start`) so that its local Y points at `end`; return their distance."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz) or 1
    node.position.set(start[0], start[1], start[2])
    node.rotation.set(math.acos(max(-1, min(1, dy / length))), math.atan2(dx, dz), 0)
    return length


class GunshipRig:
    """The propellers' hubs, and per door its struts (sleeve and rod), its rack and its railing."""

    def __init__(self, nodes: Any, models: list[Any]) -> None:
        self.hubs = nodes["hubs"]
        self.sleeves = nodes["sleeves"]
        self.rods = nodes["rods"]
        self.racks = nodes["racks"]
        self.rails = nodes["rails"]
        self.regions = [door_region(0), door_region(1)]
        self.models = models
        self.turn = 0.0

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Spin the propellers; pose the struts, racks and railings; sync the models."""
        self.turn = (self.turn + SPIN * dt) % (2 * math.pi)
        for i in range(len(self.hubs)):
            self.hubs[i].rotation.z = self.turn if i == 0 else -self.turn
        rack = stage_of(boss, RACK)
        rail = stage_of(boss, RAIL)
        for k in range(len(DOORS)):
            angle = door_angle(self.regions[k], boss)
            for j in range(2):
                ends = strut_ends(k, j, angle)
                point_at(self.sleeves[k * 2 + j], ends[0], ends[1])
                length = point_at(self.rods[k * 2 + j], ends[0], ends[1])
                self.rods[k * 2 + j].scaling.y = length
            self.racks[k].rotation.y = (1 - rack) * QUARTER
            set_enabled(self.rails[k], angle > -0.01)
            self.rails[k].rotation.z = -(1 - rail) * QUARTER
        for model in self.models:
            model.sync(lit, dt)


def _node(name: str, root: Any, at: Vec3) -> Any:
    node = new_transform_node(name, root.getScene())
    node.parent = root
    node.position.set(at[0], at[1], at[2])
    return node


def _hang(name: str, node: Any, draw: Any, neon: Any, breath: Any, models: list[Any]) -> None:
    model = build_enemy_model(name, node.getScene(), neon, draw, breath)
    model.root.parent = node
    models.append(model)


def prop_hubs() -> list[Vec3]:
    """Return the propellers' hubs (model space), behind the engines: right, then left."""
    return [
        boss_point(ENGINE_X, PROP_Y, ENGINE_H),
        boss_point(-ENGINE_X, PROP_Y, ENGINE_H),
    ]


def build_gunship_rig(root: Any, neon: Any, breath: Any) -> GunshipRig:
    """Return the rig on `root` (the boss model's)."""
    models: list[Any] = []
    nodes: Any = {"hubs": [], "sleeves": [], "rods": [], "racks": [], "rails": []}
    hubs = prop_hubs()
    for i in range(len(hubs)):
        hub = _node("canard-gunship-prop-" + str(i), root, hubs[i])
        _hang("canard-gunship-prop-" + str(i), hub, draw_blades, neon, breath, models)
        nodes["hubs"].append(hub)
    for k in range(len(DOORS)):
        name = "canard-gunship-door-" + str(k)
        for j in range(2):
            sleeve = _node(name + "-sleeve-" + str(j), root, [0, 0, 0])
            _hang(name + "-sleeve-" + str(j), sleeve, draw_sleeve, neon, breath, models)
            rod = _node(name + "-rod-" + str(j), root, [0, 0, 0])
            _hang(name + "-rod-" + str(j), rod, draw_rod, neon, breath, models)
            nodes["sleeves"].append(sleeve)
            nodes["rods"].append(rod)
        rack = _node(name + "-rack", root, rack_pivot(k))
        _hang(name + "-rack", rack, draw_rack, neon, breath, models)
        nodes["racks"].append(rack)
        rail = _node(name + "-rail", root, rail_hinge(k))
        _hang(name + "-rail", rail, _rail_drawing(rail_length(k)), neon, breath, models)
        nodes["rails"].append(rail)
    return GunshipRig(nodes, models)


def _drawn(draw: Any) -> list[Any]:
    parts = collect_parts(draw)["parts"]
    result: list[Any] = []
    for layer in LAYERS:
        result.extend(triangles(getattr(parts, layer).geometry))
    return result


def _turned(v: Vec3, rot: Vec3) -> Vec3:
    """`v` turned as a Babylon node turns it: about Z, then X, then Y (`rot` `[x, y, z]`)."""
    cz = math.cos(rot[2])
    sz = math.sin(rot[2])
    x = v[0] * cz - v[1] * sz
    y = v[0] * sz + v[1] * cz
    z = v[2]
    cx = math.cos(rot[0])
    sx = math.sin(rot[0])
    y2 = y * cx - z * sx
    z2 = y * sx + z * cx
    cy = math.cos(rot[1])
    sy = math.sin(rot[1])
    return [x * cy + z2 * sy, y2, -x * sy + z2 * cy]


def posed(tris: list[Any], at: Vec3, rot: Vec3, stretch: float = 1) -> list[Any]:
    """`tris` stretched `stretch` along local Y, turned by `rot` and moved to `at`."""
    result: list[Any] = []
    for tri in tris:
        placed: list[Any] = []
        for v in tri:
            q = _turned([v.position[0], v.position[1] * stretch, v.position[2]], rot)
            placed.append(Vertex([q[0] + at[0], q[1] + at[1], q[2] + at[2]], v.color))
        result.append(placed)
    return result


def _aimed(start: Vec3, end: Vec3) -> list[Any]:
    """Return `[rotation, length]` of a node at `start` whose local Y points at `end`."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz) or 1
    return [[math.acos(max(-1, min(1, dy / length))), math.atan2(dx, dz), 0], length]


def gunship_rig_triangles(unfold: float) -> list[Any]:
    """Return the rig's triangles (model space): at rest (0) or with its doors open (1)."""
    result: list[Any] = []
    blades = _drawn(draw_blades)
    for hub in prop_hubs():
        result.extend(posed(blades, hub, [0, 0, 0]))
    sleeve = _drawn(draw_sleeve)
    rod = _drawn(draw_rod)
    rack = _drawn(draw_rack)
    angle = -QUARTER * (1 - unfold)
    for k in range(len(DOORS)):
        for j in range(2):
            ends = strut_ends(k, j, angle)
            aim = _aimed(ends[0], ends[1])
            result.extend(posed(sleeve, ends[0], aim[0]))
            result.extend(posed(rod, ends[0], aim[0], aim[1]))
        result.extend(posed(rack, rack_pivot(k), [0, (1 - unfold) * QUARTER, 0]))
        if unfold >= 1:
            result.extend(posed(_drawn(_rail_drawing(rail_length(k))), rail_hinge(k), [0, 0, 0]))
    return result

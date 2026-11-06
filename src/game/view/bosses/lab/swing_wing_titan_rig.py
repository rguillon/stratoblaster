# Copyright (c) 2026 Renaud Guillon
"""FB-SWING-WING-TITAN-10, FB-SWING-WING-TITAN-11: the Swing-Wing Titan's view rig.

Logical pixels, nose +Z, Y up. What the simulation does not need:
- the gloves' bays (first transformation): as the wings sweep back (their moving pieces), each
  bay's two doors swing open, the fore one forward and the aft one back about their hinges
  (0.16-0.42 of the transformation), then two racks of feed tubes rise out of the bay
  (0.32-0.6), fore and aft of the battery rising between them (a part, drawn with the parts);
- the tail (second transformation): the dorsal fairing's four flaps flip open fore and aft onto
  the fuselage (0.15-0.4) over the rising racks; the tailplanes, set across the fin, swing round a
  quarter turn under it (0.15-0.42); the fin splits into its two skins, which fold out flat either
  side (0.32-0.58); the four blades, a cross round the hub, spin up (from 0.55) and keep spinning,
  the orb (a part) rising on the hub.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.swing_wing_titan import (
    BAY_DOORS,
    BAY_FLOOR,
    FAIRING,
    FAIRING_HALF,
    FIN_TIP,
    FIN_TOP,
    GLOVE_Y,
    HUB,
    RACK_POD,
    TAILPLANE_ROOT,
    TAILPLANE_SPAN,
    TAILPLANE_TIP,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_reveal import ease, share
from game.view.bosses.lab.twin_boom_lancer_rig import placed_triangles
from game.view.bosses.world_1_organic_kit import M
from game.view.enemies.enemy_mesh import build_enemy_model, collect_parts
from render.babylon import new_transform_node
from render.geometry.mesh_triangles import triangles
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["swing-wing-titan"]
QUARTER = math.pi / 2
SIDES = [-1, 1]
LAYERS = ["hull", "bare", "neon", "vein", "charge"]
SOOT = [0.035, 0.035, 0.042]
# The shares of each transformation each move takes (see the module).
DOORS = [0.16, 0.42]
TUBES = [0.32, 0.6]
FLAPS = [0.15, 0.4]
SWING = [0.15, 0.42]
SKINS = [0.32, 0.58]
SPIN_UP = [0.55, 1.0]
# How far the doors and flaps open (radians), how far the tubes sink when hidden, how fast the
# rotor spins once out (radians a second).
DOOR_OPEN = 2.0
FLAP_OPEN = 3.0
TUBES_SUNK = 7.5
SPIN = 1.7
# The top of the fin's root stub (the core's), under the tailplanes' layer; the tailplanes' layer
# under the hub (the skins' hinge).
STUB_TOP = HUB[2] - 2.4
TAILPLANE_Y = [-1.6, -0.4]
# The feed tubes: their `[x, y]` (the right bay's), radius and height when risen.
TUBES_AT = [[14, -38], [18, -38], [22, -38], [16, -20], [21, -20], [26, -20]]
TUBE_R = 1.5
TUBE_H = 6
FLAP_TOP = RACK_POD[0] + 1.3
# The rig's nodes, each after the node it hangs on (see `_hinges`).
NAMES = [
    "door-fore",
    "door-aft",
    "tubes",
    "flap-fore",
    "flap-aft",
    "hub",
    "tailplanes",
    "skin-right",
    "skin-left",
]


def _share(boss: Any, form: int, span: list[float]) -> float:
    """How far a move of transformation `form` over `span` has gone for `boss` (None: at rest)."""
    if boss == None:
        return 0
    if boss.form >= form:
        return 1
    if boss.transforming_into != form:
        return 0
    return ease(share(boss.transform, span))


def _spin_rate(boss: Any) -> float:
    """How fast the rotor spins for `boss` (radians a second)."""
    if boss == None or boss.form < 1:
        return 0
    if boss.state == "dying":
        return SPIN * 0.4
    if boss.form >= 2:
        return SPIN
    if boss.transforming_into != 2:
        return 0
    return SPIN * share(boss.transform, SPIN_UP)


def _local(outline: list[Any], z0: float) -> list[Any]:
    """Return a right-hand playfield outline, both sides, as model outlines with Z from `z0`."""
    return [[[-s * q[0], -q[1] - z0] for q in outline] for s in SIDES]


def draw_door(outline: list[Any], z0: float) -> Any:
    """Return the drawing of a pair of bay doors (both gloves'), in their hinge line's frame.

    Plated slabs under the hinge's plane, a lit edge along the seam and rivets.
    """

    def draw(p: Any) -> None:
        for piece in _local(outline, z0):
            p.hull.bevel_slab(piece, [-1.1, -0.3, 0], [0, 0.4], M.panel, None, M.base)
        for s in SIDES:
            seam = outline[2][1] if z0 > 0 else outline[0][1]
            z = -seam - z0
            p.neon.box([12, 0.4, 0.6], N, Placement([-s * 18, -0.2, z + (0.5 if z > 0 else -0.5)]))
            for x in [15, 21]:
                p.bare.box([1, 0.3, 1], SOOT, Placement([-s * x, 0, z / 2]))

    return draw


def draw_tubes(p: Any) -> None:
    """Draw the bays' feed tubes risen (model space): dark tubes on a lit collar, capped."""
    for s in SIDES:
        for q in TUBES_AT:
            at = boss_point(s * q[0], q[1], BAY_FLOOR - 2)
            p.hull.cylinder(TUBE_R, TUBE_H + 2, 6, M.panel, Placement(at), TUBE_R * 0.85)
            p.neon.ring(
                TUBE_R * 0.9, 0.4, 6, N, Placement([at[0], BAY_FLOOR + TUBE_H - 0.2, at[2]])
            )
            p.bare.cylinder(
                TUBE_R * 0.6, 0.3, 6, SOOT, Placement([at[0], BAY_FLOOR + TUBE_H, at[2]])
            )


def draw_flaps(fore: bool) -> Any:
    """Return the drawing of the dorsal fairing's fore or aft flaps, in their hinge line's frame.

    Two plates, one each side of the fin's line, a lit edge at their free end.
    """
    z0 = FAIRING[0] if fore else FAIRING[1]
    mid = (FAIRING[0] + FAIRING[1]) / 2

    def draw(p: Any) -> None:
        for s in SIDES:
            plate: list[Any] = [[1.6, z0], [FAIRING_HALF, z0], [FAIRING_HALF, mid], [1.6, mid]]
            outline = [[-s * q[0], -q[1] + z0] for q in plate]
            p.hull.bevel_slab(outline, [-1.2, -0.4, 0], [0, 0.4], M.panel, None, M.base)
            z = (-mid + z0) * 0.9
            p.neon.box(
                [FAIRING_HALF - 3, 0.4, 0.6], N, Placement([-s * (FAIRING_HALF + 1.6) / 2, 0, z])
            )

    return draw


def draw_hub(p: Any) -> None:
    """Draw the rotor's hub (in its frame): the bearing ring under the skins and its spindle."""
    p.hull.cylinder(4.5, 2.4, 10, M.panel, Placement([0, -2.4, 0]), 4)
    p.neon.ring(4.3, 0.4, 10, N, Placement([0, -0.6, 0]))
    p.hull.cylinder(2.2, 4.6, 8, M.base, Placement([0, -2.4, 0]))


def draw_skin(side: float) -> Any:
    """Return the drawing of the fin's skin on `side` (1: right), standing, in the hub's frame.

    Half of the fin above the hub: a swept plate, lit along its leading edge, a lamp at its tip;
    it folds out flat about its root.
    """
    hub = HUB[1]
    root = [11.2, -14.5]
    top = FIN_TOP - HUB[2]
    tip = [-(FIN_TIP[0] - hub), -(FIN_TIP[1] - hub)]
    outline = [[0, root[0]], [0, root[1]], [top, tip[1]], [top, tip[0]]]
    thick = [0, 0.7] if side > 0 else [-0.7, 0]
    out = -side

    def draw(p: Any) -> None:
        p.hull.slab(outline, thick, M.panel, Placement([0, 0, 0], 0, 0, QUARTER), M.base)
        lean = math.atan2(root[0] - tip[0], top)
        p.neon.box([0.4, top - 2, 0.6], N, Placement([out * 0.8, 1, root[0] - 1], 0, -lean))
        p.neon.box([0.6, 1, 4], N, Placement([out * 0.5, top - 1, (tip[0] + tip[1]) / 2]))

    return draw


def draw_tailplanes(p: Any) -> None:
    """Draw both tailplanes (in the hub's frame): tapered plates, lit leading edges and tips."""
    hub = HUB[1]
    root = [-(TAILPLANE_ROOT[0] - hub), -(TAILPLANE_ROOT[1] - hub)]
    tip = [-(TAILPLANE_TIP[0] - hub), -(TAILPLANE_TIP[1] - hub)]
    inner = 4.8
    outer = inner + TAILPLANE_SPAN
    for s in SIDES:
        x0 = -s * inner
        x1 = -s * outer
        outline = [[x0, root[0]], [x1, tip[0]], [x1, tip[1]], [x0, root[1]]]
        p.hull.bevel_slab(
            outline,
            [TAILPLANE_Y[0], TAILPLANE_Y[1] - 0.4, TAILPLANE_Y[1]],
            [0, 0.4],
            M.base,
            None,
            M.panel,
        )
        a = [x0, root[0] - 0.4]
        b = [x1, tip[0] - 0.4]
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        yaw = math.atan2(b[0] - a[0], b[1] - a[1])
        p.neon.box(
            [0.6, 0.4, length],
            N,
            Placement([(a[0] + b[0]) / 2, TAILPLANE_Y[1] - 0.2, (a[1] + b[1]) / 2], yaw),
        )
        p.neon.box([1.2, 0.8, 3], N, Placement([x1, TAILPLANE_Y[0], (tip[0] + tip[1]) / 2]))


class TitanRig:
    """The rig's nodes (see the module) and its models."""

    def __init__(self, nodes: Any, models: list[Any]) -> None:
        self.nodes = nodes
        self.models = models
        self.spin = 0.0

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Pose the rig for `boss` and sync its models."""
        n = self.nodes
        doors = _share(boss, 1, DOORS)
        n["door-fore"].rotation.x = DOOR_OPEN * doors
        n["door-aft"].rotation.x = -DOOR_OPEN * doors
        n["tubes"].position.y = -TUBES_SUNK * (1 - _share(boss, 1, TUBES))
        flaps = _share(boss, 2, FLAPS)
        n["flap-fore"].rotation.x = FLAP_OPEN * flaps
        n["flap-aft"].rotation.x = -FLAP_OPEN * flaps
        n["tailplanes"].rotation.y = QUARTER * _share(boss, 2, SWING)
        skins = _share(boss, 2, SKINS)
        n["skin-right"].rotation.z = QUARTER * skins
        n["skin-left"].rotation.z = -QUARTER * skins
        self.spin = (self.spin + _spin_rate(boss) * dt) % (2 * math.pi)
        if boss == None or boss.form + (1 if boss.transforming_into == 2 else 0) < 2:
            self.spin = 0
        n["hub"].rotation.y = self.spin
        for model in self.models:
            model.sync(lit, dt)


def _node(name: str, parent: Any, at: Vec3) -> Any:
    node = new_transform_node(name, parent.getScene())
    node.parent = parent
    node.position.set(at[0], at[1], at[2])
    return node


def _hinges() -> Any:
    """Return each hinged node's place (model space), by name, and its parent's name."""
    return {
        "door-fore": [[0, GLOVE_Y[2], -BAY_DOORS[0]], None],
        "door-aft": [[0, GLOVE_Y[2], -BAY_DOORS[2]], None],
        "tubes": [[0, -TUBES_SUNK, 0], None],
        "flap-fore": [[0, FLAP_TOP, -FAIRING[0]], None],
        "flap-aft": [[0, FLAP_TOP, -FAIRING[1]], None],
        "hub": [boss_point(HUB[0], HUB[1], HUB[2]), None],
        "tailplanes": [[0, 0, 0], "hub"],
        "skin-right": [[0, 0, 0], "hub"],
        "skin-left": [[0, 0, 0], "hub"],
    }


def _drawings() -> Any:
    """Return each node's drawings."""
    fore = [[11, BAY_DOORS[0]], [22.8, BAY_DOORS[0]], [27.5, BAY_DOORS[1]], [11, BAY_DOORS[1]]]
    aft = [[11, BAY_DOORS[1]], [27.5, BAY_DOORS[1]], [32.2, BAY_DOORS[2]], [11, BAY_DOORS[2]]]
    return {
        "door-fore": [draw_door(fore, -BAY_DOORS[0])],
        "door-aft": [draw_door(aft, -BAY_DOORS[2])],
        "tubes": [draw_tubes],
        "flap-fore": [draw_flaps(True)],
        "flap-aft": [draw_flaps(False)],
        "hub": [draw_hub],
        "tailplanes": [draw_tailplanes],
        "skin-right": [draw_skin(1)],
        "skin-left": [draw_skin(-1)],
    }


def build_titan_rig(root: Any, neon: Any, breath: Any) -> TitanRig:
    """Return the rig on `root` (the boss model's)."""
    scene = root.getScene()
    nodes: Any = {}
    models: list[Any] = []
    hinges = _hinges()
    drawings = _drawings()
    for name in NAMES:
        place = hinges[name]
        parent = root if place[1] == None else nodes[place[1]]
        node = _node("swing-wing-titan-" + name, parent, place[0])
        nodes[name] = node
        for k in range(len(drawings[name])):
            model = build_enemy_model(
                "swing-wing-titan-" + name + "-" + str(k), scene, neon, drawings[name][k], breath
            )
            model.root.parent = node
            models.append(model)
    return TitanRig(nodes, models)


def _drawn(draw: Any) -> list[Any]:
    parts = collect_parts(draw)["parts"]
    result: list[Any] = []
    for layer in LAYERS:
        result.extend(triangles(getattr(parts, layer).geometry))
    return result


def titan_triangles(form: int) -> list[Any]:
    """Return the rig's triangles (model space), at rest (`form` 0) or fully transformed."""
    k = 1 if form >= 1 else 0
    turns = {
        "door-fore": ["x", DOOR_OPEN * k],
        "door-aft": ["x", -DOOR_OPEN * k],
        "tubes": ["x", 0],
        "flap-fore": ["x", FLAP_OPEN * k],
        "flap-aft": ["x", -FLAP_OPEN * k],
        "hub": ["y", 0],
        "tailplanes": ["y", QUARTER * k],
        "skin-right": ["z", QUARTER * k],
        "skin-left": ["z", -QUARTER * k],
    }
    hinges = _hinges()
    drawings = _drawings()
    result: list[Any] = []
    for name in NAMES:
        place = hinges[name]
        at = place[0]
        if name == "tubes":
            at = [0, -TUBES_SUNK * (1 - k), 0]
        chain = [[at, turns[name][0], turns[name][1]]]
        if place[1] != None:
            parent = hinges[place[1]]
            chain.append([parent[0], turns[place[1]][0], turns[place[1]][1]])
        for draw in drawings[name]:
            result.extend(placed_triangles(_drawn(draw), chain))
    return result

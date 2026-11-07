# Copyright (c) 2026 Renaud Guillon
"""MB-WINDMILL-RAM-04: the Windmill Ram's sails, a rig of its own turning on the stern's hub.

Logical pixels, nose +Z, Y up (towards the camera). Four lattice sails on spars round a hub in
front of the tower's cap, their disc leaning forward from flat (`SAIL_TILT`) so the cross reads
from above. They turn all the time, slowly as it comes in and fights shut, faster from its
transformation on (the prow splits open and it drives on), spinning up through the transformation
and winding down as it dies. Visual only: no part, no gun is on the sails.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.windmill_ram import HUB, SAIL_REACH, SAIL_TILT
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


N = BOSS_LOOK.neon["windmill-ram"]
DEG = math.pi / 180
# The disc's lean about the model's X: its axis tilts forward (towards +Z) from straight up.
LEAN = SAIL_TILT * DEG
# Radians a second the sails turn: shut, and from its transformation on (MB-WINDMILL-RAM-04).
SPIN = [1.3, 3.4]
# A sail: its lattice from `inner` to the spar's tip, `width` wide, set off the spar's trailing
# side; the lattice bars across it.
SAIL = {"inner": 9, "width": 9, "bars": 4}
LAYERS = ["hull", "flesh", "neon", "vein", "charge", "bare"]


def _sail(p: Any, yaw: float) -> None:
    """Draw one sail along local +X turned `yaw` about the hub's axis (local Y)."""
    reach = SAIL_REACH
    inner = SAIL["inner"]
    w = SAIL["width"]
    place = Placement([0, 0, 0], yaw)
    # The spar: an iron-capped beam from the hub out to the tip.
    p.hull.box([reach - 2, 1.4, 1.8], M.panel, Placement(_turn([reach / 2 + 1, -0.7, 0], yaw), yaw))
    # The lattice's frame and its cloth: a dark panel set off the spar's trailing side.
    p.hull.slab(
        [[inner, 0.9], [reach, 0.9], [reach - 1, w], [inner, w]],
        [-0.25, 0.25],
        M.base,
        place,
        M.dark,
    )
    p.hull.box(
        [reach - inner, 0.8, 0.8],
        M.panel,
        Placement(_turn([(inner + reach) / 2, -0.4, w], yaw), yaw),
    )
    bars = SAIL["bars"]
    for k in range(bars + 1):
        x = inner + (reach - 1 - inner) * k / bars
        p.hull.box(
            [0.7, 0.7, w - 0.9], M.panel, Placement(_turn([x, -0.35, (w + 0.9) / 2], yaw), yaw)
        )
    # A light along its leading edge, and a beacon at the spar's tip.
    p.neon.box(
        [reach - inner, 0.4, 0.5], N, Placement(_turn([(inner + reach) / 2, 0.7, 0], yaw), yaw)
    )
    p.neon.box([1.2, 1.2, 1.2], N, Placement(_turn([reach + 0.2, -0.6, 0], yaw), yaw))


def _turn(p: Vec3, yaw: float) -> Vec3:
    """`p` turned `yaw` about Y, as `Placement` turns a solid."""
    c = math.cos(yaw)
    s = math.sin(yaw)
    return [p[0] * c + p[2] * s, p[1], -p[0] * s + p[2] * c]


def draw_sails(p: Any) -> None:
    """Draw the four sails and the hub, flat round local Y (their disc's axis) at the origin."""
    for k in range(4):
        _sail(p, math.pi / 4 + k * math.pi / 2)
    p.hull.cylinder(4.2, 2.6, 8, M.base, Placement([0, -1.3, 0]), 3.6)
    p.hull.cylinder(2.6, 2.2, 8, M.panel, Placement([0, 1.3, 0]), 0.8)
    p.neon.ring(4.25, 0.5, 8, N, Placement([0, 0.2, 0]))


def _hub() -> Vec3:
    return boss_point(HUB[0], HUB[1], HUB[2])


def _leaned(v: Vec3) -> Vec3:
    """Return a point of the sails' disc in model space: leaned back about X, moved to the hub."""
    c = math.cos(LEAN)
    s = math.sin(LEAN)
    hub = _hub()
    # Babylon's rotation about X: y' = y cos - z sin, z' = y sin + z cos.
    return [v[0] + hub[0], v[1] * c - v[2] * s + hub[1], v[1] * s + v[2] * c + hub[2]]


def sail_triangles(_form: int) -> list[Any]:
    """Return the sails' triangles (model space) at rest, for the wholeness checks."""
    parts = collect_parts(draw_sails)["parts"]
    result: list[Any] = []
    for layer in LAYERS:
        tris = triangles(getattr(parts, layer).geometry)
        result.extend([[Vertex(_leaned(v.position), v.color) for v in tri] for tri in tris])
    return result


def _speed(boss: Any) -> float:
    """How fast the sails turn for `boss` (radians a second)."""
    if boss == None:
        return SPIN[0]
    if boss.state == "dying":
        return SPIN[0] * 0.5
    if boss.form >= 1:
        return SPIN[1]
    if boss.transforming_into == 1:
        return SPIN[0] + (SPIN[1] - SPIN[0]) * ease(share(boss.transform, [0.1, 0.9]))
    return SPIN[0]


class SailRig:
    """The sails: a model on a spinning node, on a node leaning back at the hub."""

    def __init__(self, spinner: Any, model: Any) -> None:
        self.spinner = spinner
        self.model = model
        self.angle = 0.0

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Turn the sails on (see `_speed`) and sync them."""
        self.angle = (self.angle + _speed(boss) * dt) % (2 * math.pi)
        self.spinner.rotation.y = self.angle
        self.model.sync(lit, dt)


def build_sail_rig(root: Any, neon: Any, breath: Any) -> SailRig:
    """Return the sails on `root` (the boss model's)."""
    scene = root.getScene()
    hub = _hub()
    lean = new_transform_node("windmill-ram-sails-lean", scene)
    lean.parent = root
    lean.position.set(hub[0], hub[1], hub[2])
    lean.rotation.x = LEAN
    spinner = new_transform_node("windmill-ram-sails-spin", scene)
    spinner.parent = lean
    model = build_enemy_model("windmill-ram-sails", scene, neon, draw_sails, breath)
    model.root.parent = spinner
    return SailRig(spinner, model)

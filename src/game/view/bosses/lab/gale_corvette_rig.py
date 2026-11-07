# Copyright (c) 2026 Renaud Guillon
"""MB-GALE-CORVETTE-05: the Gale Corvette's propellers, its view rig.

Logical pixels, nose +Z, Y up. A ducted pusher propeller behind each engine nacelle, on a short
shaft. They spin all the time; as the corvette turns round (its transformation,
MB-GALE-CORVETTE-10) each swivels its shaft up a quarter turn about the nacelle's tail, its duct
coming up level over the nacelle like a lift rotor, and its spin slows, stops and runs the other
way. Visual only: the sim knows nothing of them (no part, no muzzle).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.gale_corvette import (
    NACELLE_AT,
    NACELLE_H,
    NACELLE_HALF,
    PROP_RADIUS,
    PROP_Y,
)
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


N = BOSS_LOOK.neon["gale-corvette"]
QUARTER = math.pi / 2
LAYERS = ["hull", "bare", "neon", "vein", "charge"]
# The shaft's length from the nacelle's tail to the hub; the blades' spin (radians a second).
SHAFT = PROP_Y - (NACELLE_AT[1] + NACELLE_HALF)
SPIN = 16
BLADES = 3
# Of the transformation: the swivel's span, and the spin's reversal's.
SWIVEL = [0.12, 0.7]
REVERSE = [0.05, 0.85]


def pivots() -> list[Vec3]:
    """Return each propeller's pivot (model space): its nacelle's tail, on the nacelle's axis."""
    tail = NACELLE_AT[1] + NACELLE_HALF
    return [
        boss_point(NACELLE_AT[0], tail, NACELLE_H),
        boss_point(-NACELLE_AT[0], tail, NACELLE_H),
    ]


def draw_duct(p: Any) -> None:
    """Draw a duct round the blades and its shaft, in the swivel's frame (shaft along -Z).

    A hull ring with a lit lip, two struts across it to the hub's bearing.
    """
    hub = [0, 0, -SHAFT]
    p.hull.cylinder(1.1, SHAFT, 6, M.base, Placement([0, 0, 0], 0, -QUARTER))
    p.hull.ring(PROP_RADIUS + 0.9, 2.4, 12, M.panel, Placement([0, 0, -SHAFT - 1.2], 0, QUARTER))
    p.neon.ring(PROP_RADIUS + 1.0, 0.5, 12, N, Placement([0, 0, -SHAFT + 1.0], 0, QUARTER))
    for a in [0, QUARTER]:
        p.bare.box(
            [PROP_RADIUS * 2 + 1.4, 0.6, 0.6],
            M.dark,
            Placement([hub[0], hub[1] - 0.3, hub[2] + 0.6], 0, 0, a),
        )
    p.hull.cylinder(1.6, 2.4, 8, M.panel, Placement([0, 0, -SHAFT + 0.6], 0, -QUARTER), 0.6)


def draw_blades(p: Any) -> None:
    """Draw the blades round the hub (in the hub's frame, spinning about local Z): lit tips."""
    for k in range(BLADES):
        a = k * 2 * math.pi / BLADES
        c = math.cos(a)
        s = math.sin(a)
        reach = PROP_RADIUS - 0.4
        mid = reach / 2
        p.hull.box([reach, 0.5, 2.8], M.panel, Placement([c * mid, s * mid - 0.25, 0], 0, 0, a))
        p.neon.box(
            [1.6, 0.55, 2.9],
            N,
            Placement([c * (reach - 0.7), s * (reach - 0.7) - 0.27, 0], 0, 0, a),
        )


def swivel_of(boss: Any) -> float:
    """How far up the propellers have swivelled for `boss` (None: at rest), 0 to 1."""
    if boss == None:
        return 0
    if boss.form >= 1:
        return 1
    if boss.transforming_into != 1:
        return 0
    return ease(share(boss.transform, SWIVEL))


def spin_of(boss: Any) -> float:
    """Return the blades' spin for `boss`: forward, then slowing, stopping and reversing."""
    if boss == None or (boss.form < 1 and boss.transforming_into != 1):
        return SPIN
    if boss.form >= 1:
        return -SPIN * 1.3
    k = ease(share(boss.transform, REVERSE))
    return SPIN * math.cos(math.pi * k) * (1 + 0.3 * k)


class PropRig:
    """The two propellers: for each, a swivel node (its duct) and a hub node (its blades)."""

    def __init__(self, swivels: list[Any], hubs: list[Any], models: list[Any]) -> None:
        self.swivels = swivels
        self.hubs = hubs
        self.models = models
        self.turn = 0.0

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Swivel and spin the propellers for the boss, and sync their models."""
        up = swivel_of(boss)
        self.turn = (self.turn + spin_of(boss) * dt) % (2 * math.pi)
        for i in range(len(self.swivels)):
            self.swivels[i].rotation.x = up * QUARTER
            # The left one turns the other way, a mirror image.
            self.hubs[i].rotation.z = self.turn if i == 0 else -self.turn
        for model in self.models:
            model.sync(lit, dt)


def build_prop_rig(root: Any, neon: Any, breath: Any) -> PropRig:
    """Return the propellers on `root` (the boss model's)."""
    scene = root.getScene()
    swivels: list[Any] = []
    hubs: list[Any] = []
    models: list[Any] = []
    at = pivots()
    for i in range(len(at)):
        name = "gale-corvette-prop-" + str(i)
        swivel = new_transform_node(name + "-swivel", scene)
        swivel.parent = root
        swivel.position.set(at[i][0], at[i][1], at[i][2])
        duct = build_enemy_model(name + "-duct", scene, neon, draw_duct, breath)
        duct.root.parent = swivel
        hub = new_transform_node(name + "-hub", scene)
        hub.parent = swivel
        hub.position.set(0, 0, -SHAFT)
        blades = build_enemy_model(name + "-blades", scene, neon, draw_blades, breath)
        blades.root.parent = hub
        swivels.append(swivel)
        hubs.append(hub)
        models.append(duct)
        models.append(blades)
    return PropRig(swivels, hubs, models)


def _drawn(draw: Any) -> list[Any]:
    parts = collect_parts(draw)["parts"]
    result: list[Any] = []
    for layer in LAYERS:
        result.extend(triangles(getattr(parts, layer).geometry))
    return result


def _placed(tris: list[Any], pivot: Vec3, up: float, back: float) -> list[Any]:
    """`tris` drawn in a swivel's frame (moved `back` along its -Z), swivelled `up` at `pivot`."""
    a = up * QUARTER
    c = math.cos(a)
    s = math.sin(a)
    result: list[Any] = []
    for tri in tris:
        placed: list[Any] = []
        for v in tri:
            x = v.position[0]
            y = v.position[1]
            z = v.position[2] - back
            placed.append(
                Vertex([x + pivot[0], y * c - z * s + pivot[1], y * s + z * c + pivot[2]], v.color)
            )
        result.append(placed)
    return result


def prop_triangles(unfold: float) -> list[Any]:
    """Return the propellers' triangles (model space), swivelled `unfold` of the way up."""
    result: list[Any] = []
    duct = _drawn(draw_duct)
    blades = _drawn(draw_blades)
    for pivot in pivots():
        result.extend(_placed(duct, pivot, unfold, 0))
        result.extend(_placed(blades, pivot, unfold, SHAFT))
    return result

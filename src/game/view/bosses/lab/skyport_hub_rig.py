# Copyright (c) 2026 Renaud Guillon
"""FB-SKYPORT-HUB-06: the Skyport Hub's rig.

Logical pixels, nose +Z, Y up. What moves that the fight does not need: the lift fans under its
four runways' ends spin (the rear ones riding their runways as they swing forward, spinning up as
they move), and the radar's dish turns on its mast until the radar is destroyed. Nothing here is
hit or fires.
"""

import math

from game.config.bosses.lab.skyport_hub import (
    DECK_LOW,
    FAN_OUT,
    FAN_R,
    FRONT_DEG,
    RADAR_AT,
    REAR_DEG,
    SKYPORT_HUB,
)
from game.config.bosses.moving_regions import motion_value, move_point
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.final_boss_greebles import SHADE
from game.view.bosses.lab.skyport_hub_parts import N
from game.view.bosses.region_motion import progress
from game.view.enemies.enemy_mesh import build_enemy_model
from render.babylon import new_transform_node, set_enabled
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


DEG = math.pi / 180
BLADES = 5
SPIN = 12.0
SPIN_FAST = 22.0
FAN_H = DECK_LOW - 1.2
DISH_TURN = 1.6
DISH_H = 17.5


def _region(region_id: str) -> Any:
    for region in SKYPORT_HUB.armour:
        if region.id == region_id:
            return region
    raise ValueError('The Skyport Hub has no region "' + region_id + '"')


def _part_index(part_id: str) -> int:
    parts = SKYPORT_HUB.stats.parts
    for i in range(len(parts)):
        if parts[i].id == part_id:
            return i
    return -1


def _blades(p: Any) -> None:
    """Draw a lift fan's blades round its centre (model origin): a hub and five pitched blades."""
    for k in range(BLADES):
        a = k * math.pi * 2 / BLADES
        q = [math.cos(a) * (FAN_R - 0.8) / 2, 0, math.sin(a) * (FAN_R - 0.8) / 2]
        p.bare.box([2, 0.4, FAN_R - 0.8], SHADE["light"], Placement(q, math.pi / 2 - a, 0, 0.3))
        tip = [math.cos(a) * (FAN_R - 1.4), 0.45, math.sin(a) * (FAN_R - 1.4)]
        p.neon.box([1.6, 0.12, 0.8], N, Placement(tip, math.pi / 2 - a))
    p.hull.cylinder(1.8, 1.2, 8, SHADE["mid"], Placement([0, -0.3, 0]), 1.2)


def _dish(p: Any) -> None:
    """Draw the radar's dish (model origin at its pivot): a tilted mesh dish on a yoke, a feed."""
    p.hull.box([2.4, 1.6, 2.4], SHADE["mid"], Placement([0, 0, 0]))
    p.hull.lathe(
        [[0, 0], [3.5, 0.6], [6.5, 2.2], [7.5, 3]],
        12,
        SHADE["light"],
        Placement([0, 3, -1], 0, -1.0),
        False,
    )
    p.neon.ring(7.5, 0.3, 12, N, Placement([0, 3, -1], 0, -1.0))
    p.hull.box([0.4, 0.4, 6], SHADE["dark"], Placement([0, 3.4, 2.4], 0, -1.0))


class HubRig:
    """The Skyport Hub's lift fans and radar dish (see the module)."""

    def __init__(self, fans: list[list[Any]], dish: list[Any]) -> None:
        # Per fan: `[node, model, region or None, centre (config)]`; the dish: `[node, model]`.
        self.fans = fans
        self.dish = dish
        self.radar = _part_index("radar")

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Spin the fans (moving the rear ones with their runways) and turn the dish."""
        for fan in self.fans:
            node = fan[0]
            speed = SPIN
            if fan[2] != None:
                motion = fan[2].motion
                k = progress(fan[2], boss)
                spot = move_point(motion, motion_value(motion, k), [fan[3][0], fan[3][1], FAN_H])
                at = boss_point(spot[0], spot[1], spot[2])
                node.position.set(at[0], at[1], at[2])
                speed = SPIN + (SPIN_FAST - SPIN) * k
            node.rotation.y = (node.rotation.y + speed * dt) % (math.pi * 2)
            fan[1].sync(lit, dt)
        standing = True
        if boss != None and self.radar >= 0 and self.radar < len(boss.parts):
            part = boss.parts[self.radar]
            standing = not part.destroyed and not part.hidden
        set_enabled(self.dish[0], standing)
        if standing:
            self.dish[0].rotation.y = (self.dish[0].rotation.y + DISH_TURN * dt) % (math.pi * 2)
            self.dish[1].sync(lit, dt)


def _model(name: str, root: Any, at: Vec3, draw: Any, neon: Any, breath: Any) -> list[Any]:
    """Return `[node, model]`: a model drawn by `draw` on a node of `root` at `at` (model)."""
    scene = root.getScene()
    node = new_transform_node(name, scene)
    node.parent = root
    node.position.set(at[0], at[1], at[2])
    model = build_enemy_model(name, scene, neon, draw, breath)
    model.root.parent = node
    return [node, model]


def build_hub_rig(root: Any, neon: Any, breath: Any) -> HubRig:
    """Return the Skyport Hub's rig on `root` (the boss model's)."""
    spots: list[Any] = [
        [FRONT_DEG, None],
        [180 - FRONT_DEG, None],
        [REAR_DEG, "rear-runway-right"],
        [180 - REAR_DEG, "rear-runway-left"],
    ]
    fans: list[list[Any]] = []
    for i in range(len(spots)):
        a = spots[i][0] * DEG
        centre = [FAN_OUT * math.cos(a), FAN_OUT * math.sin(a)]
        at = boss_point(centre[0], centre[1], FAN_H)
        view = _model("skyport-hub-fan-" + str(i), root, at, _blades, neon, breath)
        view[0].rotation.y = i * 0.5
        region = _region(spots[i][1]) if spots[i][1] != None else None
        fans.append([view[0], view[1], region, centre])
    dish = _model(
        "skyport-hub-dish", root, boss_point(RADAR_AT[0], RADAR_AT[1], DISH_H), _dish, neon, breath
    )
    return HubRig(fans, dish)


def rig_triangles(_unfold: float) -> list[Any]:
    """Return the rig's triangles for the wholeness check (BOSS-52): none.

    The fans spin inside their ducts, the dish on its mast.
    """
    return []

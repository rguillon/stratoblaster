# Copyright (c) 2026 Renaud Guillon
"""MB-BUNKER-SAUCER-03, MB-BUNKER-SAUCER-10: the Bunker Saucer's rig, what the fight ignores.

Logical pixels, nose +Z, Y up. Each slit's steel shutter closes its notch until its gun first comes
into use, then slides sideways into the parapet as the gun rises (BOSS-58); the cupola's periscope
sinks into it as it strains to split, and two hydraulic rams either side of the well telescope out
behind its halves as they slide apart (BOSS-45, the halves themselves are moving pieces of the
design). Nothing here is hit or fires.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.bunker_saucer import (
    BUNKER_SAUCER,
    CROWN,
    CUPOLA_TOP,
    DECK,
    NOTCH_HALF,
    PARAPET,
    SLIT_DEGS,
    slit_at,
    slit_id,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.region_motion import progress
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


N = BOSS_LOOK.neon["bunker-saucer"]
# A shutter slides this far along the rim, over this many seconds once its gun is first used.
SHUTTER_TRAVEL = 2 * NOTCH_HALF + 0.4
SHUTTER_SECONDS = 0.35
# The periscope: where it stands on the cupola's seam, how high it rises over it and how far it
# sinks; the share of the transformation it takes to sink.
PERISCOPE_AT = [0, 4]
PERISCOPE_RISE = 6.5
PERISCOPE_SINK = 0.15
# The rams: their sleeves' root off the well's housing, their heights over the crown, and where
# along the boss (Y) the two of each side stand; the gap they keep from the halves' cut faces.
RAM_ROOT = 3.6
RAM_HEIGHT = CROWN[1] + 1.6
RAM_YS = [-3.2, 3.2]
RAM_SLEEVE = 3


def _region(region_id: str) -> Any:
    for region in BUNKER_SAUCER.armour:
        if region.id == region_id:
            return region
    raise ValueError('The Bunker Saucer has no region "' + region_id + '"')


def _mount_index(mount_id: str) -> int:
    mounts = BUNKER_SAUCER.mounts
    for i in range(len(mounts)):
        if mounts[i].id == mount_id:
            return i
    return -1


def _model(name: str, root: Any, draw: Any, neon: Any, breath: Any) -> list[Any]:
    """Return `[node, model]`: a model drawn by `draw` (model space) on a node of `root`."""
    scene = root.getScene()
    node = new_transform_node(name, scene)
    node.parent = root
    model = build_enemy_model(name, scene, neon, draw, breath)
    model.root.parent = node
    return [node, model]


def _shutter(at: list[Any]) -> Any:
    """Return the drawing of the shutter closing the notch at `at` (config): ribbed steel."""
    a = math.atan2(at[1], at[0])
    c = math.cos(a)
    s = math.sin(a)
    r = PARAPET[1] - 0.9
    yaw = math.atan2(-c, -s)

    def draw(p: Any) -> None:
        q = boss_point(c * r, s * r, DECK)
        p.hull.box(
            [2 * NOTCH_HALF, PARAPET[2] - DECK - 0.3, 1.4], M.panel, Placement(q, yaw), M.base
        )

    return draw


def _draw_periscope(p: Any) -> None:
    """Draw the periscope on the cupola's seam: a steel mast, its hooded head looking forward."""
    at = boss_point(PERISCOPE_AT[0], PERISCOPE_AT[1], CUPOLA_TOP)
    p.hull.cylinder(1.1, PERISCOPE_RISE, 6, M.base, Placement(at))
    head = [at[0], CUPOLA_TOP + PERISCOPE_RISE, at[2]]
    p.hull.box([2.2, 1.8, 3.2], M.panel, Placement([head[0], head[1], head[2] + 0.6]), M.base)
    p.neon.box([1.4, 0.6, 0.2], N, Placement([head[0], head[1] + 0.6, head[2] + 2.25]))


def _ram() -> Any:
    """Return the drawing of a ram's rod: along model +Z, 1 long (the rig stretches it)."""

    def draw(p: Any) -> None:
        p.hull.cylinder(0.55, 1, 6, M.panel, Placement([0, 0, 0], 0, math.pi / 2))

    return draw


def _sleeves(side: float) -> Any:
    """Return the drawing of the rams' sleeves on `side`: fixed to the well's housing."""

    def draw(p: Any) -> None:
        for y in RAM_YS:
            q = boss_point(side * (RAM_ROOT + RAM_SLEEVE / 2), y, RAM_HEIGHT - 0.9)
            p.hull.box([RAM_SLEEVE, 1.8, 1.8], M.base, Placement(q))
            p.neon.box([0.3, 0.3, 1.9], N, Placement([q[0], RAM_HEIGHT + 0.9, q[2]]))

    return draw


class SaucerRig:
    """The Bunker Saucer's shutters, periscope and rams (see the module)."""

    def __init__(
        self, shutters: list[list[Any]], periscope: list[Any], rams: list[list[Any]]
    ) -> None:
        # Per shutter: `[node, model, mount index, slide (model x, z)]`; per ram: `[node, model,
        # region, side, sleeves]`.
        self.shutters = shutters
        self.periscope = periscope
        self.rams = rams

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Open the shutters of the guns out, sink the periscope, stretch the rams for `boss`."""
        for shutter in self.shutters:
            self._show_shutter(shutter, boss, lit, dt)
        self._show_periscope(boss, lit, dt)
        for ram in self.rams:
            self._show_ram(ram, boss, lit, dt)

    def _show_shutter(self, shutter: list[Any], boss: Any, lit: Any, dt: float) -> None:
        k = 0.0
        if boss != None and shutter[2] >= 0 and shutter[2] < len(boss.mounts):
            shown = boss.mounts[shutter[2]].shown_at
            if shown != None:
                k = max(0, min(1, (boss.age - shown) / SHUTTER_SECONDS))
        k = k * k * (3 - 2 * k)
        node = shutter[0]
        set_enabled(node, k < 1)
        if k >= 1:
            return
        way = shutter[3]
        node.position.set(way[0] * k * SHUTTER_TRAVEL, 0, way[1] * k * SHUTTER_TRAVEL)
        shutter[1].sync(lit, dt)

    def _show_periscope(self, boss: Any, lit: Any, dt: float) -> None:
        sunk = 0.0
        if boss != None:
            if boss.form >= 1:
                sunk = 1
            elif boss.transforming_into == 1:
                sunk = min(1, boss.transform / PERISCOPE_SINK)
        node = self.periscope[0]
        set_enabled(node, sunk < 1)
        if sunk >= 1:
            return
        node.position.set(0, -sunk * (PERISCOPE_RISE + 2), 0)
        self.periscope[1].sync(lit, dt)

    def _show_ram(self, ram: list[Any], boss: Any, lit: Any, dt: float) -> None:
        region = ram[2]
        offset = progress(region, boss) * region.motion.offsets[1][0]
        reach = abs(offset) - RAM_SLEEVE
        ram[4][1].sync(lit, dt)
        node = ram[0]
        set_enabled(node, reach > 0.2)
        if reach <= 0.2:
            return
        node.scaling.set(1, 1, reach)
        ram[1].sync(lit, dt)


def build_saucer_rig(root: Any, neon: Any, breath: Any) -> SaucerRig:
    """Return the Bunker Saucer's rig on `root` (the boss model's)."""
    shutters: list[list[Any]] = []
    for k in range(len(SLIT_DEGS)):
        for side in [1, -1]:
            at = slit_at(k, side)
            mount_id = slit_id(k, side)
            view = _model(
                "bunker-saucer-" + mount_id + "-shutter", root, _shutter(at), neon, breath
            )
            a = math.atan2(at[1], at[0])
            # Along the rim, counter-clockwise (config), in model axes.
            tx = -math.sin(a)
            ty = math.cos(a)
            way = [-tx * side, -ty * side]
            shutters.append([view[0], view[1], _mount_index(mount_id), way])
    periscope = _model("bunker-saucer-periscope", root, _draw_periscope, neon, breath)
    rams: list[list[Any]] = []
    for side in [1, -1]:
        name = "right" if side > 0 else "left"
        region = _region("cupola-" + name)
        sleeves = _model("bunker-saucer-sleeves-" + name, root, _sleeves(side), neon, breath)
        for y in RAM_YS:
            view = _model("bunker-saucer-ram-" + name + str(y), root, _ram(), neon, breath)
            start = boss_point(side * (RAM_ROOT + RAM_SLEEVE), y, RAM_HEIGHT)
            view[0].position.set(start[0], start[1], start[2])
            view[0].rotation.y = -side * math.pi / 2
            rams.append([view[0], view[1], region, side, sleeves])
    return SaucerRig(shutters, periscope, rams)


def rig_triangles(_unfold: float) -> list[Any]:
    """Return the rig's triangles for the wholeness check (BOSS-52): none.

    Its pieces lie on the core's: the shutters in the parapet's notches, the periscope on the
    cupola, the rams on the crown between the well's housing and the cupola's halves.
    """
    return []

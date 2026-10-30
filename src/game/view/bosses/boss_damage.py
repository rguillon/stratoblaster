"""The damage shown on a boss's parts (P07-R01): its hit flash, its smoke, its wound (P16-R05),
ported from `bosses/boss-damage.ts`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.math.rng import create_rng  # noqa: E402
from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.enemies.enemy_materials import mesh_of  # noqa: E402
from game.view.enemies.enemy_mesh import build_enemy_model  # noqa: E402
from render.babylon import (  # noqa: E402
    color3,
    new_standard_material,
    new_transform_node,
    new_weak_map,
    weak_map_get,
    weak_map_set,
)
from render.geometry.organic import organ, tendril  # noqa: E402
from render.geometry.solids import Placement, SolidBuilder  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

FLASH_CACHE = new_weak_map()


def effect_materials(scene: Any) -> Any:
    """The flash and smoke materials of the scene, created on first use."""
    mats = weak_map_get(FLASH_CACHE, scene)
    if mats == None:  # noqa: E711
        flash = new_standard_material("boss-flash", scene)
        flash.emissiveColor = color3(
            BOSS_LOOK.flash.color[0], BOSS_LOOK.flash.color[1], BOSS_LOOK.flash.color[2]
        )
        flash.disableLighting = True
        smoke = new_standard_material("boss-smoke", scene)
        smoke.emissiveColor = color3(
            BOSS_LOOK.smoke.color[0], BOSS_LOOK.smoke.color[1], BOSS_LOOK.smoke.color[2]
        )
        smoke.disableLighting = True
        smoke.alpha = BOSS_LOOK.smoke.alpha
        smoke.backFaceCulling = False
        mats = {"flash": flash, "smoke": smoke}
        weak_map_set(FLASH_CACHE, scene, mats)
    return mats


class Smoke:
    """The smoke rising from a damaged part (P07-R01): its node, and `step` to drift its puffs."""

    def __init__(self, node: Any, puffs: list[Any], radius: float) -> None:
        self.node = node
        self._puffs = puffs
        self._radius = radius
        self._time = 0.0

    def step(self, dt: float) -> None:
        """Moves the puffs: each rises and drifts back, growing and fading, then starts again."""
        look = BOSS_LOOK.smoke
        self._time += dt
        count = len(self._puffs)
        for i in range(count):
            puff = self._puffs[i]
            t = (self._time / look.seconds + i / count) % 1
            puff.position.set(0, look.rise * t + self._radius, -look.drift * t)
            puff.scaling.setAll(0.6 + t)
            puff.visibility = 1 - t


def build_smoke(name: str, radius: float, scene: Any, parent: Any) -> Smoke:
    """The smoke rising from a damaged part (P07-R01): a few puffs drifting back and fading."""
    look = BOSS_LOOK.smoke
    node = new_transform_node(name + "-smoke", scene)
    node.parent = parent
    disc = SolidBuilder()
    outline: list[Any] = []
    for k in range(6):
        a = (2 * math.pi * k) / 6
        outline.append([math.cos(a) * radius * look.size, math.sin(a) * radius * look.size])
    disc.slab(outline, [0, 0.1], [1, 1, 1])
    puffs: list[Any] = []
    for i in range(look.puffs):
        mesh = mesh_of(
            name + "-puff-" + str(i),
            disc.geometry,
            effect_materials(scene)["smoke"],
            scene,
        )
        mesh.parent = node
        puffs.append(mesh)
    return Smoke(node, puffs, radius)


class Stump:
    """The wound where a destroyed part was: its node, and `sync` to flicker its sparks."""

    def __init__(self, node: Any, model: Any, spark_chance: float, random: Any) -> None:
        self.node = node
        self._model = model
        self._spark_chance = spark_chance
        self._random = random

    def sync(self, enemy: Any, dt: float) -> None:
        """Sparks flicker at random."""
        enemy.charge = 1 if self._random() < self._spark_chance else 0
        self._model.sync(enemy, dt)


def build_stump(name: str, radius: float, scene: Any, parent: Any) -> Stump:
    """The wound where a destroyed part was (P16-R05, P07-R01): torn flesh around a dimmed organ, a
    few ribs and shards of plating sticking out, sparks flickering in it."""
    look = BOSS_LOOK.stump
    flesh = ENEMY_LOOK.flesh
    node = new_transform_node(name + "-stump", scene)
    node.parent = parent

    def draw(p: Any) -> None:
        random = create_rng(len(name) * 31 + 7)
        torn: list[Any] = []
        for k in range(7):
            a = (2 * math.pi * k) / 7
            r = radius * (0.45 + 0.2 * random())
            torn.append([math.cos(a) * r, math.sin(a) * r])
        p.flesh.bevel_slab(torn, [0, radius * 0.08, radius * 0.18], [0, radius * 0.12], flesh.wound)
        organ(p.flesh, radius * 0.22, 6, look.organ, Placement([0, radius * 0.05, 0]), 0.6)
        for k in range(3):
            a = (2 * math.pi * k) / 3 + 0.4
            cx = math.cos(a) * radius * 0.4
            cz = math.sin(a) * radius * 0.4
            tip = [cx * 1.5, radius * 0.4, cz * 1.5]
            tendril(p.flesh, [[cx, radius * 0.1, cz], tip], [radius * 0.05, 0], 3, flesh.bone)
            shard = [
                [-radius * 0.12, 0],
                [radius * 0.12, 0],
                [0, radius * 0.4],
            ]
            p.hull.slab(
                shard,
                [0, radius * 0.1],
                look.char,
                Placement([0, radius * 0.15, 0], a + 1),
            )
        p.charge.cylinder(radius * 0.12, radius * 0.3, 4, [1, 1, 1], None)

    model = build_enemy_model(name + "-stump", scene, look.spark, draw)
    model.root.parent = node
    random = create_rng(len(name) * 7919)
    return Stump(node, model, look.sparkChance, random)

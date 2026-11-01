"""The damage shown on a boss's parts (BOSS-17): its hit flash and its smoke. A destroyed part
leaves nothing behind (BOSS-18, D-225)."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.view.enemies.enemy_materials import mesh_of  # noqa: E402
from render.babylon import (  # noqa: E402
    color3,
    new_standard_material,
    new_transform_node,
    new_weak_map,
    weak_map_get,
    weak_map_set,
)
from render.geometry.solids import SolidBuilder  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402 (after the Transcrypt skip block, ENG-153)

from render.handles import StandardMaterial, WeakMap  # noqa: E402 (after the Transcrypt skip block, ENG-153)

__pragma__("noskip")

FLASH_CACHE: WeakMap[dict[str, StandardMaterial]] = new_weak_map()


def effect_materials(scene: Any) -> Any:
    """The flash and smoke materials of the scene, created on first use."""
    mats = weak_map_get(FLASH_CACHE, scene)
    if mats == None:  # noqa: E711 (absent value is undefined in the browser, ENG-161)
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
    """The smoke rising from a damaged part (BOSS-17): its node, and `step` to drift its puffs."""

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
    """The smoke rising from a damaged part (BOSS-17): a few puffs drifting back and fading."""
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

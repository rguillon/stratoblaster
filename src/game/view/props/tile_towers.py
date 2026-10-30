"""The silhouettes of the city buildings (Phase 15, reviewer 2026-10-28: "all the skyscrapers
look the same"), ported from `props/tile-towers.ts`. Each model takes the one its seed names, so
the models of a building group (which have different seeds) all differ: stepped tiers, a slab
with fins, a round tower, twin towers and a bridge, a needle set back off-centre, and blocks of
two heights side by side."""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from game.config.prop_look import PROP_COLORS as C  # noqa: E402
from game.config.prop_look import PROP_LIGHTS as L  # noqa: E402
from game.view.props.city_lots import crown, plinth, volume  # noqa: E402
from game.view.props.tile_kit import NEON, any_of, js_remainder, r, windows  # noqa: E402


class Tower:
    """What a silhouette is built with: the plot, the lot colours and the top of the building.
    `base` is the height of the plinth, where the building starts."""

    def __init__(self, k: Any, kit: Any, base: float, top: float) -> None:  # noqa: ANN401
        self.k = k
        self.kit = kit
        self.base = base
        self.top = top


def stepped(t: Tower) -> None:
    """Tiers stepping back up to the top, something on top."""
    k = t.k
    kit = t.kit
    tiers = 2 + math.floor(k.random() * 2)
    w = k.w * r(k, [0.7, 0.85])
    d = k.d * r(k, [0.7, 0.85])
    y = t.base
    for i in range(tiers):
        h = (t.top - y) / (tiers - i)
        volume(kit, [0, 0, w, d], y, h)
        y += h
        w = w * r(k, [0.72, 0.88])
        d = d * r(k, [0.72, 0.88])
    crown(kit, [0, y, 0], min(w, d) * 0.8)


def slab(t: Tower) -> None:
    """One flat slab, the full height, ribbed with fins on its long faces."""
    k = t.k
    kit = t.kit
    w = k.w * 0.85
    d = k.d * 0.55
    volume(kit, [0, 0, w, d], t.base, t.top - t.base)
    fins = max(3, math.floor(w / 4 + 0.5))
    for i in range(fins + 1):
        x = -w / 2 + (i * w) / fins
        for z in [-d / 2, d / 2]:
            k.s.box([0.6, t.top - t.base, 0.8], C.metalDark, Placement([x, t.base, z], 0, 0, 0))
    k.s.box([w * 0.3, 0.4, d * 0.6], C.metal, Placement([0, t.top, 0], 0, 0, 0))
    kit.lights.ring(min(w, d) * 0.2, 0.2, 8, L.yellowDim, Placement([0, t.top + 0.4, 0], 0, 0, 0))


def round_tower(t: Tower) -> None:
    """A round tower tapering a little, rings of light up it, and a mast."""
    k = t.k
    radius = min(k.w, k.d) * 0.4
    color = any_of(k, [C.glassBlue, C.glassDark, C.glassGreen, C.white])
    sides = 10
    k.s.cylinder(
        radius,
        t.top - t.base,
        sides,
        color,
        Placement([0, t.base, 0], 0, 0, 0),
        radius * r(k, [0.65, 0.9]),
    )
    light = any_of(k, NEON)
    rings = max(2, math.floor((t.top - t.base) / 14))
    for i in range(1, rings + 1):
        y = t.base + ((t.top - t.base) * i) / (rings + 1)
        at = radius * (1 - ((1 - 0.78) * (y - t.base)) / (t.top - t.base)) + 0.15
        k.lights.ring(at, 0.6, sides, light, Placement([0, y, 0], 0, 0, 0))
    k.s.cylinder(0.4, t.top * 0.12, 4, C.metal, Placement([0, t.top, 0], 0, 0, 0), 0.1)
    k.lights.box([0.6, 0.6, 0.6], L.red, Placement([0, t.top * 1.12, 0], 0, 0, 0))


def twin(t: Tower) -> None:
    """Two towers of different heights on the plinth, joined by a lit bridge."""
    k = t.k
    kit = t.kit
    along = k.w >= k.d
    w = k.w * 0.36 if along else k.w * 0.7
    d = k.d * 0.7 if along else k.d * 0.36
    offset = (k.w if along else k.d) * 0.27
    heights = [t.top, t.base + (t.top - t.base) * r(k, [0.65, 0.85])]
    for i, h in enumerate(heights):
        c = (-1 if i == 0 else 1) * offset
        x = c if along else 0
        z = 0 if along else c
        volume(kit, [x, z, w, d], t.base, h - t.base)
        crown(kit, [x, h, z], min(w, d) * 0.7)
    y = t.base + (heights[1] - t.base) * 0.6
    span = offset * 2 - (w if along else d)
    size = [span, 3, d * 0.5] if along else [w * 0.5, 3, span]
    k.s.box(size, C.metalDark, Placement([0, y, 0], 0, 0, 0))
    kit.lights.box(
        [size[0] * 0.9, 0.6, size[2] * 1.05], any_of(k, NEON), Placement([0, y + 1.2, 0], 0, 0, 0)
    )


def needle(t: Tower) -> None:
    """A narrow shaft set back off-centre over a low wing, with a long spire."""
    k = t.k
    kit = t.kit
    w = k.w * 0.45
    d = k.d * 0.45
    x = k.w * 0.2
    z = k.d * 0.2
    volume(
        kit,
        [-k.w * 0.15, -k.d * 0.2, k.w * 0.65, k.d * 0.55],
        t.base,
        min(12, t.top * 0.2),
    )
    shaft = t.top * 0.85
    volume(kit, [x, z, w, d], t.base, shaft - t.base)
    k.s.cylinder(
        min(w, d) * 0.35, t.top - shaft, 4, kit.roof, Placement([x, shaft, z], 0, 0, 0), 0.2
    )
    kit.lights.box([0.5, 0.5, 0.5], L.red, Placement([x, t.top, z], 0, 0, 0))


def pair(t: Tower) -> None:
    """Two blocks side by side, one low and wide, one tall, their colours different."""
    k = t.k
    kit = t.kit
    low = t.base + (t.top - t.base) * r(k, [0.3, 0.5])
    volume(kit, [-k.w * 0.2, 0, k.w * 0.55, k.d * 0.85], t.base, low - t.base)
    second = any_of(k, [C.white, C.concrete, C.glassDark, C.brick])
    volume(kit, [k.w * 0.25, k.d * 0.1, k.w * 0.45, k.d * 0.6], t.base, t.top - t.base, second)
    crown(kit, [k.w * 0.25, t.top, k.d * 0.1], min(k.w, k.d) * 0.35)
    windows(k, [k.w * 0.55, k.d * 0.85], [t.base + 1, low - 1], any_of(k, NEON), [-k.w * 0.2, 0], 4)


SILHOUETTES = [stepped, slab, round_tower, twin, needle, pair]

# Number of silhouettes: seeds 1 to this give different buildings.
SILHOUETTE_COUNT = len(SILHOUETTES)


def asymmetry(t: Tower) -> None:
    """Phase 15 (reviewer, 2026-10-28): what makes a building differ from each side: a lower
    annex against one side, off-centre, and a dark fin up one corner past the top."""
    k = t.k
    kit = t.kit
    side = math.floor(k.random() * 4)
    along_x = side % 2 == 0
    if along_x:
        length = k.w * r(k, [0.4, 0.6])
        deep = k.d * 0.3
    else:
        length = k.d * r(k, [0.4, 0.6])
        deep = k.w * 0.3
    # Inset, so the lights on its faces stay inside the plot.
    inset = 0.5
    shift = r(k, [-0.2, 0.2]) * (k.w if along_x else k.d)
    out = -1 if side < 2 else 1  # noqa: PLR2004 (a geometry constant)
    if along_x:
        x = shift
        z = out * (k.d / 2 - deep / 2 - inset)
        w = length
        d = deep
    else:
        x = out * (k.w / 2 - deep / 2 - inset)
        z = shift
        w = deep
        d = length
    volume(kit, [x, z, w, d], t.base, (t.top - t.base) * r(k, [0.2, 0.4]))
    cx = (-1 if k.random() < 0.5 else 1) * k.w * 0.32  # noqa: PLR2004 (a geometry constant)
    cz = (-1 if k.random() < 0.5 else 1) * k.d * 0.32  # noqa: PLR2004 (a geometry constant)
    k.s.box([0.8, t.top * 1.08 - t.base, 0.8], C.metalDark, Placement([cx, t.base, cz], 0, 0, 0))


def city_building(k: Any, kit: Any, height: list[float], asymmetric: bool = False) -> None:  # noqa: ANN401, FBT001, FBT002
    """A city building up to a height in `height`, of the silhouette its seed names; with
    `asymmetric`, an annex and a fin make it differ from each side."""
    base = plinth(kit, [0, 0, k.w, k.d])
    # A lit strip along the front of the plinth, inside the plot, so every building shows at night.
    kit.lights.box([k.w * 0.6, 0.3, 0.4], L.window, Placement([0, base, -k.d / 2 + 0.4], 0, 0, 0))
    index = js_remainder(k.seed - 1, len(SILHOUETTES))
    build = SILHOUETTES[index] if 0 <= index < len(SILHOUETTES) else stepped
    tower = Tower(k, kit, base, r(k, height))
    build(tower)
    if asymmetric:
        asymmetry(tower)

"""The small homes of the villages and the worker homes (Phase 15, reviewer 2026-10-28), ported
from `props/tile-homesteads.ts`: small homes of the future on paved plots, no garden, no tile roof.
Each model takes the silhouette its seed names: a capsule, a dome, stacked cubes, stacked
containers, a lit grow tower and a home beside a solar shed."""

import math

from game.config.prop_look import PROP_COLORS as C
from game.config.prop_look import PROP_LIGHTS as L
from game.view.props.tile_kit import NEON, TileKit, any_of, js_remainder, r
from game.view.props.tile_residences import deck
from render.geometry.solids import Placement

SHELLS = [C.white, C.silver, C.panel, C.concrete]
GLASS = [C.glassBlue, C.glassDark, C.glass]


def capsule(k: TileKit) -> None:
    """A capsule lying on its side on two cradles, along the plot's long side, lit along it."""
    along = k.w >= k.d
    length = k.w * 0.8 if along else k.d * 0.8
    across = k.d if along else k.w
    radius = min(2.2, across * 0.3)
    # Built along X, then turned a quarter round when the plot is long along Z.
    yaw = 0 if along else -math.pi / 2

    def place_at(x: float, y: float, z: float) -> list[float]:
        return [x, y, z] if along else [-z, y, x]

    y = radius + 0.6
    k.s.cylinder(
        radius,
        length,
        10,
        any_of(k, SHELLS),
        Placement(place_at(length / 2, y, 0), yaw, 0, math.pi / 2),
    )
    for c in [-0.3, 0.3]:
        k.s.box(
            [0.6, 0.8, radius * 1.6], C.metalDark, Placement(place_at(c * length, 0, 0), yaw, 0, 0)
        )
    k.lights.box(
        [length * 0.7, 0.3, 0.2],
        any_of(k, NEON),
        Placement(place_at(0, y, -radius - 0.05), yaw, 0, 0),
    )


def dome(k: TileKit) -> None:
    """A low dome on a ring wall, a mast with a red light."""
    radius = min(k.w, k.d) * 0.4
    k.s.cylinder(radius, 1.5, 12, any_of(k, SHELLS))
    colors = [C.white, C.silver]
    colors.extend(GLASS)
    k.s.lathe(
        [
            [radius, 1.5],
            [radius * 0.75, 1.5 + radius * 0.6],
            [0, 1.5 + radius * 0.8],
        ],
        12,
        any_of(k, colors),
    )
    k.lights.ring(radius + 0.1, 0.2, 12, any_of(k, NEON), Placement([0, 1.2, 0], 0, 0, 0))
    k.s.box([0.2, 3, 0.2], C.metal, Placement([radius * 0.5, 1.5 + radius * 0.5, 0], 0, 0, 0))
    k.lights.box([0.4, 0.4, 0.4], L.red, Placement([radius * 0.5, 4.5 + radius * 0.5, 0], 0, 0, 0))


def cubes(k: TileKit) -> None:
    """Two or three cubes stacked off each other, glass on their fronts."""
    s = min(k.w, k.d) * 0.45
    n = 2 + math.floor(k.random() * 2)
    for i in range(n):
        x = ((i % 2) - 0.5) * s * 0.6
        z = (i - 1) * s * 0.25
        k.s.box(
            [s, s * 0.6, s], any_of(k, SHELLS), Placement([x, i * s * 0.6, z], 0, 0, 0), C.metalDark
        )
        k.s.box(
            [s * 0.7, s * 0.35, 0.15],
            any_of(k, GLASS),
            Placement([x, i * s * 0.6 + s * 0.12, z - s / 2 - 0.05], 0, 0, 0),
        )
    k.lights.box([s * 0.6, 0.15, 0.15], L.window, Placement([0, n * s * 0.6, 0], 0, 0, 0))


def containers(k: TileKit) -> None:
    """Containers stacked crosswise as a home, a lit door."""
    w = min(k.w * 0.85, 12)
    d = min(k.d * 0.5, 2.6)
    colors = [C.containerRed, C.containerBlue, C.silver, C.white]
    k.s.box([w, 2.6, d], any_of(k, colors), Placement([0, 0, -d * 0.3], 0, 0, 0))
    k.s.box([d, 2.6, min(k.d * 0.85, w)], any_of(k, colors), Placement([w * 0.2, 2.6, 0], 0, 0, 0))
    k.lights.box([1, 2, 0.15], L.window, Placement([-w * 0.3, 0, -d * 0.8 - 0.1], 0, 0, 0))
    k.lights.box(
        [0.15, 0.15, min(k.d * 0.8, w)],
        any_of(k, NEON),
        Placement([w * 0.2 - d / 2, 5.1, 0], 0, 0, 0),
    )


def grow_tower(k: TileKit) -> None:
    """A glass grow tower lit from inside, a small home at its foot."""
    s = min(k.w, k.d) * 0.35
    h = r(k, [8, 11])
    k.s.box([s, h, s], C.glassBlue, Placement([k.w * 0.2, 0, k.d * 0.1], 0, 0, 0), C.metalDark)
    y = 1.5
    while y < h:
        k.lights.box(
            [s * 1.02, 0.2, s * 1.02], L.violet, Placement([k.w * 0.2, y, k.d * 0.1], 0, 0, 0)
        )
        y += 2
    k.s.box(
        [k.w * 0.4, 3, k.d * 0.4],
        any_of(k, SHELLS),
        Placement([-k.w * 0.2, 0, -k.d * 0.15], 0, 0, 0),
        C.metalDark,
    )
    k.lights.box(
        [k.w * 0.3, 0.8, 0.15], L.window, Placement([-k.w * 0.2, 1.2, -k.d * 0.35 - 0.05], 0, 0, 0)
    )


def solar_shed(k: TileKit) -> None:
    """A flat-roofed home beside a shed under tilted solar panels."""
    along = k.w >= k.d
    a = -k.w * 0.22 if along else -k.d * 0.22
    b = k.w * 0.25 if along else k.d * 0.25

    def at(c: float) -> list[float]:
        return [c, 0, 0] if along else [0, 0, c]

    hw = k.w * 0.4 if along else k.w * 0.6
    hd = k.d * 0.6 if along else k.d * 0.4
    k.s.box([hw, 3.4, hd], any_of(k, SHELLS), Placement(at(a), 0, 0, 0), C.metalDark)
    k.lights.box(
        [hw * 0.7, 0.8, 0.15],
        L.window,
        Placement([at(a)[0], 1.3, at(a)[2] - hd / 2 - 0.05], 0, 0, 0),
    )
    k.s.box([hw * 0.8, 2.4, hd * 0.8], C.metalDark, Placement(at(b), 0, 0, 0))
    k.s.box([hw * 0.9, 0.12, hd * 0.9], C.solar, Placement([at(b)[0], 3, at(b)[2]], 0, -0.4, 0))


SILHOUETTES = [capsule, dome, cubes, containers, grow_tower, solar_shed]


def build_homestead(k: TileKit) -> None:
    """A small home of the villages and the worker homes, of the silhouette its seed names, on a
    paved plot."""
    deck(k)
    index = js_remainder(k.seed - 1, len(SILHOUETTES))
    build = SILHOUETTES[index] if 0 <= index < len(SILHOUETTES) else dome
    build(k)

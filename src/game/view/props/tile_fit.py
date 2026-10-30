"""Every prop follows the block size rule (Phase 15, reviewer 2026-10-28), ported from
`props/tile-fit.ts`: its footprint is stretched along X and Z to the nearest whole number of
tiles, less the margin of the buildings, centred on the origin. Heights are kept."""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402

from render.scenery.scenery_look import PropModelFactory  # noqa: E402

__pragma__("noskip")

from game.config.tile_buildings import BUILDING_MARGIN, TILE  # noqa: E402
from render.geometry.gradient_shapes import ColoredGeometry  # noqa: E402
from render.scenery.scenery_look import PropGeometry, PropPlume  # noqa: E402


def tiles_for(size: float) -> int:
    """The whole tiles nearest to `size`, at least one."""
    tile: float = TILE.size
    return max(1, math.floor(size / tile + 0.5))


def fitted(tiles: float) -> float:
    """Width of a footprint of `tiles` tiles."""
    tile: float = TILE.size
    margin: float = BUILDING_MARGIN
    return tiles * tile - 2 * margin


def moved(geo: ColoredGeometry, mapper: Callable[[float, float], list[float]]) -> ColoredGeometry:
    """`geo` with each vertex's X and Z moved by `mapper` (a function of (x, z))."""
    result = ColoredGeometry()
    positions = list(geo.positions)
    for i in range(0, len(positions), 3):
        xz = mapper(positions[i], positions[i + 2])
        positions[i] = xz[0]
        positions[i + 2] = xz[1]
    result.positions = positions
    result.indices = list(geo.indices)
    result.colors = list(geo.colors)
    return result


def fit_to_tiles(geometry: PropGeometry) -> PropGeometry:
    """`geometry` stretched to a footprint of whole tiles (see the module doc)."""
    positions = geometry.structure.positions
    xs = [positions[i] for i in range(0, len(positions), 3)]
    zs = [positions[i] for i in range(2, len(positions), 3)]
    if len(xs) == 0:
        return geometry
    x0 = min(xs)
    x1 = max(xs)
    z0 = min(zs)
    z1 = max(zs)
    sx = fitted(tiles_for(x1 - x0)) / (x1 - x0) if x1 > x0 else 1
    sz = fitted(tiles_for(z1 - z0)) / (z1 - z0) if z1 > z0 else 1
    cx = (x0 + x1) / 2
    cz = (z0 + z1) / 2

    def mapper(x: float, z: float) -> list[float]:
        return [(x - cx) * sx, (z - cz) * sz]

    lights = None
    if geometry.lights != None:  # noqa: E711 (no lights)
        lights = moved(geometry.lights, mapper)
    plumes = None
    if geometry.plumes != None:  # noqa: E711 (no plumes)
        plumes = []
        for p in geometry.plumes:
            xz = mapper(p.at[0], p.at[2])
            plumes.append(PropPlume((xz[0], p.at[1], xz[1]), p.kind, p.scale))
    return PropGeometry(moved(geometry.structure, mapper), lights, plumes)


def fitted_model(factory: PropModelFactory) -> PropModelFactory:
    """A model factory that stretches what `factory` builds to whole tiles."""

    def make() -> PropGeometry:
        return fit_to_tiles(factory())

    return make


def on_tiles(models: dict[str, PropModelFactory]) -> dict[str, PropModelFactory]:
    """`models` with each one stretched to whole tiles."""
    result: dict[str, PropModelFactory] = {}
    for model_id, factory in models.items():
        result[model_id] = fitted_model(factory)
    return result

"""The street surfaces of a terrain chunk (phase 15): each street piece as a textured surface draped
on the ground, its layered fallback, and the grid of tiles. Pure (no Babylon): the ground worker
makes them for the level's chunks, or the main thread does when there is no worker (see
`road_sources`). Both run the same code, so they give the same geometry.

The road atlas that the surfaces' texture coordinates point into is kept here too: its pixels are
sent with the chunks when they have changed.
"""

from org.transcrypt.stubs.browser import __pragma__

from core.scenery.road_tiles import cached_road_pieces
from render.scenery.road_atlas import RoadAtlas
from render.scenery.road_surface import build_road_surfaces
from render.scenery.tile_road_geometry import build_tile_grid

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# Colour of the grid of tiles drawn with `tiles=1` (phase 15).
GRID_COLOR = (0, 0.9, 1)


class RoadChunk:
    """The street geometry of one terrain chunk: `index`; `surfaces` (textured, drawn opaque);
    `layered` (the streets the atlas has no room for); `grid` (the tile grid, or None); `atlas` (the
    atlas pixels, when they changed, or None)."""

    def __init__(self, index: int, surfaces: Any, layered: Any, grid: Any) -> None:
        self.index = index
        self.surfaces = surfaces
        self.layered = layered
        self.grid = grid
        self.atlas: Any = None


class TileRoadChunks:
    """The street surfaces of a level's terrain chunks, from its road pieces and heights."""

    def __init__(self, roads: Any, tiles: Any, tile_look: Any, ground: Any) -> None:
        self._tiles = tiles
        self._look = tile_look
        self._ground = ground
        self._pieces = cached_road_pieces(roads, tiles)
        self._atlas = RoadAtlas(tiles, tile_look)

    def chunk(self, index: int, z_min: float, z_max: float, grid: bool) -> RoadChunk:
        """The street geometry of chunk `index` over [z_min, z_max); with `grid`, the tile grid."""
        ground = self._ground

        def height(x: float, z: float) -> float:
            value: float = ground.height(x, z)
            return value

        surfaces, layered = build_road_surfaces(
            self._pieces, self._tiles, self._look, self._atlas, height, z_min, z_max
        )
        grid_geo = None
        if grid:
            grid_geo = build_tile_grid(self._pieces, self._tiles, height, z_min, z_max, GRID_COLOR)
        return RoadChunk(index, surfaces, layered, grid_geo)

    def atlas_changed(self) -> bool:
        """Whether the atlas has pixels not sent yet."""
        return self._atlas.dirty

    def atlas_pixels(self) -> Any:
        """The atlas's pixels (the live array): sent when `atlas_changed`, which then clears."""
        self._atlas.dirty = False
        return self._atlas.data

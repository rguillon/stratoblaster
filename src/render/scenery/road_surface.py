"""Each road piece as one surface draped on the ground, cut on a world lattice, its markings from
the road atlas (phase 15, experiment, reviewer 2026-10-28).

Ported from `render/scenery/road-surface.ts`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.geometry.gradient_shapes import ColoredGeometry
from render.scenery.tile_road_geometry import add_piece

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402

from core.scenery.road_tiles import RoadPiece  # noqa: E402
from core.scenery.scenery_level import TileRules  # noqa: E402
from render.scenery.road_atlas import RoadAtlas  # noqa: E402
from render.scenery.tile_road_geometry import TileRoadLook  # noqa: E402

Height = Callable[[float, float], float]
__pragma__("noskip")


class TexturedGeometry(ColoredGeometry):
    """A geometry with texture coordinates."""

    def __init__(self) -> None:
        ColoredGeometry.__init__(self)
        self.uvs: list[float] = []


def cuts(a: float, b: float, cell: float) -> list[float]:
    """The cuts of [a, b] on the world lattice of `cell`."""
    out = [a]
    c = (math.floor(a / cell) + 1) * cell
    while c < b - 1e-6:
        out.append(c)
        c += cell
    out.append(b)
    return out


def _add_surface(
    geo: TexturedGeometry,
    piece: RoadPiece,
    rect: tuple[float, float, float, float],
    tile: TileRules,
    lift: float,
    ground: Height,
) -> None:
    u0, v0, u1, v1 = rect
    size = piece.size * tile.size
    ox = piece.x * tile.size
    oz = piece.z * tile.size
    cell = tile.size / 2
    xs = cuts(ox, ox + size, cell)
    zs = cuts(oz, oz + size, cell)
    base = len(geo.positions) // 3
    for z in zs:
        for x in xs:
            geo.positions.extend([x, ground(x, z) + lift, z])
            geo.colors.extend([1, 1, 1, 1])
            geo.uvs.extend([u0 + ((x - ox) / size) * (u1 - u0), v0 + ((z - oz) / size) * (v1 - v0)])
    nx = len(xs) - 1
    for j in range(len(zs) - 1):
        for i in range(nx):
            a = base + j * (nx + 1) + i
            c = a + nx + 1
            geo.indices.extend([a, a + 1, c, a + 1, c + 1, c])


def build_road_surfaces(  # noqa: PLR0917
    pieces: list[RoadPiece],
    tile: TileRules,
    look: TileRoadLook,
    atlas: RoadAtlas,
    ground: Height,
    z_min: float,
    z_max: float,
) -> tuple[TexturedGeometry, ColoredGeometry]:
    """The pieces whose middle is in [z_min, z_max): textured surfaces, and the layered geometry of
    those the atlas has no room for. Returns (surfaces, layered)."""
    surfaces = TexturedGeometry()
    layered = ColoredGeometry()
    for piece in pieces:
        mid = (piece.z + piece.size / 2) * tile.size
        if mid < z_min or mid >= z_max:
            continue
        rect = atlas.rect_of(piece)
        if rect:
            _add_surface(surfaces, piece, rect, tile, look.lift, ground)
        else:
            add_piece(layered, piece, tile, look, ground)
    return surfaces, layered

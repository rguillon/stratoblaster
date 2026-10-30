"""The road pieces painted once into one texture, an atlas (phase 15, experiment, reviewer
2026-10-28), so each piece is drawn as one surface (no stacked layers to fight in depth). Pure: the
atlas is an RGBA pixel array; the scenery stage uploads it.

Ported from `render/scenery/road-atlas.ts`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from render.scenery.road_paint import paint_piece  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from core.scenery.road_tiles import RoadPiece  # noqa: E402
from core.scenery.scenery_level import TileRules  # noqa: E402
from render.scenery.tile_road_geometry import TileRoadLook  # noqa: E402

AtlasRect = tuple[float, float, float, float]
__pragma__("noskip")

# Pixels per tile in the atlas.
ATLAS_PX = 64
# Pieces up to this many tiles fit in a slot.
SLOT_TILES = 3
# Pixels repeated round each slot, so mipmaps do not bleed from a neighbour.
PAD = 4
SLOT = SLOT_TILES * ATLAS_PX + 2 * PAD
# Slots per row and per column.
SLOTS = 8
ATLAS_SIZE = SLOT * SLOTS


def _uint8_array(length: int) -> Any:
    """A zero-filled `Uint8Array` of `length` bytes (the atlas is pure: no Babylon here)."""
    __pragma__("js", "{}", "return new Uint8Array(length);")
    return None


def _clamp_index(v: int, n: int) -> int:
    """`v` kept to 0..n-1 (plain comparisons: Transcrypt's min and max are slow)."""
    if v < 0:
        return 0
    if v > n - 1:
        return n - 1
    return v


def _key_of(p: RoadPiece) -> str:
    """Key of a piece's look: its size and its open sides (where it is does not matter)."""
    sides: list[str] = []
    for s in p.sides:
        if s:
            sides.append(str(s.size) + "/" + str(s.offset))
        else:
            sides.append("-")
    return str(p.size) + ":" + ",".join(sides)


class RoadAtlas:
    """The road pieces of one look, painted into the slots of an atlas as they are first asked
    for."""

    def __init__(self, tile: TileRules, look: TileRoadLook) -> None:
        self.data = _uint8_array(ATLAS_SIZE * ATLAS_SIZE * 4)
        """The RGBA pixels (a `Uint8Array`)."""
        self.dirty = False
        """Whether pixels changed since the last upload."""
        self._tile = tile
        self._look = look
        self._slots: dict[str, AtlasRect] = {}

    def rect_of(self, piece: RoadPiece) -> AtlasRect | None:
        """Where `piece` is in the atlas; None if it does not fit a slot, or the atlas is full."""
        key = _key_of(piece)
        known = self._slots.get(key)
        if known:
            return known
        slot = len(self._slots)
        if piece.size > SLOT_TILES or slot >= SLOTS * SLOTS:
            return None
        n = piece.size * ATLAS_PX
        sx = (slot % SLOTS) * SLOT
        sy = math.floor(slot / SLOTS) * SLOT
        self._blit(paint_piece(piece, self._tile, self._look, n), n, sx, sy)
        rect: AtlasRect = (
            (sx + PAD) / ATLAS_SIZE,
            (sy + PAD) / ATLAS_SIZE,
            (sx + PAD + n) / ATLAS_SIZE,
            (sy + PAD + n) / ATLAS_SIZE,
        )
        self._slots[key] = rect
        self.dirty = True
        return rect

    def _blit(self, pixels: list[Any], n: int, sx: int, sy: int) -> None:
        """Writes `pixels` (`n` x `n`) at (sx + PAD, sy + PAD), its edge pixels repeated into the
        pad."""

        for y in range(-PAD, n + PAD):
            for x in range(-PAD, n + PAD):
                c = pixels[_clamp_index(y, n) * n + _clamp_index(x, n)]
                if not c:
                    c = self._look.sidewalk
                o = ((sy + PAD + y) * ATLAS_SIZE + sx + PAD + x) * 4
                self.data[o] = math.floor(c[0] * 255 + 0.5)
                self.data[o + 1] = math.floor(c[1] * 255 + 0.5)
                self.data[o + 2] = math.floor(c[2] * 255 + 0.5)
                self.data[o + 3] = 255

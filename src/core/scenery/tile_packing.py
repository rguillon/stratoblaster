"""P15-R07, R08: buildings of whole tiles packed in the blocks of a district (phase 15). Ported
from `core/scenery/tile-packing.ts`."""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402

from core.scenery.height_field import HeightField  # noqa: E402
from core.scenery.scenery_level import PropKindRule, PropRules, TileRules  # noqa: E402

__pragma__("noskip")

from core.scenery.ordering import stable_sort_by  # noqa: E402
from core.scenery.road_tiles import tile_key  # noqa: E402

INFINITY = float("Infinity")

# Facings by quarter turn: the side the front faces, as a step in tiles, and the turn.
FACINGS = [
    (0, -1, 0),
    (0, 1, math.pi),
    (1, 0, -math.pi / 2),
    (-1, 0, math.pi / 2),
]
# Chance of either way round (a coin toss).
HALF = 0.5
# Most tiles any footprint is long.
LONGEST = 6


class TileSpot:
    """A building's tiles: from tile (`x`, `z`), `w` × `d` of them in world X and Z."""

    def __init__(self, kind: PropKindRule, x: int, z: int, w: int, d: int, rotation: float) -> None:
        self.kind = kind
        self.x = x
        self.z = z
        self.w = w
        self.d = d
        self.rotation = rotation
        """Turn around Y (radians): its front (-Z) faces a road next to it when there is one."""


class TileBlock:
    """A block in tiles: [x0, x1) × [z0, z1)."""

    def __init__(self, x0: int, x1: int, z0: int, z1: int) -> None:
        self.x0 = x0
        self.x1 = x1
        self.z0 = z0
        self.z1 = z1


class PackSite:
    """What packing a block needs to know."""

    def __init__(
        self,
        free: Callable[[int, int], bool],
        road: Callable[[int, int], bool],
        kinds_at: Callable[[int, int, int], Sequence[PropKindRule]],
        random: Callable[[int], float],
    ) -> None:
        self.free = free
        """Whether tile (`x`, `z`) is free: not a road, not taken, ground fit to build on."""
        self.road = road
        """Whether a road runs over tile (`x`, `z`)."""
        self.kinds_at = kinds_at
        """The kinds a building at tile (`x`, `z`) may be, in the order to try them."""
        self.random = random
        """A random number (0..1) for draw `k`."""


def _fits(site: PackSite, block: TileBlock, x: int, z: int, w: int, d: int) -> bool:
    """Whether all the tiles of a spot are free and inside the block."""
    if x < block.x0 or z < block.z0 or x + w > block.x1 or z + d > block.z1:
        return False
    for i in range(w):
        for j in range(d):
            if not site.free(x + i, z + j):
                return False
    return True


def _faces(site: PackSite, x: int, z: int, w: int, d: int, facing: tuple[int, int, float]) -> bool:
    """Whether a road runs along the side of a spot that `facing` looks at."""
    dx, dz, _ = facing
    if dz != 0:
        row = z - 1 if dz < 0 else z + d
        return any(site.road(x + i, row) for i in range(w))
    column = x - 1 if dx < 0 else x + w
    return any(site.road(column, z + j) for j in range(d))


def _run(site: PackSite, block: TileBlock, x: int, z: int, dx: int, dz: int) -> int:
    """Free tiles in a line through free tile (x, z), along (dx, dz), up to `LONGEST` + 1."""
    count = 1
    for sign in [1, -1]:
        k = 1
        while k < LONGEST and count <= LONGEST:
            tx = x + sign * k * dx
            tz = z + sign * k * dz
            if tx < block.x0 or tz < block.z0 or tx >= block.x1 or tz >= block.z1:
                break
            if not site.free(tx, tz):
                break
            count += 1
            k += 1
    return count


def _room_for(kw: int, kd: int, across: int, along: int) -> bool:
    """Cheap first: the free run through the tile, each way, must hold the footprint."""
    return min(kw, kd) <= min(across, along) and max(kw, kd) <= max(across, along)


def _corners_at(x: int, z: int, w: int, d: int) -> list[tuple[int, int]]:
    """The spots `w` × `d` with tile (x, z) as one of their corners."""
    return [(x, z), (x - w + 1, z), (x, z - d + 1), (x - w + 1, z - d + 1)]


def _away_from_roads(site: PackSite, spot: TileSpot) -> bool:
    """Whether no road runs along any side of `spot`."""
    return not any(_faces(site, spot.x, spot.z, spot.w, spot.d, g) for g in FACINGS)


def _turn_of(r: float, facing: tuple[int, int, float]) -> float:
    """A random turn (draw `r`): that of `facing` or the half turn from it, so the footprint stays
    the facing's."""
    return facing[2] if r < HALF else facing[2] + math.pi


def _spot_for(  # noqa: PLR0917 (positional data fields: Transcrypt drops keyword arguments)
    site: PackSite,
    block: TileBlock,
    kind: PropKindRule,
    x: int,
    z: int,
    r: float,
    room: tuple[int, int],
) -> TileSpot | None:
    """The spot for `kind` with tile (`x`, `z`) as one of its corners, facing a road if it can
    (front on a road side, P15-R08), or else any way the draw `r` picks. `room` is the free tiles in
    a line through (x, z) along X, and along Z."""
    tiles = kind.tiles if kind.tiles is not None else (1, 1)
    kw = tiles[0]
    kd = tiles[1]
    if not _room_for(kw, kd, room[0], room[1]):
        return None
    fallback: TileSpot | None = None
    for facing in FACINGS:
        w, d = (kw, kd) if facing[1] != 0 else (kd, kw)
        for sx, sz in _corners_at(x, z, w, d):
            if not _fits(site, block, sx, sz, w, d):
                continue
            spot = TileSpot(kind, sx, sz, w, d, facing[2])
            if _faces(site, sx, sz, w, d, facing):
                return spot
            # Standing there with a road along a side it cannot face is not allowed (P15-R08).
            if fallback is None and _away_from_roads(site, spot):
                fallback = TileSpot(kind, sx, sz, w, d, _turn_of(r, facing))
    # No way of standing there faces a road: only away from the streets, any way.
    return fallback


def _free_tiles(site: PackSite, block: TileBlock) -> list[tuple[int, int]]:
    """The free tiles of `block`, in a random order."""
    tiles: list[tuple[int, int, float]] = []
    for x in range(block.x0, block.x1):
        for z in range(block.z0, block.z1):
            if site.free(x, z):
                tiles.append((x, z, site.random(len(tiles) * 3 + 1)))
    ordered = stable_sort_by(tiles, lambda t: t[2])
    return [(t[0], t[1]) for t in ordered]


def _spot_at(  # noqa: PLR0917 (positional data fields: Transcrypt drops keyword arguments)
    site: PackSite,
    block: TileBlock,
    x: int,
    z: int,
    n: int,
    left: float,
    first: bool,
) -> TileSpot | None:
    """The first kind `kinds_at` gives for free tile (x, z) (the `n`th drawn) that fits there, not
    much over the `left` tiles still to cover (the last building may overshoot a little)."""
    room = (_run(site, block, x, z, 1, 0), _run(site, block, x, z, 0, 1))
    for kind in site.kinds_at(x, z, n):
        spot = _spot_for(site, block, kind, x, z, site.random(n * 3 + 2), room)
        if spot is not None and (first or spot.w * spot.d <= left + 1.5):
            return spot
    return None


def pack_block(
    site: PackSite,
    block: TileBlock,
    density: float,
    take: Callable[[TileSpot], None],
) -> None:
    """Packs `block` with buildings until about `density` of its free tiles are covered (P15-R08):
    tiles are taken in a random order; each gets the first kind `kinds_at` gives that fits there.
    `take` marks the tiles of each building placed."""
    tiles = _free_tiles(site, block)
    target = density * len(tiles)
    covered = 0.0
    for n, (x, z) in enumerate(tiles):
        if covered >= target - 0.5:
            return
        if not site.free(x, z):
            continue
        spot = _spot_at(site, block, x, z, n, target - covered, covered == 0)
        if spot is None:
            continue
        take(spot)
        covered += spot.w * spot.d


class TileGround:
    """The ground of the tiles, from the heights at their corners (each asked once, shared by the
    four tiles around it): a tile is fit to build on when its lowest corner is at least
    `min_height` and its corners differ by at most `max_slope` over half a tile."""

    def __init__(self, field: HeightField, tiles: TileRules, rules: PropRules) -> None:
        self._field = field
        self._tiles = tiles
        self._rules = rules
        self._corners: dict[str, float] = {}
        self._fit: dict[str, bool] = {}

    def _corner(self, x: int, z: int) -> float:
        k = str(tile_key(x, z))
        if k not in self._corners:
            self._corners[k] = self._field.height(x * self._tiles.size, z * self._tiles.size)
        return self._corners[k]

    def _range(self, x: int, z: int) -> tuple[float, float]:
        """Lowest and highest corner of tile (x, z)."""
        hs = [
            self._corner(x, z),
            self._corner(x + 1, z),
            self._corner(x, z + 1),
            self._corner(x + 1, z + 1),
        ]
        low = hs[0]
        high = hs[0]
        for h in hs:
            low = min(low, h)
            high = max(high, h)
        return low, high

    def fit(self, x: int, z: int, key: int | None = None) -> bool:
        """Whether tile (x, z), of key `key`, is fit to build on."""
        k = str(key if key is not None else tile_key(x, z))
        if k not in self._fit:
            low, high = self._range(x, z)
            self._fit[k] = (
                low >= self._rules.min_height
                and (high - low) / (self._tiles.size / 2) <= self._rules.max_slope
            )
        return self._fit[k]

    def lowest(self, spot: TileSpot) -> float:
        """Lowest ground under the tiles of `spot`, so the building never floats."""
        low = INFINITY
        for i in range(spot.w + 1):
            for j in range(spot.d + 1):
                low = min(low, self._corner(spot.x + i, spot.z + j))
        return low

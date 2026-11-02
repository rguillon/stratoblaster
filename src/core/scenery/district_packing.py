# Copyright (c) 2026 Renaud Guillon
"""GFX-BLDG-05.

The buildings of the districts laid on tiles (phase 15), packed by `pack_districts` for
`prop_placement`.
"""

import math

from core.math.noise import hash_2d
from core.scenery.away_placement import Building
from core.scenery.draws import weighted
from core.scenery.ground_boxes import PropPlacement
from core.scenery.ordering import stable_sort_by
from core.scenery.road_tiles import (
    has_tile_key,
    road_pieces,
    road_tiles,
    tile_has,
    tile_key,
)
from core.scenery.tile_packing import PackSite, TileBlock, TileGround, pack_block

# isort: split
# __pragma__ ("skip")
from collections.abc import Callable, Sequence

from core.scenery.height_field import HeightField
from core.scenery.road_network import RoadNetwork
from core.scenery.road_types import Road
from core.scenery.scenery_level import (
    PropGroupRule,
    PropKindRule,
    PropRules,
    TerrainSection,
    TileRules,
)
from core.scenery.street_links import Block
from core.scenery.tile_packing import TileSpot

# __pragma__ ("noskip")


class DistrictSite:
    """What packing the districts needs from the prop placer."""

    def __init__(
        self,
        field: HeightField,
        rules: PropRules,
        roads: RoadNetwork,
        seed: int,
        group_at: Callable[[float, float, TerrainSection], PropGroupRule | None],
        occupy: Callable[[Building], None],
    ) -> None:
        self.field = field
        self.rules = rules
        self.roads = roads
        self.seed = seed
        self.group_at = group_at
        """The building group of the area around (`x`, `z`), among those `section` allows."""
        self.occupy = occupy


def _area(kind: PropKindRule) -> float:
    """Tiles a kind of whole tiles stands on."""
    tiles = kind.tiles
    if tiles is None:
        return 0
    return tiles[0] * tiles[1]


class _Tries:
    """For each kind of whole tiles of a group.

    The order a tile tries the kinds in when it is drawn first: it, then the others from the largest
    down, then the lots.
    """

    def __init__(self, kinds: list[PropKindRule], orders: list[list[PropKindRule]]) -> None:
        self.kinds = kinds
        self._orders = orders

    def get(self, kind: PropKindRule) -> list[PropKindRule]:
        """Return the order of `kind`, one of `kinds` (the last when it is none of the others)."""
        last = len(self.kinds) - 1
        for i in range(last):
            if self.kinds[i] is kind:
                return self._orders[i]
        return self._orders[last]


def _tries_of(group: PropGroupRule, lots: Sequence[PropKindRule]) -> _Tries:
    kinds = [k for k in group.kinds if k.tiles is not None]
    by_area = stable_sort_by(kinds, lambda k: -_area(k))
    orders: list[list[PropKindRule]] = []
    for k in kinds:
        order: list[PropKindRule] = [k]
        order.extend([o for o in by_area if o is not k])
        order.extend(lots)
        orders.append(order)
    return _Tries(kinds, orders)


def _tile_block(block: Block, t: float) -> TileBlock:
    """Return a block in whole tiles."""
    return TileBlock(
        math.floor(block.x_min / t + 0.5),
        math.floor(block.x_max / t + 0.5),
        math.floor(block.z_min / t + 0.5),
        math.floor(block.z_max / t + 0.5),
    )


def _random_of(site: DistrictSite, block_index: int) -> Callable[[int], float]:
    """Return the random draws (0..1) of block `block_index`."""

    def random(k: int) -> float:
        return hash_2d(block_index, k, site.seed * 41 + 7)

    return random


class _TriesCache:
    """The tries of each group met so far (`_tries_of`), made once."""

    def __init__(self, lots: Sequence[PropKindRule]) -> None:
        self._lots = lots
        self._tries: list[tuple[PropGroupRule, _Tries]] = []

    def order_for(self, group: PropGroupRule) -> _Tries:
        """Return the tries of `group`, made the first time it is asked for."""
        for g, order in self._tries:
            if g is group:
                return order
        order = _tries_of(group, self._lots)
        self._tries.append((group, order))
        return order


def _kinds_at_for(
    site: DistrictSite,
    section: TerrainSection,
    lots: Sequence[PropKindRule],
    order_for: Callable[[PropGroupRule], _Tries],
    t: float,
    random: Callable[[int], float],
) -> Callable[[int, int, int], Sequence[PropKindRule]]:
    """Return the kinds a tile of a block of `section` tries, in order (see `pack_block`).

    `random` is the block's own draws.
    """

    def kinds_at(x: int, z: int, n: int) -> Sequence[PropKindRule]:
        group = site.group_at((x + 0.5) * t, (z + 0.5) * t, section)
        if group is None:
            return lots
        order = order_for(group)
        # The kinds drawn from are the order's own, so the kind drawn has its order.
        pick = weighted(order.kinds, random(n * 3 + 3))
        return order.get(pick) if pick is not None else lots

    return kinds_at


class RoadTilesCache:
    """The tiles the roads of a network cover.

    Worked out once per list of roads (the packing asks for them in every chunk; the list changes
    only when the runout's streets are laid).
    """

    def __init__(self) -> None:
        self._roads: Sequence[Road] | None = None
        self._tiles: dict[str, bool] = {}

    def of(self, roads: Sequence[Road], tiles: TileRules) -> dict[str, bool]:
        """Return the tiles `roads` cover on the grid `tiles`."""
        if self._roads is None or self._roads is not roads:
            self._tiles = road_tiles(road_pieces(roads, tiles))
            self._roads = roads
        return self._tiles


def pack_districts(
    site: DistrictSite,
    within: Callable[[float], bool],
    tiles: TileRules,
    road: dict[str, bool],
) -> None:
    """Packs the district blocks whose middle `within` accepts with whole-tile buildings.

    Buildings (GFX-BLDG-03, GFX-BLDG-06) are at scale 1, turned by quarter turns to face a street,
    then lots where no building of the area's group fits. `road`: the tiles the roads cover (see
    `RoadTilesCache`).
    """
    t = tiles.size
    taken: dict[str, bool] = {}
    grounds = TileGround(site.field, tiles, site.rules)
    lots = stable_sort_by(list(site.rules.lots or []), lambda k: -_area(k))
    tries = _TriesCache(lots)

    def take(spot: TileSpot) -> None:
        for a in range(spot.w):
            for b in range(spot.d):
                taken[str(tile_key(spot.x + a, spot.z + b))] = True
        x = (spot.x + spot.w / 2) * t
        z = (spot.z + spot.d / 2) * t
        placement = PropPlacement(spot.kind.id, x, grounds.lowest(spot), z, spot.rotation, 1)
        site.occupy(Building(placement, (spot.w * t) / 2, (spot.d * t) / 2))

    def free(x: int, z: int) -> bool:
        key = tile_key(x, z)
        return (
            (not tile_has(road, x, z)) and (not has_tile_key(taken, key)) and grounds.fit(x, z, key)
        )

    def road_at(x: int, z: int) -> bool:
        return tile_has(road, x, z)

    for i, block in enumerate(site.roads.blocks):
        cz = (block.z_min + block.z_max) / 2
        if not within(cz):
            continue
        section = site.field.section_at(cz).section
        random = _random_of(site, i)
        kinds_at = _kinds_at_for(site, section, lots, lambda g: tries.order_for(g), t, random)
        pack = PackSite(free, road_at, kinds_at, random)
        pack_block(pack, _tile_block(block, t), section.building_density, take)

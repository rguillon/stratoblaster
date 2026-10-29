"""P15-R07, R08: the buildings of the districts laid on tiles (phase 15), split out of
`prop-placement.ts`. Ported from `core/scenery/district-packing.ts`."""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402

from core.scenery.height_field import HeightField  # noqa: E402
from core.scenery.road_network import RoadNetwork  # noqa: E402
from core.scenery.scenery_level import (  # noqa: E402
    PropGroupRule,
    PropKindRule,
    PropRules,
    TerrainSection,
    TileRules,
)  # noqa: E402
from core.scenery.street_links import Block  # noqa: E402
from core.scenery.tile_packing import TileSpot  # noqa: E402

__pragma__("noskip")

from core.math.noise import hash_2d  # noqa: E402
from core.scenery.away_placement import Building  # noqa: E402
from core.scenery.draws import weighted  # noqa: E402
from core.scenery.ground_boxes import PropPlacement  # noqa: E402
from core.scenery.ordering import stable_sort_by  # noqa: E402
from core.scenery.road_tiles import has_tile_key, road_pieces, road_tiles, tile_has, tile_key  # noqa: E402
from core.scenery.tile_packing import PackSite, TileBlock, TileGround, pack_block  # noqa: E402


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
    """For each kind of whole tiles of a group, the order a tile tries the kinds in when it is drawn
    first: it, then the others from the largest down, then the lots."""

    def __init__(self, kinds: list[PropKindRule], orders: list[list[PropKindRule]]) -> None:
        self.kinds = kinds
        self._orders = orders

    def get(self, kind: PropKindRule) -> list[PropKindRule] | None:
        for i, k in enumerate(self.kinds):
            if k is kind:
                return self._orders[i]
        return None


def _tries_of(group: PropGroupRule, lots: Sequence[PropKindRule]) -> _Tries:
    kinds = [k for k in group.kinds if k.tiles is not None]
    by_area = stable_sort_by(kinds, lambda k: -_area(k))
    orders: list[list[PropKindRule]] = []
    for k in kinds:
        order: list[PropKindRule] = [k]
        for o in by_area:
            if o is not k:
                order.append(o)
        order.extend(lots)
        orders.append(order)
    return _Tries(kinds, orders)


def _tile_block(block: Block, t: float) -> TileBlock:
    """A block in whole tiles."""
    return TileBlock(
        math.floor(block.x_min / t + 0.5),
        math.floor(block.x_max / t + 0.5),
        math.floor(block.z_min / t + 0.5),
        math.floor(block.z_max / t + 0.5),
    )


def _random_of(site: DistrictSite, block_index: int) -> Callable[[int], float]:
    """The random draws (0..1) of block `block_index`."""

    def random(k: int) -> float:
        return hash_2d(block_index, k, site.seed * 41 + 7)

    return random


def _kinds_at_for(
    site: DistrictSite,
    section: TerrainSection,
    lots: Sequence[PropKindRule],
    order_for: Callable[[PropGroupRule], _Tries],
    t: float,
    random: Callable[[int], float],
) -> Callable[[int, int, int], Sequence[PropKindRule]]:
    """The kinds a tile of a block of `section` tries, in order (see `pack_block`); `random` is the
    block's own draws."""

    def kinds_at(x: int, z: int, n: int) -> Sequence[PropKindRule]:
        group = site.group_at((x + 0.5) * t, (z + 0.5) * t, section)
        if group is None:
            return lots
        order = order_for(group)
        pick = weighted(order.kinds, random(n * 3 + 3))
        if pick is None and len(order.kinds) > 0:
            pick = order.kinds[0]
        found = order.get(pick) if pick is not None else None
        return found if found is not None else lots

    return kinds_at


def pack_districts(  # noqa: C901 (mirrors the TypeScript closure structure)
    site: DistrictSite,
    within: Callable[[float], bool],
    tiles: TileRules,
) -> None:
    """Packs the blocks of the districts whose middle `within` accepts with buildings of whole tiles
    (P15-R07, R08): at scale 1, turned by quarter turns to face a street, then lots where no
    building of the area's group fits."""
    t = tiles.size
    road = road_tiles(road_pieces(site.roads.roads, tiles))
    taken: dict[str, bool] = {}
    grounds = TileGround(site.field, tiles, site.rules)
    lots = stable_sort_by(list(site.rules.lots or []), lambda k: -_area(k))
    tries: list[tuple[PropGroupRule, _Tries]] = []

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

    def order_for(group: PropGroupRule) -> _Tries:
        for g, order in tries:
            if g is group:
                return order
        order = _tries_of(group, lots)
        tries.append((group, order))
        return order

    for i, block in enumerate(site.roads.blocks):
        cz = (block.z_min + block.z_max) / 2
        if not within(cz):
            continue
        section = site.field.section_at(cz).section
        random = _random_of(site, i)
        kinds_at = _kinds_at_for(site, section, lots, order_for, t, random)
        pack = PackSite(free, road_at, kinds_at, random)
        pack_block(pack, _tile_block(block, t), section.building_density, take)

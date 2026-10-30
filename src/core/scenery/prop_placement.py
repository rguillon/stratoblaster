"""Places props on a level (P04-R04, P04-R07)

Buildings stand only along the roads: each slot of the road network gets a building with the
section's building density, set back from the road edge and facing it, if the ground under its
footprint is flat enough, above `min_height`, clear of the other roads and of the buildings already
placed. Slots of main roads are served first, so they get the street fronts. A low-frequency zone
noise picks the building group of each area among the groups the section allows, so industrial
buildings, labs and homes gather in clusters. With `loners` and `hamlets` (phase 6 review), a few
lone buildings and bunches of buildings also stand away from the roads. Trees of the kinds the
section allows grow on a grid of cells, away from the roads and the buildings, on rougher ground
too.

Buildings are placed in chunks: the Z chunks of `CHUNK_SIZE`, in increasing order, each one with
the same phases (blocks, road slots, hamlets, loners) over its own span. `ensure_placed` places the
chunks up to a Z, so the level's buildings come as it scrolls, not all before it starts. Each
chunk depends only on the chunks before it, so the buildings are the same whatever the order and
the distance the chunks are asked for in (only the first chunk not placed yet moves). Trees come
from a hash of their cell and are checked against the buildings `place` has placed around them. A
building belongs to the chunk that contains its centre; a cell to the area that contains its corner.
The runout's streets are laid (`RoadNetwork.add_runout`) before the chunk `RUNOUT_GATE` before its
start is placed, so the chunks before it never see them.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402

from core.scenery.ground_boxes import BuildingRecord, GroundBox  # noqa: E402
from core.scenery.height_field import HeightField  # noqa: E402
from core.scenery.road_network import RoadNetwork  # noqa: E402
from core.scenery.road_types import RoadSlot, RoadSnapshot  # noqa: E402
from core.scenery.scenery_level import (  # noqa: E402
    BlockFill,
    PropGroupRule,
    PropKindRule,
    PropRules,
    TerrainSection,
)
from core.scenery.street_links import Block  # noqa: E402

__pragma__("noskip")

from core.math.noise import create_noise2d, hash_2d  # noqa: E402
from core.scenery.away_placement import (  # noqa: E402
    AWAY_MARGIN,
    Building,
    ZSpan,
    place_hamlets,
    place_loners,
)
from core.scenery.block_towers import tower_in  # noqa: E402
from core.scenery.district_packing import DistrictSite, RoadTilesCache, pack_districts  # noqa: E402
from core.scenery.draws import allowed, between, weighted  # noqa: E402
from core.scenery.float_placement import fixed_pieces, floating_in  # noqa: E402
from core.scenery.ground_boxes import (  # noqa: E402
    BuildingIndex,
    GroundArea,
    PlacerSnapshot,
    PropPlacement,
    inside,
    overlap,
)
from core.scenery.ground_fit import SampledGround, lowest_under, standing_height  # noqa: E402
from core.scenery.ordering import stable_sort_by  # noqa: E402
from core.scenery.street_grid import block_parts  # noqa: E402

# Draws of a slot (building, kind, scale) and of a cell (trees): each draw has its own stream.
DRAW_BUILDING = 0
DRAW_KIND = 1
DRAW_SCALE = 2
DRAW_TREES = 3
# Draws per tree: position X, position Z, kind, scale, turn, whether it stands at a wood's edge.
TREE_DRAWS = 6
# Blocks are cut into parts of about this size, one tower each at most…
PART_SIZE = 30
# …and at most this many parts across either way.
MAX_PARTS = 4
# D-212: with woods, each cell tries the most trees give or take this share.
WOODS_SPREAD = 0.2
# D-212: the trees of a cell stand on its ground sampled this often (the terrain's mesh is sampled
# every 8), and this far past the cell (their footprints reach out of it).
TREE_GROUND_STEP = 8
TREE_GROUND_MARGIN = 8
# Half the diagonal of a square of side 1: how far a cell's corner is from its middle.
SQRT_HALF = math.sqrt(0.5)
# Smaller kinds a building slot tries when its first choice does not fit.
FALLBACKS = 3
# Lone buildings and hamlets stand within this share of the offscreen X of the level's middle…
AWAY_SPREAD = 0.5

INFINITY = float("Infinity")

# Z length of a chunk of buildings, in world units (see the module doc).
CHUNK_SIZE = 200
# Buildings and trees reach this far from their centre or cell: a tree looks this far past its
# area for buildings to keep clear of, so every building that could touch it is placed by then.
TREE_REACH = CHUNK_SIZE
# The runout's streets are laid before the chunk containing this far before its start is placed.
RUNOUT_GATE = 2 * CHUNK_SIZE


def chunk_of(z: float) -> int:
    """The index of the chunk that contains Z `z`."""
    return math.floor(z / CHUNK_SIZE)


class ChunkBuildings:
    """The buildings of chunk `k`, in the order they were placed (plain data for the worker)."""

    def __init__(self, k: int, buildings: Sequence[BuildingRecord]) -> None:
        self.k = k
        self.buildings = buildings


def _largest_footprint(kinds: Sequence[PropKindRule]) -> float:
    largest = 0.0
    for k in range(len(kinds)):
        f = kinds[k].footprint
        largest = max(largest, f)
    return largest


class _Box:
    """A box of ground taken by a tree (for the ground index): its centre and half-extent."""

    def __init__(self, x: float, z: float, half: float) -> None:
        self.placement = PropPlacement("", x, 0, z, 0, 1)
        self.half_x = half
        self.half_z = half


class _AwaySite:
    """What `place_hamlets` and `place_loners` need from the placer (phase 6 review)."""

    def __init__(self, placer: "PropPlacer") -> None:
        self._placer = placer
        self.length_ = placer.field.length_
        self.offscreen_x = placer.roads.offscreen_x
        self.seed = placer.seed

    def section_at(self, z: float) -> TerrainSection:
        return self._placer.field.section_at(z).section

    def group_at(self, x: float, z: float, section: TerrainSection) -> PropGroupRule | None:
        return self._placer.group_at(x, z, section)

    def clear_of_roads(self, x: float, z: float, clearance: float) -> bool:
        return self._placer.roads.clear_of(x, z, clearance)

    def ground(self, x: float, z: float, radius: float) -> float | None:
        placer = self._placer
        return standing_height(
            placer.field,
            [x, z, radius],
            [placer.rules.max_slope, placer.rules.min_height],
        )

    def add(self, building: BuildingRecord, gap: float | None) -> bool:
        if not self._placer.free(building, gap):
            return False
        self._placer.occupy(building)
        return True


class PropPlacer:
    """Places the props of a level (see the module doc)."""

    def __init__(
        self,
        field: HeightField,
        rules: PropRules,
        seed: int,
        roads: RoadNetwork,
        sea_level: float | None = None,
        made: PlacerSnapshot | None = None,
    ) -> None:
        """`sea_level`: the level's sea level, if it has a sea: floating props float on it (phase
        8).
        `made`: the buildings placed before (e.g. in a worker, P13-R03): taken as they are."""
        self.field = field
        self.rules = rules
        self.seed = seed
        self.roads = roads
        self.sea_level = sea_level
        self._zones = create_noise2d(seed + 3)
        # D-212: where the woods are.
        self._woods = create_noise2d(seed + 5)
        self._buildings: list[BuildingRecord] = []
        self._occupied = BuildingIndex()
        # Phase 9: set pieces and lines, larger than a bucket: every placement checks them all.
        self._fixed: list[BuildingRecord] = []
        # The chunks from the first (its span reaches back past the level's start) to the last
        # (its span reaches on past its end), and the first one not placed yet.
        self._first = chunk_of(-AWAY_MARGIN)
        self._last = chunk_of(field.length_ + AWAY_MARGIN)
        self._placed_to = self._first
        self._asked_to = self._first
        self._road_tiles = RoadTilesCache()
        self.runout_added: RoadSnapshot | None = None
        """What laying the runout's streets added (the first lay's, see `lay_runout`)."""
        self.ask: Callable[[float], None] | None = None
        """Asks another place (the worker) to place the chunks up to a Z (see `want_placed`)."""
        if made is not None:
            self._restore(made)
            return
        # Phase 9: set pieces, then (phase 8) lines of props first: the rest keeps clear of them.
        self._fixed.extend(fixed_pieces(rules, field, sea_level))
        for piece in self._fixed:
            self.occupy(piece)

    @property
    def runout_laid(self) -> bool:
        """Whether the runout's streets are laid (see `RoadNetwork.add_runout`)."""
        return self.roads.runout_laid

    def lay_runout(self, made: RoadSnapshot | None = None) -> RoadSnapshot:
        """Lays the runout's streets (or takes those `made` before, e.g. in a worker), and returns
        what they added. Once only (see `RoadNetwork.add_runout`): the first call's result is kept
        as `runout_added`."""
        added = self.roads.add_runout(made)
        if self.runout_added is None and self.roads.runout_laid:
            self.runout_added = added
        return added

    def _gate_chunk(self) -> int | None:
        """The chunk that needs the runout's streets laid before it is placed, if the level has a
        runout."""
        start = self.roads.runout_from
        if start is None:
            return None
        return chunk_of(start - RUNOUT_GATE)

    def _lay_runout_for(self, k: int) -> None:
        """Lays the runout's streets if chunk `k` is one that needs them."""
        gate = self._gate_chunk()
        if gate is not None and k >= gate and not self.roads.runout_laid:
            self.lay_runout()

    @property
    def placed_to(self) -> int:
        """The first chunk not placed yet."""
        return self._placed_to

    @property
    def chunks_done(self) -> bool:
        """Whether every chunk of the level is placed."""
        return self._placed_to > self._last

    def ensure_placed_chunks(self, z: float) -> list[ChunkBuildings]:
        """Places the chunks not placed yet up to the one that contains `z` (idempotent), and
        returns them, in order, with their buildings. The runout's streets are laid before the chunk
        that needs them (see `RUNOUT_GATE`)."""
        target = min(max(chunk_of(z), self._first), self._last)
        made: list[ChunkBuildings] = []
        while self._placed_to <= target:
            k = self._placed_to
            self._lay_runout_for(k)
            made.append(ChunkBuildings(k, self._place_chunk(k)))
            self._placed_to = k + 1
        return made

    def ensure_placed(self, z: float) -> list[BuildingRecord]:
        """Places the chunks not placed yet up to the one that contains `z` here (idempotent), and
        returns the buildings placed now."""
        made: list[BuildingRecord] = []
        for chunk in self.ensure_placed_chunks(z):
            made.extend(chunk.buildings)
        return made

    def want_placed(self, z: float) -> None:
        """Asks for the chunks up to the one that contains `z`: from the worker that places them,
        if there is one (see `ask`), else places them here now."""
        if self.ask is None:
            self.ensure_placed(z)
            return
        target = min(max(chunk_of(z), self._first), self._last)
        if target >= self._asked_to:
            self._asked_to = target + 1
            self.ask(z)

    def receive(self, chunks: Sequence[ChunkBuildings]) -> None:
        """Takes the chunks placed elsewhere (the worker's), in order. A chunk placed here already
        is skipped: both place the same buildings."""
        for chunk in chunks:
            if chunk.k == self._placed_to:
                for building in chunk.buildings:
                    self.occupy(building)
                self._placed_to = chunk.k + 1

    def _span_of(self, k: int) -> ZSpan:
        """The Z span of chunk `k`: the first and the last reach past the level at both ends."""
        from_ = -INFINITY if k == self._first else k * CHUNK_SIZE
        to = INFINITY if k == self._last else (k + 1) * CHUNK_SIZE
        return ZSpan(from_, to)

    def _place_chunk(self, k: int) -> list[BuildingRecord]:
        """The buildings of chunk `k`, placed now."""
        before = len(self._buildings)
        self._place_buildings(self._span_of(k))
        return self._buildings[before:]

    def _place_buildings(self, span: ZSpan) -> None:
        """The buildings of the blocks, the road slots and the spots away from the roads in
        `span`."""

        def within(z: float) -> bool:
            return z >= span.from_ and z < span.to

        tiles = self.roads.tiles
        if tiles is not None:
            site = DistrictSite(
                self.field,
                self.rules,
                self.roads,
                self.seed,
                lambda x, z, section: self.group_at(x, z, section),  # noqa: PLW0108 (Transcrypt: keep the lambda, it binds self)
                lambda building: self.occupy(building),  # noqa: PLW0108 (Transcrypt: keep the lambda, it binds self)
            )
            road = self._road_tiles.of(self.roads.roads, tiles)
            pack_districts(site, within, tiles, road)
        else:
            for i, block in enumerate(self.roads.blocks):
                if within((block.z_min + block.z_max) / 2):
                    self._fill_block(block, i)
        slots = [slot for slot in self.roads.slots if within(slot.z)]
        main_first = stable_sort_by(slots, lambda slot: 1 if slot.road.kind == "cross" else 0)
        for slot in main_first:
            if self.field.section_at(slot.z).section.blocks is not None:
                continue
            building = self._building_by(slot)
            if building is not None:
                self.occupy(building)
        hamlets = self.rules.hamlets
        loners = self.rules.loners
        if hamlets is not None:
            place_hamlets(_AwaySite(self), hamlets, span)
        if loners is not None:
            place_loners(_AwaySite(self), loners, span)

    def group_at(self, x: float, z: float, section: TerrainSection) -> PropGroupRule | None:
        """The building group of the area around (`x`, `z`), among those `section` allows."""
        f = self.rules.zone_frequency
        zone = (self._zones(x * f, z * f) + 1) / 2
        groups = allowed(self.rules.groups, section.groups)
        return weighted(groups, min(0.999999, max(0, zone)))

    def place(self, area: GroundArea) -> list[PropPlacement]:
        """Buildings and trees that lie in `area` (the buildings around it are placed first)."""
        placements = self.place_without_trees(area)
        placements.extend(self.trees_in(area))
        return placements

    def _ensure_around(self, area: GroundArea) -> None:
        """Places the buildings that could stand round `area` (and lays the runout's streets)."""
        self.ensure_placed(area.z_max + TREE_REACH)
        gate = self._gate_chunk()
        if gate is not None and chunk_of(area.z_max + TREE_REACH) >= gate:
            self.lay_runout()

    def place_without_trees(self, area: GroundArea) -> list[PropPlacement]:
        """The buildings and floating props that lie in `area` (see `place`)."""
        self._ensure_around(area)
        placements = [
            b.placement for b in self._buildings if inside(area, b.placement.x, b.placement.z)
        ]
        floating = self.rules.floating
        if floating is not None and self.sea_level is not None:
            placements.extend(floating_in(floating, self.field, self.sea_level, self.seed, area))
        return placements

    def trees_in(self, area: GroundArea) -> list[PropPlacement]:
        """The trees of the cells whose corner lies in `area` (see `place`): areas side by side,
        cut on the cells' edges or not, get each tree once (D-212: a chunk's trees come a row of
        cells at a time)."""
        self._ensure_around(area)
        placements: list[PropPlacement] = []
        cell = self.rules.cell_size
        i0 = math.ceil(area.x_min / cell)
        i1 = math.ceil(area.x_max / cell)
        j0 = math.ceil(area.z_min / cell)
        j1 = math.ceil(area.z_max / cell)
        for j in range(j0, j1):
            for i in range(i0, i1):
                placements.extend(self._trees(i, j))
        return placements

    def _random(self, i: int, j: int, draw: int) -> float:
        return hash_2d(i, j, self.seed * 31 + draw)

    def free(self, area: GroundBox, gap: float | None = None) -> bool:
        """Whether the ground box of `area` keeps `gap` clear of the placed buildings (default: the
        road setback)."""
        g = gap if gap is not None else self.roads.setback
        for b in self._fixed:
            if overlap(b, area, g):
                return False
        return self._occupied.clear(area, g)

    def _restore(self, made: PlacerSnapshot) -> None:
        """The buildings placed before, occupying the ground in the order they were placed."""
        self._fixed.extend(made.buildings[0 : made.fixed])
        for building in made.buildings:
            self.occupy(building)
        self._placed_to = made.placed_to
        self._asked_to = made.placed_to

    def snapshot(self) -> PlacerSnapshot:
        """What this placer placed so far (P13-R03)."""
        return PlacerSnapshot(list(self._buildings), len(self._fixed), self._placed_to)

    def occupy(self, building: BuildingRecord) -> None:
        self._buildings.append(building)
        self._occupied.add(building)

    def _fill_block(self, block: Block, index: int) -> None:
        """Fills a block of a section with `blocks` (phase 4 review): a podium over the whole block,
        if the section has podiums, and buildings on its roof (or on the ground), one per part of
        the block (parts of about 30, up to 4 × 4), a large kind of the section's groups that fits
        each part."""
        section = self.field.section_at((block.z_min + block.z_max) / 2).section
        fill = section.blocks
        if fill is None:
            return

        def r(draw: int) -> float:
            return hash_2d(index, draw, self.seed * 37 + 11)

        w = block.x_max - block.x_min
        d = block.z_max - block.z_min
        roof = self._podium(block, fill, r)
        groups = allowed(self.rules.groups, section.groups)

        def across(size: float) -> int:
            return min(MAX_PARTS, max(1, math.floor(size / PART_SIZE + 0.5)))

        parts = block_parts(block, across(w), across(d))
        towers = math.floor(between(fill.towers, r(2)) + 0.5)
        keyed = [(part, r(10 + k)) for k, part in enumerate(parts)]
        ordered = stable_sort_by(keyed, lambda pair: pair[1])
        for k, (part, _order) in enumerate(ordered[0:towers]):
            tower = tower_in(part, groups, roof if roof is not None else 0, r(20 + k))
            if tower is None:
                continue
            # Without a podium, on the lowest ground under its own plan, so it never floats.
            placement = tower.placement
            y = (
                roof
                if roof is not None
                else lowest_under(self.field, placement.x, placement.z, tower.half_x)
            )
            self.occupy(
                Building(
                    PropPlacement(
                        placement.kind,
                        placement.x,
                        y,
                        placement.z,
                        placement.rotation,
                        placement.scale,
                    ),
                    tower.half_x,
                    tower.half_z,
                )
            )

    def _podium(self, block: Block, fill: BlockFill, r: Callable[[int], float]) -> float | None:
        """Places the podium of a block, if its section has podiums; the height of its roof."""
        w = block.x_max - block.x_min
        d = block.z_max - block.z_min
        cx = (block.x_min + block.x_max) / 2
        cz = (block.z_min + block.z_max) / 2
        corners = [
            (block.x_min, block.z_min),
            (block.x_max, block.z_min),
            (block.x_min, block.z_max),
            (block.x_max, block.z_max),
        ]
        heights = [self.field.height(x, z) for x, z in corners]
        ground = min(heights)
        height = between(fill.podium_height, r(0)) + max(heights) - ground
        index = math.floor(r(1) * len(fill.podiums))
        if index >= len(fill.podiums):
            return None
        podium = fill.podiums[index]
        self.occupy(
            Building(
                PropPlacement(podium, cx, ground, cz, 0, 1, [w, height, d]),
                w / 2,
                d / 2,
            )
        )
        return ground + height

    def _building_by(self, slot: RoadSlot) -> BuildingRecord | None:
        """The first of the kinds `slot` tries that fits there, free of the others (reviewer,
        2026-10-28: the smaller ones are only fitted when the ones before do not fit)."""
        for kind in self._candidates(slot):
            building = self._fit(slot, kind)
            if building is not None and self.free(building):
                return building
        return None

    def _candidates(self, slot: RoadSlot) -> list[PropKindRule]:
        """The kinds a slot tries in turn: none when the density draw says no building; else the
        kind
        drawn in the area's group, then the smaller kinds of that group from the largest down (at
        most
        `FALLBACKS`), so gaps too small for the first choice still get a building."""

        def r(draw: int) -> float:
            return self._random(slot.road.index, slot.index, draw)

        section = self.field.section_at(slot.z).section
        if r(DRAW_BUILDING) >= section.building_density:
            return []
        group = self.group_at(slot.x, slot.z, section)
        if group is None:
            return []
        kind = weighted(group.kinds, r(DRAW_KIND))
        if kind is None:
            return []
        smaller = [k for k in group.kinds if k.footprint < kind.footprint]
        smaller = stable_sort_by(smaller, lambda k: -k.footprint)[0:FALLBACKS]
        result = [kind]
        result.extend(smaller)
        return result

    def _fit(self, slot: RoadSlot, kind: PropKindRule) -> BuildingRecord | None:
        """`kind` standing by `slot`, or None when the roads or the ground do not allow it."""
        scale = between(kind.scale, self._random(slot.road.index, slot.index, DRAW_SCALE))
        # A square plan stands at the setback; anything else keeps its footprint circle clear.
        reach = kind.footprint if kind.frontage is None else kind.frontage * scale
        offset = slot.road.width / 2 + self.roads.setback + reach
        x = slot.x + slot.nx * offset
        z = slot.z + slot.nz * offset
        # Clear of every road, its own too where it curves back towards the building.
        if not self.roads.clear_of(x, z, reach + self.roads.setback - 1e-6):
            return None
        y = standing_height(
            self.field,
            [x, z, kind.footprint],
            [self.rules.max_slope, self.rules.min_height],
        )
        if y is None:
            return None
        # The model's front (-Z) faces the road.
        rotation = math.atan2(slot.nx, slot.nz)
        # Box of ground taken: the turned square, or the box around the footprint circle.
        turned = abs(math.cos(rotation)) + abs(math.sin(rotation))
        half = kind.footprint if kind.frontage is None else kind.frontage * scale * turned
        return Building(PropPlacement(kind.id, x, y, z, rotation, scale), half, half)

    def _tree_count(self, i: int, j: int, density: float) -> int:
        """The trees tried in cell (`i`, `j`) of a section of tree `density`: any number up to
        `trees_per_cell` times the density; with `forests` (D-212), about `trees_per_cell` (give or
        take `WOODS_SPREAD`), so the cells do not show in a wood."""
        draw = self._random(i, j, DRAW_TREES)
        most = self.rules.trees_per_cell
        if density <= 0:
            return 0
        if self.rules.forests is None:
            return math.floor(draw * (most + 1) * density)
        return math.floor(most * (1 + (draw - 0.5) * 2 * WOODS_SPREAD))

    def _woods_cover(self, j: int, density: float) -> float:
        """How much of the ground of row `j` of cells the woods cover (D-212): the section's tree
        `density` times its grass share (`Surface.lush`, blended between sections as the ground's
        cover is), so the woods grow on the grass."""
        if self.rules.forests is None:
            return density
        lush = self.field.surface((j + 0.5) * self.rules.cell_size).lush
        return density * (lush if lush is not None else 0)

    def _in_woods(self, x: float, z: float, draw: float, cover: float) -> bool:
        """Whether a tree at (`x`, `z`) grows (D-212): in a wood, or at its edge by `draw`. `cover`
        (see `_woods_cover`) sets how much of the ground the woods cover: all the noise over
        `threshold` at 1, less below (the threshold raised towards 1). Every tree grows without
        `forests`."""
        forests = self.rules.forests
        if forests is None:
            return True
        f = forests.frequency
        wood = (self._woods(x * f, z * f) + 1) / 2
        full = 1 if cover > 1 else cover
        threshold = forests.threshold + (1 - full) * (1 - forests.threshold)
        return wood >= threshold + draw * forests.edge

    def _trees(self, i: int, j: int) -> list[PropPlacement]:
        cell = self.rules.cell_size
        section = self.field.section_at((j + 0.5) * cell).section
        trees = allowed(self.rules.trees, section.trees)
        density = section.tree_density
        count = self._tree_count(i, j, density)
        cover = self._woods_cover(j, density)
        placements: list[PropPlacement] = []
        if cover <= 0 or count <= 0 or len(trees) == 0:
            return placements
        # D-212: a cell far enough from every road and building spares its trees those checks
        # (a wood tries many trees per cell).
        reach = cell * SQRT_HALF + _largest_footprint(trees)
        middle_x = (i + 0.5) * cell
        middle_z = (j + 0.5) * cell
        clear = self.roads.clear_of(middle_x, middle_z, self.rules.tree_clearance + reach)
        empty = self.free(_Box(middle_x, middle_z, reach))
        # Sampled once the first tree of the cell needs it (D-212).
        ground_of: list[SampledGround] = []
        limits = [self.rules.tree_max_slope, self.rules.min_height]
        seed = self.seed * 31 + DRAW_TREES + 1
        for n in range(count):
            # The draws of tree `n` (`TREE_DRAWS` each), straight from the hash: this loop is hot.
            at = seed + n * TREE_DRAWS
            x = (i + hash_2d(i, j, at)) * cell
            z = (j + hash_2d(i, j, at + 1)) * cell
            if not self._in_woods(x, z, hash_2d(i, j, at + 5), cover):
                continue
            kind = weighted(trees, hash_2d(i, j, at + 2))
            if kind is None:
                continue
            ground = kind.footprint
            if not clear and not self.roads.clear_of(x, z, self.rules.tree_clearance + ground):
                continue
            if not empty and not self.free(_Box(x, z, ground)):
                continue
            if len(ground_of) == 0:
                m = TREE_GROUND_MARGIN
                ground_of.append(
                    SampledGround(
                        self.field, i * cell - m, j * cell - m, cell + 2 * m, TREE_GROUND_STEP
                    )
                )
            y = standing_height(ground_of[0], [x, z, ground], limits)
            if y is not None:
                placements.append(
                    PropPlacement(
                        kind.id,
                        x,
                        y,
                        z,
                        hash_2d(i, j, at + 4) * 2 * math.pi,
                        between(kind.scale, hash_2d(i, j, at + 3)),
                    )
                )
        return placements

"""Data that describes the ground of a scrolling level (P04-R01, P04-R04, P04-R06)

World units are logical pixels: X across the level (0 under the middle of the playfield), Z along
it (the level scrolls towards +Z), Y up. Heights are absolute; the sea, when there is one, sits at
`sea.level`.

The records are classes here, with the optional fields last (default None). A
partial record is a record whose missing fields are None.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

Range = tuple[float, float]
Point2 = tuple[float, float]
IntPair = tuple[int, int]
__pragma__("noskip")


class Relief:
    """Fractal relief added to a section's base height."""

    def __init__(
        self,
        base: float,
        amplitude: float,
        frequency: float,
        octaves: int,
        style: str,
        max_height: float | None = None,
    ) -> None:
        """`base`: height of the ground where the relief is zero. `amplitude`: largest height the
        relief adds (or removes, for smooth relief). `frequency`: cycles per world unit of the
        first octave. `style`: `smooth` (rolling ground from `base - amplitude` to
        `base + amplitude`) or `ridged` (sharp crests from `base` up to `base + amplitude`, mountain
        ranges). `max_height`: heights above this are softly squashed, so peaks stay under the
        flight altitude."""
        self.base = base
        self.amplitude = amplitude
        self.frequency = frequency
        self.octaves = octaves
        self.style = style
        self.max_height = max_height


class Meander:
    """A winding line across Z: `x + amplitude * sin(2π z / wavelength + phase)`."""

    def __init__(self, x: float, amplitude: float, wavelength: float) -> None:
        self.x = x
        self.amplitude = amplitude
        self.wavelength = wavelength


class Flatten:
    """Flattens a band of ground around a meander line (room for buildings)."""

    def __init__(
        self,
        path: Meander,
        half_width: float,
        edge: float,
        height: float,
        roughness: float,
    ) -> None:
        """`edge`: width of the slope from the flat band back to the relief. `roughness`: small
        relief left on the flat band."""
        self.path = path
        self.half_width = half_width
        self.edge = edge
        self.height = height
        self.roughness = roughness


class Channel:
    """Carves a canyon along a meander line."""

    def __init__(self, path: Meander, half_width: float, wall: float, floor: float) -> None:
        """`half_width`: half-width of the canyon floor. `wall`: width of each wall, from the floor
        to the rim. `floor`: height of the canyon floor (below the sea level, it holds a river)."""
        self.path = path
        self.half_width = half_width
        self.wall = wall
        self.floor = floor


class Shore:
    """Drops the ground under the sea on one side of a meander line."""

    def __init__(self, path: Meander, land_side: float, width: float, seabed: float) -> None:
        """`land_side`: the land is at X greater than the shore line (`1`) or smaller (`-1`).
        `width`: width of the slope from the land down to the sea bed."""
        self.path = path
        self.land_side = land_side
        self.width = width
        self.seabed = seabed


class Surface:
    """What covers the ground of a section, as shares (0..1) of alternative ground textures over
    the default one: `lush` (grass), `paved` (concrete, asphalt) and `sandy` (desert sand,
    P06-R06)."""

    def __init__(self, lush: float | None, paved: float | None, sandy: float | None) -> None:
        self.lush = lush
        self.paved = paved
        self.sandy = sandy


class Dunes:
    """Sand dunes (P06-R06): parallel crests every `wavelength`, each with a long gentle windward
    slope and a short steep lee slope, whose lines wander with noise and whose heights vary, added
    on top of the section's relief."""

    def __init__(self, height: float, wavelength: float, angle_deg: float, warp: float) -> None:
        """`height`: height of the highest crests above the relief. `wavelength`: distance between
        two crests. `angle_deg`: direction the crests face, in degrees from +Z (the wind blows that
        way). `warp`: how far the crest lines wander, in wavelengths."""
        self.height = height
        self.wavelength = wavelength
        self.angle_deg = angle_deg
        self.warp = warp


class Lakes:
    """Frozen lakes (phase 8, P08-R03): round basins scattered over a section, one chance in each
    square of `spacing` units, flattened to `level` (below the terrain look's `lowHeight`, so they
    get its low ground: ice) over `radius`, with a shore `edge` wide."""

    def __init__(
        self,
        spacing: float,
        chance: float,
        radius: Range,
        level: float,
        edge: float,
    ) -> None:
        """`chance`: chance (0..1) that a square of `spacing` has a lake."""
        self.spacing = spacing
        self.chance = chance
        self.radius = radius
        self.level = level
        self.edge = edge


class Crevasses:
    """Crevasses (phase 8, P08-R07): narrow cuts `depth` deep and `width` wide, about every
    `spacing` units, running across the level at `angle_deg` from +X, their lines bent by noise
    (`warp`, in spacings) and broken into pieces: about `share` (0..1) of each line is cut."""

    def __init__(
        self,
        spacing: float,
        width: float,
        depth: float,
        angle_deg: float,
        warp: float,
        share: float,
    ) -> None:
        self.spacing = spacing
        self.width = width
        self.depth = depth
        self.angle_deg = angle_deg
        self.warp = warp
        self.share = share


class StreetGrid:
    """A dense network of straight streets over a section (phase 4 review): streets across the
    level (rows) every `rows` units and streets along it (columns) every `columns` units, of which
    each stretch between two crossings is built with the chance `links`. Streets meet at crossings
    and T-junctions; none ends on screen. The winding roads and the paths stay out of these
    sections."""

    def __init__(self, rows: Range, columns: Range, links: float) -> None:
        """`rows`: distance along Z between two rows. `columns`: distance along X between two
        columns. `links`: chance (0..1) that a stretch of street between two crossings is built."""
        self.rows = rows
        self.columns = columns
        self.links = links


class BlockFill:
    """How the blocks of a section's street grid are filled (phase 4 review): a podium covering the
    whole block, of a random height, with towers of the section's building groups on its roof; or,
    without podiums, buildings standing on the ground side by side over the whole block."""

    def __init__(self, podiums: Sequence[str], podium_height: Range, towers: Range) -> None:
        """`podiums`: ids of podium models: a unit square plan, 1 high, stretched to each block
        (may be empty). `towers`: how many towers stand on a podium, or buildings on a block."""
        self.podiums = podiums
        self.podium_height = podium_height
        self.towers = towers


class TerrainSection:
    """One stretch of a level, sculpted from a relief and optional operations."""

    def __init__(  # noqa: PLR0917 (positional data fields: Transcrypt drops keyword arguments)
        self,
        name: str,
        seconds: float,
        relief: Relief,
        building_density: float,
        tree_density: float,
        flatten: Flatten | None = None,
        channel: Channel | None = None,
        shore: Shore | None = None,
        dunes: Dunes | None = None,
        lakes: Lakes | None = None,
        crevasses: Crevasses | None = None,
        float_density: float | None = None,
        surface: Surface | None = None,
        trees: Sequence[str] | None = None,
        groups: Sequence[str] | None = None,
        streets: StreetGrid | None = None,
        blocks: BlockFill | None = None,
    ) -> None:
        """`name`: shown by debug tools, e.g. `canyon`. `seconds`: how long the section takes to fly
        over, at the level's scroll speed. `float_density`: chance (0..1) that a cell of the sea
        gets
        floating props (`PropRules.floating`). `building_density`: chance (0..1) that a building
        slot
        along a road of this section gets a building. `tree_density`: chance (0..1) that an empty
        candidate spot of this section gets trees. `surface`: ground cover (default: none, the
        level's default ground). `trees`: ids of the tree kinds that grow here (default: all of
        them). `groups`: ids of the building groups that stand here (default: all of them).
        `streets`: a network of straight streets over this section, instead of roads and paths.
        `blocks`: fill each block of the street grid with buildings (on a podium), instead of
        street fronts."""
        self.name = name
        self.seconds = seconds
        self.relief = relief
        self.building_density = building_density
        self.tree_density = tree_density
        self.flatten = flatten
        self.channel = channel
        self.shore = shore
        self.dunes = dunes
        self.lakes = lakes
        self.crevasses = crevasses
        self.float_density = float_density
        self.surface = surface
        self.trees = trees
        self.groups = groups
        self.streets = streets
        self.blocks = blocks


class Drift:
    """Floating props drift slowly to and fro (or a line of props, as ore wagons do): up to `x` and
    `z` world units from where they were placed, over `period` seconds."""

    def __init__(self, x: float, z: float, period: float) -> None:
        self.x = x
        self.z = z
        self.period = period


class PropKindRule:
    """A kind of prop the placement can choose, with its relative weight."""

    def __init__(  # noqa: PLR0917 (positional data fields: Transcrypt drops keyword arguments)
        self,
        id: str,
        weight: float,
        footprint: float,
        scale: Range,
        frontage: float | None = None,
        drift: Drift | None = None,
        tiles: IntPair | None = None,
    ) -> None:
        """`id`: key of the prop's model in the game's view. `footprint`: radius of ground the prop
        stands on (at its largest scale); it must be about flat. `scale`: random scale range.
        `frontage`: half the side of the square the model fits in, at scale 1, for buildings with a
        square plan: they then stand right at the street setback and pack against their neighbours,
        instead of keeping the whole `footprint` circle clear (phase 4 review). `drift`: floating
        props (phase 8: ice floes) drift slowly to and fro. `tiles`: phase 15 (P15-R07): the W × D
        tiles the model stands on, in its own X and Z (its front is -Z)."""
        self.id = id
        self.weight = weight
        self.footprint = footprint
        self.scale = scale
        self.frontage = frontage
        self.drift = drift
        self.tiles = tiles


class FloatRules:
    """Props floating on the sea (phase 8, P08-R07: ice floes and icebergs): in cells of
    `cell_size`, up to `per_cell` each with the chance of their section's `float_density`, where
    the sea is at least `depth` deep under their whole footprint. They float at the sea level."""

    def __init__(
        self,
        cell_size: float,
        per_cell: float,
        depth: float,
        kinds: Sequence[PropKindRule],
    ) -> None:
        self.cell_size = cell_size
        self.per_cell = per_cell
        self.depth = depth
        self.kinds = kinds


class PropLine:
    """A line of props along the level (phase 8, P08-R03: a pipeline on stilts): one `kind` every
    `spacing` along `path`, turned along it, standing where the ground is above the sea level and
    no steeper than `max_slope`, in the sections whose names are listed (all when omitted). They
    are placed before the buildings, which keep clear of them."""

    def __init__(  # noqa: PLR0917 (positional data fields: Transcrypt drops keyword arguments)
        self,
        kind: str,
        path: Meander,
        spacing: float,
        footprint: float,
        max_slope: float,
        sections: Sequence[str] | None = None,
        over_water: bool | None = None,
        drift: Drift | None = None,
    ) -> None:
        """`footprint`: radius of ground each piece takes, for the buildings to keep clear of.
        `over_water` (phase 9): the line also crosses water (a pipeline on stilts over a swamp): its
        pieces stand on the ground, or at the sea level where the ground is under it. `drift`
        (phase 10): the pieces move to and fro together (ore wagons along a rail line)."""
        self.kind = kind
        self.path = path
        self.spacing = spacing
        self.footprint = footprint
        self.max_slope = max_slope
        self.sections = sections
        self.over_water = over_water
        self.drift = drift


class Landmark:
    """A set piece (phase 9: a dam across a lake, a waterfall on a river, a temple): one prop of
    `kind` at `z` along the level, at `x` across it or on `path` (its width then across the path),
    standing on the ground or, with `on_water`, at the sea level. It is placed first, whatever the
    slope, and the buildings and trees keep clear of its `footprint` (but not the blocks of a street
    grid: no set piece goes in one) (a box `footprint` wide each way, or `[half_x, half_z]`)."""

    def __init__(  # noqa: PLR0917 (positional data fields: Transcrypt drops keyword arguments)
        self,
        kind: str,
        z: float,
        footprint: Point2,
        x: float | None = None,
        path: Meander | None = None,
        rotation: float | None = None,
        scale: float | None = None,
        on_water: bool | None = None,
    ) -> None:
        """`rotation`: turn around the vertical axis (radians), added to the path's heading if
        any."""
        self.kind = kind
        self.z = z
        self.footprint = footprint
        self.x = x
        self.path = path
        self.rotation = rotation
        self.scale = scale
        self.on_water = on_water


class PropGroupRule:
    """Buildings of a group cluster together: a low-frequency noise picks the group of each area."""

    def __init__(
        self,
        id: str,
        weight: float,
        kinds: Sequence[PropKindRule],
    ) -> None:
        self.id = id
        self.weight = weight
        self.kinds = kinds


class Loners:
    """A few lone buildings away from the roads: one per square of `cell` units, with the chance
    `chance` times the section's building density, at least `clearance` from every road edge."""

    def __init__(self, cell: float, chance: float, clearance: float) -> None:
        self.cell = cell
        self.chance = chance
        self.clearance = clearance


class HamletRules:
    """Hamlets (phase 6 review): one every `spacing` along the level, in sections with buildings
    (`building_density` > 0) and no street grid. A hamlet is `buildings` buildings of one group,
    all turned the same way, within `radius` of its centre, `gap` apart and at least `clearance`
    from every road edge. Its centre is tried at a few places across the level."""

    def __init__(
        self,
        spacing: Range,
        buildings: Range,
        radius: float,
        gap: float,
        clearance: float,
    ) -> None:
        self.spacing = spacing
        self.buildings = buildings
        self.radius = radius
        self.gap = gap
        self.clearance = clearance


class CarRules:
    """Cars driving on the streets and main roads: one chance per road point to start there."""

    def __init__(  # noqa: PLR0917 (positional data fields: Transcrypt drops keyword arguments)
        self,
        kinds: Sequence[str],
        density: float,
        lift: float,
        scale: float,
        length: float,
        speed: Range,
        sidewalk: float | None = None,
    ) -> None:
        """`density`: chance that a point of a street or main road has a car. `lift`: cars stand on
        the road surface, this high above the ground. `length`: about the length of a car: cars are
        hidden this close to the ends of their road. `speed`: speeds (world units per second); all
        the cars of one lane share one. `sidewalk` (phase 15): width of the sidewalks of the
        streets, which cars keep off (default 0)."""
        self.kinds = kinds
        self.density = density
        self.lift = lift
        self.scale = scale
        self.length_ = length
        self.speed = speed
        self.sidewalk = sidewalk


class Forests:
    """Trees gather in woods (D-212): a low-frequency noise of `frequency` cycles per world unit
    over the ground; a tree stands only where it is over `threshold` (0..1), surely `edge` over it,
    by chance in between (ragged edges)."""

    def __init__(self, frequency: float, threshold: float, edge: float) -> None:
        self.frequency = frequency
        self.threshold = threshold
        self.edge = edge


class PropRules:
    """Where and which props stand on the ground (P04-R04). Buildings follow the roads (R07)."""

    def __init__(  # noqa: PLR0917 (positional data fields: Transcrypt drops keyword arguments)
        self,
        cell_size: float,
        tree_clearance: float,
        max_slope: float,
        tree_max_slope: float,
        min_height: float,
        zone_frequency: float,
        groups: Sequence[PropGroupRule],
        trees: Sequence[PropKindRule],
        trees_per_cell: float,
        cars: CarRules | None = None,
        loners: Loners | None = None,
        hamlets: HamletRules | None = None,
        floating: FloatRules | None = None,
        lines: Sequence[PropLine] | None = None,
        landmarks: Sequence[Landmark] | None = None,
        lots: Sequence[PropKindRule] | None = None,
        forests: Forests | None = None,
    ) -> None:
        """`cell_size`: trees grow in the cells of a grid of this size. `tree_clearance`: trees keep
        this far from the road edges. `max_slope`: steepest ground (height difference over the
        footprint radius) a building stands on. `tree_max_slope`: trees stand on steeper ground than
        buildings. `min_height`: no prop stands below this height (e.g. just above the sea).
        `zone_frequency`: cycles per world unit of the noise that picks a building group per area.
        `trees_per_cell`: most trees in one empty cell. `cars`: cars driving on the streets and main
        roads. `hamlets`: bunches of buildings close together away from the roads. `floating`: props
        floating on the sea. `lines`: lines of props along the level. `landmarks`: set pieces at
        given
        places. `lots` (phase 15, P15-R08): props of whole tiles (car parks, yards, plazas, parks)
        for
        the tiles of a district's blocks that no building of their group fits. `forests` (D-212):
        trees gather in woods (default: they grow evenly)."""
        self.cell_size = cell_size
        self.tree_clearance = tree_clearance
        self.max_slope = max_slope
        self.tree_max_slope = tree_max_slope
        self.min_height = min_height
        self.zone_frequency = zone_frequency
        self.groups = groups
        self.trees = trees
        self.trees_per_cell = trees_per_cell
        self.cars = cars
        self.loners = loners
        self.hamlets = hamlets
        self.floating = floating
        self.lines = lines
        self.landmarks = landmarks
        self.lots = lots
        self.forests = forests


class TileRules:
    """The grid of square tiles the districts are laid on (phase 15, P15-R01): `size` world units a
    side, the width of a one-lane-each-way street with its two sidewalks, each `sidewalk` wide."""

    def __init__(self, size: float, sidewalk: float) -> None:
        self.size = size
        self.sidewalk = sidewalk


class Boulevard:
    """Wider avenues of the street grids (see `RoadRules.boulevards`)."""

    def __init__(self, lanes: int, width: float, share: float) -> None:
        """`lanes`: 3 or 4 lanes each way."""
        self.lanes = lanes
        self.width = width
        self.share = share


class MeanderRange:
    """The ranges of a main road's meander: its amplitude and its wavelength."""

    def __init__(self, amplitude: Range, wavelength: Range) -> None:
        self.amplitude = amplitude
        self.wavelength = wavelength


class Dual:
    """2×2 roads (phase 4 review): the first `main_roads` main roads, and a share `avenues` of the
    lines of the street grids, are `width` wide with two lanes each way."""

    def __init__(self, width: float, main_roads: int, avenues: float) -> None:
        self.width = width
        self.main_roads = main_roads
        self.avenues = avenues


class Junction:
    """Where a path meets a road it widens to `width`, narrowing back to `cross_width` over
    `length`, so it merges into the road."""

    def __init__(self, width: float, length: float) -> None:
        self.width = width
        self.length_ = length


class NoCrossings:
    """Phase 6 review: roads never cross, they only meet where a path joins a road. Main roads keep
    at least `gap` apart (each one after the first follows the one before it, on one side); a path
    starts on a main road and ends off the screen or on another main road or street, `gap` clear of
    everything else; street grids have T-junctions only."""

    def __init__(self, gap: float) -> None:
        self.gap = gap


class RoadRules:
    """Randomly generated roads and paths (P04-R07): `main_roads` roads wind along the whole level,
    and paths branch off them across it to past the screen edges. Buildings stand only along
    them."""

    def __init__(  # noqa: PLR0917 (positional data fields: Transcrypt drops keyword arguments)
        self,
        main_roads: int,
        spread: float,
        meander: MeanderRange,
        cross_spacing: Range,
        cross_bend: float,
        main_width: float,
        cross_width: float,
        dual: Dual,
        junction: Junction,
        offscreen_x: float,
        turn_rate: float,
        min_height: float,
        max_slope: float,
        min_run: int,
        step: float,
        slot_spacing: float,
        setback: float,
        boulevards: Sequence[Boulevard] | None = None,
        no_crossings: NoCrossings | None = None,
        tiles: TileRules | None = None,
    ) -> None:
        """`spread`: main roads are centred somewhere within X in [-spread, spread].
        `cross_spacing`:
        distance along Z between two paths. `cross_bend`: largest sideways bend of a path.
        `boulevards` (reviewer, 2026-10-28): a share `share` of the grid lines are `width` wide with
        `lanes` lanes each way. They run straight through their district: every stretch is built,
        and where a crossing must go (`no_crossings`), the side street is cut. `offscreen_x`: roads
        only start and end beyond X = ±offscreen_x, outside the screen. `turn_rate`: sharpest turn
        of
        a road leaving the screen, in radians per `step`. `min_height`: no road on ground lower than
        this (the sea) or steeper than `max_slope`. `min_run`: pieces of road shorter than this many
        points are dropped. `step`: distance between two points of a road's centre line.
        `slot_spacing`: distance between two building slots along a road. `setback`: gap between the
        road edge and a building's footprint. `no_crossings`: see `NoCrossings`. `tiles` (phase 15):
        the districts are laid on a grid of tiles."""
        self.main_roads = main_roads
        self.spread = spread
        self.meander = meander
        self.cross_spacing = cross_spacing
        self.cross_bend = cross_bend
        self.main_width = main_width
        self.cross_width = cross_width
        self.dual = dual
        self.junction = junction
        self.offscreen_x = offscreen_x
        self.turn_rate = turn_rate
        self.min_height = min_height
        self.max_slope = max_slope
        self.min_run = min_run
        self.step = step
        self.slot_spacing = slot_spacing
        self.setback = setback
        self.boulevards = boulevards
        self.no_crossings = no_crossings
        self.tiles = tiles


class Sea:
    """The sea of a level: its surface height."""

    def __init__(self, level: float) -> None:
        self.level = level


class SceneryLevel:
    """The ground of a scrolling level: terrain, optional sea, roads and props."""

    def __init__(  # noqa: PLR0917 (positional data fields: Transcrypt drops keyword arguments)
        self,
        id: str,
        name: str,
        seed: int,
        scroll_speed: float,
        transition: float,
        sections: Sequence[TerrainSection],
        roads: RoadRules,
        props: PropRules,
        sea: Sea | None = None,
        runout: float | None = None,
    ) -> None:
        """`scroll_speed`: ground speed under the playfield, in world units per second (GD-01).
        `transition`: width of ground (in Z) over which two sections blend into each other.
        `runout`:
        seconds at the end of the last section that are only flown over past the level's end, during
        a final boss fight (P07-R03, see `with_runout`)."""
        self.id = id
        self.name = name
        self.seed = seed
        self.scroll_speed = scroll_speed
        self.transition = transition
        self.sections = sections
        self.roads = roads
        self.props = props
        self.sea = sea
        self.runout = runout


class PlacedSection:
    """A section with its place along the level."""

    def __init__(self, section: TerrainSection, start: float, end: float) -> None:
        self.section = section
        self.start = start
        self.end = end


def layout_sections(level: SceneryLevel) -> list[PlacedSection]:
    """Places the sections end to end from Z = 0, each `seconds × scroll_speed` long."""
    if len(level.sections) == 0:
        raise ValueError('Level "' + level.id + '" has no section')
    if not (level.scroll_speed > 0):
        raise ValueError("The scroll speed must be positive")
    placed: list[PlacedSection] = []
    start = 0.0
    for section in level.sections:
        if not (section.seconds > 0):
            raise ValueError('Section "' + section.name + '" has no length')
        end = start + section.seconds * level.scroll_speed
        placed.append(PlacedSection(section, start, end))
        start = end
    return placed


def level_duration(level: SceneryLevel) -> float:
    """How long the level lasts, in seconds (P04-R06)."""
    total = 0.0
    for section in level.sections:
        total += section.seconds
    return total


def level_length(level: SceneryLevel) -> float:
    """Length of the level along Z, in world units."""
    return level_duration(level) * level.scroll_speed


def with_runout(level: SceneryLevel, seconds: float) -> SceneryLevel:
    """`level` with `seconds` more of its last section (P07-R03): ground drawn past the level's end,
    for a final boss fight that keeps the ground scrolling."""
    if len(level.sections) == 0 or seconds <= 0:
        return level
    last = level.sections[len(level.sections) - 1]
    extended = _with_seconds(last, last.seconds + seconds)
    sections = list(level.sections[: len(level.sections) - 1])
    sections.append(extended)
    runout = (level.runout if level.runout is not None else 0) + seconds
    return SceneryLevel(
        level.id,
        level.name,
        level.seed,
        level.scroll_speed,
        level.transition,
        sections,
        level.roads,
        level.props,
        level.sea,
        runout,
    )


def _with_seconds(section: TerrainSection, seconds: float) -> TerrainSection:
    """A copy of `section` with another length."""
    return TerrainSection(
        section.name,
        seconds,
        section.relief,
        section.building_density,
        section.tree_density,
        section.flatten,
        section.channel,
        section.shore,
        section.dunes,
        section.lakes,
        section.crevasses,
        section.float_density,
        section.surface,
        section.trees,
        section.groups,
        section.streets,
        section.blocks,
    )


def runout_start(level: SceneryLevel) -> float | None:
    """Z where the runout of `level` starts (see `SceneryLevel.runout`), if it has one."""
    if not level.runout:
        return None
    return level_length(level) - level.runout * level.scroll_speed

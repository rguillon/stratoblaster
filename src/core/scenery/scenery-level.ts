/*
 * Data that describes the ground of a scrolling level (P04-R01, P04-R04, P04-R06). World units
 * are logical pixels: X across the level (0 under the middle of the playfield), Z along it
 * (the level scrolls towards +Z), Y up. Heights are absolute; the sea, when there is one,
 * sits at `sea.level`.
 */

/** Fractal relief added to a section's base height. */
export interface Relief {
  /** Height of the ground where the relief is zero. */
  readonly base: number;
  /** Largest height the relief adds (or removes, for smooth relief). */
  readonly amplitude: number;
  /** Cycles per world unit of the first octave. */
  readonly frequency: number;
  readonly octaves: number;
  /**
   * `smooth`: rolling ground from `base - amplitude` to `base + amplitude`.
   * `ridged`: sharp crests from `base` up to `base + amplitude` (mountain ranges).
   */
  readonly style: 'smooth' | 'ridged';
  /** Heights above this are softly squashed, so peaks stay under the flight altitude. */
  readonly maxHeight?: number;
}

/** A winding line across Z: `x + amplitude * sin(2π z / wavelength + phase)`. */
export interface Meander {
  readonly x: number;
  readonly amplitude: number;
  readonly wavelength: number;
}

/** Flattens a band of ground around a meander line (room for buildings). */
export interface Flatten {
  readonly path: Meander;
  readonly halfWidth: number;
  /** Width of the slope from the flat band back to the relief. */
  readonly edge: number;
  readonly height: number;
  /** Small relief left on the flat band. */
  readonly roughness: number;
}

/** Carves a canyon along a meander line. */
export interface Channel {
  readonly path: Meander;
  /** Half-width of the canyon floor. */
  readonly halfWidth: number;
  /** Width of each wall, from the floor to the rim. */
  readonly wall: number;
  /** Height of the canyon floor (below the sea level, it holds a river). */
  readonly floor: number;
}

/** Drops the ground under the sea on one side of a meander line. */
export interface Shore {
  readonly path: Meander;
  /** The land is at X greater than the shore line (`1`) or smaller (`-1`). */
  readonly landSide: 1 | -1;
  /** Width of the slope from the land down to the sea bed. */
  readonly width: number;
  readonly seabed: number;
}

/**
 * What covers the ground of a section, as shares (0..1) of alternative ground textures over the
 * default one: `lush` (grass), `paved` (concrete, asphalt) and `sandy` (desert sand, P06-R06).
 */
export interface Surface {
  readonly lush: number;
  readonly paved: number;
  readonly sandy: number;
}

/**
 * Sand dunes (P06-R06): parallel crests every `wavelength`, each with a long gentle windward
 * slope and a short steep lee slope, whose lines wander with noise and whose heights vary,
 * added on top of the section's relief.
 */
export interface Dunes {
  /** Height of the highest crests above the relief. */
  readonly height: number;
  /** Distance between two crests. */
  readonly wavelength: number;
  /** Direction the crests face, in degrees from +Z (the wind blows that way). */
  readonly angleDeg: number;
  /** How far the crest lines wander, in wavelengths. */
  readonly warp: number;
}

/**
 * Frozen lakes (phase 8, P08-R03): round basins scattered over a section, one chance in each
 * square of `spacing` units, flattened to `level` (below the terrain look's `lowHeight`, so they
 * get its low ground: ice) over `radius`, with a shore `edge` wide.
 */
export interface Lakes {
  readonly spacing: number;
  /** Chance (0..1) that a square of `spacing` has a lake. */
  readonly chance: number;
  readonly radius: readonly [number, number];
  readonly level: number;
  readonly edge: number;
}

/**
 * Crevasses (phase 8, P08-R07): narrow cuts `depth` deep and `width` wide, about every
 * `spacing` units, running across the level at `angleDeg` from +X, their lines bent by noise
 * (`warp`, in spacings) and broken into pieces: about `share` (0..1) of each line is cut.
 */
export interface Crevasses {
  readonly spacing: number;
  readonly width: number;
  readonly depth: number;
  readonly angleDeg: number;
  readonly warp: number;
  readonly share: number;
}

/**
 * A dense network of straight streets over a section (phase 4 review): streets across the level
 * (rows) every `rows` units and streets along it (columns) every `columns` units, of which each
 * stretch between two crossings is built with the chance `links`. Streets meet at crossings and
 * T-junctions; none ends on screen. The winding roads and the paths stay out of these sections.
 */
export interface StreetGrid {
  /** Distance along Z between two rows. */
  readonly rows: readonly [number, number];
  /** Distance along X between two columns. */
  readonly columns: readonly [number, number];
  /** Chance (0..1) that a stretch of street between two crossings is built. */
  readonly links: number;
}

/** One stretch of a level, sculpted from a relief and optional operations. */
export interface TerrainSection {
  /** Shown by debug tools, e.g. `canyon`. */
  readonly name: string;
  /** How long the section takes to fly over, at the level's scroll speed. */
  readonly seconds: number;
  readonly relief: Relief;
  readonly flatten?: Flatten;
  readonly channel?: Channel;
  readonly shore?: Shore;
  readonly dunes?: Dunes;
  readonly lakes?: Lakes;
  readonly crevasses?: Crevasses;
  /** Chance (0..1) that a cell of the sea gets floating props (`PropRules.floating`). */
  readonly floatDensity?: number;
  /** Chance (0..1) that a building slot along a road of this section gets a building. */
  readonly buildingDensity: number;
  /** Chance (0..1) that an empty candidate spot of this section gets trees. */
  readonly treeDensity: number;
  /** Ground cover (default: none, the level's default ground). */
  readonly surface?: Partial<Surface>;
  /** Ids of the tree kinds that grow here (default: all of them). */
  readonly trees?: readonly string[];
  /** Ids of the building groups that stand here (default: all of them). */
  readonly groups?: readonly string[];
  /** A network of straight streets over this section, instead of roads and paths. */
  readonly streets?: StreetGrid;
  /** Fill each block of the street grid with buildings (on a podium), instead of street fronts. */
  readonly blocks?: BlockFill;
}

/**
 * How the blocks of a section's street grid are filled (phase 4 review): a podium covering the
 * whole block, of a random height, with towers of the section's building groups on its roof; or,
 * without podiums, buildings standing on the ground side by side over the whole block.
 */
export interface BlockFill {
  /** Ids of podium models: a unit square plan, 1 high, stretched to each block (may be empty). */
  readonly podiums: readonly string[];
  readonly podiumHeight: readonly [number, number];
  /** How many towers stand on a podium, or buildings on a block. */
  readonly towers: readonly [number, number];
}

/** A kind of prop the placement can choose, with its relative weight. */
export interface PropKindRule {
  /** Key of the prop's model in the game's view. */
  readonly id: string;
  readonly weight: number;
  /** Radius of ground the prop stands on (at its largest scale); it must be about flat. */
  readonly footprint: number;
  /** Random scale range. */
  readonly scale: readonly [number, number];
  /**
   * Half the side of the square the model fits in, at scale 1, for buildings with a square
   * plan: they then stand right at the street setback and pack against their neighbours, instead
   * of keeping the whole `footprint` circle clear (phase 4 review).
   */
  readonly frontage?: number;
  /**
   * Floating props (phase 8: ice floes) drift slowly to and fro: up to `x` and `z` world units
   * from where they were placed, over `period` seconds.
   */
  readonly drift?: { readonly x: number; readonly z: number; readonly period: number };
}

/**
 * Props floating on the sea (phase 8, P08-R07: ice floes and icebergs): in cells of `cellSize`,
 * up to `perCell` each with the chance of their section's `floatDensity`, where the sea is at
 * least `depth` deep under their whole footprint. They float at the sea level.
 */
export interface FloatRules {
  readonly cellSize: number;
  readonly perCell: number;
  readonly depth: number;
  readonly kinds: readonly PropKindRule[];
}

/**
 * A line of props along the level (phase 8, P08-R03: a pipeline on stilts): one `kind` every
 * `spacing` along `path`, turned along it, standing where the ground is above the sea level and
 * no steeper than `maxSlope`, in the sections whose names are listed (all when omitted). They
 * are placed before the buildings, which keep clear of them.
 */
export interface PropLine {
  readonly kind: string;
  readonly path: Meander;
  readonly spacing: number;
  /** Radius of ground each piece takes, for the buildings to keep clear of. */
  readonly footprint: number;
  readonly maxSlope: number;
  readonly sections?: readonly string[];
  /**
   * Phase 9: the line also crosses water (a pipeline on stilts over a swamp): its pieces stand on
   * the ground, or at the sea level where the ground is under it.
   */
  readonly overWater?: boolean;
}

/**
 * A set piece (phase 9: a dam across a lake, a waterfall on a river, a temple): one prop of
 * `kind` at `z` along the level, at `x` across it or on `path` (its width then across the path), standing
 * on the ground or, with `onWater`, at the sea level. It is placed first, whatever the slope, and
 * the buildings and trees keep clear of its `footprint` (a box `footprint` wide each way, or
 * `[halfX, halfZ]`).
 */
export interface Landmark {
  readonly kind: string;
  readonly z: number;
  readonly x?: number;
  readonly path?: Meander;
  /** Turn around the vertical axis (radians), added to the path's heading if any. */
  readonly rotation?: number;
  readonly scale?: number;
  readonly footprint: number | readonly [halfX: number, halfZ: number];
  readonly onWater?: boolean;
}

/** Buildings of a group cluster together: a low-frequency noise picks the group of each area. */
export interface PropGroupRule {
  readonly id: string;
  readonly weight: number;
  readonly kinds: readonly PropKindRule[];
}

/** Where and which props stand on the ground (P04-R04). Buildings follow the roads (R07). */
export interface PropRules {
  /** Trees grow in the cells of a grid of this size. */
  readonly cellSize: number;
  /** Trees keep this far from the road edges. */
  readonly treeClearance: number;
  /** Steepest ground (height difference over the footprint radius) a building stands on. */
  readonly maxSlope: number;
  /** Trees stand on steeper ground than buildings. */
  readonly treeMaxSlope: number;
  /** No prop stands below this height (e.g. just above the sea). */
  readonly minHeight: number;
  /** Cycles per world unit of the noise that picks a building group per area. */
  readonly zoneFrequency: number;
  readonly groups: readonly PropGroupRule[];
  readonly trees: readonly PropKindRule[];
  /** Most trees in one empty cell. */
  readonly treesPerCell: number;
  /** Cars driving on the streets and main roads (phase 4 review, see `Traffic`). */
  readonly cars?: CarRules;
  /**
   * Phase 6 review: a few lone buildings away from the roads. Each square of `cell` units gets
   * one with the chance `chance × buildingDensity` of its section, at least `clearance` from
   * every road edge. Not in the sections with street grids.
   */
  readonly loners?: { readonly cell: number; readonly chance: number; readonly clearance: number };
  /** Phase 6 review: hamlets, bunches of buildings close together away from the roads. */
  readonly hamlets?: HamletRules;
  /** Phase 8: props floating on the sea (ice floes, icebergs). */
  readonly floating?: FloatRules;
  /** Phase 8: lines of props along the level (a pipeline). */
  readonly lines?: readonly PropLine[];
  /** Phase 9: set pieces at given places (a dam, waterfalls, a temple). */
  readonly landmarks?: readonly Landmark[];
}

/**
 * Hamlets (phase 6 review): one every `spacing` along the level, in sections with buildings
 * (`buildingDensity` > 0) and no street grid. A hamlet is `buildings` buildings of one group,
 * all turned the same way, within `radius` of its centre, `gap` apart and at least `clearance`
 * from every road edge. Its centre is tried at a few places across the level.
 */
export interface HamletRules {
  readonly spacing: readonly [number, number];
  readonly buildings: readonly [number, number];
  readonly radius: number;
  readonly gap: number;
  readonly clearance: number;
}

/** Cars driving on the streets and main roads: one chance per road point to start there. */
export interface CarRules {
  readonly kinds: readonly string[];
  /** Chance that a point of a street or main road has a car. */
  readonly density: number;
  /** Cars stand on the road surface, this high above the ground. */
  readonly lift: number;
  readonly scale: number;
  /** About the length of a car: cars are hidden this close to the ends of their road. */
  readonly length: number;
  /** Speeds (world units per second); all the cars of one lane share one. */
  readonly speed: readonly [number, number];
}

type Range = readonly [number, number];

/**
 * Randomly generated roads and paths (P04-R07): `mainRoads` roads wind along the whole level,
 * and paths branch off them across it to past the screen edges. Buildings stand only along them.
 */
export interface RoadRules {
  readonly mainRoads: number;
  /** Main roads are centred somewhere within X ∈ [-spread, spread]. */
  readonly spread: number;
  readonly meander: { readonly amplitude: Range; readonly wavelength: Range };
  /** Distance along Z between two paths. */
  readonly crossSpacing: Range;
  /** Largest sideways bend of a path. */
  readonly crossBend: number;
  readonly mainWidth: number;
  readonly crossWidth: number;
  /**
   * 2×2 roads (phase 4 review): the first `mainRoads` main roads, and a share `avenues` of the
   * lines of the street grids, are `width` wide with two lanes each way.
   */
  readonly dual: { readonly width: number; readonly mainRoads: number; readonly avenues: number };
  /**
   * Where a path meets a road it widens to `width`, narrowing back to `crossWidth` over
   * `length`, so it merges into the road.
   */
  readonly junction: { readonly width: number; readonly length: number };
  /**
   * Roads only start and end beyond X = ±offscreenX, outside the screen: a road that must stop
   * turns off the screen first, and paths run from their road to past the screen edge.
   */
  readonly offscreenX: number;
  /** Sharpest turn of a road leaving the screen, in radians per `step`. */
  readonly turnRate: number;
  /** No road on ground lower than this (the sea) or steeper than `maxSlope`. */
  readonly minHeight: number;
  readonly maxSlope: number;
  /** Pieces of road shorter than this many points are dropped. */
  readonly minRun: number;
  /** Distance between two points of a road's centre line. */
  readonly step: number;
  /** Distance between two building slots along a road. */
  readonly slotSpacing: number;
  /** Gap between the road edge and a building's footprint. */
  readonly setback: number;
  /**
   * Phase 6 review: roads never cross, they only meet where a path joins a road. Main roads keep
   * at least `gap` apart (each one after the first follows the one before it, on one side); a
   * path starts on a main road and ends off the screen or on another main road or street, `gap`
   * clear of everything else; street grids have T-junctions only. Unset (Level Zero): main
   * roads and paths may cross, and streets meet at crossings too.
   */
  readonly noCrossings?: { readonly gap: number };
}

/** The ground of a scrolling level: terrain, optional sea, roads and props. */
export interface SceneryLevel {
  readonly id: string;
  readonly name: string;
  readonly seed: number;
  /** Ground speed under the playfield, in world units per second (GD-01). */
  readonly scrollSpeed: number;
  /** Width of ground (in Z) over which two sections blend into each other. */
  readonly transition: number;
  readonly sections: readonly TerrainSection[];
  readonly sea?: { readonly level: number };
  readonly roads: RoadRules;
  readonly props: PropRules;
}

/** A section with its place along the level. */
export interface PlacedSection {
  readonly section: TerrainSection;
  readonly start: number;
  readonly end: number;
}

/** Places the sections end to end from Z = 0, each `seconds × scrollSpeed` long. */
export function layoutSections(level: SceneryLevel): PlacedSection[] {
  if (level.sections.length === 0) throw new RangeError(`Level "${level.id}" has no section`);
  if (!(level.scrollSpeed > 0)) throw new RangeError('The scroll speed must be positive');
  let start = 0;
  return level.sections.map((section) => {
    if (!(section.seconds > 0)) throw new RangeError(`Section "${section.name}" has no length`);
    const end = start + section.seconds * level.scrollSpeed;
    const placed = { section, start, end };
    start = end;
    return placed;
  });
}

/** How long the level lasts, in seconds (P04-R06). */
export function levelDuration(level: SceneryLevel): number {
  return level.sections.reduce((sum, s) => sum + s.seconds, 0);
}

/** Length of the level along Z, in world units. */
export function levelLength(level: SceneryLevel): number {
  return levelDuration(level) * level.scrollSpeed;
}

/**
 * `level` with `seconds` more of its last section (P07-R03): ground drawn past the level's end,
 * for a final boss fight that keeps the ground scrolling.
 */
export function withRunout(level: SceneryLevel, seconds: number): SceneryLevel {
  const last = level.sections.at(-1);
  if (!last || seconds <= 0) return level;
  return {
    ...level,
    sections: [...level.sections.slice(0, -1), { ...last, seconds: last.seconds + seconds }],
  };
}

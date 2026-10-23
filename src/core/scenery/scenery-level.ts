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
 * default one: `lush` (grass) and `paved` (concrete, asphalt).
 */
export interface Surface {
  readonly lush: number;
  readonly paved: number;
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
  /** Fill each block of the street grid with a podium and towers, instead of street fronts. */
  readonly blocks?: BlockFill;
}

/**
 * How the blocks of a section's street grid are filled (phase 4 review): a podium covering the
 * whole block, of a random height, with towers of the section's building groups on its roof.
 */
export interface BlockFill {
  /** Ids of podium models: a unit square plan, 1 high, stretched to each block. */
  readonly podiums: readonly string[];
  readonly podiumHeight: readonly [number, number];
  /** How many towers stand on a podium. */
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

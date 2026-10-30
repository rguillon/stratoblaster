import { pick, randomIn, type Random } from '../../core/math/rng';
import type { ColoredGeometry } from '../../render/geometry/gradient-shapes';

type Rgb = readonly [number, number, number];
type Range = readonly [number, number];

/** One row of buildings along each side of the street. */
export interface CityRow {
  /** Distance from the street edge to the facades of this row. */
  readonly facadeOffset: number;
  /** Building length along the street (Z). */
  readonly width: Range;
  readonly gap: Range;
  /** Building size away from the street (X). */
  readonly depth: Range;
  readonly height: Range;
  /** Whether blade signs hang from this row's facades. */
  readonly signs: boolean;
}

export interface CityOptions {
  /** The chunk spans Z in [0, length]; two chunks end to end tile seamlessly. */
  readonly length: number;
  /** Facades of the first row stand at X = ±streetHalfWidth. */
  readonly streetHalfWidth: number;
  readonly rows: readonly CityRow[];
  readonly colors: { readonly wall: Rgb; readonly facade: Rgb; readonly roof: Rgb };
  readonly street: {
    /** The ground spans X in [-halfWidth, halfWidth]. */
    readonly halfWidth: number;
    readonly color: Rgb;
    /** Dashed lane lines at these X positions. */
    readonly laneX: readonly number[];
    readonly dash: number;
    readonly dashPeriod: number;
    readonly lineWidth: number;
    readonly lineColor: Rgb;
  };
  readonly windows: WindowOptions;
  /** Neon colours of the signs and roof trims. */
  readonly neonColors: readonly Rgb[];
  readonly signs: {
    readonly chance: number;
    readonly width: Range;
    readonly height: Range;
    readonly baseHeight: Range;
    readonly panel: Rgb;
    /** Lines of "text" drawn as bars on each sign. */
    readonly lines: number;
  };
  readonly trim: { readonly chance: number; readonly height: number };
}

export interface WindowOptions {
  readonly cellWidth: number;
  readonly cellHeight: number;
  readonly width: number;
  readonly height: number;
  /** Height of the windowless ground floor. */
  readonly groundFloor: number;
  readonly litChance: number;
  readonly brightness: Range;
  readonly colors: readonly Rgb[];
}

/** Dark, non-glowing parts (`structure`) and self-lit neon parts (`lights`) of a city piece. */
export interface CityGeometry {
  readonly structure: ColoredGeometry;
  readonly lights: ColoredGeometry;
}

function emptyGeometry(): ColoredGeometry {
  return { positions: [], indices: [], colors: [] };
}

function quad(geo: ColoredGeometry, corners: readonly number[], [r, g, b]: Rgb): void {
  const base = geo.positions.length / 3;
  geo.positions.push(...corners);
  for (let i = 0; i < 4; i++) geo.colors.push(r, g, b, 1);
  geo.indices.push(base, base + 1, base + 2, base, base + 2, base + 3);
}

/** A rectangle in the plane X = `x`. */
function quadX(geo: ColoredGeometry, x: number, [y0, y1]: Range, [z0, z1]: Range, rgb: Rgb) {
  quad(geo, [x, y0, z0, x, y1, z0, x, y1, z1, x, y0, z1], rgb);
}

/** A rectangle in the plane Y = `y`. */
function quadY(geo: ColoredGeometry, y: number, [x0, x1]: Range, [z0, z1]: Range, rgb: Rgb) {
  quad(geo, [x0, y, z0, x1, y, z0, x1, y, z1, x0, y, z1], rgb);
}

/** A rectangle in the plane Z = `z`, facing the camera (which looks towards +Z). */
function quadZ(geo: ColoredGeometry, z: number, [x0, x1]: Range, [y0, y1]: Range, rgb: Rgb) {
  quad(geo, [x0, y0, z, x1, y0, z, x1, y1, z, x0, y1, z], rgb);
}

function scaled([r, g, b]: Rgb, k: number): Rgb {
  return [r * k, g * k, b * k];
}

function litWindowColor(random: Random, windows: WindowOptions): Rgb {
  return scaled(pick(random, windows.colors), randomIn(random, windows.brightness));
}

/** Calls `cell(u0, v0)` for each lit cell of a `width × height` window grid. */
function forEachLitWindow(
  random: Random,
  windows: WindowOptions,
  width: number,
  height: number,
  cell: (u: number, v: number) => void,
): void {
  const cols = Math.floor(width / windows.cellWidth);
  const rows = Math.floor((height - windows.groundFloor) / windows.cellHeight);
  const marginU = (width - cols * windows.cellWidth) / 2 + (windows.cellWidth - windows.width) / 2;
  const marginV = windows.groundFloor + (windows.cellHeight - windows.height) / 2;
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      if (random() < windows.litChance) {
        cell(marginU + col * windows.cellWidth, marginV + row * windows.cellHeight);
      }
    }
  }
}

/** A blade sign hanging from a facade into the street, facing the camera. */
function addSign(
  lights: ColoredGeometry,
  random: Random,
  options: CityOptions,
  facadeX: number,
  side: number,
  z: number,
): void {
  const { signs } = options;
  const width = randomIn(random, signs.width);
  const height = randomIn(random, signs.height);
  const y0 = randomIn(random, signs.baseHeight);
  const color = pick(random, options.neonColors);
  const xIn = side * (facadeX - 0.1);
  const xOut = side * (facadeX - 0.1 - width);
  const border = 0.18;
  quadZ(lights, z, [xIn, xOut], [y0, y0 + height], color);
  const innerIn = xIn - side * border;
  const innerOut = xOut + side * border;
  quadZ(lights, z - 0.02, [innerIn, innerOut], [y0 + border, y0 + height - border], signs.panel);
  // Bars of random length suggest lines of text.
  const step = (height - 2 * border) / (2 * signs.lines + 1);
  for (let line = 0; line < signs.lines; line++) {
    const y = y0 + border + (2 * line + 1) * step;
    const length = (width - 2 * border) * randomIn(random, [0.45, 0.9]);
    const start = innerIn - side * ((width - 2 * border - length) / 2);
    quadZ(lights, z - 0.04, [start, start - side * length], [y, y + step], color);
  }
}

function addBuilding(
  city: CityGeometry,
  random: Random,
  options: CityOptions,
  row: CityRow,
  side: number,
  [z0, z1]: Range,
): void {
  const { structure, lights } = city;
  const facadeX = options.streetHalfWidth + row.facadeOffset;
  const depth = randomIn(random, row.depth);
  const height = randomIn(random, row.height);
  const x0 = side * facadeX;
  const x1 = side * (facadeX + depth);
  quadX(structure, x0, [0, height], [z0, z1], options.colors.facade);
  quadZ(structure, z0, [x0, x1], [0, height], options.colors.wall);
  quadY(structure, height, [x0, x1], [z0, z1], options.colors.roof);

  const windowX = x0 - side * 0.05;
  forEachLitWindow(random, options.windows, z1 - z0, height, (u, v) => {
    const color = litWindowColor(random, options.windows);
    quadX(
      lights,
      windowX,
      [v, v + options.windows.height],
      [z0 + u, z0 + u + options.windows.width],
      color,
    );
  });
  if (random() < options.trim.chance) {
    const color = pick(random, options.neonColors);
    quadX(lights, x0 - side * 0.08, [height - options.trim.height, height], [z0, z1], color);
  }
  if (row.signs && random() < options.signs.chance) {
    addSign(lights, random, options, facadeX, side, z0 + 0.6);
  }
}

function addStreet(city: CityGeometry, options: CityOptions): void {
  const { street, length } = options;
  quadY(city.structure, 0, [-street.halfWidth, street.halfWidth], [0, length], street.color);
  const half = street.lineWidth / 2;
  for (let z = 0; z + street.dash <= length; z += street.dashPeriod) {
    for (const x of street.laneX) {
      quadY(city.lights, 0.02, [x - half, x + half], [z, z + street.dash], street.lineColor);
    }
  }
}

/**
 * A stretch of night city along a street running towards +Z: rows of dark buildings on
 * both sides, lit windows on the facades facing the street, neon roof trims and blade signs,
 * and dashed lane lines. Everything comes from `random`, so a seeded generator gives the
 * same city every time.
 */
export function buildCityChunk(options: CityOptions, random: Random): CityGeometry {
  const city: CityGeometry = { structure: emptyGeometry(), lights: emptyGeometry() };
  addStreet(city, options);
  for (const row of options.rows) {
    for (const side of [-1, 1]) {
      let z = randomIn(random, row.gap);
      for (;;) {
        const width = randomIn(random, row.width);
        if (z + width > options.length) break;
        addBuilding(city, random, options, row, side, [z, z + width]);
        z += width + randomIn(random, row.gap);
      }
    }
  }
  return city;
}

export interface SkylineOptions {
  /** The skyline spans X in [-halfWidth, halfWidth]. */
  readonly halfWidth: number;
  readonly width: Range;
  readonly height: Range;
  readonly color: Rgb;
  readonly windows: WindowOptions;
}

/**
 * Flat silhouettes of distant towers in the XY plane (bottom at Y = 0), with a few lit
 * windows slightly in front of them.
 */
export function buildSkyline(options: SkylineOptions, random: Random): CityGeometry {
  const city: CityGeometry = { structure: emptyGeometry(), lights: emptyGeometry() };
  let x = -options.halfWidth;
  while (x < options.halfWidth) {
    const width = randomIn(random, options.width);
    const height = randomIn(random, options.height);
    quadZ(city.structure, 0, [x, x + width], [0, height], options.color);
    const left = x;
    forEachLitWindow(random, options.windows, width, height, (u, v) => {
      const color = litWindowColor(random, options.windows);
      const x0 = left + u;
      quadZ(
        city.lights,
        -0.05,
        [x0, x0 + options.windows.width],
        [v, v + options.windows.height],
        color,
      );
    });
    x += width;
  }
  return city;
}

export interface RainOptions {
  readonly count: number;
  /** Drops span X in [-halfWidth, halfWidth], Y in [0, height) and Z in `z`. */
  readonly halfWidth: number;
  readonly height: number;
  readonly z: Range;
  readonly length: Range;
  readonly width: number;
  readonly color: Rgb;
}

/**
 * Thin vertical rain streaks facing the camera. The pattern is drawn twice, stacked, so
 * moving the mesh down by up to `height` and wrapping loops without a gap.
 */
export function buildRain(options: RainOptions, random: Random): ColoredGeometry {
  const geo = emptyGeometry();
  for (let i = 0; i < options.count; i++) {
    const x = randomIn(random, [-options.halfWidth, options.halfWidth]);
    const y = random() * options.height;
    const z = randomIn(random, options.z);
    const length = randomIn(random, options.length);
    for (const offset of [0, options.height]) {
      quadZ(geo, z, [x, x + options.width], [y + offset, y + offset + length], options.color);
    }
  }
  return geo;
}

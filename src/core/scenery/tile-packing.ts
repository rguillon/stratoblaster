// P15-R07, R08: buildings of whole tiles packed in the blocks of a district (phase 15).
import { tileKey } from './road-tiles';
import type { HeightField } from './height-field';
import type { PropKindRule, PropRules, TileRules } from './scenery-level';

/** A building's tiles: from tile (`x`, `z`), `w` × `d` of them in world X and Z. */
export interface TileSpot {
  readonly kind: PropKindRule;
  readonly x: number;
  readonly z: number;
  readonly w: number;
  readonly d: number;
  /** Turn around Y (radians): its front (-Z) faces a road next to it when there is one. */
  readonly rotation: number;
}

/** What packing a block needs to know. */
export interface PackSite {
  /** Whether tile (`x`, `z`) is free: not a road, not taken, ground fit to build on. */
  readonly free: (x: number, z: number) => boolean;
  readonly road: (x: number, z: number) => boolean;
  /** The kinds a building at tile (`x`, `z`) may be, in the order to try them. */
  readonly kindsAt: (x: number, z: number, draw: number) => readonly PropKindRule[];
  /** A random number (0..1) for draw `k`. */
  readonly random: (k: number) => number;
}

/** Facings by quarter turn: the side the front faces, as a step in tiles, and the turn. */
const FACINGS = [
  { dx: 0, dz: -1, rotation: 0 },
  { dx: 0, dz: 1, rotation: Math.PI },
  { dx: 1, dz: 0, rotation: -Math.PI / 2 },
  { dx: -1, dz: 0, rotation: Math.PI / 2 },
] as const;

/** Whether all the tiles of a spot are free and inside the block. */
function fits(site: PackSite, block: TileBlock, x: number, z: number, w: number, d: number) {
  if (x < block.x0 || z < block.z0 || x + w > block.x1 || z + d > block.z1) return false;
  for (let i = 0; i < w; i++)
    for (let j = 0; j < d; j++) if (!site.free(x + i, z + j)) return false;
  return true;
}

/** Whether a road runs along the side of a spot that `facing` looks at. */
function faces(
  site: PackSite,
  x: number,
  z: number,
  w: number,
  d: number,
  f: (typeof FACINGS)[number],
) {
  if (f.dz !== 0) {
    const row = f.dz < 0 ? z - 1 : z + d;
    for (let i = 0; i < w; i++) if (site.road(x + i, row)) return true;
    return false;
  }
  const column = f.dx < 0 ? x - 1 : x + w;
  for (let j = 0; j < d; j++) if (site.road(column, z + j)) return true;
  return false;
}

/** Most tiles any footprint is long. */
const LONGEST = 6;

/** Free tiles in a line through free tile (x, z), along (dx, dz), up to {@link LONGEST} + 1. */
function run(
  site: PackSite,
  block: TileBlock,
  x: number,
  z: number,
  dx: number,
  dz: number,
): number {
  let count = 1;
  for (const sign of [1, -1]) {
    for (let k = 1; k < LONGEST && count <= LONGEST; k++) {
      const [tx, tz] = [x + sign * k * dx, z + sign * k * dz];
      if (tx < block.x0 || tz < block.z0 || tx >= block.x1 || tz >= block.z1 || !site.free(tx, tz))
        break;
      count++;
    }
  }
  return count;
}

/** A block in tiles: [x0, x1) × [z0, z1). */
export interface TileBlock {
  readonly x0: number;
  readonly x1: number;
  readonly z0: number;
  readonly z1: number;
}

/**
 * The spot for `kind` with tile (`x`, `z`) as one of its corners, facing a road if it can (front
 * on a road side, P15-R08), or else any way the draw `r` picks.
 */
function spotFor(
  site: PackSite,
  block: TileBlock,
  kind: PropKindRule,
  [x, z]: readonly [number, number],
  r: number,
  /** Free tiles in a line through (x, z) along X, and along Z. */
  room: readonly [number, number],
): TileSpot | undefined {
  const [kw, kd] = kind.tiles ?? [1, 1];
  if (!roomFor([kw, kd], room)) return undefined;
  let fallback: TileSpot | undefined;
  for (const f of FACINGS) {
    const [w, d] = f.dz !== 0 ? [kw, kd] : [kd, kw];
    for (const [sx, sz] of cornersAt([x, z], w, d)) {
      if (!fits(site, block, sx, sz, w, d)) continue;
      const spot = { kind, x: sx, z: sz, w, d, rotation: f.rotation };
      if (faces(site, sx, sz, w, d, f)) return spot;
      // Standing there with a road along a side it cannot face is not allowed (P15-R08).
      fallback ??= awayFromRoads(site, spot) ? { ...spot, rotation: turnOf(r, f) } : undefined;
    }
  }
  // No way of standing there faces a road: only away from the streets, any way.
  return fallback;
}

/** Cheap first: the free run through the tile, each way, must hold the footprint one way round. */
function roomFor([kw, kd]: readonly [number, number], [across, along]: readonly [number, number]) {
  return Math.min(kw, kd) <= Math.min(across, along) && Math.max(kw, kd) <= Math.max(across, along);
}

/** The spots `w` × `d` with tile (x, z) as one of their corners. */
function cornersAt([x, z]: readonly [number, number], w: number, d: number) {
  return [
    [x, z],
    [x - w + 1, z],
    [x, z - d + 1],
    [x - w + 1, z - d + 1],
  ] as const;
}

/** Whether no road runs along any side of `spot`. */
function awayFromRoads(site: PackSite, { x, z, w, d }: TileSpot): boolean {
  return !FACINGS.some((g) => faces(site, x, z, w, d, g));
}

/** A random turn (draw `r`): that of `f` or the half turn from it, so the footprint stays `f`'s. */
const turnOf = (r: number, f: (typeof FACINGS)[number]): number =>
  r < 0.5 ? f.rotation : f.rotation + Math.PI;

/**
 * Packs `block` with buildings until about `density` of its free tiles are covered (P15-R08):
 * tiles are taken in a random order; each gets the first kind `kindsAt` gives that fits there.
 * `take` marks the tiles of each building placed.
 */
export function packBlock(
  site: PackSite,
  block: TileBlock,
  density: number,
  take: (spot: TileSpot) => void,
): void {
  const tiles = freeTiles(site, block);
  const target = density * tiles.length;
  let covered = 0;
  for (const [n, [x, z]] of tiles.entries()) {
    if (covered >= target - 0.5) return;
    if (!site.free(x, z)) continue;
    const spot = spotAt(site, block, [x, z, n], [target - covered, covered === 0]);
    if (!spot) continue;
    take(spot);
    covered += spot.w * spot.d;
  }
}

/** The free tiles of `block`, in a random order. */
function freeTiles(site: PackSite, block: TileBlock): [number, number][] {
  const tiles: [number, number, number][] = [];
  for (let x = block.x0; x < block.x1; x++) {
    for (let z = block.z0; z < block.z1; z++) {
      if (site.free(x, z)) tiles.push([x, z, site.random(tiles.length * 3 + 1)]);
    }
  }
  return tiles.sort((a, b) => a[2] - b[2]).map(([x, z]) => [x, z]);
}

/**
 * The first kind `kindsAt` gives for free tile (x, z) (the `n`th drawn) that fits there, not
 * much over the `left` tiles still to cover (the last building may overshoot a little).
 */
function spotAt(
  site: PackSite,
  block: TileBlock,
  [x, z, n]: readonly [number, number, number],
  [left, first]: readonly [number, boolean],
): TileSpot | undefined {
  const room = [run(site, block, x, z, 1, 0), run(site, block, x, z, 0, 1)] as const;
  for (const kind of site.kindsAt(x, z, n)) {
    const spot = spotFor(site, block, kind, [x, z], site.random(n * 3 + 2), room);
    if (spot && (first || spot.w * spot.d <= left + 1.5)) return spot;
  }
  return undefined;
}

/**
 * The ground of the tiles, from the heights at their corners (each asked once, shared by the
 * four tiles around it): a tile is fit to build on when its lowest corner is at least
 * `minHeight` and its corners differ by at most `maxSlope` over half a tile.
 */
export class TileGround {
  readonly #corners = new Map<number, number>();
  readonly #fit = new Map<number, boolean>();

  constructor(
    private readonly field: HeightField,
    private readonly tiles: TileRules,
    private readonly rules: Pick<PropRules, 'maxSlope' | 'minHeight'>,
  ) {}

  #corner(x: number, z: number): number {
    const key = tileKey(x, z);
    let h = this.#corners.get(key);
    if (h === undefined) {
      h = this.field.height(x * this.tiles.size, z * this.tiles.size);
      this.#corners.set(key, h);
    }
    return h;
  }

  /** Lowest and highest corner of tile (x, z). */
  #range(x: number, z: number): [number, number] {
    const hs = [
      this.#corner(x, z),
      this.#corner(x + 1, z),
      this.#corner(x, z + 1),
      this.#corner(x + 1, z + 1),
    ];
    return [Math.min(...hs), Math.max(...hs)];
  }

  /** Whether tile (x, z), of key `key`, is fit to build on. */
  fit(x: number, z: number, key = tileKey(x, z)): boolean {
    let fit = this.#fit.get(key);
    if (fit === undefined) {
      const [low, high] = this.#range(x, z);
      fit =
        low >= this.rules.minHeight && (high - low) / (this.tiles.size / 2) <= this.rules.maxSlope;
      this.#fit.set(key, fit);
    }
    return fit;
  }

  /** Lowest ground under the tiles of `spot`, so the building never floats. */
  lowest(spot: Pick<TileSpot, 'x' | 'z' | 'w' | 'd'>): number {
    let low = Infinity;
    for (let i = 0; i <= spot.w; i++) {
      for (let j = 0; j <= spot.d; j++) low = Math.min(low, this.#corner(spot.x + i, spot.z + j));
    }
    return low;
  }
}

export { tileKey };

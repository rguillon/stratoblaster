import { hash2D, smoothstep, type Noise2D } from '../math/noise';
import type { Crevasses, Lakes } from './scenery-level';

// Sculpt operations of the frozen lands (phase 8, P08-R03, P08-R07): frozen lakes and the
// crevasses of a glacier. Pure and deterministic for a given seed.

/** Hash streams of a lake's square: whether it has one, where, how big. */
const LAKE_DRAWS = { Has: 0, X: 1, Z: 2, Radius: 3 } as const;
/** Scale (in spacings) of the noise that breaks the crevasse lines into pieces. */
const CREVASSE_PIECES = 1.3;
/** Share of a crevasse's half width that is its flat-bottomed floor. */
const CREVASSE_FLOOR = 0.35;

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

/** One square's lake: its centre and radius. */
interface Lake {
  readonly cx: number;
  readonly cz: number;
  readonly radius: number;
}

/**
 * The frozen lakes of `lakes` (see {@link withLakes}), each square's lake worked out once when
 * first needed (reviewer, 2026-10-28: the ground asks for the same squares again and again).
 */
export class LakeField {
  readonly #squares = new Map<number, Lake | null>();

  constructor(
    private readonly lakes: Lakes,
    private readonly seed: number,
  ) {}

  /** `h` with the lakes flattened into it at (`x`, `z`). */
  apply(x: number, z: number, h: number): number {
    const { spacing, edge, level } = this.lakes;
    const [i0, j0] = [Math.floor(x / spacing), Math.floor(z / spacing)];
    let height = h;
    for (let j = j0 - 1; j <= j0 + 1; j++) {
      for (let i = i0 - 1; i <= i0 + 1; i++) {
        const lake = this.#lake(i, j);
        if (!lake) continue;
        const d = Math.hypot(x - lake.cx, z - lake.cz);
        if (d < lake.radius + edge) {
          height = lerp(level, height, smoothstep(lake.radius, lake.radius + edge, d));
        }
      }
    }
    return height;
  }

  /** The lake of square (`i`, `j`), if it has one (|j| stays far below a million). */
  #lake(i: number, j: number): Lake | null {
    const key = i * 1_000_003 + j;
    let lake = this.#squares.get(key);
    if (lake === undefined) {
      lake = squareLake(this.lakes, this.seed, i, j);
      this.#squares.set(key, lake);
    }
    return lake;
  }
}

/** The lake of square (`i`, `j`) of `lakes`, or null. */
function squareLake(lakes: Lakes, seed: number, i: number, j: number): Lake | null {
  const { spacing, edge } = lakes;
  const r = (draw: number): number => hash2D(i, j, seed * 41 + draw);
  if (r(LAKE_DRAWS.Has) >= lakes.chance) return null;
  // Kept within its square, so a lake never reaches past the squares around it.
  const radius = lerp(lakes.radius[0], lakes.radius[1], r(LAKE_DRAWS.Radius));
  const room = Math.max(0, spacing / 2 - radius - edge);
  const cx = (i + 0.5) * spacing + (r(LAKE_DRAWS.X) * 2 - 1) * room;
  const cz = (j + 0.5) * spacing + (r(LAKE_DRAWS.Z) * 2 - 1) * room;
  return { cx, cz, radius };
}

/**
 * `h` with the frozen lakes of `lakes` flattened into it at (`x`, `z`): each square of
 * `spacing` may hold one lake, round, at its level within `radius`, its shore rising back to the
 * ground over `edge`.
 */
export function withLakes(lakes: Lakes, seed: number, x: number, z: number, h: number): number {
  return new LakeField(lakes, seed).apply(x, z, h);
}

/**
 * How deep the crevasses of `crevasses` cut the ground at (`x`, `z`): 0 between them, up to
 * `depth` at the bottom of one. The lines run at `angleDeg`, bent by `noise`, and are broken
 * into pieces by it.
 */
export function crevasseDepth(crevasses: Crevasses, noise: Noise2D, x: number, z: number): number {
  const { spacing, width, depth } = crevasses;
  const angle = (crevasses.angleDeg * Math.PI) / 180;
  const scale = spacing * CREVASSE_PIECES;
  const across = (x * Math.sin(angle) + z * Math.cos(angle)) / spacing;
  const phase = across + crevasses.warp * noise(x / (spacing * 3), z / (spacing * 3));
  const t = phase - Math.floor(phase);
  const distance = Math.min(t, 1 - t) * spacing;
  const half = width / 2;
  const cut = 1 - smoothstep(half * CREVASSE_FLOOR, half, distance);
  if (cut <= 0 || crevasses.share <= 0) return 0;
  if (crevasses.share >= 1) return depth * cut;
  // Pieces: the line is cut where a second noise is above a threshold set by `share`.
  const piece = noise(x / scale + 23, z / scale - 11) * 0.5 + 0.5;
  const threshold = 1 - crevasses.share;
  return depth * cut * smoothstep(threshold - 0.05, threshold + 0.05, piece);
}

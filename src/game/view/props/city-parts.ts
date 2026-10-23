import { createRng, pick, randomIn, type Random } from '../../../core/math/rng';
import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { buildLot, type Lot } from './city-lots';

// Phase 4 review: city buildings assembled from lots (a stepped tower, a round tower, a slab, a
// courtyard or an L-shaped block, each with its own facade), so the city centre shows buildings
// as varied as the industrial zone. Everything stays within X, Z ∈ [-HALF, HALF], on Y = 0.

/** Half the side of the square every city building fits in. */
export const CITY_HALF = 9;

/** Space left between the lots of a building. */
const LOT_GAP = 1.5;

type Rgb = readonly [number, number, number];

const FACADES: readonly Rgb[] = [C.glassBlue, C.concrete, C.concreteDark, C.brick, C.white];
const WINDOWS: readonly Rgb[] = [L.windowDim, L.cyanDim, L.pinkDim];

/** Cuts `[-half, half]` in one or two spans at a random point. */
function spans(half: number, split: boolean, random: Random): (readonly [number, number])[] {
  if (!split) return [[-half, half]];
  const cut = randomIn(random, [-0.35, 0.35]) * half;
  return [
    [-half, cut],
    [cut, half],
  ];
}

/**
 * The lots of a building: the whole square for small ones, 2 or 3 unequal lots for medium ones
 * and 4 for the largest.
 */
function lots(half: number, random: Random): Lot[] {
  const large = half > CITY_HALF;
  const xs = spans(half, large, random);
  const zs = spans(half, half >= 2 * CITY_HALF || (large && random() < 0.5), random);
  return xs.flatMap(([x0, x1]) =>
    zs.map(([z0, z1]): Lot => [(x0 + x1) / 2, (z0 + z1) / 2, x1 - x0 - LOT_GAP, z1 - z0 - LOT_GAP]),
  );
}

/** One of the city buildings, decided by `seed`, fitting in a square of half side `half`. */
export function buildCityBuilding(seed: number, half = CITY_HALF): PropGeometry {
  const random = createRng(seed * 104729 + half * 31 + 7);
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  const windows = pick(random, WINDOWS);
  for (const lot of lots(half, random)) {
    buildLot({ s, l, facade: pick(random, FACADES), windows, random }, lot);
  }
  return { structure: s.geometry, lights: l.geometry };
}

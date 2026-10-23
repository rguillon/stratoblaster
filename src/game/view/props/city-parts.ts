import { createRng, pick, randomIn, type Random } from '../../../core/math/rng';
import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { windowBands } from './city-props';

// Phase 4 review: city buildings assembled from parts (1 to 3 tiers stepping back, a facade
// colour, a window colour, and one of five crowns), so the city centre shows many different
// buildings. Everything stays within X, Z ∈ [-HALF, HALF], standing on Y = 0.

/** Half the side of the square every city building fits in. */
export const CITY_HALF = 9;

type Rgb = readonly [number, number, number];

const FACADES: readonly Rgb[] = [C.glassBlue, C.concrete, C.concreteDark, C.brick, C.white];
const WINDOWS: readonly Rgb[] = [L.windowDim, L.cyanDim, L.pinkDim];

/** Top of the building at its centre, and the size of its top tier. */
interface Top {
  readonly y: number;
  readonly size: number;
}

function crown(s: SolidBuilder, l: SolidBuilder, top: Top, random: Random): void {
  const { y, size } = top;
  const style = Math.floor(random() * 5);
  if (style === 0) {
    s.lathe(
      [
        [size * 0.25, y],
        [0, y + randomIn(random, [8, 16])],
      ],
      4,
      C.metal,
    );
  } else if (style === 1) {
    const h = randomIn(random, [8, 14]);
    s.cylinder(0.4, h, 4, C.metal, { at: [0, y, 0] });
    l.box([1, 1, 1], L.red, { at: [0, y + h, 0] });
  } else if (style === 2) {
    s.lathe(
      [
        [size * 0.7, y],
        [0, y + size * 0.5],
      ],
      4,
      C.roof,
      { yaw: Math.PI / 4 },
    );
  } else if (style === 3) {
    s.cylinder(size * 0.35, 0.6, 8, C.metalDark, { at: [0, y, 0] });
    l.ring(size * 0.36, 0.3, 8, L.yellow, { at: [0, y + 0.4, 0] });
  } else {
    s.box([size * 0.4, 2, size * 0.3], C.metalDark, { at: [-size * 0.2, y, 0] });
    s.box([size * 0.2, 1.4, size * 0.2], C.metal, { at: [size * 0.25, y, size * 0.2] });
  }
}

/**
 * One of the city buildings, decided by `seed`, fitting in a square of half side `half`. Bigger
 * ones (phase 4 review) stand on a low, wide podium that fills their block, with towers on it.
 */
export function buildCityBuilding(seed: number, half = CITY_HALF): PropGeometry {
  const random = createRng(seed * 104729 + 7);
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  const facade = pick(random, FACADES);
  const windows = pick(random, WINDOWS);
  const large = half > CITY_HALF;
  const tiers = large ? 2 + Math.floor(random() * 2) : 1 + Math.floor(random() * 3);
  const base = randomIn(random, [1.2 * half, 2 * half]);
  let size = base;
  let y = 0;
  for (let t = 0; t < tiers; t++) {
    const podium = large && t === 0;
    const height = podium ? randomIn(random, [8, 14]) : randomIn(random, [12, 30]);
    s.box([size, height, size * 0.85], podium ? C.concreteDark : facade, { at: [0, y, 0] }, C.roof);
    windowBands(l, [size, size * 0.85], [y + 3, y + height - 2], 6, 2, windows);
    y += height;
    if (t < tiers - 1)
      size *= podium ? randomIn(random, [0.35, 0.6]) : randomIn(random, [0.6, 0.8]);
  }
  // Now and then a neon sign over the entrance.
  if (random() < 0.5) {
    const sign = pick(random, [L.pinkDim, L.cyanDim]);
    l.box([base * 0.5, 1.6, 0.3], sign, { at: [0, 4, -base * 0.425 - 0.3] });
  }
  crown(s, l, { y, size }, random);
  return { structure: s.geometry, lights: l.geometry };
}

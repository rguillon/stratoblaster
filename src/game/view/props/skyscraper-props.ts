import { createRng, pick, randomIn } from '../../../core/math/rng';
import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { crown, plinth, volume, type LotKit } from './city-lots';

// P10-R08 (reviewer's rework, 2026-10-27): the skyscrapers of World 4's downtown, three to four
// times as tall as the city towers of Level Zero. Everything stays within X, Z ∈ [-half, half],
// on Y = 0.

type Rgb = readonly [number, number, number];

const FACADES: readonly Rgb[] = [C.glassBlue, C.glassDark, C.glassGreen, C.concrete, C.white];
const WINDOWS: readonly Rgb[] = [L.windowDim, L.cyanDim, L.whiteDim, L.yellowDim];
const ROOFS: readonly Rgb[] = [C.roof, C.metal, C.metalDark];
const NEON: readonly Rgb[] = [L.cyan, L.pink, L.red];

/**
 * A skyscraper decided by `seed`, in a square of half side `half`: a base over the whole plot,
 * a shaft of 1 to 3 tiers stepping back, 110 to 170 high, rows of lit windows, sometimes neon
 * lines up two corners, and a spire, a mast, a pyramid or roof units on top.
 */
export function buildSkyscraper(seed: number, half: number): PropGeometry {
  const random = createRng(seed * 7919 + 13);
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder({ openBottoms: true });
  const kit: LotKit = {
    s,
    l,
    facade: pick(random, FACADES),
    windows: pick(random, WINDOWS),
    roof: pick(random, ROOFS),
    random,
  };
  const side = 2 * half - 1;
  let y = plinth(kit, [0, 0, side, side]);
  const tiers = 1 + Math.floor(random() * 3);
  const height = randomIn(random, [110, 170]);
  let width = side * randomIn(random, [0.6, 0.8]);
  for (let t = 0; t < tiers; t++) {
    const h = (height - y) / (tiers - t) + (t < tiers - 1 ? randomIn(random, [-6, 6]) : 0);
    volume(kit, [0, 0, width, width], y, h);
    if (t === 0 && random() < 0.5) {
      const neon = pick(random, NEON);
      for (const c of [-1, 1]) {
        l.box([0.4, h - 4, 0.4], neon, { at: [(c * width) / 2, y + 2, -width / 2] });
      }
    }
    y += h;
    if (t < tiers - 1) width *= randomIn(random, [0.7, 0.85]);
  }
  crown(kit, [0, y, 0], width);
  return { structure: s.geometry, lights: l.geometry };
}

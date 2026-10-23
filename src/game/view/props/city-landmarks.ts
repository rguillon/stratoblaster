import { pick, randomIn } from '../../../core/math/rng';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { crown, plinth, volume, type Lot, type LotKit } from './city-lots';

// Phase 4 review: more kinds of city lots, so the city centre does not repeat itself: twin
// towers with a skybridge, a glass dome, a plaza with trees and a fountain, a parking garage, a
// tower with a slanted top, a tower with a helipad, a roof garden block, a hexagonal tower and a
// stack of twisted blocks.

/** Two slim towers joined by a lit skybridge. */
function twinTowers(kit: LotKit, lot: Lot): void {
  const { random } = kit;
  const [x, z, w, d] = lot;
  const base = plinth(kit, lot);
  const along = w >= d;
  const size = Math.min(along ? w / 2 : d / 2, along ? d : w) * 0.75;
  const h = randomIn(random, [35, 60]);
  const gap = (along ? w : d) / 4;
  for (const k of [-1, 1]) {
    const [tx, tz] = along ? [x + k * gap, z] : [x, z + k * gap];
    volume(kit, [tx, tz, size, size], base, h);
    crown(kit, [tx, base + h, tz], size);
  }
  const bridge = along
    ? ([2 * gap, 2.5, size * 0.4] as const)
    : ([size * 0.4, 2.5, 2 * gap] as const);
  kit.s.box(bridge, C.glassBlue, { at: [x, base + h * 0.6, z] });
  kit.l.box([bridge[0] + 0.2, 0.4, bridge[2] + 0.2], kit.windows, {
    at: [x, base + h * 0.6 + 2.6, z],
  });
}

/** A low drum under a glass dome, with a lit ring. */
function dome(kit: LotKit, lot: Lot): void {
  const { s, l, random } = kit;
  const [x, z, w, d] = lot;
  const base = plinth(kit, lot);
  const r = (Math.min(w, d) / 2) * 0.85;
  const drum = randomIn(random, [4, 10]);
  s.cylinder(r, drum, 10, kit.facade, { at: [x, base, z] });
  const top = base + drum;
  const ring = (k: number): [number, number] => [
    r * Math.cos((Math.PI * k) / 8),
    top + r * 0.8 * Math.sin((Math.PI * k) / 8),
  ];
  s.lathe(
    [ring(0), ring(1), ring(2), ring(3), [0, top + r * 0.8]],
    10,
    pick(random, [C.glassBlue, C.glass, C.metal]),
    { at: [x, 0, z] },
  );
  l.ring(r * 1.02, 0.8, 10, kit.windows, { at: [x, top - 1.2, z] });
}

/** An open plaza: paving, trees, benches and a lit fountain, with a kiosk. */
function plaza(kit: LotKit, [x, z, w, d]: Lot): void {
  const { s, l, random } = kit;
  s.box([w, 0.4, d], pick(random, [C.concrete, C.white, C.brick]), { at: [x, 0, z] });
  const r = Math.min(w, d) * 0.15;
  s.cylinder(r, 0.8, 8, C.concreteDark, { at: [x, 0.4, z] });
  l.ring(r * 0.8, 0.5, 8, L.cyanDim, { at: [x, 0.8, z] });
  for (const [tx, tz] of [
    [-1, -1],
    [1, 1],
  ] as const) {
    const at = [x + tx * w * 0.32, 0.4, z + tz * d * 0.32] as const;
    s.cylinder(0.3, 1.5, 4, C.bark, { at });
    s.lathe(
      [
        [1.8, 1.5],
        [0, 5],
      ],
      6,
      pick(random, [C.leaf, C.leafDark, C.leafLight]),
      { at },
    );
  }
  s.box([3, 3, 3], kit.facade, { at: [x + w * 0.3, 0.4, z] }, kit.roof);
}

/** A parking garage: open decks on posts, with cars on the top deck. */
function parking(kit: LotKit, [x, z, w, d]: Lot): void {
  const { s, random } = kit;
  const decks = 2 + Math.floor(random() * 2);
  for (let k = 0; k < decks; k++) {
    s.box([w * 0.95, 0.6, d * 0.95], C.concrete, { at: [x, k * 3.2, z] });
    if (k > 0) {
      for (const [px, pz] of [
        [-1, -1],
        [1, -1],
        [-1, 1],
        [1, 1],
      ] as const) {
        s.box([0.6, 2.6, 0.6], C.concreteDark, {
          at: [x + px * w * 0.44, (k - 1) * 3.2 + 0.6, z + pz * d * 0.44],
        });
      }
    }
  }
  const top = (decks - 1) * 3.2 + 0.6;
  for (let k = 0; k < 3; k++) {
    const at = [
      x + randomIn(random, [-0.35, 0.35]) * w,
      top,
      z + randomIn(random, [-0.35, 0.35]) * d,
    ] as const;
    s.box([1.6, 1, 3.4], pick(random, [C.containerRed, C.containerBlue, C.white, C.metal]), { at });
  }
}

/** A tower whose top is cut by a slanted glass roof. */
function slantedTower(kit: LotKit, lot: Lot): void {
  const { s, random } = kit;
  const [x, z, w, d] = lot;
  const base = plinth(kit, lot);
  const [tw, td] = [w * randomIn(random, [0.55, 0.8]), d * randomIn(random, [0.55, 0.8])];
  const h = randomIn(random, [30, 60]);
  volume(kit, [x, z, tw, td], base, h);
  const slope = randomIn(random, [0.35, 0.6]);
  s.box([tw, 0.8, td / Math.cos(slope)], C.glassBlue, { at: [x, base + h, z], pitch: slope });
}

/** A tower with a lit helipad on its roof. */
function helipadTower(kit: LotKit, lot: Lot): void {
  const { s, l, random } = kit;
  const [x, z, w, d] = lot;
  const base = plinth(kit, lot);
  const size = Math.min(w, d) * randomIn(random, [0.6, 0.8]);
  const h = randomIn(random, [25, 55]);
  volume(kit, [x, z, size, size], base, h);
  const r = size * 0.4;
  s.cylinder(r, 0.5, 8, C.metalDark, { at: [x, base + h, z] });
  l.ring(r * 0.85, 0.3, 8, L.yellow, { at: [x, base + h + 0.4, z] });
  l.box([0.5, 0.2, r * 0.8], L.yellow, { at: [x - r * 0.25, base + h + 0.55, z] });
  l.box([0.5, 0.2, r * 0.8], L.yellow, { at: [x + r * 0.25, base + h + 0.55, z] });
  l.box([r * 0.5, 0.2, 0.5], L.yellow, { at: [x, base + h + 0.55, z] });
}

/** A mid-rise block with a green roof garden and its trees. */
function roofGarden(kit: LotKit, [x, z, w, d]: Lot): void {
  const { s, random } = kit;
  const h = randomIn(random, [10, 22]);
  volume(kit, [x, z, w * 0.95, d * 0.95], 0, h);
  s.box([w * 0.8, 0.5, d * 0.8], C.leafDark, { at: [x, h, z] });
  for (const k of [-1, 0, 1]) {
    const at = [x + k * w * 0.25, h + 0.5, z + k * d * 0.2] as const;
    s.lathe(
      [
        [1.4, 0],
        [0, 3.5],
      ],
      5,
      pick(random, [C.leaf, C.leafLight]),
      { at },
    );
  }
}

/** A hexagonal tower tapering up, with lit rings. */
function hexTower(kit: LotKit, lot: Lot): void {
  const { s, l, random } = kit;
  const [x, z, w, d] = lot;
  const base = plinth(kit, lot);
  const r = (Math.min(w, d) / 2) * randomIn(random, [0.6, 0.85]);
  const h = randomIn(random, [35, 70]);
  const top = r * randomIn(random, [0.45, 0.75]);
  s.cylinder(r, h, 6, kit.facade, { at: [x, base, z] }, top);
  for (let y = 5; y + 2 < h - 4; y += 10) {
    l.ring(r - ((r - top) * y) / h + 0.15, 1.5, 6, kit.windows, { at: [x, base + y, z] });
  }
  crown(kit, [x, base + h, z], top * 2);
}

/** Blocks stacked with a twist, each one turned from the one below. */
function twisted(kit: LotKit, lot: Lot): void {
  const { s, random } = kit;
  const [x, z, w, d] = lot;
  let y = plinth(kit, lot);
  // Turned blocks must stay in the lot: their diagonal fits its smaller side.
  const size = (Math.min(w, d) / Math.SQRT2) * 0.95;
  const levels = 3 + Math.floor(random() * 3);
  for (let k = 0; k < levels; k++) {
    const h = randomIn(random, [6, 10]);
    const facade = k % 2 === 0 ? kit.facade : pick(random, [C.glassBlue, C.white, C.concreteDark]);
    s.box([size, h, size], facade, { at: [x, y, z], yaw: (k * Math.PI) / 8 }, kit.roof);
    y += h;
  }
  crown(kit, [x, y, z], size * 0.6);
}

/** The extra kinds of lots, and those of them that need a wide lot. */
export const LANDMARK_LOTS = [
  twinTowers,
  dome,
  plaza,
  parking,
  slantedTower,
  helipadTower,
  roofGarden,
  hexTower,
  twisted,
] as const;
export const WIDE_LANDMARKS: readonly ((kit: LotKit, lot: Lot) => void)[] = [twinTowers, dome];

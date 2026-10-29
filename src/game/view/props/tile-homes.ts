import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { any, frontLights, gable, NEON, plot, r, tree, windows, type TileKit } from './tile-kit';

// Phase 15 (P15-R09): the homes made for the grid of tiles: houses with their gardens, terraces,
// flats, workshops, farms and desert homes. See `tile-kit.ts` for the plot.

const WALLS = [C.white, C.farmWall, C.brick, C.concrete] as const;
const ROOFS = [C.roof, C.farmRoof, C.brick, C.metalDark] as const;

/** A house at the front of its plot, a garden with a tree or two behind it. */
export function buildHouse(k: TileKit): void {
  plot(k, C.leafDark);
  const bw = Math.min(k.w - 2, r(k, [6, 8]));
  const bd = Math.min(k.d * 0.6, r(k, [5, 7]));
  const z = -k.d / 2 + bd / 2 + 1;
  const h = r(k, [3.5, 5]);
  k.s.box([bw, h, bd], any(k, WALLS), { at: [0, 0, z] });
  gable(k, [bw, bd], h, r(k, [2, 3]), any(k, ROOFS), [0, z]);
  windows(k, [bw, bd], [1, h - 0.5], L.window, [0, z], 2.5);
  const back = (k.d / 2 + (z + bd / 2)) / 2;
  for (let i = 0; i < Math.max(1, Math.round(k.d / 10)); i++) {
    tree(k, r(k, [-k.w / 3, k.w / 3]), back + r(k, [-1, 1]) * (k.d / 6), r(k, [3, 4.5]));
  }
}

/** A modern villa: two offset flat-roofed slabs, a pool, a lawn. */
export function buildVilla(k: TileKit): void {
  plot(k, C.leaf);
  const [w, d] = [k.w * 0.7, k.d * 0.45];
  k.s.box([w, 4, d], C.white, { at: [-k.w * 0.1, 0, -k.d * 0.2] }, C.roof);
  k.s.box([w * 0.6, 3.5, d * 0.8], C.concreteDark, { at: [k.w * 0.05, 4, -k.d * 0.15] }, C.roof);
  k.s.box([k.w * 0.35, 0.3, k.d * 0.2], C.glassBlue, { at: [k.w * 0.2, 0, k.d * 0.28] });
  k.l.box([k.w * 0.35, 0.1, 0.2], L.cyan, { at: [k.w * 0.2, 0.32, k.d * 0.18] });
  windows(k, [w, d], [1, 3.5], L.window, [-k.w * 0.1, -k.d * 0.2], 2.5);
  tree(k, -k.w * 0.25, k.d * 0.25, Math.min(3.5, k.w * 0.3));
}

/** A small cottage: a low house under a steep roof, a garden round it. */
export function buildCottage(k: TileKit): void {
  plot(k, C.leafDark);
  const s = Math.min(k.w, k.d) * 0.55;
  k.s.box([s, 3, s * 0.8], any(k, [C.farmWall, C.white, C.adobe]), { at: [0, 0, -k.d * 0.12] });
  gable(k, [s, s * 0.8], 3, 3, any(k, [C.thatch, C.farmRoof, C.roof]), [0, -k.d * 0.12]);
  k.l.box([1, 1, 0.2], L.window, { at: [s * 0.25, 1, -k.d * 0.12 - s * 0.4 - 0.1] });
  tree(k, k.w * 0.3, k.d * 0.3, 3);
}

/** A row of terraced houses along the plot's long side, small back yards. */
export function buildTerrace(k: TileKit): void {
  plot(k, C.leafDark);
  const alongZ = k.d > k.w;
  const [len, depth] = alongZ ? [k.d, k.w] : [k.w, k.d];
  const n = Math.max(2, Math.round(len / 4.5));
  const each = len / n;
  const h = r(k, [5, 7]);
  const wall = any(k, [C.brick, C.farmWall, C.concrete]);
  for (let i = 0; i < n; i++) {
    const a = -len / 2 + each * (i + 0.5);
    const hh = h + (i % 2) * 0.4;
    const [x, z] = alongZ ? [-depth * 0.15, a] : [a, -depth * 0.15];
    const [bw, bd] = alongZ ? [depth * 0.65, each - 0.3] : [each - 0.3, depth * 0.65];
    k.s.box([bw, hh, bd], wall, { at: [x, 0, z] });
    gable(k, [bw, bd], hh, 2, C.roof, [x, z], alongZ);
    windows(k, [bw, bd], [1, hh - 0.6], L.window, [x, z], 2.6);
  }
}

/** A block of flats: 3 to 6 floors, a flat roof with its plant, lit windows. */
export function buildFlats(k: TileKit): void {
  plot(k, C.concreteDark);
  const [w, d] = [k.w - 1.5, k.d - 1.5];
  const h = r(k, [10, 18]);
  k.s.box([w, h, d], any(k, [C.brick, C.concrete, C.farmWall]), {}, C.roof);
  k.s.box([w * 0.3, 2, d * 0.3], C.metalDark, { at: [w * 0.2, h, 0] });
  windows(k, [w, d], [1.5, h - 1], any(k, [L.window, L.windowDim]), [0, 0], 3);
  frontLights(k, w, -d / 2, 1.8, any(k, NEON));
}

/** A workshop: a saw-tooth roofed shed, a yard with crates at the front. */
export function buildWorkshop(k: TileKit): void {
  plot(k, C.concreteDark);
  const [w, d] = [k.w - 1, k.d * 0.7];
  const z = (k.d - d) / 2 - 0.5;
  const h = r(k, [5, 7]);
  k.s.box([w, h, d], any(k, [C.brick, C.corrugated, C.metal]), { at: [0, 0, z] });
  const teeth = Math.max(1, Math.round(d / 5));
  for (let i = 0; i < teeth; i++) {
    const tz = z - d / 2 + (d / teeth) * (i + 0.5);
    gable(k, [w, d / teeth], h, 1.6, C.roof, [0, tz]);
  }
  for (let i = 0; i < 3; i++) {
    k.s.box([1.4, 1.2, 1.4], any(k, [C.wood, C.containerBlue, C.rust]), {
      at: [r(k, [-k.w / 3, k.w / 3]), 0, -k.d / 2 + 1.5],
    });
  }
  frontLights(k, w, z - d / 2, h - 1, L.yellowDim);
}

/** A farmhouse with a barn beside it, a vegetable plot. */
export function buildFarmhouse(k: TileKit): void {
  plot(k, C.leaf);
  k.s.box([k.w * 0.4, 4, k.d * 0.35], C.farmWall, { at: [-k.w * 0.22, 0, -k.d * 0.2] });
  gable(k, [k.w * 0.4, k.d * 0.35], 4, 2.5, C.farmRoof, [-k.w * 0.22, -k.d * 0.2]);
  k.l.box([1.2, 1, 0.2], L.window, { at: [-k.w * 0.22, 1.4, -k.d * 0.38] });
  buildShed(k, [k.w * 0.25, k.d * 0.15], [k.w * 0.4, k.d * 0.5]);
  for (let i = 0; i < 4; i++) {
    k.s.box([k.w * 0.4, 0.5, 0.8], C.leafLight, { at: [-k.w * 0.22, 0.2, k.d * 0.15 + i * 1.6] });
  }
}

function buildShed(
  k: TileKit,
  [x, z]: readonly [number, number],
  [w, d]: readonly [number, number],
) {
  k.s.box([w, 5, d], C.containerRed, { at: [x, 0, z] });
  gable(k, [w, d], 5, 3, C.metalDark, [x, z], true);
}

/** A long barn and a pair of silos. */
export function buildBarn(k: TileKit): void {
  plot(k, C.dryLeaf);
  buildShed(k, [-k.w * 0.12, 0], [k.w * 0.6, k.d - 2]);
  k.l.box([2, 2.5, 0.2], L.yellowDim, { at: [-k.w * 0.12, 0, -(k.d - 2) / 2 - 0.1] });
  for (const z of [-k.d * 0.2, k.d * 0.15]) {
    k.s.cylinder(1.8, 9, 8, C.silver, { at: [k.w * 0.32, 0, z] });
    k.s.cylinder(1.8, 1.2, 8, C.metal, { at: [k.w * 0.32, 9, z] }, 0.3);
  }
}

/** Glass greenhouses in rows, lit inside. */
export function buildGreenhouse(k: TileKit): void {
  plot(k, C.leafDark);
  const rows = Math.max(1, Math.round(k.w / 5));
  const each = k.w / rows;
  for (let i = 0; i < rows; i++) {
    const x = -k.w / 2 + each * (i + 0.5);
    k.s.box([each - 1, 2.5, k.d - 1.5], C.glassGreen, { at: [x, 0, 0] });
    gable(k, [each - 1, k.d - 1.5], 2.5, 1.5, C.glassGreen, [x, 0], true);
    k.l.box([0.2, 0.2, k.d - 2], L.toxicDim, { at: [x, 2.4, 0] });
  }
}

/** Adobe homes: flat roofs, parapets, a windcatcher on some, a palm in the yard. */
export function buildAdobe(k: TileKit): void {
  plot(k, C.sand);
  const n = Math.max(1, Math.round((k.w * k.d) / 70));
  for (let i = 0; i < n; i++) {
    const [w, d] = [k.w / Math.min(n, 2) - 1.5, k.d / Math.ceil(n / 2) - 1.5];
    const x = n > 1 ? (i % 2 === 0 ? -1 : 1) * (k.w / 4) : 0;
    const z = n > 2 ? (i < 2 ? -1 : 1) * (k.d / 4) : 0;
    const h = r(k, [3.5, 6]);
    k.s.box([w, h, d], any(k, [C.adobe, C.adobeDark]), { at: [x, 0, z] }, C.adobeRoof);
    k.s.box([w, 0.6, 0.4], C.adobeDark, { at: [x, h, z - d / 2 + 0.2] });
    if (k.random() < 0.5) k.s.box([1.4, 3, 1.4], C.adobeDark, { at: [x + w / 4, h, z] });
    k.l.box([1, 1.4, 0.2], L.window, { at: [x, 1, z - d / 2 - 0.1] });
  }
}

/** A courtyard house: four wings round a yard with a fountain and palms. */
export function buildCourtyard(k: TileKit): void {
  plot(k, C.paving);
  const [w, d, t] = [k.w - 1, k.d - 1, 4];
  for (const [x, z, bw, bd] of [
    [0, -d / 2 + t / 2, w, t],
    [0, d / 2 - t / 2, w, t],
    [-w / 2 + t / 2, 0, t, d - 2 * t],
    [w / 2 - t / 2, 0, t, d - 2 * t],
  ] as const) {
    k.s.box([bw, 5, bd], C.adobe, { at: [x, 0, z] }, C.adobeRoof);
  }
  k.s.cylinder(1.5, 0.8, 8, C.adobeDark, { at: [0, 0, 0] });
  k.l.ring(1.2, 0.3, 8, L.cyan, { at: [0, 0.8, 0] });
  k.l.box([2, 2, 0.2], L.window, { at: [0, 0, -d / 2 - 0.1] });
}

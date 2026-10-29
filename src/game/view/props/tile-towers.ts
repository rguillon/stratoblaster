import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { crown, plinth, volume, type LotKit } from './city-lots';
import { any, NEON, r, windows, type TileKit } from './tile-kit';

// Phase 15 (reviewer, 2026-10-28: "all the skyscrapers look the same"): the silhouettes of the
// city buildings. Each model takes the one its seed names, so the models of a building group
// (which have different seeds) all differ: stepped tiers, a slab with fins, a round tower, twin
// towers and a bridge, a needle set back off-centre, and blocks of two heights side by side.

/** What a silhouette is built with: the plot, the lot colours and the top of the building. */
interface Tower {
  readonly k: TileKit;
  readonly kit: LotKit;
  /** Height of the plinth, where the building starts. */
  readonly base: number;
  readonly top: number;
}

/** Tiers stepping back up to the top, something on top. */
function stepped({ k, kit, base, top }: Tower): void {
  const tiers = 2 + Math.floor(k.random() * 2);
  let [w, d, y] = [k.w * r(k, [0.7, 0.85]), k.d * r(k, [0.7, 0.85]), base];
  for (let t = 0; t < tiers; t++) {
    const h = (top - y) / (tiers - t);
    volume(kit, [0, 0, w, d], y, h);
    y += h;
    [w, d] = [w * r(k, [0.72, 0.88]), d * r(k, [0.72, 0.88])];
  }
  crown(kit, [0, y, 0], Math.min(w, d) * 0.8);
}

/** One flat slab, the full height, ribbed with fins on its long faces. */
function slab({ k, kit, base, top }: Tower): void {
  const [w, d] = [k.w * 0.85, k.d * 0.55];
  volume(kit, [0, 0, w, d], base, top - base);
  const fins = Math.max(3, Math.round(w / 4));
  for (let i = 0; i <= fins; i++) {
    const x = -w / 2 + (i * w) / fins;
    for (const z of [-d / 2, d / 2])
      k.s.box([0.6, top - base, 0.8], C.metalDark, { at: [x, base, z] });
  }
  k.s.box([w * 0.3, 0.4, d * 0.6], C.metal, { at: [0, top, 0] });
  k.l.ring(Math.min(w, d) * 0.2, 0.2, 8, L.yellowDim, { at: [0, top + 0.4, 0] });
}

/** A round tower tapering a little, rings of light up it, and a mast. */
function round({ k, base, top }: Tower): void {
  const radius = Math.min(k.w, k.d) * 0.4;
  const color = any(k, [C.glassBlue, C.glassDark, C.glassGreen, C.white]);
  const sides = 10;
  k.s.cylinder(radius, top - base, sides, color, { at: [0, base, 0] }, radius * r(k, [0.65, 0.9]));
  const light = any(k, NEON);
  const rings = Math.max(2, Math.floor((top - base) / 14));
  for (let i = 1; i <= rings; i++) {
    const y = base + ((top - base) * i) / (rings + 1);
    const at = radius * (1 - ((1 - 0.78) * (y - base)) / (top - base)) + 0.15;
    k.l.ring(at, 0.6, sides, light, { at: [0, y, 0] });
  }
  k.s.cylinder(0.4, top * 0.12, 4, C.metal, { at: [0, top, 0] }, 0.1);
  k.l.box([0.6, 0.6, 0.6], L.red, { at: [0, top * 1.12, 0] });
}

/** Two towers of different heights on the plinth, joined by a lit bridge. */
function twin({ k, kit, base, top }: Tower): void {
  const along = k.w >= k.d;
  const [w, d] = along ? [k.w * 0.36, k.d * 0.7] : [k.w * 0.7, k.d * 0.36];
  const offset = (along ? k.w : k.d) * 0.27;
  const heights = [top, base + (top - base) * r(k, [0.65, 0.85])];
  heights.forEach((h, i) => {
    const c = (i === 0 ? -1 : 1) * offset;
    const [x, z] = along ? [c, 0] : [0, c];
    volume(kit, [x, z, w, d], base, h - base);
    crown(kit, [x, h, z], Math.min(w, d) * 0.7);
  });
  const y = base + ((heights[1] ?? top) - base) * 0.6;
  const span = offset * 2 - (along ? w : d);
  const size: [number, number, number] = along ? [span, 3, d * 0.5] : [w * 0.5, 3, span];
  k.s.box(size, C.metalDark, { at: [0, y, 0] });
  k.l.box([size[0] * 0.9, 0.6, size[2] * 1.05], any(k, NEON), { at: [0, y + 1.2, 0] });
}

/** A narrow shaft set back off-centre over a low wing, with a long spire. */
function needle({ k, kit, base, top }: Tower): void {
  const [w, d] = [k.w * 0.45, k.d * 0.45];
  const [x, z] = [k.w * 0.2, k.d * 0.2];
  volume(kit, [-k.w * 0.15, -k.d * 0.2, k.w * 0.65, k.d * 0.55], base, Math.min(12, top * 0.2));
  const shaft = top * 0.85;
  volume(kit, [x, z, w, d], base, shaft - base);
  k.s.cylinder(Math.min(w, d) * 0.35, top - shaft, 4, kit.roof, { at: [x, shaft, z] }, 0.2);
  k.l.box([0.5, 0.5, 0.5], L.red, { at: [x, top, z] });
}

/** Two blocks side by side, one low and wide, one tall, their colours different. */
function pair({ k, kit, base, top }: Tower): void {
  const low = base + (top - base) * r(k, [0.3, 0.5]);
  volume(kit, [-k.w * 0.2, 0, k.w * 0.55, k.d * 0.85], base, low - base);
  const second = any(k, [C.white, C.concrete, C.glassDark, C.brick]);
  volume(kit, [k.w * 0.25, k.d * 0.1, k.w * 0.45, k.d * 0.6], base, top - base, second);
  crown(kit, [k.w * 0.25, top, k.d * 0.1], Math.min(k.w, k.d) * 0.35);
  windows(k, [k.w * 0.55, k.d * 0.85], [base + 1, low - 1], any(k, NEON), [-k.w * 0.2, 0], 4);
}

const SILHOUETTES = [stepped, slab, round, twin, needle, pair] as const;

/** Number of silhouettes: seeds 1 to this give different buildings. */
export const SILHOUETTE_COUNT = SILHOUETTES.length;

/**
 * Phase 15 (reviewer, 2026-10-28): what makes a building differ from each side: a lower annex
 * against one side, off-centre, and a dark fin up one corner past the top.
 */
function asymmetry({ k, kit, base, top }: Tower): void {
  const side = Math.floor(k.random() * 4);
  const alongX = side % 2 === 0;
  const [len, deep] = alongX
    ? [k.w * r(k, [0.4, 0.6]), k.d * 0.3]
    : [k.d * r(k, [0.4, 0.6]), k.w * 0.3];
  // Inset, so the lights on its faces stay inside the plot.
  const inset = 0.5;
  const shift = r(k, [-0.2, 0.2]) * (alongX ? k.w : k.d);
  const out = side < 2 ? -1 : 1;
  const [x, z] = alongX
    ? [shift, out * (k.d / 2 - deep / 2 - inset)]
    : [out * (k.w / 2 - deep / 2 - inset), shift];
  const [w, d] = alongX ? [len, deep] : [deep, len];
  volume(kit, [x, z, w, d], base, (top - base) * r(k, [0.2, 0.4]));
  const [cx, cz] = [
    (k.random() < 0.5 ? -1 : 1) * k.w * 0.32,
    (k.random() < 0.5 ? -1 : 1) * k.d * 0.32,
  ];
  k.s.box([0.8, top * 1.08 - base, 0.8], C.metalDark, { at: [cx, base, cz] });
}

/**
 * A city building up to a height in `height`, of the silhouette its seed names; with
 * `asymmetric`, an annex and a fin make it differ from each side.
 */
export function cityBuilding(
  k: TileKit,
  kit: LotKit,
  height: readonly [number, number],
  asymmetric = false,
): void {
  const base = plinth(kit, [0, 0, k.w, k.d]);
  // A lit strip along the front of the plinth, inside the plot, so every building shows at night.
  k.l.box([k.w * 0.6, 0.3, 0.4], L.window, { at: [0, base, -k.d / 2 + 0.4] });
  const build = SILHOUETTES[(k.seed - 1) % SILHOUETTES.length] ?? stepped;
  const tower = { k, kit, base, top: r(k, height) };
  build(tower);
  if (asymmetric) asymmetry(tower);
}

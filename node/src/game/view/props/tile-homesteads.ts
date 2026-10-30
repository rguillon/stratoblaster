import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { deck } from './tile-residences';
import { any, NEON, r, type Rgb, type TileKit } from './tile-kit';

// Phase 15 (reviewer, 2026-10-28: the villages and the worker homes as one, reworked as the
// terraces and suburbs were): small homes of the future on paved plots, no garden, no tile roof.
// Each model takes the silhouette its seed names: a capsule, a dome, stacked cubes, stacked
// containers, a lit grow tower and a home beside a solar shed.

const SHELLS: readonly Rgb[] = [C.white, C.silver, C.panel, C.concrete];
const GLASS: readonly Rgb[] = [C.glassBlue, C.glassDark, C.glass];

/** A capsule lying on its side on two cradles, along the plot's long side, lit along it. */
function capsule(k: TileKit): void {
  const along = k.w >= k.d;
  const [len, across] = along ? [k.w * 0.8, k.d] : [k.d * 0.8, k.w];
  const radius = Math.min(2.2, across * 0.3);
  // Built along X, then turned a quarter round when the plot is long along Z.
  const yaw = along ? 0 : -Math.PI / 2;
  const at = (x: number, y: number, z: number): [number, number, number] =>
    along ? [x, y, z] : [-z, y, x];
  const y = radius + 0.6;
  k.s.cylinder(radius, len, 10, any(k, SHELLS), { at: at(len / 2, y, 0), roll: Math.PI / 2, yaw });
  for (const c of [-0.3, 0.3])
    k.s.box([0.6, 0.8, radius * 1.6], C.metalDark, { at: at(c * len, 0, 0), yaw });
  k.l.box([len * 0.7, 0.3, 0.2], any(k, NEON), { at: at(0, y, -radius - 0.05), yaw });
}

/** A low dome on a ring wall, a mast with a red light. */
function dome(k: TileKit): void {
  const radius = Math.min(k.w, k.d) * 0.4;
  k.s.cylinder(radius, 1.5, 12, any(k, SHELLS));
  k.s.lathe(
    [
      [radius, 1.5],
      [radius * 0.75, 1.5 + radius * 0.6],
      [0, 1.5 + radius * 0.8],
    ],
    12,
    any(k, [C.white, C.silver, ...GLASS]),
  );
  k.l.ring(radius + 0.1, 0.2, 12, any(k, NEON), { at: [0, 1.2, 0] });
  k.s.box([0.2, 3, 0.2], C.metal, { at: [radius * 0.5, 1.5 + radius * 0.5, 0] });
  k.l.box([0.4, 0.4, 0.4], L.red, { at: [radius * 0.5, 4.5 + radius * 0.5, 0] });
}

/** Two or three cubes stacked off each other, glass on their fronts. */
function cubes(k: TileKit): void {
  const s = Math.min(k.w, k.d) * 0.45;
  const n = 2 + Math.floor(k.random() * 2);
  for (let i = 0; i < n; i++) {
    const [x, z] = [((i % 2) - 0.5) * s * 0.6, (i - 1) * s * 0.25];
    k.s.box([s, s * 0.6, s], any(k, SHELLS), { at: [x, i * s * 0.6, z] }, C.metalDark);
    k.s.box([s * 0.7, s * 0.35, 0.15], any(k, GLASS), {
      at: [x, i * s * 0.6 + s * 0.12, z - s / 2 - 0.05],
    });
  }
  k.l.box([s * 0.6, 0.15, 0.15], L.window, { at: [0, n * s * 0.6, 0] });
}

/** Containers stacked crosswise as a home, a lit door. */
function containers(k: TileKit): void {
  const [w, d] = [Math.min(k.w * 0.85, 12), Math.min(k.d * 0.5, 2.6)];
  const colors = [C.containerRed, C.containerBlue, C.silver, C.white];
  k.s.box([w, 2.6, d], any(k, colors), { at: [0, 0, -d * 0.3] });
  k.s.box([d, 2.6, Math.min(k.d * 0.85, w)], any(k, colors), { at: [w * 0.2, 2.6, 0] });
  k.l.box([1, 2, 0.15], L.window, { at: [-w * 0.3, 0, -d * 0.8 - 0.1] });
  k.l.box([0.15, 0.15, Math.min(k.d * 0.8, w)], any(k, NEON), { at: [w * 0.2 - d / 2, 5.1, 0] });
}

/** A glass grow tower lit from inside, a small home at its foot. */
function growTower(k: TileKit): void {
  const s = Math.min(k.w, k.d) * 0.35;
  const h = r(k, [8, 11]);
  k.s.box([s, h, s], C.glassBlue, { at: [k.w * 0.2, 0, k.d * 0.1] }, C.metalDark);
  for (let y = 1.5; y < h; y += 2)
    k.l.box([s * 1.02, 0.2, s * 1.02], L.violet, { at: [k.w * 0.2, y, k.d * 0.1] });
  k.s.box(
    [k.w * 0.4, 3, k.d * 0.4],
    any(k, SHELLS),
    { at: [-k.w * 0.2, 0, -k.d * 0.15] },
    C.metalDark,
  );
  k.l.box([k.w * 0.3, 0.8, 0.15], L.window, { at: [-k.w * 0.2, 1.2, -k.d * 0.35 - 0.05] });
}

/** A flat-roofed home beside a shed under tilted solar panels. */
function solarShed(k: TileKit): void {
  const along = k.w >= k.d;
  const [a, b] = along ? [-k.w * 0.22, k.w * 0.25] : [-k.d * 0.22, k.d * 0.25];
  const at = (c: number): [number, number, number] => (along ? [c, 0, 0] : [0, 0, c]);
  const [hw, hd] = along ? [k.w * 0.4, k.d * 0.6] : [k.w * 0.6, k.d * 0.4];
  k.s.box([hw, 3.4, hd], any(k, SHELLS), { at: at(a) }, C.metalDark);
  k.l.box([hw * 0.7, 0.8, 0.15], L.window, { at: [at(a)[0], 1.3, at(a)[2] - hd / 2 - 0.05] });
  k.s.box([hw * 0.8, 2.4, hd * 0.8], C.metalDark, { at: at(b) });
  k.s.box([hw * 0.9, 0.12, hd * 0.9], C.solar, { at: [at(b)[0], 3, at(b)[2]], pitch: -0.4 });
}

const SILHOUETTES = [capsule, dome, cubes, containers, growTower, solarShed] as const;

/** A small home of the villages and the worker homes, of the silhouette its seed names. */
export function buildHomestead(k: TileKit): void {
  deck(k);
  const build = SILHOUETTES[(k.seed - 1) % SILHOUETTES.length] ?? dome;
  build(k);
}

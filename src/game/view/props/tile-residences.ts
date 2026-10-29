import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { any, NEON, plot, r, windows, type Rgb, type TileKit } from './tile-kit';

// Phase 15 (reviewer, 2026-10-28: "gather the terraces and suburbs into the same category, remove
// the green, make it more diverse, this is the future, no need for tile roofs"): the homes of the
// residential districts, on paved plots, flat or metal roofed. Each model takes the silhouette its
// seed names, so a group's models all differ: cantilevered slabs, pods, a row of modules under
// solar panels, stepped terraces, a house on stilts and a wedge under a sloping metal roof.

const SHELLS: readonly Rgb[] = [C.white, C.silver, C.panel, C.concrete];
const GLASS: readonly Rgb[] = [C.glassBlue, C.glassDark, C.glass];
const DECKS: readonly Rgb[] = [C.concrete, C.concreteDark, C.metalDark];

/** The paved plot, a lit strip along the path to the door at the front. */
export function deck(k: TileKit): void {
  plot(k, any(k, DECKS));
  k.l.box([0.3, 0.05, k.d * 0.3], any(k, NEON), { at: [k.w * 0.3, 0.2, -k.d * 0.3] });
}

/** Two slabs, the upper one turned across the lower and overhanging it, lit underneath. */
function cantilever(k: TileKit): void {
  const [w, d] = [k.w * 0.7, k.d * 0.55];
  const shell = any(k, SHELLS);
  k.s.box([w, 3.5, d], shell, { at: [-k.w * 0.1, 0, -k.d * 0.1] }, C.metalDark);
  k.s.box([w * 0.75, 0.6, d * 1.4], any(k, GLASS), { at: [k.w * 0.05, 3.5, 0] });
  k.s.box([w * 0.8, 3, d * 1.5], shell, { at: [k.w * 0.08, 4.1, 0] }, C.metalDark);
  k.l.box([w * 0.7, 0.15, 0.3], any(k, NEON), { at: [k.w * 0.08, 4, -d * 0.75] });
  windows(k, [w * 0.8, d * 1.5], [4.6, 6.6], L.window, [k.w * 0.08, 0], 2.5);
}

/** One or two round pods under domes, a ring of light round each. */
function pods(k: TileKit): void {
  const long = Math.max(k.w, k.d) > Math.min(k.w, k.d) * 1.5;
  const radius = Math.min(k.w, k.d) * 0.38;
  const shell = any(k, SHELLS);
  const light = any(k, NEON);
  const spots: [number, number][] = long
    ? k.w > k.d
      ? [
          [-k.w * 0.25, 0],
          [k.w * 0.25, 0],
        ]
      : [
          [0, -k.d * 0.25],
          [0, k.d * 0.25],
        ]
    : [[0, 0]];
  spots.forEach(([x, z], i) => {
    const h = 3 + i * 1.5;
    k.s.cylinder(radius, h, 12, shell, { at: [x, 0, z] });
    k.s.lathe(
      [
        [radius, h],
        [radius * 0.8, h + radius * 0.45],
        [0, h + radius * 0.65],
      ],
      12,
      any(k, GLASS),
      { at: [x, 0, z] },
    );
    k.l.ring(radius + 0.1, 0.25, 12, light, { at: [x, h - 0.6, z] });
  });
}

/** A row of modules of different heights along the long side, solar panels tilted on top. */
function modules(k: TileKit): void {
  const alongZ = k.d > k.w;
  const [len, depth] = alongZ ? [k.d, k.w] : [k.w, k.d];
  const n = Math.max(2, Math.round(len / 5));
  const each = len / n;
  for (let i = 0; i < n; i++) {
    const a = -len / 2 + each * (i + 0.5);
    const h = r(k, [4, 7.5]);
    const [x, z] = alongZ ? [0, a] : [a, 0];
    const [bw, bd] = alongZ ? [depth * 0.7, each - 0.6] : [each - 0.6, depth * 0.7];
    k.s.box([bw, h, bd], any(k, SHELLS), { at: [x, 0, z] }, C.metalDark);
    k.s.box([bw * 0.8, 0.12, bd * 0.8], C.solar, {
      at: [x, h + 0.5, z],
      ...(alongZ ? { roll: 0.35 } : { pitch: -0.35 }),
    });
    windows(k, [bw, bd], [1, h - 0.8], i % 2 === 0 ? L.window : any(k, NEON), [x, z], 2.4);
  }
}

/** Terraces stepping back and up, a lit band along each step's edge. */
function stepped(k: TileKit): void {
  const steps = 3;
  const light = any(k, NEON);
  const shell = any(k, SHELLS);
  for (let i = 0; i < steps; i++) {
    const [w, d] = [k.w * (0.85 - i * 0.2), k.d * (0.8 - i * 0.18)];
    const z = i * k.d * 0.08;
    k.s.box([w, 2.8, d], shell, { at: [0, i * 2.8, z] }, C.concreteDark);
    k.l.box([w * 0.9, 0.15, 0.2], light, { at: [0, (i + 1) * 2.8, z - d / 2 - 0.1] });
    k.s.box([w * 0.9, 1.4, 0.2], any(k, GLASS), { at: [0, i * 2.8 + 0.8, z - d / 2 - 0.05] });
  }
}

/** A glass-fronted box raised on thin legs, a car port under it. */
function stilts(k: TileKit): void {
  const [w, d] = [k.w * 0.8, k.d * 0.6];
  const lift = 3;
  for (const [sx, sz] of [
    [-1, -1],
    [1, -1],
    [-1, 1],
    [1, 1],
  ] as const) {
    k.s.box([0.35, lift, 0.35], C.metal, { at: [(sx * w) / 2.3, 0, (sz * d) / 2.3] });
  }
  k.s.box([w, 3.5, d], any(k, SHELLS), { at: [0, lift, 0] }, C.metalDark);
  k.s.box([w * 0.85, 2.4, 0.2], any(k, GLASS), { at: [0, lift + 0.5, -d / 2 - 0.05] });
  k.l.box([w * 0.8, 0.12, 0.12], L.window, { at: [0, lift + 2.95, -d / 2 - 0.15] });
  k.s.box([2, 1.1, 3.6], any(k, [C.containerRed, C.containerBlue, C.silver]), {
    at: [w * 0.15, 0, 0],
  });
  k.l.box([w * 0.6, 0.1, d * 0.6], any(k, NEON), { at: [0, lift - 0.15, 0] });
}

/** A wedge: a block under one metal roof sloping from the back down to the front, glazed end. */
function wedge(k: TileKit): void {
  const [w, d] = [k.w * 0.8, k.d * 0.7];
  const [low, high] = [3, r(k, [6, 8])];
  const shell = any(k, SHELLS);
  k.s.box([w, low, d], shell);
  const roof = C.metalDark;
  const [x0, x1, z0, z1] = [-w / 2, w / 2, -d / 2, d / 2];
  k.s.face(
    [
      [x0, low, z0],
      [x0, high, z1],
      [x1, high, z1],
      [x1, low, z0],
    ],
    roof,
  );
  k.s.face(
    [
      [x0, low, z1],
      [x0, high, z1],
      [x0, low, z0],
    ],
    shell,
  );
  k.s.face(
    [
      [x1, low, z0],
      [x1, high, z1],
      [x1, low, z1],
    ],
    shell,
  );
  k.s.box([w, high - low, 0.2], any(k, GLASS), { at: [0, low, z1 - 0.1] });
  k.l.box([w * 0.9, 0.2, 0.2], any(k, NEON), { at: [0, low - 0.1, z0 - 0.15] });
  windows(k, [w, d], [1, low - 0.5], L.window, [0, 0], 2.5);
}

const SILHOUETTES = [cantilever, pods, modules, stepped, stilts, wedge] as const;

/** Number of silhouettes: seeds 1 to this give different homes. */
export const RESIDENCE_COUNT = SILHOUETTES.length;

/** A home of the residential districts, of the silhouette its seed names, on a paved plot. */
export function buildResidence(k: TileKit): void {
  deck(k);
  const build = SILHOUETTES[(k.seed - 1) % SILHOUETTES.length] ?? cantilever;
  build(k);
}

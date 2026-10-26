import type { OutlinePoint } from '../../../../render/geometry/outline';
import { ENEMY_LOOK } from '../../../config/enemy-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { decal, SIDES } from '../../enemies/enemy-shapes';
import { DECK_TOP, EMERALD, JUNGLE, MAGENTA } from './verdant-crown-garden';
import { rect } from './verdant-crown-parts';

// P09-R09, 3-5: the Verdant Crown's city round its dome: overgrown towers with lit windows, moss
// on their roofs and vines climbing them, moss patches and vines across the deck. Model space:
// logical pixels, nose +Z (down the screen), Y up towards the camera.
type Rgb = readonly [number, number, number];

const H = ENEMY_LOOK.hull;

/** A tower: where (model x, z, right half, mirrored), its footprint and height. */
const TOWERS = [
  [22, 66, 9, 8, 12],
  [44, 30, 8, 9, 17],
  [52, -4, 8, 10, 11],
  [40, -68, 9, 8, 15],
  [18, -76, 7, 7, 9],
  [20, -40, 7, 8, 19],
  [56, 20, 6, 6, 8],
] as const;
/** Moss patches on the deck (right half, mirrored): centre, width, length. */
const MOSS = [
  [14, 58, 10, 7],
  [36, -18, 8, 6],
  [8, -66, 7, 9],
  [50, 8, 6, 8],
] as const;
/** Vines crawling over the deck, as chains of points (right half, mirrored). */
const VINES: readonly (readonly OutlinePoint[])[] = [
  [
    [60, -12],
    [54, -18],
    [44, -16],
    [36, -22],
  ],
  [
    [4, 40],
    [12, 46],
    [18, 40],
  ],
];
const WINDOW = { w: 1.4, h: 1.2, rows: 4 } as const;

type Tower = readonly [x: number, z: number, w: number, d: number, h: number];

/**
 * Lit panes down the front of a tower (its front at `tz + td / 2`, sloping back by its chamfer of
 * 1 as it rises), a few dark.
 */
function windows({ neon }: EnemyParts, [tx, tz, tw, td, th]: Tower, lit: Rgb): void {
  const cols = Math.max(1, Math.floor((tw - 2) / 2.4));
  const rows = Math.floor((th - 2) / WINDOW.rows);
  const pane = (x: number, y: number): [number, number, number] => [
    x,
    y,
    tz + td / 2 - (y - DECK_TOP) / th + 0.12,
  ];
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if ((r * 5 + c * 3 + Math.round(tx)) % 4 === 0) continue;
      const cx = tx + (c - (cols - 1) / 2) * 2.4;
      const [a, b] = [cx - WINDOW.w / 2, cx + WINDOW.w / 2];
      const y = DECK_TOP + 2 + r * WINDOW.rows;
      neon.face([pane(a, y), pane(b, y), pane(b, y + WINDOW.h), pane(a, y + WINDOW.h)], lit);
    }
  }
}

/** An overgrown tower: a chamfered block, its lit windows, moss on its roof, a vine up its side. */
function tower(p: EnemyParts, t: Tower, i: number): void {
  const [x, z, w, d, h] = t;
  const top = DECK_TOP + h;
  p.hull.bevelSlab(rect(w, d, [x, z]), [DECK_TOP - 1, DECK_TOP, top], [0, 1], H.panel, {}, H.base);
  p.hull.bevelSlab(rect(w - 2.4, d - 2.4, [x, z]), [top, top, top + 0.8], [0, 0.6], JUNGLE.moss);
  windows(p, t, i % 2 === 0 ? EMERALD : MAGENTA);
  const side = x > 0 ? 1 : -1;
  p.hull.box([0.8, h * 0.8, 1.2], JUNGLE.leaf, { at: [x + side * (w / 2 - 0.2), DECK_TOP, z] });
}

/** A vine crawling over the deck through `points`, leaves along it. */
function vine({ hull }: EnemyParts, points: readonly OutlinePoint[]): void {
  points.slice(1).forEach(([bx, bz], k) => {
    const [ax, az] = points[k] ?? [bx, bz];
    const [dx, dz] = [bx - ax, bz - az];
    const at: [number, number, number] = [ax, DECK_TOP, az];
    hull.box([0.9, 0.7, Math.hypot(dx, dz)], JUNGLE.leaf, {
      at: [(ax + bx) / 2, DECK_TOP, (az + bz) / 2],
      yaw: Math.atan2(dx, dz),
    });
    hull.box([2, 0.4, 1.4], JUNGLE.moss, { at, yaw: k });
  });
}

/** The city round the dome (P09-R09): towers, moss and vines, on both sides of the deck. */
export function drawCity(p: EnemyParts): void {
  for (const s of SIDES) {
    TOWERS.forEach(([x, z, w, d, h], i) => {
      tower(p, [s * x, z, w, d, h], i + (s > 0 ? 0 : 1));
    });
    for (const [x, z, w, d] of MOSS)
      decal(p.hull, rect(w, d, [s * x, z]), DECK_TOP + 0.05, JUNGLE.moss);
    for (const points of VINES)
      vine(
        p,
        points.map(([x, z]): OutlinePoint => [s * x, z]),
      );
  }
}

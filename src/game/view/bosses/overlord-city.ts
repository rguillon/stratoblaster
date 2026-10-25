import type { OutlinePoint } from '../../../render/geometry/outline';
import type { SolidBuilder } from '../../../render/geometry/solids';
import { BOSS_LOOK } from '../../config/boss-look';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { decal, flipX } from '../enemies/enemy-shapes';

// P07-R05: the Overlord's city: towers standing on its deck, lit windows, neon edges. Model
// space: logical pixels, nose +Z (down the screen), Y up towards the camera.
const H = ENEMY_LOOK.hull;
const WHITE = [1, 1, 1] as const;
/** Purple: the boss's neon (GD-61). */
export const OVERLORD_NEON = BOSS_LOOK.neon.overlord ?? WHITE;
/** Heights of the deck's top and of the raised boulevard along its middle. */
export const OVERLORD_DECK = { top: 6, boulevard: 10 } as const;

type Rgb = readonly [number, number, number];

/** A rectangle `w` wide and `d` long around (x, z). */
export function box2d(w: number, d: number, [x, z]: OutlinePoint = [0, 0]): OutlinePoint[] {
  return [
    [x - w / 2, z - d / 2],
    [x + w / 2, z - d / 2],
    [x + w / 2, z + d / 2],
    [x - w / 2, z + d / 2],
  ];
}

/**
 * A symmetric outline from its right half (x > 0, from the front to the tail), closed across
 * the nose at `nose` on the axis.
 */
export function symmetric(half: readonly OutlinePoint[], nose?: number): OutlinePoint[] {
  const tip: OutlinePoint[] = nose === undefined ? [] : [[0, nose]];
  return [...tip, ...half, ...flipX(half).reverse()];
}

/**
 * Neon walls along the edges `edges` of `outline` (edge i from point i to the next), from `y0`
 * to `y1`, stood `lift` outside the outline: lit edges with nothing hidden inside the hull.
 */
export function edgeLights(
  neon: SolidBuilder,
  outline: readonly OutlinePoint[],
  edges: readonly number[],
  [y0, y1]: readonly [number, number],
  color: Rgb,
  lift = 0.35,
): void {
  const area = outline.reduce((sum, [x1, z1], i) => {
    const [x2, z2] = outline[(i + 1) % outline.length] ?? [x1, z1];
    return sum + x1 * z2 - x2 * z1;
  }, 0);
  // Counter-clockwise in (x, z), the outside is on the right of each edge, (dz, -dx).
  const out = area > 0 ? 1 : -1;
  for (const i of edges) {
    const [px, pz] = outline[i] ?? [0, 0];
    const [qx, qz] = outline[(i + 1) % outline.length] ?? [px, pz];
    const length = Math.hypot(qx - px, qz - pz) || 1;
    const [nx, nz] = [(out * lift * (qz - pz)) / length, (-out * lift * (qx - px)) / length];
    const [a, b] =
      out > 0
        ? [
            [px, pz],
            [qx, qz],
          ]
        : [
            [qx, qz],
            [px, pz],
          ];
    const at = (p: readonly number[], y: number): [number, number, number] => [
      (p[0] ?? 0) + nx,
      y,
      (p[1] ?? 0) + nz,
    ];
    neon.face([at(a, y0), at(a, y1), at(b, y1), at(b, y0)], color);
  }
}

/** A tower of the city: where (right side, mirrored left), its footprint and height. */
interface Tower {
  readonly x: number;
  readonly z: number;
  readonly w: number;
  readonly d: number;
  readonly h: number;
  readonly antenna?: boolean;
}

const TOWERS: readonly Tower[] = [
  { x: 50, z: 6, w: 10, d: 14, h: 14 },
  { x: 37, z: 9, w: 8, d: 8, h: 23, antenna: true },
  { x: 56, z: -8, w: 8, d: 8, h: 18, antenna: true },
  { x: 35, z: -53, w: 9, d: 6, h: 10 },
  { x: 44, z: -49, w: 6, d: 6, h: 14 },
  { x: 51, z: 26, w: 6, d: 8, h: 9 },
  { x: 24, z: 54, w: 8, d: 6, h: 7 },
];
/** How far the towers' tops are inset (their chamfer). */
const TOWER_INSET = 1.2;

/** A tower: a chamfered block, rows of lit windows on its front, a lit roof edge, an antenna. */
function drawTower({ hull, neon }: EnemyParts, { x, z, w, d, h, antenna }: Tower): void {
  const base = OVERLORD_DECK.top;
  const footprint = box2d(w, d, [x, z]);
  hull.bevelSlab(footprint, [base - 1, base, base + h], [0, TOWER_INSET], H.panel, {}, H.base);
  const rows = Math.floor(h / 6);
  for (let k = 1; k <= rows; k++) {
    const t = k / (rows + 1);
    // The front slopes back by the inset as it rises: the windows follow it.
    const front = z + d / 2 - TOWER_INSET * t + 0.15;
    neon.box([w * 0.6, 1, 0.4], OVERLORD_NEON, { at: [x, base + h * t, front] });
  }
  const roof = box2d(w - 2 * TOWER_INSET - 1, 1, [x, z + d / 2 - 2]);
  decal(neon, roof, base + h + 0.05, OVERLORD_NEON);
  if (antenna) {
    hull.cylinder(0.8, 9, 4, H.dark, { at: [x, base + h, z - 1] }, 0.3);
    neon.box([1.2, 1.2, 1.2], OVERLORD_NEON, { at: [x, base + h + 8.5, z - 1] });
  }
}

/** Lit windows (neon strips) along the boulevard, in front of and behind the citadel. */
const STREETS: readonly OutlinePoint[][] = [
  box2d(1.2, 12, [8, 42]),
  box2d(1.2, 26, [13, -39]),
  box2d(1.2, 20, [20, -36]),
];

/** P07-R05: the city on the Overlord's deck, mirrored on both sides. */
export function drawCity(parts: EnemyParts): void {
  for (const tower of TOWERS) {
    drawTower(parts, tower);
    drawTower(parts, { ...tower, x: -tower.x });
  }
  for (const street of STREETS) {
    const y = OVERLORD_DECK.boulevard + 0.04;
    decal(parts.neon, street, y, OVERLORD_NEON);
    decal(parts.neon, flipX(street), y, OVERLORD_NEON);
  }
}

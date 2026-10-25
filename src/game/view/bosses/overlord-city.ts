import type { OutlinePoint } from '../../../render/geometry/outline';
import type { SolidBuilder } from '../../../render/geometry/solids';
import { BOSS_LOOK } from '../../config/boss-look';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { decal, flipX } from '../enemies/enemy-shapes';

// P07-R05: the Overlord's city: shared shapes, towers standing on its deck with lit windows and
// rooftop clutter, neon edges. Model space: logical pixels, nose +Z (down the screen), Y up
// towards the camera; +X is the screen's left.
const H = ENEMY_LOOK.hull;
const WHITE = [1, 1, 1] as const;
/** Purple: the boss's neon (GD-61). */
export const OVERLORD_NEON = BOSS_LOOK.neon.overlord ?? WHITE;
/** Heights of the deck's top and of the raised boulevard along its middle. */
export const OVERLORD_DECK = { top: 6, boulevard: 10 } as const;

type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

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

/** What stands on a tower's roof: air-conditioning boxes, a water tank, an aerial mast. */
export type Roof = 'ac' | 'tank' | 'mast';

/** A tower of the city: where, its footprint and height, a narrower tier on top, its roof. */
export interface Tower {
  readonly x: number;
  readonly z: number;
  readonly w: number;
  readonly d: number;
  readonly h: number;
  /** A setback tier on top: its width, depth and height. */
  readonly tier?: readonly [number, number, number];
  readonly roof?: Roof;
}

/** How far the towers' tops are inset (their chamfer). */
const TOWER_INSET = 1.2;
const WINDOW = { w: 1.3, h: 1.1, rows: 4.2 } as const;

/**
 * Lit windows on the front of a block `w` wide standing at (x, base, z + d / 2), `h` high, its
 * front sloping back by the inset as it rises: a grid of panes, a few dark.
 */
function frontWindows(neon: SolidBuilder, [x, base, front]: Vec3, w: number, h: number): void {
  const cols = Math.max(1, Math.floor((w - 2) / 2.2));
  const rows = Math.floor((h - 1) / WINDOW.rows);
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if ((r * 7 + c * 3 + Math.round(x)) % 5 === 0) continue;
      const cx = x + (c - (cols - 1) / 2) * 2.2;
      const pane = (dx: number, y: number): Vec3 => {
        const t = (y - base) / h;
        return [cx + dx, y, front - TOWER_INSET * t + 0.12];
      };
      const y0 = base + 2 + r * WINDOW.rows;
      const [a, b] = [-WINDOW.w / 2, WINDOW.w / 2];
      const corners = [pane(a, y0), pane(b, y0), pane(b, y0 + WINDOW.h), pane(a, y0 + WINDOW.h)];
      neon.face(corners, OVERLORD_NEON);
    }
  }
}

/** The clutter on a roof at height `y` around (x, z). */
function drawRoof({ hull, neon, charge }: EnemyParts, roof: Roof, [x, y, z]: Vec3): void {
  if (roof === 'ac') {
    hull.box([2.2, 1.2, 2], H.base, { at: [x - 1.4, y, z - 0.6] }, H.panel);
    hull.box([1.6, 1, 1.6], H.base, { at: [x + 1.5, y, z + 0.4] }, H.panel);
    decal(hull, box2d(1.4, 1.2, [x - 1.4, z - 0.6]), y + 1.25, H.dark);
  } else if (roof === 'tank') {
    hull.cylinder(1.8, 2.6, 6, H.panel, { at: [x, y, z] }, 1.5);
    neon.ring(1.85, 0.4, 6, OVERLORD_NEON, { at: [x, y + 1.2, z] });
  } else {
    hull.cylinder(0.7, 10, 4, H.dark, { at: [x, y, z] }, 0.25);
    charge.box([1.1, 1.1, 1.1], WHITE, { at: [x, y + 9.6, z] });
  }
}

/** A tower: a chamfered block, lit windows on its front, a lit roof edge, a tier and its roof. */
export function drawTower(parts: EnemyParts, { x, z, w, d, h, tier, roof }: Tower): void {
  const { hull, neon } = parts;
  const base = OVERLORD_DECK.top;
  hull.bevelSlab(
    box2d(w, d, [x, z]),
    [base - 1, base, base + h],
    [0, TOWER_INSET],
    H.panel,
    {},
    H.base,
  );
  frontWindows(neon, [x, base, z + d / 2], w, h);
  let top = base + h;
  if (tier) {
    const [tw, td, th] = tier;
    hull.bevelSlab(
      box2d(tw, td, [x, z - 0.5]),
      [top, top, top + th],
      [0, 0.8],
      H.base,
      {},
      H.panel,
    );
    frontWindows(neon, [x, top, z - 0.5 + td / 2], tw, th);
    top += th;
  } else {
    decal(neon, box2d(w - 2 * TOWER_INSET - 1, 0.8, [x, z + d / 2 - 2]), top + 0.05, OVERLORD_NEON);
  }
  if (roof) drawRoof(parts, roof, [x, top, z - 0.5]);
}

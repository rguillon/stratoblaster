import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { decal } from '../enemies/enemy-shapes';
import { box2d, drawTower, OVERLORD_DECK, OVERLORD_NEON, type Tower } from './overlord-city';

// P07-R05 (phase 7 review: more detail, not symmetrical): the Overlord's skyline, a different
// city on each side of the boulevard. A broadcast spire and a neon billboard on the left (+X,
// the screen's left), the command tower on the right. Model space: logical pixels, nose +Z, Y up.
const H = ENEMY_LOOK.hull;
const WHITE = [1, 1, 1] as const;
const N = OVERLORD_NEON;

type Vec3 = [number, number, number];
/** A rectangle on the billboard's face: x0, y0, x1, y1. */
type Rect = readonly [number, number, number, number];

/** The towers, left and right: none mirrored, kept off the wing roots (|x| ≤ 54). */
const TOWERS: readonly Tower[] = [
  // Left (+X).
  { x: 35, z: -9, w: 7, d: 8, h: 19, roof: 'mast' },
  { x: 50, z: 7, w: 7, d: 10, h: 12, roof: 'ac' },
  { x: 51, z: 24, w: 6, d: 6, h: 8, roof: 'tank' },
  { x: 31, z: -53, w: 8, d: 6, h: 13, tier: [5, 3.5, 5] },
  { x: 42, z: -51, w: 6, d: 6, h: 8, roof: 'ac' },
  { x: 22, z: 52, w: 7, d: 5, h: 6 },
  // Right (-X).
  { x: -34, z: -12, w: 7, d: 7, h: 25, tier: [4.5, 4, 5], roof: 'mast' },
  { x: -51, z: -11, w: 6, d: 9, h: 14, roof: 'tank' },
  { x: -33, z: 15, w: 7, d: 7, h: 10, roof: 'ac' },
  { x: -51, z: 16, w: 6, d: 9, h: 7, roof: 'ac' },
  { x: -52, z: 27, w: 5, d: 5, h: 12 },
  { x: -36, z: -53, w: 7, d: 6, h: 19, roof: 'mast' },
  { x: -46, z: -49, w: 5, d: 5, h: 7 },
  { x: -25, z: 51, w: 6, d: 6, h: 11, roof: 'tank' },
];

/** The spire's foot on the left, and its height. */
const SPIRE = { x: 46, z: -6, top: 50 } as const;

/** A broadcast spire on the left: a block, a tapered mast ringed with neon, a beacon on top. */
function drawSpire({ hull, neon, charge }: EnemyParts): void {
  const { x, z, top } = SPIRE;
  const base = OVERLORD_DECK.top;
  hull.bevelSlab(box2d(9, 9, [x, z]), [base - 1, base, base + 9], [0, 1.5], H.panel, {}, H.base);
  decal(neon, box2d(5, 0.8, [x, z + 2.8]), base + 9.05, N);
  hull.cylinder(2.8, top - base - 9, 4, H.dark, { at: [x, base + 9, z], yaw: Math.PI / 4 }, 0.5);
  for (const [y, r] of [
    [24, 2],
    [34, 1.4],
    [43, 0.9],
  ] as const) {
    neon.ring(r + 0.3, 0.8, 4, N, { at: [x, y, z], yaw: Math.PI / 4 });
  }
  charge.lathe(
    [
      [1.2, 0],
      [0.9, 1.2],
      [0, 1.8],
    ],
    6,
    WHITE,
    { at: [x, top, z] },
  );
}

/** The billboard's foot on the left: its board faces the nose, leaning back towards the camera. */
const BILLBOARD = { x: 39, z: 16, y: 14, w: 18, h: 9, lean: -0.5 } as const;
/** The bars of its logo (x, height), and its strips of text lit by the charge (x0, y0, x1, y1). */
const LOGO = [
  [-6.5, 5],
  [-4.6, 3],
  [-2.7, 5.5],
] as const;
const TEXT = [
  [0.5, 5.2, 7, 6.4],
  [0.5, 2.6, 5.5, 3.6],
] as const;

/** A neon billboard on stilts: a dark board, a lit frame, a logo, text flickering with the charge. */
function drawBillboard({ hull, neon, charge }: EnemyParts): void {
  const { x, z, y, w, h, lean } = BILLBOARD;
  for (const dx of [-w / 3, w / 3]) {
    hull.box([1.2, y + 2 - OVERLORD_DECK.top, 1.2], H.dark, {
      at: [x + dx, OVERLORD_DECK.top, z - 1],
    });
  }
  hull.box([w, h, 1], H.dark, { at: [x, y, z], pitch: lean });
  const [c, s] = [Math.cos(lean), Math.sin(lean)];
  // A point (dx, dy) of the board's face, just out of it.
  const onFace = (dx: number, dy: number): Vec3 => [
    x + dx,
    y + dy * c - 0.6 * s,
    z + dy * s + 0.6 * c,
  ];
  const quad = (lit: 'neon' | 'charge', [x0, y0, x1, y1]: Rect): void => {
    const corners = [onFace(x0, y0), onFace(x1, y0), onFace(x1, y1), onFace(x0, y1)];
    if (lit === 'neon') neon.face(corners, N);
    else charge.face(corners, WHITE);
  };
  const hw = w / 2;
  const bars: readonly Rect[] = [
    [-hw, 0, hw, 0.7],
    [-hw, h - 0.7, hw, h],
    [-hw, 0, -hw + 0.7, h],
    [hw - 0.7, 0, hw, h],
  ];
  for (const bar of bars) quad('neon', bar);
  for (const [gx, gh] of LOGO) quad('neon', [gx, 1.8, gx + 1.3, 1.8 + gh]);
  for (const line of TEXT) quad('charge', line);
}

/** The command tower's cab (lathe profile, bottom to top): wider than its shaft, windows all round. */
const CAB = [
  [6, 0],
  [8.6, 2.5],
  [8.8, 6.5],
  [6.5, 8.5],
] as const;
const COMMAND = { x: -42, z: 1, shaft: 20 } as const;

/** The command tower on the right: a shaft, a cab ringed with lit windows, a dish and masts. */
function drawCommandTower({ hull, neon, charge }: EnemyParts): void {
  const { x, z, shaft } = COMMAND;
  const base = OVERLORD_DECK.top;
  const top = base + shaft;
  hull.bevelSlab(box2d(11, 11, [x, z]), [base - 1, base, base + 6], [0, 1.5], H.panel, {}, H.base);
  hull.cylinder(4.6, shaft, 8, H.base, { at: [x, base, z], yaw: Math.PI / 8 }, 4);
  hull.lathe(CAB, 8, H.panel, { at: [x, top, z], yaw: Math.PI / 8 });
  neon.ring(8.85, 2, 8, N, { at: [x, top + 3.4, z], yaw: Math.PI / 8 });
  neon.ring(4.7, 1, 8, N, { at: [x, base + 9, z], yaw: Math.PI / 8 });
  const roof = top + 8.5;
  // A dish leaning towards the nose, an aerial with a light that charges.
  hull.cylinder(0.6, 2.4, 6, H.dark, { at: [x + 2, roof, z - 2], pitch: 0.5 }, 4.2);
  hull.cylinder(0.5, 12, 4, H.dark, { at: [x - 3, roof, z + 1] }, 0.2);
  charge.box([1.1, 1.1, 1.1], WHITE, { at: [x - 3, roof + 11.6, z + 1] });
}

/** P07-R05 (phase 7 review): the Overlord's city, its towers and landmarks. */
export function drawSkyline(parts: EnemyParts): void {
  for (const tower of TOWERS) drawTower(parts, tower);
  drawSpire(parts);
  drawBillboard(parts);
  drawCommandTower(parts);
}

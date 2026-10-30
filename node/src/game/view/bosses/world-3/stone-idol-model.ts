import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { SectionPoint } from '../../../../render/geometry/solids';
import type { EnemyModel } from '../../../../render/game-view';
import {
  IDOL_JEWEL,
  IDOL_NOSTRILS,
  IDOL_PARTS,
  STONE_IDOL,
} from '../../../config/bosses/world-3/stone-idol';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { flipX, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { H, neonBand, QUARTER, socket, WHITE } from '../mini-boss-shapes';
import { eyeball, eyeSocket, FACE, IDOL_NEON, mouth } from './stone-idol-parts';
import { crack, leaf, moss, STONE, vine } from './stone-idol-stone';
import { reactorSac } from '../../enemies/organic-parts';
import { F, gland, JUNGLE_FLESH, sinew, veinTo } from './jungle-flesh';

// P09-R09, 3-3: the Stone Idol. Logical pixels, nose +Z (the chin, down the screen), Y up
// (towards the camera): a carved head flying face up, so the camera sees its face.

/** The head seen from above (its right half, +X): a broad face, a flat crown, a heavy chin. */
const HEAD_RIGHT: OutlinePoint[] = [
  [0, 50],
  [24, 46],
  [36, 36],
  [44, 22],
  [47, 6],
  [47, -12],
  [44, -30],
  [36, -42],
  [22, -48],
  [0, -50],
];
const HEAD: OutlinePoint[] = [...HEAD_RIGHT, ...flipX(HEAD_RIGHT).reverse().slice(1, -1)];
/** The helmet over the forehead (an Olmec headdress), outline seen from above. */
const HELMET: OutlinePoint[] = [
  [0, -47],
  [23, -45],
  [35, -38],
  [42, -26],
  [41, -18],
  [0, -21],
  [-41, -18],
  [-42, -26],
  [-35, -38],
  [-23, -45],
];
/** The nose: a rounded ridge (loft section) from between the brows to its tip over the mouth. */
const NOSE_SECTION: readonly SectionPoint[] = [
  [1, 0],
  [0.65, 0.75],
  [0, 1],
  [-0.65, 0.75],
  [-1, 0],
];
const NOSE = [
  [-8, 4, FACE - 1, 14],
  [6, 6, FACE - 1, 18],
  [16, 8, FACE - 1, 18.5],
  [20.5, 8, FACE - 1, 17],
] as const;
/** The neon cracks across the face (paths seen from above), lit from inside the stone. */
const CRACKS: readonly (readonly (readonly [number, number])[])[] = [
  [
    [-14, -46],
    [-10, -36],
    [-15, -28],
    [-12, -20],
  ],
  [
    [30, 16],
    [24, 22],
    [26, 30],
    [19, 38],
    [21, 45],
  ],
  [
    [-28, 14],
    [-36, 20],
    [-34, 30],
  ],
  [
    [8, -16],
    [14, -6],
  ],
];

/** The carved head: its block, the neon glowing under its rim, the helmet and the brows. */
function drawHead(p: EnemyParts): void {
  const { hull, flesh, neon } = p;
  // P16-R05: a living head of grey-green flesh, the carved stone grown over it as armour (its
  // helmet, brows, nose and ear spools), roots of sinew trailing from its chin.
  flesh.bevelSlab(HEAD, [-10, 2, FACE], [6, 5], F.sinew, {}, JUNGLE_FLESH);
  neonBand(neon, HEAD, [-4.5, -1.5], [0.92, 0.975], IDOL_NEON);
  hull.bevelSlab(HELMET, [FACE - 1, FACE + 2, FACE + 5], [0, 1.5], STONE.base, {}, STONE.light);
  neon.box([60, 0.6, 0.6], IDOL_NEON, { at: [0, FACE + 3.2, -19.6], yaw: 0 });
  // The brow ridge over the eyes, broken on the left (the model's +X).
  hull.box([30, 3.5, 6], STONE.base, { at: [-19, FACE - 0.5, -10] }, STONE.light);
  hull.box([22, 3, 6], STONE.base, { at: [21, FACE - 0.5, -10], yaw: 0.08 }, STONE.light);
  hull.box([5, 2.4, 4], STONE.dark, { at: [36, FACE - 0.5, -12], yaw: 0.6 }, STONE.base);
  hull.loft(
    NOSE_SECTION,
    NOSE,
    STONE.base,
    {},
    { paint: (side) => (side === 1 ? STONE.light : undefined) },
  );
  // The ear spools on the sides, lit in their bores.
  for (const s of SIDES) {
    const spool = { at: [s * 45, 1, 2] as [number, number, number], roll: -s * QUARTER };
    hull.cylinder(7, 5, 8, STONE.dark, spool, 6);
    neon.ring(3, 0.8, 8, IDOL_NEON, { at: [s * 49.6, 1, 2], roll: -s * QUARTER });
  }
}

/** The forehead jewel (its last-stage spiral) and the nostrils (its fans), charge-lit. */
function drawGuns({ hull, neon, charge, muzzle }: EnemyParts): void {
  for (const jewel of IDOL_JEWEL.map((m) => bossPoint(...m))) {
    const [x, y, z] = jewel;
    hull.cylinder(4.2, 1.2, 8, STONE.gilt, { at: [x, FACE + 5, z] }, 3.6);
    neon.ring(4.3, 0.5, 8, IDOL_NEON, { at: [x, FACE + 5.6, z] });
    const gem = [
      [3, FACE + 6.2],
      [3.4, y - 1.6],
      [0, y],
    ] as const;
    charge.lathe(gem, 6, WHITE, { at: [x, 0, z] });
    muzzle(jewel, 'ring');
  }
  for (const nostril of IDOL_NOSTRILS.map((m) => bossPoint(...m))) {
    const [x, y, z] = nostril;
    hull.cylinder(2.2, 0.8, 6, STONE.deep, { at: [x, y, z - 1.4], pitch: QUARTER });
    charge.cylinder(1.6, 0.6, 6, WHITE, { at: [x, y, z - 0.6], pitch: QUARTER }, 1.2);
    muzzle(nostril, 'gun');
  }
}

/** P16-R05: the sinew roots trailing from its chin, its veins and glands. */
function drawRoots(p: EnemyParts): void {
  for (const [x, bow] of [
    [-16, -3],
    [14, 4],
    [28, 2],
  ] as const) {
    sinew(
      p,
      [
        [x, 2, 44],
        [x + bow, -4, 53],
      ],
      [bow, -2, 0],
      2,
      F.sinew,
    );
  }
  for (const s of SIDES) {
    veinTo(
      p,
      [
        [s * 8, FACE + 0.3, 26],
        [s * 34, FACE + 0.3, 30],
      ],
      [0, 0, 6],
      IDOL_NEON,
      1.2,
    );
    gland(p, [s * 38, FACE - 0.5, -32], 3, IDOL_NEON);
  }
}

/** Its cracks, the moss in its hollows, the vines over its crown, and the thrusters it flies on. */
function drawJungle(p: EnemyParts): void {
  const { hull, neon } = p;
  for (const path of CRACKS) crack(neon, path, FACE + 0.15, IDOL_NEON);
  crack(
    neon,
    [
      [-24, -40],
      [-30, -33],
      [-27, -27],
    ],
    FACE + 5.1,
    IDOL_NEON,
  );
  for (const [x, z, size] of [
    [-22, 20, 4.5],
    [30, 30, 3.5],
    [12, 42, 3],
    [-38, -6, 3.5],
    [24, -40, 4],
  ] as const) {
    moss(hull, [x, z < -20 ? FACE + 5 : FACE, z], size, x);
  }
  vine(hull, [
    [18, FACE + 5, -40],
    [30, FACE + 4.6, -34],
    [40, FACE, -26],
    [46.5, 4, -22],
    [48, -6, -20],
  ]);
  vine(hull, [
    [-10, FACE + 5, -44],
    [-14, FACE + 2, -49],
    [-15, -2, -51],
    [-13, -8, -50],
  ]);
  vine(hull, [
    [-30, FACE, 32],
    [-36, FACE - 2, 36],
    [-38, -2, 39],
  ]);
  leaf(hull, [-40, FACE - 4, 25], 4, 3);
  drawRoots(p);
  for (const s of SIDES) {
    reactorSac(p, [s * 16, -3, -48.5], 4.5, IDOL_NEON, { flesh: F.purple });
    hull.cylinder(5.4, 3, 8, H.dark, { at: [s * 16, -3, -50], pitch: -QUARTER });
  }
}

const [ex, ey] = IDOL_PARTS.eye;
const [mx, my] = IDOL_PARTS.mouth;

/**
 * P09-R09: the Stone Idol, a flying stone head with neon cracks, glowing eyes and mouth; moss
 * and vines over its crown, an Olmec helmet, a jewel on its forehead.
 */
export function buildStoneIdol(scene: Scene): EnemyModel {
  return buildBossModel(STONE_IDOL, scene, IDOL_NEON, {
    core: (p) => {
      drawHead(p);
      drawGuns(p);
      drawJungle(p);
      for (const s of SIDES) socket(p.hull, bossPoint(s * ex, ey, FACE - 1), 9, 1.2);
      socket(p.hull, bossPoint(mx, my, FACE - 0.6), 8, 0.6);
    },
    parts: { 'eye-left': eyeSocket, 'eye-right': eyeSocket, mouth },
    turrets: { 'eye-left': eyeball, 'eye-right': eyeball },
  });
}

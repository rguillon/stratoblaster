import type { Scene } from '@babylonjs/core/scene';
import type { LoftStation } from '../../../../render/geometry/solids';
import type { EnemyModel } from '../../../../render/game-view';
import {
  GOLEM_BROW,
  GOLEM_STACK,
  OBSIDIAN_GOLEM,
} from '../../../config/bosses/world-4/obsidian-golem';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { HULL_SECTION, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { mirrored } from '../final-boss-shapes';
import { vent } from '../mini-boss-greebles';
import { H, offset, SHADE, socket, WHITE } from '../mini-boss-shapes';
import { barrel } from './magma-salamander-parts';
import {
  armLimbs,
  cannonMount,
  cannonTurret,
  crack,
  emitter,
  fist,
  GOLEM_NEON,
  MAGMA,
  OBSIDIAN,
  plate,
} from './obsidian-golem-parts';
import { backRibs, fleshShell, glands, magmaVein, reactorSacs, SKIN } from './living-forge';

// P10-R11, 4-3: the Obsidian Golem. Logical pixels, nose +Z, Y up (towards the camera). A massive
// flying fortress shaped like a hunched giant: a broad armoured torso of black obsidian plates
// split by glowing magma seams, a small helmed head low on its chest, a furnace stack on its
// back, heavy pauldrons, two arms bending at the shoulder and elbow down to huge fists (limbs on
// joints), the shoulder cannons behind the pauldrons, the armour plate and the chest emitter
// on its front.
// P16-R06: a living hunched giant, its flesh torso and hump ribbed in bone and veined with magma,
// obsidian growths for pauldrons, knuckles and chest plate, a metal helm and guns grafted on.
type Vec3 = [number, number, number];

/** The torso seen from above (right half, chest to back). */
const TORSO = mirrored([
  [0, 30],
  [18, 28],
  [32, 18],
  [40, 4],
  [38, -16],
  [28, -32],
  [0, -36],
]);
/** The hunched upper torso on it, back to front (loft stations: z, half width, bottom, top). */
const HUMP: readonly LoftStation[] = [
  [-32, 22, 16, 23],
  [-12, 30, 16, 28],
  [8, 28, 16, 26],
  [22, 18, 16, 21],
];
/** The magma seams across its back, as paths of points (x, z) on the hump's top. */
const SEAMS: readonly (readonly (readonly [number, number])[])[] = [
  [
    [-16, 12],
    [-6, 4],
    [4, 8],
    [16, 0],
  ],
  [
    [-18, -10],
    [-8, -6],
    [2, -14],
    [14, -10],
  ],
  [
    [0, -14],
    [-2, -26],
  ],
];
/** The head: a small helm low on its chest, from its nape to its brow. */
const HELM: readonly LoftStation[] = [
  [8, 9, 16, 28],
  [16, 10, 16, 29],
  [22, 8, 17, 26],
];

/** The torso: a slab of dark metal, the obsidian hump on it, magma seams across its back. */
function drawTorso(p: EnemyParts): void {
  const { hull, neon } = p;
  p.flesh.bevelSlab(TORSO, [-4, 2, 16], [4, 3], SKIN.base, {}, SKIN.panel);
  fleshShell(p.flesh, HULL_SECTION, HUMP, [SKIN.dark, SKIN.base]);
  backRibs(p, [-22, -10], { halfWidth: 26, y: 12, height: 15, thickness: 1.2 });
  for (const s of SIDES) {
    magmaVein(
      p,
      [
        [s * 30, 16.2, 16],
        [s * 34, 16.2, -2],
        [s * 28, 16.2, -24],
      ],
      1.4,
    );
    glands(p, [[s * 32, 15.8, -30]], 2.4, GOLEM_NEON);
  }
  for (const path of SEAMS) crack(neon, path, 28.2);
  for (const s of SIDES) {
    neon.box([0.7, 0.6, 50], GOLEM_NEON, { at: [s * 39.6, 10, -6], yaw: s * 0.05 });
    vent(hull, [s * 20, 16.2, -26], [8, 6], 3, s * 0.2);
    hull.box([10, 0.5, 8], SHADE.soot, { at: [s * 26, 16.1, 18 - s * 6] });
    socket(hull, [s * 46, 0, -20], 9, 2);
  }
}

/** The head: a helm with a glowing visor, the twin guns under its brow. */
function drawHead(p: EnemyParts): void {
  const { hull, neon, charge } = p;
  hull.loft(HULL_SECTION, HELM, H.panel);
  neon.box([14, 1.2, 1], GOLEM_NEON, { at: [0, 25.6, 22.2] });
  charge.box([10, 0.6, 0.6], WHITE, { at: [0, 26, 22.5] });
  hull.box([3, 4, 10], SHADE.edge, { at: [0, 28.6, 14] });
  for (const tip of GOLEM_BROW.map((m) => bossPoint(...m))) {
    hull.box([3.6, 3, 4], H.dark, { at: offset(tip, 0, -1.5, -6) });
    barrel(p, tip, [1.1, 5]);
  }
}

/** The pauldrons over its shoulders: domes of obsidian ringed in orange. */
function drawPauldrons({ hull, neon }: EnemyParts): void {
  for (const s of SIDES) {
    const at: Vec3 = [s * 38, 14, 2];
    hull.lathe(
      [
        [13, 0],
        [13.6, 4],
        [10, 9],
        [4, 11],
        [0, 11.4],
      ],
      8,
      OBSIDIAN,
      { at, yaw: Math.PI / 8 },
    );
    neon.ring(13.7, 0.8, 8, GOLEM_NEON, { at: offset(at, 0, 1.4, 0), yaw: Math.PI / 8 });
    crack(
      neon,
      [
        [s * 32, 6],
        [s * 38, 0],
        [s * 44, 3],
      ],
      at[1] + 9.8,
    );
  }
}

/** The furnace stack on its back, its glowing top where the core's rings leave from. */
function drawStack({ hull, neon, charge, muzzle }: EnemyParts): void {
  const [top] = GOLEM_STACK.map((m) => bossPoint(...m));
  if (!top) return;
  const foot = offset(top, 0, -(top[1] - 18), 0);
  hull.cylinder(7, top[1] - 19, 8, H.base, { at: foot }, 5.4);
  hull.ring(7.2, 1.6, 8, SHADE.soot, { at: offset(foot, 0, 4, 0) });
  neon.ring(5.6, 1, 8, MAGMA, { at: offset(top, 0, -2.2, 0) });
  charge.cylinder(4.6, 1, 8, WHITE, { at: offset(top, 0, -1, 0) });
  muzzle(top, 'ring');
}

/** Its reactors under the back, and the sockets where the plate and the emitter are bolted. */
function drawUnderside(p: EnemyParts): void {
  reactorSacs(
    p,
    [
      [16, 4, -36],
      [-16, 4, -36],
    ],
    4.4,
    MAGMA,
  );
  reactorSacs(p, [[0, 4, -36]], 3.6, MAGMA);
  socket(p.hull, [0, 0, 34], 10, 3);
  p.neon.box([30, 0.6, 0.8], MAGMA, { at: [0, 2.4, 29.6] });
}

/**
 * P10-R11: the Obsidian Golem, a massive armoured flying fortress of black obsidian with glowing
 * magma seams and two huge fists on bending arms.
 */
export function buildObsidianGolem(scene: Scene): EnemyModel {
  return buildBossModel(OBSIDIAN_GOLEM, scene, GOLEM_NEON, {
    core: (p) => {
      drawTorso(p);
      drawHead(p);
      drawPauldrons(p);
      drawStack(p);
      drawUnderside(p);
    },
    parts: {
      'fist-left': fist,
      'fist-right': fist,
      'cannon-left': cannonMount,
      'cannon-right': cannonMount,
      emitter,
      plate,
    },
    turrets: { 'cannon-left': cannonTurret, 'cannon-right': cannonTurret },
    limbs: armLimbs(),
  });
}

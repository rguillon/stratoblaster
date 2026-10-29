import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { LoftStation } from '../../../../render/geometry/solids';
import type { EnemyModel } from '../../../../render/game-view';
import { CANOPY_SPIDER, SPIDER_CROWN } from '../../../config/bosses/world-3/canopy-spider';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { ribs, ROUND_SECTION, SHELL_SECTION } from '../../../../render/geometry/organic';
import { F, veinTo } from './jungle-flesh';
import { bossPoint, buildBossModel } from '../boss-model';
import { seam, vent } from '../mini-boss-greebles';
import { H, offset, QUARTER, SHADE, socket, WHITE } from '../mini-boss-shapes';
import { legGunPod, legLimbs, legPoints, SPIDER_RED } from './canopy-spider-legs';
import { eggSac } from './canopy-spider-sac';
import { moss, sagging, vine } from './toucan-jungle';

// P09-R09, 3-2: the Canopy Spider. Logical pixels, nose +Z, Y up (towards the camera). A
// walker-ship hanging over the canopy: an armoured cephalothorax carrying the head, its eyes and
// fangs at the front and the crown emitter on its back; a big abdomen behind it, the egg sac (a
// part) at its tip; four legs stepping in turn (limbs on joints, see `canopy-spider-legs.ts`).
type Vec3 = [number, number, number];

/** The cephalothorax, back to front (loft stations: z, half width, bottom, top). */
const THORAX: readonly LoftStation[] = [
  [-10, 12, -1, 11],
  [0, 17, -3, 15],
  [12, 16, -3, 15],
  [22, 12, -2, 12.5],
  [30, 7, 0, 8.5],
];
/** The abdomen, from its tip (where the egg sac hangs) to its waist. */
const ABDOMEN: readonly LoftStation[] = [
  [-47, 5, 3, 9],
  [-40, 14, -1, 19],
  [-34, 18, -2, 21],
  [-20, 18, -2, 21],
  [-12, 14, 0, 18],
  [-7, 8, 3, 12],
];
/** The red hourglass on the abdomen's back (right half, front to back). */
const HOURGLASS: OutlinePoint[] = [
  [0, -20],
  [5, -21],
  [1, -27],
  [5, -33],
  [0, -34],
  [-5, -33],
  [-1, -27],
  [-5, -21],
];
/** The eyes: the two big ones at the front, then the smaller ones (x, height, z, radius). */
const EYES: readonly (readonly [number, number, number, number])[] = [
  [3.6, 6.8, 28.6, 2.3],
  [5.6, 7.4, 24, 1.5],
  [2.4, 11, 22.4, 1.2],
];

/** The cephalothorax and the abdomen: dark armour, the red hourglass, moss on the plates. */
function drawBody(p: EnemyParts): void {
  const { hull, flesh, neon } = p;
  // P16-R06: a living spider: a chitin-shelled cephalothorax, a swollen purple abdomen with bone
  // ribs and pulsing veins, a sinew waist; metal plates and vents grafted on.
  flesh.loft(SHELL_SECTION, THORAX, F.purple, {}, {});
  flesh.loft(ROUND_SECTION, ABDOMEN, F.purple, {}, {});
  flesh.box([12, 6, 6], F.sinew, { at: [0, 2, -8] });
  ribs(flesh, [-18, -28, -38], { halfWidth: 15, y: 6, height: 15.4, thickness: 0.8 }, F.bone);
  for (const s of SIDES) {
    veinTo(
      p,
      [
        [s * 3, 21.2, -14],
        [s * 9, 19, -44],
      ],
      [s * 4, 0.6, 0],
      SPIDER_RED,
      1.1,
    );
  }
  neon.slab(HOURGLASS, [21.05, 21.35], SPIDER_RED, { at: [0, -0.3, 0] });
  for (const s of SIDES) {
    seam(hull, [s * 5, 12], [s * 4, -6], [12, 0.8, 0.6], H.dark);
    seam(hull, [s * 8, -19], [s * 8, -35], [21, 1, 0.5], SHADE.edge);
    vent(hull, [s * 7, 11, 14], [3, 5], 3, s * 0.1);
    vine(hull, sagging([s * 17, 12, -14], [s * 15, 9, -42], 5, 3), 0.5);
  }
  moss(hull, [10, 20.6, -36], 3.4, 0.4);
  moss(hull, [-10, 20.6, -22], 3.2, 1.9);
  moss(hull, [-6, 12.2, 8], 3, 3.3);
  hull.box([5, 1.4, 4], SHADE.patch, { at: [-9, 20.4, -38], yaw: 0.4 });
}

/** The head: the red neon eyes, the fangs under them, the hips' sockets on the thorax. */
function drawHead(p: EnemyParts): void {
  const { hull, flesh, neon, charge } = p;
  for (const s of SIDES) {
    for (const [x, y, z, r] of EYES) {
      const eye: Vec3 = [s * x, y, z];
      flesh.cylinder(r * 1.3, 0.8, 7, F.crimson, { at: offset(eye, 0, -0.6, 0), pitch: 0.7 });
      neon.cylinder(r, 0.7, 8, SPIDER_RED, { at: eye, pitch: 0.7 });
      charge.cylinder(r * 0.45, 0.3, 6, WHITE, { at: offset(eye, 0, 0.45, 0.35), pitch: 0.7 });
    }
    // The fangs (chelicerae), curving down in front of the head.
    // P16-R06: flesh chelicerae, bone fangs, a metal cap grafted on each.
    flesh.box([3.4, 4, 7], F.sinew, { at: [s * 3.6, -1, 31], pitch: 0.5 }, F.crimson);
    hull.box([3.6, 1, 3], H.panel, { at: [s * 3.6, 1.4, 29.5], pitch: 0.5 });
    flesh.cylinder(1.1, 5, 4, F.bone, { at: [s * 3.6, 0.5, 36], pitch: 2.2 }, 0);
  }
}

/** The hips' sockets, and the crown emitter on the thorax's back (the core's spirals). */
function drawCrown({ hull, neon, charge, muzzle }: EnemyParts): void {
  for (const leg of ['fore-left', 'fore-right', 'aft-left', 'aft-right'] as const) {
    const [hip] = legPoints(leg);
    socket(hull, offset(hip, 0, -4, 0), 4.6, 5);
  }
  const [crown] = SPIDER_CROWN.map((m) => bossPoint(...m));
  if (!crown) return;
  hull.lathe(
    [
      [6, 0],
      [5.6, 2.4],
      [3.6, 4.6],
      [2.4, 5],
    ],
    8,
    H.panel,
    { at: offset(crown, 0, -6.6, 0), yaw: Math.PI / 8 },
  );
  neon.ring(5.9, 0.6, 8, SPIDER_RED, { at: offset(crown, 0, -5.8, 0), yaw: Math.PI / 8 });
  hull.cylinder(2.2, 1.2, 8, H.dark, { at: offset(crown, 0, -1.8, 0) });
  charge.cylinder(1.8, 0.6, 8, WHITE, { at: offset(crown, 0, -0.6, 0) });
  muzzle(crown, 'ring');
  for (const s of SIDES) {
    hull.box([1.4, 3, 6], SHADE.edge, { at: offset(crown, s * 4.4, -5, -1), roll: s * 0.3 });
  }
  hull.box([3, 1.4, 8], H.dark, { at: offset(crown, 0, -6.4, -8), pitch: QUARTER / 6 });
}

/**
 * P09-R09: the Canopy Spider, a four-legged walker-ship hanging over the canopy, its legs
 * stepping in turn, red neon eyes, moss and vines on its armour.
 */
export function buildCanopySpider(scene: Scene): EnemyModel {
  return buildBossModel(CANOPY_SPIDER, scene, SPIDER_RED, {
    core: (p) => {
      drawBody(p);
      drawHead(p);
      drawCrown(p);
    },
    parts: {
      'leg-fore-left': legGunPod,
      'leg-fore-right': legGunPod,
      'leg-aft-left': legGunPod,
      'leg-aft-right': legGunPod,
      'egg-sac': eggSac,
    },
    limbs: legLimbs(),
  });
}

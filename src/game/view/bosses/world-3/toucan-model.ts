import type { Scene } from '@babylonjs/core/scene';
import type { LoftStation } from '../../../../render/geometry/solids';
import type { EnemyModel } from '../../../../render/game-view';
import { TOUCAN, TOUCAN_CHEEK_GUNS, TOUCAN_CREST } from '../../../config/bosses/world-3/toucan';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { reactorSac } from '../../enemies/organic-parts';
import { ROUND_SECTION } from '../../../../render/geometry/organic';
import { F, sinew, spine } from './jungle-flesh';
import { bossPoint, buildBossModel } from '../boss-model';
import { mirrored, strip } from '../final-boss-shapes';
import { seam, vent } from '../mini-boss-greebles';
import { H, offset, QUARTER, SHADE, socket, WHITE } from '../mini-boss-shapes';
import { moss, sagging, vine } from './toucan-jungle';
import { beak, TOUCAN_ORANGE, TOUCAN_YELLOW, wingPod } from './toucan-parts';

// P09-R09, 3-2: the Toucan. Logical pixels, nose +Z, Y up (towards the camera). A stubby
// gunship: a round black body, short wings carrying the fan pods, a fanned tail, and the huge
// bright beak (its cannon, a part) in front of its head.
type Vec3 = [number, number, number];

/** The body along the centre line, tail to head (loft stations: z, half width, bottom, top). */
const BODY: readonly LoftStation[] = [
  [-36, 5, 0, 5],
  [-26, 11, -2, 9.5],
  [-10, 16, -4, 13],
  [6, 17, -4, 15],
  [15, 14.5, -3, 14.2],
  [21, 10.6, -1.5, 12.6],
];
/** The cream bib under its head (the lower sides of the body's last bands). */
const BIB: readonly [number, number, number] = [0.7, 0.64, 0.42];
const BIB_SIDES = new Set([0, 1, 7, 8]);
/** The wings seen from above (right half, front to back), the pods at their ends. */
const WINGS = mirrored([
  [0, 13],
  [14, 12],
  [26, 9],
  [30, 4],
  [30, -9],
  [24, -15],
  [12, -17],
  [0, -17],
]);
/** The tail's fan of feathers seen from above (right half, from the body back). */
const TAIL = mirrored([
  [0, -30],
  [8, -32],
  [11, -45],
  [5, -48],
  [0, -44],
]);

/** The body: black plates, a cream bib, orange neon along its flanks, moss on its back. */
function drawBody(p: EnemyParts): void {
  const { hull, flesh, neon } = p;
  const paint = (side: number, band: number) =>
    band === 4 && BIB_SIDES.has(side) ? BIB : undefined;
  // P16-R05: a round, living bird's body of dark purple flesh, a bone ribcage over its back.
  flesh.loft(ROUND_SECTION, BODY, F.purple, {}, { paint });
  spine(
    p,
    BODY.slice(1).map(([z, , , t]) => [0, t + 0.3, z] as const),
    { at: [-20, -12, -4], halfWidth: 13, y: 2, height: 11.8 },
    TOUCAN_ORANGE,
  );
  for (const s of SIDES) {
    strip(neon, [s * 15.6, 4], [s * 12, -20], 0.8, [3.6, 4.4], TOUCAN_ORANGE);
    seam(hull, [s * 6, 10], [s * 7, -22], [12.4, 0.8, 0.5], H.dark);
    vent(hull, [s * 9, 11.4, -14], [3.2, 6], 3, s * 0.12);
  }
  moss(hull, [5, 14.2, -4], 4.2, 0.7);
  moss(hull, [-7, 12.2, -19], 3.4, 2.1);
}

/** The wings and the tail: dark, bevelled, neon on their edges, vines hanging from them. */
function drawWingsAndTail(p: EnemyParts): void {
  const { hull, flesh, neon } = p;
  // P16-R05: short, heavy membrane wings (still, P16-R01) on bone struts, a fan of bone quills.
  flesh.bevelSlab(WINGS, [-1.5, 0, 2], [0.8, 1], F.membrane, {}, F.purple);
  flesh.bevelSlab(TAIL, [0.5, 1.5, 3], [0.4, 0.8], F.membrane, {}, F.crimson);
  for (const s of SIDES) {
    for (const [x, z] of [
      [30, 4],
      [30, -9],
      [24, -15],
    ] as const) {
      sinew(
        p,
        [
          [s * 4, 2.4, 0],
          [s * x, 2.2, z],
        ],
        [0, 0.6, 0],
        1,
        F.bone,
      );
    }
    sinew(
      p,
      [
        [s * 2, 3.2, -30],
        [s * 10, 3.2, -45],
      ],
      [0, 0.3, 0],
      0.7,
      F.bone,
    );
  }
  for (const s of SIDES) {
    strip(neon, [s * 14, 12.2], [s * 25.5, 9.4], 0.8, [1.9, 2.3], TOUCAN_YELLOW);
    strip(neon, [s * 8.5, -33], [s * 10.6, -44.5], 0.7, [2.9, 3.3], TOUCAN_ORANGE);
    seam(hull, [s * 18, 8], [s * 22, -14], [2, 0.6, 0.4], H.dark);
    vine(hull, sagging([s * 12, -0.5, -16.5], [s * 26, -0.5, -14.5], 5, 3.5));
    moss(hull, [s * 20, 2, -4], 3, s);
    reactorSac(p, [s * 4.5, 3, -36.2], 2.8, TOUCAN_ORANGE);
  }
}

/** The head: its round neon eyes either side, the cheek guns under them, the crest emitter. */
function drawHead(p: EnemyParts): void {
  const { hull, neon, charge, muzzle } = p;
  for (const s of SIDES) {
    const eye: Vec3 = [s * 12.4, 8.6, 15];
    hull.cylinder(3.2, 0.8, 8, H.dark, { at: eye, roll: -s * QUARTER });
    neon.ring(3.3, 0.9, 8, TOUCAN_YELLOW, { at: offset(eye, s * 0.4, 0, 0), roll: -s * QUARTER });
    charge.cylinder(1.5, 0.5, 8, WHITE, { at: offset(eye, s * 0.6, 0, 0), roll: -s * QUARTER });
  }
  for (const tip of TOUCAN_CHEEK_GUNS.map((m) => bossPoint(...m))) {
    const [x, y, z] = tip;
    hull.box([4.4, 4, 7], H.panel, { at: [x, y - 2.4, z - 10] }, H.base);
    hull.cylinder(1.2, 6.4, 6, H.dark, { at: [x, y, z - 7], pitch: QUARTER });
    charge.cylinder(1.25, 0.6, 6, WHITE, { at: [x, y, z - 0.6], pitch: QUARTER });
    muzzle(tip);
  }
  const [crest] = TOUCAN_CREST.map((m) => bossPoint(...m));
  if (!crest) return;
  socket(hull, offset(crest, 0, -3.4, 0), 3.4, 1.6);
  neon.ring(3.5, 0.5, 8, TOUCAN_ORANGE, { at: offset(crest, 0, -2.2, 0) });
  hull.cylinder(2.2, 1.2, 8, H.panel, { at: offset(crest, 0, -1.8, 0) }, 1.8);
  charge.cylinder(1.6, 0.6, 8, WHITE, { at: offset(crest, 0, -0.6, 0) });
  muzzle(crest, 'ring');
  hull.box([2.6, 2.4, 7], SHADE.edge, { at: offset(crest, 0, -2.6, -7), pitch: -0.25 });
}

/**
 * P09-R09: the Toucan, a stubby gunship with a huge bright beak, yellow and orange neon, moss on
 * its back and vines hanging from its wings.
 */
export function buildToucan(scene: Scene): EnemyModel {
  return buildBossModel(TOUCAN, scene, TOUCAN_YELLOW, {
    core: (p) => {
      drawBody(p);
      drawWingsAndTail(p);
      drawHead(p);
    },
    parts: { 'pod-left': wingPod, 'pod-right': wingPod, beak },
  });
}

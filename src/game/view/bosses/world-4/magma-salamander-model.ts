import type { Scene } from '@babylonjs/core/scene';
import type { LoftStation } from '../../../../render/geometry/solids';
import type { EnemyModel } from '../../../../render/game-view';
import {
  MAGMA_SALAMANDER,
  SALAMANDER_JAWS,
  SALAMANDER_VENT,
} from '../../../config/bosses/world-4/magma-salamander';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { FIGHTER_SECTION, HULL_SECTION, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { vent } from '../mini-boss-greebles';
import { H, offset, QUARTER, SHADE, socket, WHITE } from '../mini-boss-shapes';
import { segment } from '../world-3/toucan-jungle';
import {
  barrel,
  fin,
  MOLTEN,
  moltenSeam,
  SALAMANDER_NEON,
  SCORCH,
  tail,
  tailLimbs,
} from './magma-salamander-parts';

// P10-R11, 4-3: the Magma Salamander. Logical pixels, nose +Z, Y up (towards the camera). A
// segmented lizard-ship: a flat, wedge-shaped head, a body of overlapping armour plates with
// magma glowing in the seams between them, four clawed legs splayed out, a spiny fin on each
// side of its back (its parts) and a tail curling back to its right (on two joints).
type Vec3 = [number, number, number];

/** The underbody along the centre line, tail to neck (loft stations: z, half width, bottom, top). */
const BELLY: readonly LoftStation[] = [
  [-26, 6, 0, 6],
  [-12, 12, -1, 9.5],
  [8, 13, -1, 10.5],
  [26, 10, 0, 9.5],
  [36, 7, 1, 8],
];
/** The armour plates over the body, back to front: from and to (z), half width, top. */
const PLATES: readonly (readonly [number, number, number, number])[] = [
  [-26, -18, 8, 8],
  [-17, -4, 13.5, 11],
  [-2, 10, 14.5, 12],
  [12, 24, 13, 11.5],
  [26, 35, 10, 10],
];
/** The head: a flat wedge, from its neck to its snout. */
const HEAD: readonly LoftStation[] = [
  [34, 8, 0, 9],
  [44, 10.5, -0.5, 9],
  [54, 8.5, 0, 7],
  [60, 5.5, 0.5, 5],
  [64, 2, 1, 3],
];
/** Where its legs leave the body (z, front ones first) and which way their feet point. */
const LEGS: readonly (readonly [z: number, reach: number])[] = [
  [22, 7],
  [-8, -7],
];

/** The underbody and its plates, a molten seam glowing between each plate and the next. */
function drawBody({ hull, neon }: EnemyParts): void {
  hull.loft(HULL_SECTION, BELLY, H.dark);
  PLATES.forEach(([z0, z1, half, top], i) => {
    const plate: LoftStation[] = [
      [z0, half * 0.85, 1, top - 1.2],
      [z0 + 2, half, 0.5, top],
      [z1 - 2, half, 0.5, top],
      [z1, half * 0.88, 1, top - 1],
    ];
    hull.loft(FIGHTER_SECTION, plate, i % 2 === 0 ? H.base : H.panel, {}, {});
    if (i > 0) moltenSeam(neon, [half * 1.5, top - 1.6, z0 - 0.5]);
  });
  for (const s of SIDES) {
    neon.box([0.6, 0.5, 40], SALAMANDER_NEON, { at: [s * 13.6, 6.2, 4], yaw: s * 0.04 });
    hull.box([4, 0.5, 6], SCORCH, { at: [s * 6, 11.6, 16 - s * 10] });
  }
  vent(hull, [-6, 12.2, 3], [5, 6], 3);
}

/** The head: a flat wedge with orange eyes, the jaw guns either side of the snout. */
function drawHead(p: EnemyParts): void {
  const { hull, neon, charge } = p;
  hull.loft(FIGHTER_SECTION, HEAD, H.base);
  hull.box([12, 1.6, 12], H.dark, { at: [0, -0.6, 54] });
  moltenSeam(neon, [12, 7.6, 37]);
  for (const s of SIDES) {
    neon.box([3, 1, 4], SALAMANDER_NEON, { at: [s * 7.2, 7.6, 47], yaw: s * 0.4 });
    charge.box([1.4, 0.4, 1.8], WHITE, { at: [s * 7.2, 8.6, 47], yaw: s * 0.4 });
    hull.box([1.4, 2, 9], SHADE.edge, { at: [s * 9, 7, 42], yaw: s * 0.2 });
  }
  for (const tip of SALAMANDER_JAWS.map((m) => bossPoint(...m))) {
    hull.box([3, 3, 6], H.panel, { at: offset(tip, 0, -1.5, -9) }, SHADE.edge);
    barrel(p, tip, [1, 5.5]);
  }
}

/** Four clawed legs splayed out from its sides, armoured at the shoulder. */
function drawLegs({ hull, neon }: EnemyParts): void {
  for (const s of SIDES) {
    for (const [z, reach] of LEGS) {
      const hip: Vec3 = [s * 11, 3, z];
      const knee: Vec3 = [s * 21, 5, z + reach * 0.4];
      const foot: Vec3 = [s * 27, 0, z + reach];
      segment(hull, [hip, knee], [3, 2.4], H.panel, 5);
      segment(hull, [knee, foot], [2.2, 1.4], H.base, 5);
      hull.cylinder(3.2, 2.4, 6, H.dark, { at: offset(knee, 0, -1.2, 0) });
      neon.box([1, 0.6, 1], MOLTEN, { at: offset(knee, 0, 1.6, 0) });
      for (const yaw of [-0.5, 0, 0.5]) {
        const toe = Math.sign(reach) * 3.4;
        hull.box([0.9, 0.9, 3.4], SHADE.edge, {
          at: offset(foot, Math.sin(yaw) * toe, -0.4, Math.cos(yaw) * toe),
          yaw,
        });
      }
    }
  }
}

/** The fins' sockets on its back, the magma vent between them, and its reactors. */
function drawBack(p: EnemyParts): void {
  const { hull, neon, charge, muzzle } = p;
  for (const s of SIDES) {
    socket(hull, [s * 14, 3, -4], 4, 6);
    p.reactor([s * 6, 3, -25], 2.2);
  }
  const [top] = SALAMANDER_VENT.map((m) => bossPoint(...m));
  if (!top) return;
  hull.cylinder(5.4, top[1] - 10.4, 7, SCORCH, { at: offset(top, 0, -(top[1] - 10), 0) }, 3.4);
  neon.ring(3.6, 0.6, 7, MOLTEN, { at: offset(top, 0, -1.2, 0) });
  charge.cylinder(2.8, 0.6, 7, WHITE, { at: offset(top, 0, -0.6, 0) });
  muzzle(top, 'ring');
  hull.box([2, 1, 6], H.dark, { at: offset(top, 0, -4, 6), pitch: QUARTER / 8 });
}

/**
 * P10-R11: the Magma Salamander, a segmented lizard-ship with a molten glow between its plates,
 * orange-yellow neon, spiny back fins and a lashing tail.
 */
export function buildMagmaSalamander(scene: Scene): EnemyModel {
  return buildBossModel(MAGMA_SALAMANDER, scene, SALAMANDER_NEON, {
    core: (p) => {
      drawBody(p);
      drawHead(p);
      drawLegs(p);
      drawBack(p);
    },
    parts: { 'fin-left': fin, 'fin-right': fin, tail },
    limbs: tailLimbs(),
  });
}

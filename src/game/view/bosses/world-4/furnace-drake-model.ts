import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../../render/game-view';
import {
  DRAKE_HEART,
  DRAKE_WING,
  FURNACE_DRAKE,
} from '../../../config/bosses/world-4/furnace-drake';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { HULL_SECTION, POD_SECTION, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel, type LimbDrawing } from '../boss-model';
import { rod } from '../final-boss-greebles';
import { seam, vent } from '../mini-boss-greebles';
import { H, SHADE, WHITE } from '../mini-boss-shapes';
import { DRAKE_ORANGE, DRAKE_RED, jaw, SOOT, spike, wing } from './furnace-drake-parts';

// P10-R11, 4-4: the Furnace Drake. Logical pixels, nose +Z, Y up (towards the camera). A
// dragon-shaped gunship: a heavy armoured torso with a furnace glowing through a grate in its
// back, molten seams between its soot-black plates, four clawed legs tucked under it, a long
// spiked tail lashing behind, beating wings and a horned head on a swaying neck.
type Vec3 = [number, number, number];

/** The torso along the centre line (loft stations: z, half width, bottom, top). */
const TORSO = [
  [-22, 6, -1, 6],
  [-12, 11, -3, 10],
  [0, 13, -4, 12],
  [10, 11, -3, 10.5],
  [17, 7, -1, 8],
] as const;
/** The tail, hips to tip (on its joint at the hips): a tapering spiked whip. */
const TAIL = [
  [-20, 5, -0.5, 5.5],
  [-31, 3.8, 0, 4.6],
  [-43, 2.6, 0.5, 3.6],
  [-53, 1.4, 1, 2.6],
  [-57, 0.4, 1.6, 2],
] as const;
/** The legs, front then back (left side, +X): hip, knee and claw, folded under the torso. */
const LEGS: readonly (readonly [Vec3, Vec3, Vec3])[] = [
  [
    [8, -1, 9],
    [15, -3, 13],
    [14, -5, 19],
  ],
  [
    [8, -1, -12],
    [16, -3, -14],
    [15, -5, -7],
  ],
];
/** The furnace heart's grate on its back (a lathe dome), glowing as its next spiral charges. */
const HEART = [
  [4.6, 0],
  [4, 1.6],
  [2.2, 2.6],
  [0, 2.9],
] as const;

/** The torso: plates, molten seams between them, soot, spines down the back, legs and reactors. */
function drawTorso(p: EnemyParts): void {
  const { hull, neon } = p;
  hull.loft(HULL_SECTION, TORSO, H.base);
  for (const s of SIDES) {
    seam(neon, [s * 9, -14], [s * 10.5, 9], [9.3, 0.5, 0.3], DRAKE_ORANGE);
    seam(neon, [s * 11.8, -6], [s * 12.4, 4], [6.5, 0.4, 0.4], DRAKE_RED);
    seam(hull, [s * 5, -18], [s * 6, 14], [11.4, 2.2, 0.3], SOOT);
    vent(hull, [s * 6.5, 10.4, 10], [3.4, 4], 3);
    // The shoulder the wing turns in.
    const [rx, ry] = DRAKE_WING.root;
    hull.cylinder(4.2, 6, 8, H.dark, { at: bossPoint(s * rx, ry, 1) });
    p.reactor([s * 4, 2, -22.4], 2.2);
  }
  for (const z of [12, -12, -18]) spike(hull, [0, 11, z], [1.6, 4], H.dark, 0.7);
  drawLegs(p);
}

/** Four short legs folded under the torso, ending in claws. */
function drawLegs({ hull }: EnemyParts): void {
  for (const s of SIDES) {
    for (const [hip, knee, claw] of LEGS) {
      const side = (v: Vec3): Vec3 => [s * v[0], v[1], v[2]];
      rod(hull, side(hip), side(knee), 1.6, H.panel);
      rod(hull, side(knee), side(claw), 1.1, H.dark);
      spike(hull, side(claw), [0.8, 3], SHADE.edge, -1.2);
    }
  }
}

/** The furnace heart on its back, where its spirals leave from. */
function drawHeart({ hull, neon, charge, muzzle }: EnemyParts): void {
  const [top] = DRAKE_HEART.map((m) => bossPoint(...m));
  if (!top) return;
  const [x, y, z] = top;
  hull.cylinder(6, 4, 8, H.dark, { at: [x, y - 6.4, z] }, 5);
  neon.ring(5.2, 0.5, 8, DRAKE_ORANGE, { at: [x, y - 2.6, z] });
  charge.lathe(HEART, 8, WHITE, { at: [x, y - 2.9, z] });
  for (const dx of [-2, 0, 2]) hull.box([0.5, 0.5, 8], SOOT, { at: [x + dx, y - 0.4, z] });
  muzzle(top, 'ring');
}

/** The tail on its joint at the hips: spikes down its back, a glowing blade at its tip. */
const TAIL_LIMB: LimbDrawing = {
  draw: ({ hull, neon }) => {
    hull.loft(POD_SECTION, TAIL, H.panel);
    for (const [z, h] of [
      [-26, 5],
      [-35, 4.2],
      [-44, 3.4],
    ] as const) {
      spike(hull, [0, h, z], [1.3, 3], H.dark, 0.7);
    }
    seam(neon, [0, -22], [0, -52], [5.6, 0.4, 0.3], DRAKE_RED);
    for (const s of SIDES) {
      hull.box([5, 0.8, 4], SHADE.edge, { at: [s * 2.4, 1.6, -54], yaw: s * 0.7 });
      seam(neon, [s * 2, -48], [s * 3.6, -55], [2.4, 0.4, 0.4], DRAKE_ORANGE);
    }
  },
};

/**
 * P10-R11: the Furnace Drake, a dragon-shaped gunship (3.5 L) of soot-black plates with red and
 * orange neon: beating wings with a fan pod under each, a horned head breathing flame, a furnace
 * glowing in its back and a spiked tail lashing behind.
 */
export function buildFurnaceDrake(scene: Scene): EnemyModel {
  return buildBossModel(FURNACE_DRAKE, scene, DRAKE_RED, {
    core: (p) => {
      drawTorso(p);
      drawHeart(p);
      p.hull.box([8, 1, 3], SOOT, { at: [0, 11, -12] });
    },
    parts: { 'wing-left': wing, 'wing-right': wing, jaw },
    limbs: { tail: TAIL_LIMB },
  });
}

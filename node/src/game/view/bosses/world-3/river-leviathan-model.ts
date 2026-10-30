import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../../render/game-view';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import {
  LEVIATHAN_CREST,
  LEVIATHAN_FANGS,
  LEVIATHAN_LENS,
  RIVER_LEVIATHAN,
  SEGMENTS,
} from '../../../config/bosses/world-3/river-leviathan';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { angryEyes, decal, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import type { PartDrawing } from '../boss-model';
import { H, offset, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';
import { SUB_SECTION } from '../world-2/narwhal-parts';
import { barrelTo, moss, scutes, stone } from './mangrove-croc-jungle';
import { F, gland } from './jungle-flesh';
import {
  LEVIATHAN_TEAL as N,
  leviathanBody,
  missileRack,
  ringTurret,
  turretMount,
} from './river-leviathan-body';

// P09-R09, 3-1: the River Leviathan. Logical pixels, nose +Z, Y up (towards the camera). A
// serpent-ship: an armoured, wedge-shaped head (its core) with a dorsal crest, glaring teal eyes,
// fang guns and a laser lens on its snout; behind it, its swaying body (`river-leviathan-body`).
type Vec3 = [number, number, number];

/** The head (loft stations, neck to snout: z, half width, bottom, top). */
const HEAD = [
  [-24, 13, -3, 10],
  [-12, 17, -4, 13],
  [2, 18, -4, 13.5],
  [14, 15, -3, 11],
  [23, 10, -1.5, 8],
  [29, 5.5, 0.5, 6],
] as const;
/** The dorsal crest on the head, seen from the side (z, height), rolled upright. */
const CREST: readonly OutlinePoint[] = [
  [-18, 12.5],
  [-12, 17.5],
  [4, 17.5],
  [10, 13],
];
/** The crest emitter's housing (a lathe profile from the crest's top). */
const EMITTER = [
  [3.6, 0],
  [3.4, 0.8],
  [2.2, 1.3],
  [0, 1.5],
] as const;

/** The head's hull, its jaw line, the teal light along its back and its glaring eyes. */
function drawHead(p: EnemyParts): void {
  const { hull, flesh, neon } = p;
  // P16-R06: a living serpent's head of teal flesh, its scutes and jaw line grafted armour.
  flesh.loft(SUB_SECTION, HEAD, F.teal);
  for (const s of SIDES) gland(p, [s * 9, 10.6, 10], 2.2, N);
  // The jaw line: a dark lip round the snout, under the eyes.
  for (const s of SIDES) {
    hull.box([2, 2.4, 22], H.dark, { at: [s * 13.5, 1, 12], yaw: -s * 0.3 });
    hull.box([1.4, 1.2, 16], SHADE.edge, { at: [s * 15.4, 9.6, -6] });
  }
  neon.box([1.2, 0.5, 30], N, { at: [0, 13.55, -6] });
  for (const eye of angryEyes([0, 18], 9, [6, 1.6], 0.35)) decal(neon, eye, 11.4, N);
  scutes(
    hull,
    ([-16, -6] as const).flatMap((z) => SIDES.map((s): Vec3 => [s * 8, 13, z])),
    2,
  );
  moss(
    hull,
    [
      [-11, -20],
      [-4, -18],
      [-5, -12],
      [-12, -14],
    ],
    12.5,
  );
  stone(hull, [10, 12.6, -16], 2.4, 0.7);
}

/** The crest on its back and the ring emitter at its top (the core's spirals). */
function drawCrest({ hull, flesh, neon, charge, muzzle }: EnemyParts): void {
  const [tip] = LEVIATHAN_CREST;
  if (!tip) return;
  const top = bossPoint(...tip);
  // P16-R06: a membrane fin on its back, the emitter grafted at its top.
  flesh.slab(CREST, [-1.4, 1.4], F.membrane, { pitch: -QUARTER, yaw: -QUARTER }, F.bone);
  const base = offset(top, 0, -1.5, 0);
  hull.lathe(EMITTER, 8, H.dark, { at: base });
  neon.ring(3.7, 0.5, 8, N, { at: base });
  charge.cylinder(1.2, 0.2, 6, WHITE, { at: offset(top, 0, -0.2, 0) });
  muzzle(top, 'ring');
}

/** The snout: the laser lens at its tip, the fang guns at its cheeks, teeth under its lip. */
function drawSnout(p: EnemyParts): void {
  const { hull, neon, charge, muzzle } = p;
  const [lens] = LEVIATHAN_LENS;
  if (lens) {
    const at = bossPoint(...lens);
    hull.cylinder(3.6, 5, 8, H.panel, { at: offset(at, 0, 0, -5), pitch: QUARTER }, 3);
    neon.ring(3.2, 0.6, 8, N, { at: offset(at, 0, 0, -1.6), pitch: QUARTER });
    charge.cylinder(2.4, 0.6, 8, WHITE, { at: offset(at, 0, 0, -0.6), pitch: QUARTER });
    muzzle(at, 'laser');
  }
  for (const tip of LEVIATHAN_FANGS) {
    barrelTo(p, tip, [1.3, 6]);
    const [x, , z] = bossPoint(...tip);
    hull.box([3.6, 3, 5], H.dark, { at: [x, 1.6, z - 9] }, H.panel);
    p.flesh.cylinder(0.9, 2.6, 4, F.bone, { at: [x * 0.6, 2, z - 1], pitch: Math.PI }, 0);
  }
}

/**
 * P09-R09: the River Leviathan, a segmented serpent-ship 6 L long, teal neon along its spine:
 * an armoured head with a crest, its four segments with their ring turrets and its tail with a
 * missile rack swaying one after the other behind it, moss and vines from the river.
 */
export function buildRiverLeviathan(scene: Scene): EnemyModel {
  const segments: Record<string, PartDrawing> = {};
  const turrets: Record<string, PartDrawing> = {};
  for (const k of SEGMENTS) {
    segments[`segment-${String(k)}`] = turretMount;
    turrets[`segment-${String(k)}`] = ringTurret;
  }
  return buildBossModel(RIVER_LEVIATHAN, scene, N, {
    core: (p) => {
      drawHead(p);
      drawCrest(p);
      drawSnout(p);
    },
    parts: { ...segments, 'tail-rack': missileRack },
    turrets,
    limbs: leviathanBody(),
  });
}

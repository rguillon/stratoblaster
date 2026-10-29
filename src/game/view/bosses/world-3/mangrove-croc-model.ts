import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../../render/game-view';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import { CROC_DOME, MANGROVE_CROC } from '../../../config/bosses/world-3/mangrove-croc';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { decal, sideStripe, SIDES } from '../../enemies/enemy-shapes';
import { reactorSac } from '../../enemies/organic-parts';
import { organ, ROUND_SECTION } from '../../../../render/geometry/organic';
import { F, gland, JUNGLE_FLESH, spine } from './jungle-flesh';
import { bossPoint, buildBossModel } from '../boss-model';
import { vent } from '../mini-boss-greebles';
import { H, offset, SHADE, WHITE } from '../mini-boss-shapes';
import { moss, scutes, stone, SWAMP, vine } from './mangrove-croc-jungle';
import { CROC_GREEN as N, CROC_JAWS, jawCannon, pontoon } from './mangrove-croc-parts';

// P09-R09, 3-1: the Mangrove Croc. Logical pixels, nose +Z, Y up (towards the camera). A long,
// low hover-gunboat shaped like a crocodile: a scaly armoured back, a broad head with raised
// green neon eyes, jaws that open and close around the jaw cannon, and two side pontoons.
type Vec3 = [number, number, number];

/** The hull (loft stations, tail to snout: z, half width, bottom, top): long, low and broad. */
const HULL = [
  [-50, 2.5, 1.5, 4],
  [-42, 7, 0, 6.5],
  [-28, 13, -2.5, 9],
  [-8, 17, -3, 10.5],
  [10, 15, -2.5, 10],
  [22, 11, -1.5, 8.5],
  [30, 7.5, -0.5, 6],
] as const;
/** The hover skirt under the hull, seen from above. */
const SKIRT: readonly OutlinePoint[] = [
  [0, -44],
  [13, -30],
  [18, -6],
  [15, 14],
  [9, 28],
  [-9, 28],
  [-15, 14],
  [-18, -6],
  [-13, -30],
];
/** The eyes on the head: where each sits (x across, z along) and the bump's radius and height. */
const EYE = { x: 7, z: 17, radius: 3.6, height: 10.4 } as const;
/** Rows of scutes either side of the spine (x, from z, to z, step). */
const SCUTE_ROWS = [
  [4, -40, 6, 7],
  [-4, -40, 6, 7],
  [10, -26, -2, 8],
  [-10, -26, -2, 8],
] as const;
/** The ring dome on its back (a lathe profile around the dome's axis). */
const DOME = [
  [6.5, 0],
  [6.5, 1.5],
  [5, 4],
  [2.4, 5.2],
  [0, 5.4],
] as const;

/** The hull's height at `z` (the top of its loft there), for things laid on it. */
function topAt(z: number): number {
  for (let i = 1; i < HULL.length; i++) {
    const [a, b] = [HULL[i - 1], HULL[i]];
    if (!a || !b || z > b[0]) continue;
    return a[3] + ((b[3] - a[3]) * (z - a[0])) / (b[0] - a[0]);
  }
  return HULL.at(-1)?.[3] ?? 0;
}

/** The hull, its skirt, its green neon chines and the pontoons' pylons. */
function drawHull(p: EnemyParts): void {
  const { hull, flesh, neon } = p;
  // P16-R05: a living croc's swollen, moss-skinned body; its hover skirt a grafted metal belly.
  flesh.loft(ROUND_SECTION, HULL, JUNGLE_FLESH);
  hull.bevelSlab(SKIRT, [-4.5, -3.5, -2.5], [0.5, 0.5], H.dark, {}, SWAMP.mud);
  spine(
    p,
    HULL.slice(1).map(([z, , , t]) => [0, t + 0.4, z] as const),
    { at: [-30, -18, -6], halfWidth: 9, y: 4, height: 6.2 },
    N,
  );
  for (const side of [1, 6]) {
    neon.loft(
      sideStripe(ROUND_SECTION, side, [0.2, 0.45], 1.03),
      HULL.slice(1, 6),
      N,
      {},
      {
        open: true,
      },
    );
  }
  for (const s of SIDES) {
    for (const z of [-14, 2]) {
      hull.box([16, 2.4, 4], H.dark, { at: [s * 20, 3, z] }, H.panel);
      hull.box([2, 4, 3], SHADE.edge, { at: [s * 15, 2, z] });
    }
    vine(hull, [s * 15, 5, -14], [s * 23, 4.5, 2], 4.5);
  }
}

/** The head: its two raised eyes with green neon slits, nostrils at the snout, a brow ridge. */
function drawHead(p: EnemyParts): void {
  const { hull, flesh, neon, charge } = p;
  for (const s of SIDES) {
    const at: Vec3 = [s * EYE.x, topAt(EYE.z) - 1, EYE.z];
    // P16-R05: a bulging flesh eye socket, its eye a gland under the neon slit.
    organ(flesh, EYE.radius, 6, F.sinew, { at }, (EYE.height - at[1]) / (EYE.radius * 2));
    gland(p, [s * EYE.x, EYE.height - 1.6, EYE.z], 1.6, N);
    const slit: OutlinePoint[] = [
      [s * (EYE.x - 2.4), EYE.z - 0.6],
      [s * (EYE.x + 2.2), EYE.z - 1.6],
      [s * (EYE.x + 2.2), EYE.z + 0.4],
      [s * (EYE.x - 2.4), EYE.z + 1.2],
    ];
    decal(neon, slit, EYE.height + 0.05, N);
    hull.box([4, 1.2, 1.4], H.dark, { at: [s * 3.2, topAt(27) - 0.4, 27] });
  }
  hull.box([12, 1.4, 3], SHADE.edge, { at: [0, topAt(13), 13] });
  charge.box([5, 0.4, 2], WHITE, { at: [0, topAt(22) + 0.05, 22] });
}

/** Its scaly back: rows of scutes, moss in the hollows, river stones, a vent and the ring dome. */
function drawBack(p: EnemyParts): void {
  const { hull, neon, charge, muzzle } = p;
  for (const [x, from, to, step] of SCUTE_ROWS) {
    const points: Vec3[] = [];
    for (let z = from; z <= to; z += step) points.push([x, topAt(z) - 0.3, z]);
    scutes(hull, points, Math.abs(x) < 6 ? 2.2 : 1.8);
  }
  moss(
    hull,
    [
      [-3, -36],
      [3, -34],
      [2, -22],
      [-2, -24],
    ],
    topAt(-30) + 0.1,
  );
  moss(
    hull,
    [
      [6, -2],
      [13, 0],
      [11, 8],
      [5, 6],
    ],
    topAt(3) - 0.2,
  );
  stone(hull, [-11, topAt(6) - 0.8, 6], 2.6, 0.4);
  stone(hull, [9, topAt(-34) - 0.6, -34], 2, 1.2);
  vent(hull, [0, topAt(-2) + 0.1, 1], [8, 5], 3);
  const [emitter] = CROC_DOME;
  if (!emitter) return;
  const top = bossPoint(...emitter);
  const base: Vec3 = [top[0], topAt(top[2]) - 0.5, top[2]];
  hull.lathe(
    DOME.map(([r, y]) => [r, y * ((top[1] - base[1] - 0.6) / 5.4)] as const),
    8,
    H.panel,
    { at: base },
  );
  neon.ring(6.7, 0.7, 8, N, { at: offset(base, 0, 0.6, 0) });
  charge.cylinder(1.5, 0.6, 6, WHITE, { at: offset(top, 0, -0.6, 0) }, 0.8);
  muzzle(top, 'ring');
}

/**
 * P09-R09: the Mangrove Croc, a long, low hover-gunboat 3 L long, green neon: a crocodile's
 * scaly armoured hull on a hover skirt, raised neon eyes, jaws opening and closing around the
 * jaw cannon in its throat, two side pontoons with fan guns, moss and vines from the delta.
 */
export function buildMangroveCroc(scene: Scene): EnemyModel {
  return buildBossModel(MANGROVE_CROC, scene, N, {
    core: (p) => {
      drawHull(p);
      drawHead(p);
      drawBack(p);
      for (const s of SIDES) reactorSac(p, [s * 4, 3, -45], 2.2, N, { flesh: F.sinew });
    },
    parts: { 'jaw-cannon': jawCannon, 'pontoon-left': pontoon, 'pontoon-right': pontoon },
    limbs: CROC_JAWS,
  });
}

import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { EnemyModel } from '../../../../render/game-view';
import { OWL_CHIN_GUNS, OWL_CROWN, SNOW_OWL } from '../../../config/bosses/world-2/snow-owl';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { canopyPaint, FIGHTER_SECTION, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { lamps, seam, vent } from '../mini-boss-greebles';
import { H, QUARTER, scaled, SHADE, socket, WHITE } from '../mini-boss-shapes';
import { eye, FROST, icicles, ICE, OWL_WHITE, radarPod } from './snow-owl-parts';

// P08-R10, 2-3: the Snow Owl. Logical pixels, nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];

/** Navigation lights: red to port (+X, the screen's left), green to starboard. */
const PORT_RED = [1, 0.1, 0.12] as const;
const STARBOARD_GREEN = [0.2, 1, 0.35] as const;

/** The right wing seen from above, from the leading edge's root out to the tip and back. */
const HALF_WING = [
  [0, 15],
  [14, 14],
  [28, 10],
  [40, 5],
  [48, 1],
  [51, -3],
  [49, -7],
  [45, -8],
  [42, -6],
  [39, -10],
  [35, -8],
  [31, -12],
  [27, -10],
  [22, -14],
  [14, -14],
  [6, -17],
  [0, -18],
] as const;
/** Both wings: an owl's broad, rounded wing, its trailing edge cut into feathers. */
const WING: OutlinePoint[] = [
  ...HALF_WING,
  ...HALF_WING.slice(1, -1)
    .reverse()
    .map(([x, z]): OutlinePoint => [-x, z]),
];
/** The leading edge's neon, root to tip (one wing; mirrored for the other). */
const LEADING_EDGE = [
  [5, 13.6],
  [14, 12.8],
  [28, 8.8],
  [40, 3.8],
  [47, 0.4],
] as const;
/** The body along the centre line (loft stations: z, half width, bottom, top). */
const BODY = [
  [-27, 5, -1, 6],
  [-18, 10, -3, 10],
  [-4, 13, -4, 12],
  [10, 12, -3, 11],
  [20, 9, -2, 8],
  [24, 5, 0, 5],
] as const;
/** Where the trailing edge's icicles hang (one wing; mirrored for the other). */
const WING_ICICLES: Vec3[] = [
  [43, -1, -6.5],
  [37, -1, -8],
  [29, -1, -10],
  [20, -1, -12.5],
];

/** The wings: dark metal under a crust of snow, white neon along their leading edges. */
function drawWings({ hull, neon }: EnemyParts): void {
  hull.bevelSlab(WING, [-1.2, 0, 1.6], [0.8, 1.2], H.base, {}, H.panel);
  // Snow lies on the front of the wings; the feathers behind stay dark.
  hull.bevelSlab(scaled(WING, 0.86, 0, 2), [1.5, 1.7, 2.1], [0, 0.5], ICE, {}, FROST);
  for (const s of SIDES) {
    LEADING_EDGE.slice(1).forEach(([x, z], i) => {
      const [ax, az] = LEADING_EDGE[i] ?? [x, z];
      seam(neon, [s * ax, az], [s * x, z], [1.6, 0.8, 0.7], OWL_WHITE);
    });
    // Feather lines across the trailing edge.
    for (const [x, z] of [
      [45, -3],
      [38, -5],
      [30, -7],
      [21, -9],
    ] as const) {
      seam(hull, [s * x, z + 4], [s * (x - 2), z - 3], [1.7, 0.6, 0.4], H.dark);
    }
    icicles(hull, WING_ICICLES, s);
    socket(hull, [s * 38, 1.6, 2], 8, 1);
  }
  lamps(neon, [[50.5, 0.4, -3]], 1.4, PORT_RED);
  lamps(neon, [[-50.5, 0.4, -3]], 1.4, STARBOARD_GREEN);
}

/** The body: a rounded fuselage, snow on its back, ear tufts, vents and twin reactors. */
function drawBody(p: EnemyParts): void {
  const { hull, neon } = p;
  hull.loft(FIGHTER_SECTION, BODY, H.panel, {}, { paint: canopyPaint([1, 2], FROST) });
  // The neck holding the eye's housing.
  hull.cylinder(6, 5, 8, H.dark, { at: [0, 5, 23], pitch: QUARTER, yaw: Math.PI / 8 });
  for (const s of SIDES) {
    // Ear tufts, swept back over the head, a white light on each tip.
    hull.box([2.4, 9, 4], H.base, { at: [s * 6.5, 8, 15], roll: -s * 0.45, pitch: -0.5 }, FROST);
    neon.box([1.2, 1.2, 1.2], OWL_WHITE, { at: [s * 9.9, 14.6, 10.7] });
    vent(hull, [s * 8, 8.6, -10], [3.5, 7], 3, s * 0.15);
    neon.box([0.6, 0.4, 14], OWL_WHITE, { at: [s * 10.6, 6.2, -8], yaw: s * 0.05 });
    p.reactor([s * 4, 2.5, -27.2], 2.6);
  }
  seam(hull, [0, 2], [0, -20], [11, 0.8, 0.5], H.dark);
}

/** The crown emitter on the back (its rings) and the chin guns either side of the eye. */
function drawGuns({ hull, neon, charge, muzzle }: EnemyParts): void {
  const [crown] = OWL_CROWN.map((m) => bossPoint(...m));
  if (crown) {
    hull.cylinder(3.4, 1.5, 8, H.base, { at: [crown[0], crown[1] - 2, crown[2]] });
    neon.ring(3.5, 0.4, 8, OWL_WHITE, { at: [crown[0], crown[1] - 1.2, crown[2]] });
    charge.cylinder(2, 0.5, 8, WHITE, { at: [crown[0], crown[1] - 0.5, crown[2]] });
    muzzle(crown, 'ring');
  }
  for (const tip of OWL_CHIN_GUNS.map((m) => bossPoint(...m))) {
    const [x, y, z] = tip;
    hull.box([5, 4.5, 9], H.base, { at: [x, y - 2.6, z - 12] }, H.panel);
    hull.cylinder(1.3, 9.4, 6, H.dark, { at: [x, y, z - 10], pitch: QUARTER });
    charge.cylinder(1.35, 0.6, 6, WHITE, { at: [x, y, z - 0.6], pitch: QUARTER });
    muzzle(tip);
  }
}

/**
 * P08-R10: the Snow Owl, a wide-winged recon drone with white neon: snow on its broad wings,
 * two radar pods with turning antennas on them and a big round sensor eye at its front.
 */
export function buildSnowOwl(scene: Scene): EnemyModel {
  return buildBossModel(SNOW_OWL, scene, OWL_WHITE, {
    core: (p) => {
      drawWings(p);
      drawBody(p);
      drawGuns(p);
      p.hull.box([12, 0.4, 3], SHADE.edge, { at: [0, 11.5, 2] });
    },
    parts: { 'pod-left': radarPod, 'pod-right': radarPod, eye },
  });
}

import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { EnemyModel } from '../../../../render/game-view';
import { OWL_CHIN_GUNS, OWL_CROWN, SNOW_OWL } from '../../../config/bosses/world-2/snow-owl';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { canopyPaint, FIGHTER_SECTION, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { lamps, seam } from '../mini-boss-greebles';
import { H, QUARTER, scaled, SHADE, WHITE } from '../mini-boss-shapes';
import { ribs } from '../../../../render/geometry/organic';
import { reactorSac } from '../../enemies/organic-parts';
import { eye, icicles, OWL_WHITE, radarPod } from './snow-owl-parts';
import { crystals, gland, ICE_FLESH, sinew, spineRow } from './w2-organic';

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
function drawWings({ hull, flesh, neon }: EnemyParts): void {
  // P16-R05: broad membrane wings on bone struts, rime on their fronts; too big to flutter.
  flesh.bevelSlab(WING, [-1.2, 0, 1.6], [0.8, 1.2], ICE_FLESH.membrane, {}, ICE_FLESH.purple);
  flesh.bevelSlab(
    scaled(WING, 0.86, 0, 2),
    [1.5, 1.7, 2.1],
    [0, 0.5],
    ICE_FLESH.teal,
    {},
    ICE_FLESH.rime,
  );
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
      sinew(flesh, [s * 6, 2.4, 2], [s * (x - 2), 2, z - 3], 0.7, ICE_FLESH.bone, [0, 0.6, 4]);
    }
    sinew(flesh, [s * 5, 2.4, 10], [s * 50, 1.8, -2], 1.1, ICE_FLESH.bone, [0, 1, 6]);
    icicles(flesh, WING_ICICLES, s);
    hull.ring(8, 1, 8, H.panel, { at: [s * 38, 1.6, 2] });
  }
  lamps(neon, [[50.5, 0.4, -3]], 1.4, PORT_RED);
  lamps(neon, [[-50.5, 0.4, -3]], 1.4, STARBOARD_GREEN);
}

/** The body: a rounded fuselage, snow on its back, ear tufts, vents and twin reactors. */
function drawBody(p: EnemyParts): void {
  const { hull, flesh, neon } = p;
  // P16-R05: a plump body of cold flesh, ribbed, a sinewy neck holding the great eye.
  hull.ring(6.4, 1.2, 8, H.panel, { at: [0, 5, 21], pitch: QUARTER });
  flesh.loft(
    FIGHTER_SECTION,
    BODY,
    ICE_FLESH.teal,
    {},
    { paint: canopyPaint([1, 2], ICE_FLESH.rime) },
  );
  ribs(flesh, [-16, -8, 0], { halfWidth: 11, y: 4, height: 7, thickness: 0.7 }, ICE_FLESH.bone);
  flesh.cylinder(6, 5, 7, ICE_FLESH.sinew, { at: [0, 5, 23], pitch: QUARTER, yaw: Math.PI / 8 });
  for (const s of SIDES) {
    // Ear tufts, swept back over the head, a white light on each tip.
    flesh.box(
      [2.4, 9, 4],
      ICE_FLESH.purple,
      { at: [s * 6.5, 8, 15], roll: -s * 0.45, pitch: -0.5 },
      ICE_FLESH.rime,
    );
    neon.box([1.2, 1.2, 1.2], OWL_WHITE, { at: [s * 9.9, 14.6, 10.7] });
    gland(p, [s * 7, 9.4, -10], 1.2, OWL_WHITE);
    crystals(flesh, [s * 5, 9, -20], 2.6);
    neon.box([0.6, 0.4, 14], OWL_WHITE, { at: [s * 10.6, 6.2, -8], yaw: s * 0.05 });
    reactorSac(p, [s * 4, 2.5, -27.2], 2.6, OWL_WHITE, { flesh: ICE_FLESH.purple });
  }
  spineRow(flesh, [0, 12, 4], [0, 9, -18], 4, 2.6);
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
 * P16-R05: now a living owl of cold flesh with membrane wings on bone, its radomes grafted on
 * swollen nacelles, its eye a real eye in a lid of flesh.
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

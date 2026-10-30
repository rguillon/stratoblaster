import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { EnemyModel } from '../../../../render/game-view';
import {
  AURORA_COLLAR,
  AURORA_HUB_GUNS,
  AURORA_STATION,
} from '../../../config/bosses/world-2/aurora-station';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { POD_SECTION, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { lamps, plate, rect, seam } from '../mini-boss-greebles';
import { curve, organ, tendril } from '../../../../render/geometry/organic';
import { reactorSac } from '../../enemies/organic-parts';
import { crystals, glowVein, ICE_FLESH, sinew } from './w2-organic';
import { H, QUARTER, SHADE, socket, WHITE } from '../mini-boss-shapes';
import {
  AURORA_GREEN,
  AURORA_VIOLET,
  cryoCannon,
  cryoTurret,
  dish,
  emitter,
  emitterTurret,
  hangar,
  iced,
  icicles,
} from './aurora-station-parts';

// P08-R10, 2-3: the Aurora Station. Logical pixels, nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];

/** The hub: a wide octagonal drum (a lathe profile). */
const HUB = [
  [0, -6],
  [20, -6],
  [25, -2],
  [25, 3],
  [21, 7],
  [0, 7],
] as const;
/** An eighth of a turn: the octagons' flat faces to the front. */
const EIGHTH = Math.PI / 8;
/** A habitat module behind the hub (loft stations; one either side of the centre line). */
const HABITAT = [
  [-56, 4, -2, 6],
  [-50, 7, -3, 9],
  [-26, 7, -3, 9],
  [-20, 5, -1, 7],
] as const;
/** A radiator wing behind the truss (the right one; mirrored for the left). */
const RADIATOR: OutlinePoint[] = [
  [20, -24],
  [76, -26],
  [84, -32],
  [84, -46],
  [20, -48],
];
/** Where the radiators' icicles hang (one radiator; mirrored for the other). */
const RADIATOR_ICICLES: Vec3[] = [
  [30, -0.6, -47],
  [46, -0.6, -46.5],
  [62, -0.6, -46],
  [78, -0.6, -45],
];

/** The hub, its module and the mast the turning dish stands on; the collar its spirals leave. */
function drawHub(p: EnemyParts): void {
  const { hull, flesh, neon, charge, muzzle } = p;
  // P16-R06: the bell of a great ice jellyfish, a metal collar grafted round its crown.
  flesh.lathe(HUB, 8, ICE_FLESH.purple, { yaw: EIGHTH });
  flesh.cylinder(20.5, 0.3, 8, ICE_FLESH.rime, { at: [0, 7, 0], yaw: EIGHTH });
  neon.ring(25.1, 1, 8, AURORA_GREEN, { at: [0, -0.5, 0], yaw: EIGHTH });
  hull.cylinder(11, 6, 8, H.panel, { at: [0, 7, 0], yaw: EIGHTH }, 10);
  for (const a of [0, 1, 2, 3, 4, 5]) {
    const yaw = (a * Math.PI) / 3 + 0.3;
    glowVein(
      p,
      [Math.sin(yaw) * 11, 7.4, Math.cos(yaw) * 11],
      [Math.sin(yaw) * 23, 3, Math.cos(yaw) * 23],
      1,
      AURORA_GREEN,
    );
  }
  neon.ring(10.9, 0.8, 8, AURORA_VIOLET, { at: [0, 9.5, 0], yaw: EIGHTH });
  for (const collar of AURORA_COLLAR.map((m) => bossPoint(...m))) {
    charge.cylinder(4.2, 1, 8, WHITE, { at: [collar[0], collar[1] - 1, collar[2]] });
    muzzle(collar, 'ring');
    hull.cylinder(1.8, 5, 6, H.dark, { at: collar });
  }
  for (const s of SIDES) {
    crystals(flesh, [s * 16, 6.5, -8], 3.5);
    socket(hull, [s * 36, 1, 40], 7.5, 0.8);
  }
}

/** The truss: a girder across to the cryo cannons, struts to the emitters, the hangar's spine. */
function drawTruss({ hull, flesh, neon }: EnemyParts): void {
  // P16-R06: a spine of bone across to the cryo bladders, arms of sinew out to the emitters.
  flesh.box([10, 5, 26], ICE_FLESH.sinew, { at: [0, -1, 33] }, ICE_FLESH.rime);
  for (const s of SIDES) {
    tendril(
      flesh,
      curve([s * 20, 0, -4], [s * 58, 0, -4], [0, 2, 1], 3),
      [3, 2.2],
      5,
      ICE_FLESH.bone,
    );
    sinew(flesh, [s * 15, 0, 14], [s * 33, 0, 36], 2.2, ICE_FLESH.sinew);
    for (const x of [30, 42]) organ(flesh, 2.6, 5, ICE_FLESH.bone, { at: [s * x, -2.5, -4] }, 0.9);
    hull.ring(3.2, 1.2, 6, H.panel, { at: [s * 50, 0, -4], roll: QUARTER });
    neon.box([30, 0.5, 0.6], s > 0 ? AURORA_GREEN : AURORA_VIOLET, {
      at: [s * 38, 0.6, -0.4],
    });
  }
}

/** The habitat modules behind the hub (violet windows) and their reactors. */
function drawHabitats(p: EnemyParts): void {
  const { hull, neon } = p;
  for (const s of SIDES) {
    p.flesh.loft(POD_SECTION, HABITAT, ICE_FLESH.membrane, { at: [s * 12, 0, 0] }, { paint: iced });
    lamps(
      neon,
      [-28, -34, -40, -46].map((z): Vec3 => [s * 19, 4, z]),
      1.2,
      AURORA_VIOLET,
    );
    reactorSac(p, [s * 12, 2.5, -56], 3.4, AURORA_GREEN, { flesh: ICE_FLESH.purple });
  }
  tendril(p.flesh, curve([0, 0, -20], [0, 0, -52], [0, 2, 0], 3), [2.6, 1], 5, ICE_FLESH.sinew);
  plate(hull, rect(5, 8), [2.8, 0.5], H.panel, { at: [0, 0, -30] });
}

/** The radiator wings behind the truss: iced panels, dark ribs, a green edge light. */
function drawRadiators({ hull, flesh, neon }: EnemyParts): void {
  for (const s of SIDES) {
    // P16-R06: frilled membrane fins on bone rays, where the radiators were; too big to flutter.
    const outline = RADIATOR.map(([x, z]): OutlinePoint => [s * x, z]);
    flesh.bevelSlab(outline, [-0.6, 0, 1], [0.4, 0.6], ICE_FLESH.membrane, {}, ICE_FLESH.teal);
    for (const x of [30, 42, 54, 66, 78]) {
      sinew(flesh, [s * (x - 4), 1, -25], [s * x, 1, -46.5], 0.6, ICE_FLESH.bone, [0, 0.4, 0]);
    }
    seam(neon, [s * 84.2, -32], [s * 84.2, -46], [0.2, 0.5, 0.6], AURORA_GREEN);
    seam(hull, [s * 18, -30], [s * 21, -30], [0, 3, 3], H.panel);
    icicles(flesh, RADIATOR_ICICLES, s);
  }
}

/** The hub guns either side of the hangar's spine (the core's aimed shots, bursts and fans). */
function drawGuns({ hull, charge, muzzle }: EnemyParts): void {
  for (const tip of AURORA_HUB_GUNS.map((m) => bossPoint(...m))) {
    const [x, y, z] = tip;
    hull.box([4, 4.5, 6], H.panel, { at: [x, y - 3, z - 7] }, SHADE.edge);
    hull.cylinder(1.3, 6.4, 6, H.dark, { at: [x, y, z - 7], pitch: QUARTER });
    charge.cylinder(1.35, 0.6, 6, WHITE, { at: [x, y, z - 0.6], pitch: QUARTER });
    muzzle(tip);
  }
}

/**
 * P08-R10: the Aurora Station, a flying research station in green and violet neon: a hub under
 * a slowly turning dish, two dish emitters and a drone hangar at its nose, two cryo cannons at
 * the ends of its truss, habitat modules and iced radiator wings behind.
 * P16-R06: now a living ice jellyfish, a bell of cold flesh under a frilled crown, a bone spine
 * out to its cryo bladders, egg sacs and membrane fins behind, metal grafts on its guns.
 */
export function buildAuroraStation(scene: Scene): EnemyModel {
  return buildBossModel(AURORA_STATION, scene, AURORA_GREEN, {
    core: (p) => {
      drawHub(p);
      drawTruss(p);
      drawHabitats(p);
      drawRadiators(p);
      drawGuns(p);
    },
    ring: dish,
    parts: {
      'emitter-left': emitter,
      'emitter-right': emitter,
      'cryo-left': cryoCannon,
      'cryo-right': cryoCannon,
      hangar,
    },
    turrets: {
      'cryo-left': cryoTurret,
      'cryo-right': cryoTurret,
      'emitter-left': emitterTurret,
      'emitter-right': emitterTurret,
    },
  });
}

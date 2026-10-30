import type { SolidBuilder } from '../../../../render/geometry/solids';
import { BOSS_LOOK } from '../../../config/boss-look';
import { mirror } from '../../../config/bosses/boss-kit';
import { AURORA_EMITTER } from '../../../config/bosses/world-2/aurora-station';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { POD_SECTION, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint } from '../boss-model';
import { organ, ribs } from '../../../../render/geometry/organic';
import { lamps, plate, rect } from '../mini-boss-greebles';
import { crystals, gland, ICE_FLESH } from './w2-organic';
import { conduit } from '../mini-boss-mechanism';
import { H, offset, QUARTER, SHADE, turret, WHITE } from '../mini-boss-shapes';

// P08-R10, 2-3: the Aurora Station's parts (dish emitters, cryo cannons, drone hangar), its
// turning dish and its frost. Logical pixels, nose +Z, Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** The Aurora Station's green neon, and the violet one it shares its lights with. */
export const AURORA_GREEN: Rgb = BOSS_LOOK.neon['aurora-station'] ?? [0.3, 1, 0.55];
export const AURORA_VIOLET: Rgb = [0.62, 0.3, 1];
/** Snow lying on its top faces, and the bluer ice of its crust and icicles (World 2 frost). */
export const FROST: Rgb = [0.75, 0.82, 0.9];
export const ICE: Rgb = ICE_FLESH.crystal;

/** Icicles hanging from each point (`[x, y, z]`, `x` times `side`): thin cones of ice. */
export function icicles(hull: SolidBuilder, points: readonly Vec3[], side = 1): void {
  points.forEach(([x, y, z], i) => {
    const length = 3.5 + (i % 3) * 1.3;
    hull.cylinder(0.9, length, 4, ICE, { at: [side * x, y, z], pitch: Math.PI }, 0);
  });
}

/** A dish: a shallow bowl `r` wide around its axis (a lathe profile). */
const bowl = (r: number) =>
  [
    [0.4, 0],
    [r, r * 0.35],
    [r * 0.8, r * 0.45],
    [0, r * 0.2],
  ] as const;

/** A dish emitter's pylon around its centre `at` (P08-R10): its dish turns on it. */
export function emitter(p: EnemyParts, at: Vec3): void {
  // P16-R06: a swollen node of flesh at the end of its arm, a metal socket for the dish.
  organ(p.flesh, 7, 6, ICE_FLESH.purple, { at: offset(at, 0, -2, -3) }, 0.5);
  p.hull.box([4, 6, 5], H.panel, { at: offset(at, 0, 2, -3) }, H.base);
  gland(p, offset(at, Math.sign(at[0]) * 5, 2, -6), 1, AURORA_GREEN);
}

/**
 * A dish emitter's turret, turning on its pylon (phase 8 review: it aims its laser): an upright
 * dish facing down the screen, struts holding its projector at the focus, where the laser
 * leaves from.
 */
export function emitterTurret(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  // The right emitter (screen right) is on the model's -X side.
  const lasers = at[0] < 0 ? AURORA_EMITTER : mirror(AURORA_EMITTER);
  const [tip] = lasers.map((m) => bossPoint(...m));
  if (!tip) return;
  const [x, y, z] = tip;
  const forward = { pitch: QUARTER };
  hull.lathe(bowl(9), 10, SHADE.edge, { at: [x, y, z - 15], ...forward });
  neon.ring(9.1, 0.6, 10, AURORA_VIOLET, { at: [x, y, z - 12.2], ...forward });
  hull.cylinder(1.4, 10, 6, H.dark, { at: [x, y, z - 11], ...forward });
  neon.ring(1.8, 0.6, 6, AURORA_GREEN, { at: [x, y, z - 5], ...forward });
  charge.cylinder(2, 1, 8, WHITE, { at: [x, y, z - 1], ...forward });
  muzzle(tip, 'laser');
  for (const [dx, dy] of [
    [7.5, -2],
    [-7.5, -2],
    [0, 8.5],
  ] as const) {
    conduit(hull, [x + dx, y + dy, z - 12], [x, y, z - 3], 0.4, 0);
  }
  // Snow caught on the dish's top rim, icicles under its lower rim.
  hull.box([8, 1, 2.4], FROST, { at: [x, y + 8.6, z - 12.4] });
  icicles(p.flesh, [
    [x + 4, y - 7.5, z - 12],
    [x - 3, y - 8.3, z - 12],
  ]);
}

/** A cryo cannon's tank (loft stations around the part's centre), its top iced over. */
const TANK = [
  [-20, 6, -4, 4],
  [-12, 12, -5, 6],
  [6, 12, -5, 6],
  [14, 7, -3, 4],
] as const;

/**
 * A cryo cannon's body around its centre `at` (P08-R10): a cryogenic tank on the station's
 * truss, iced over, two coolant flasks behind its turret ({@link cryoTurret}).
 */
export function cryoCannon(p: EnemyParts, at: Vec3): void {
  const { flesh, neon } = p;
  // P16-R06: a cryo bladder of flesh, rimed over, two glands of coolant behind its gun.
  flesh.loft(POD_SECTION, TANK, ICE_FLESH.teal, { at: [at[0], 0, at[2]] }, { paint: iced });
  ribs(
    flesh,
    [at[2] - 8, at[2]],
    { halfWidth: 12, y: -2, height: 7, thickness: 0.7 },
    ICE_FLESH.bone,
    { at: [at[0], 0, 0] },
  );
  for (const s of SIDES) {
    const flask = offset(at, s * 6, 6, -14);
    organ(flesh, 3.6, 6, ICE_FLESH.membrane, { at: flask }, 0.7);
    neon.ring(3.7, 0.6, 8, AURORA_VIOLET, { at: offset(flask, 0, 2, 0) });
    neon.box([0.6, 0.4, 14], AURORA_GREEN, { at: offset(at, s * 12.3, 1, -3) });
  }
  icicles(flesh, [offset(at, 6, -4, 9), offset(at, -2, -4.5, 10), offset(at, -8, -4, 6)]);
}

/** Ice on the top of a {@link POD_SECTION} loft (its side 2). */
export function iced(side: number): Rgb | undefined {
  return side === 2 ? ICE_FLESH.rime : undefined;
}

/** A cryo cannon's turret: a single wide-bored barrel, a violet ring round its foot. */
export function cryoTurret(p: EnemyParts, at: Vec3): void {
  turret(p, offset(at, 0, 6, 0), {
    radius: 11,
    barrels: 1,
    gap: 0,
    bore: 2.6,
    length: 9,
    neon: AURORA_VIOLET,
    hatch: -Math.sign(at[0]),
  });
}

/**
 * The drone hangar around its centre `at` (P08-R10): a snow-roofed bay at the station's nose,
 * its open door framed in violet, where its Hornets leave from.
 */
export function hangar(p: EnemyParts, at: Vec3): void {
  const { hull, flesh, neon } = p;
  // P16-R06: a brood pouch of flesh at the nose, its mouth framed in violet.
  flesh.bevelSlab(rect(26, 24), [-3, 0, 8], [1, 3], ICE_FLESH.sinew, { at }, ICE_FLESH.rime);
  flesh.box([18, 7, 0.8], ICE_FLESH.seam, { at: offset(at, 0, -1.5, 11.8) });
  neon.box([20, 0.8, 0.6], AURORA_VIOLET, { at: offset(at, 0, 5.6, 12.2) });
  for (const s of SIDES) {
    neon.box([0.8, 7, 0.6], AURORA_VIOLET, { at: offset(at, s * 9.8, -1.4, 12.2) });
    lamps(neon, [offset(at, s * 11, 8, 9), offset(at, s * 11, 8, -9)], 1.2, AURORA_GREEN);
  }
  plate(hull, rect(10, 6), [8, 0.8], H.panel, { at: offset(at, 0, 0, -4) });
  crystals(flesh, offset(at, -8, 8, 2), 3.5);
  icicles(flesh, [offset(at, 6, 5.5, 12.4), offset(at, 0, 5.5, 12.4), offset(at, -6, 5.5, 12.4)]);
}

/** The dish's tilt: it looks up and forward, and turns with the boss's spin. */
const DISH_TILT = 0.6;

/**
 * The big dish on top (P08-R10), drawn on the model's ring so that it turns slowly: a snow-filled
 * bowl on a turntable, a violet rim, and its feed horn lit green at the focus.
 */
export function dish({ hull, flesh, neon }: EnemyParts): void {
  // P16-R06: the crown, a frilled bowl of membrane turning on its stalk.
  const tilt = { pitch: DISH_TILT };
  const axis = (along: number): Vec3 => [
    0,
    19 + along * Math.cos(DISH_TILT),
    along * Math.sin(DISH_TILT),
  ];
  hull.cylinder(4, 2, 8, H.panel, { at: [0, 17, 0] });
  flesh.lathe(bowl(15), 12, ICE_FLESH.membrane, { at: axis(0), ...tilt });
  neon.ring(15.1, 0.6, 12, AURORA_VIOLET, { at: axis(4.9), ...tilt });
  flesh.cylinder(0.9, 10, 4, ICE_FLESH.sinew, { at: axis(0), ...tilt });
  neon.box([2.2, 2.2, 2.2], AURORA_GREEN, { at: axis(10), ...tilt });
  hull.box([5, 4, 3], H.base, { at: [0, 15.5, -4] }, SHADE.edge);
}

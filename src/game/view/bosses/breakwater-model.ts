import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import { BOSS_LOOK } from '../../config/boss-look';
import { BREAKWATER } from '../../config/bosses/mini-bosses';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { decal, flipX, SIDES } from '../enemies/enemy-shapes';
import { buildBossModel } from './boss-model';
import { cog, conduit, glowLine, ram } from './mini-boss-mechanism';
import { dish, hazard, lamps, mast, plate, seam, vent } from './mini-boss-greebles';
import { H, neonBand, offset, scaled, SHADE, socket, turret } from './mini-boss-shapes';

// P07-R05, 1-2: the Breakwater. Logical pixels, nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];

const ORANGE = BOSS_LOOK.neon.breakwater ?? [1, 0.5, 0.05];

/** The barge's hull seen from above: a long, square-cut hull, bulging where the mortars sit. */
const BARGE_HULL = [
  [-24, 27],
  [24, 27],
  [31, 20],
  [31, 6],
  [39, 0],
  [39, -24],
  [31, -30],
  [31, -34],
  [24, -40],
  [-24, -40],
  [-31, -34],
  [-31, -30],
  [-39, -24],
  [-39, 0],
  [-31, 6],
  [-31, 20],
] as const;
/** Heights of the hull: its keel, its widest line, its deck. */
const HULL_Y = [-5, -1, 4] as const;
/**
 * The left (+X) gunwale's armour blocks, bow to stern (mirrored on the right): fat plates along
 * the deck's edge, with gaps where the machinery driving the ramp and mortars shows through.
 */
const GUNWALE = [
  [
    [21, 22],
    [27, 17],
    [27, 10.5],
    [22.3, 10.5],
    [21, 12],
  ],
  [
    [27, 3],
    [27, -23],
    [21, -23],
    [21, -16],
    [23, -12],
    [23, 3],
  ],
  [
    [27, -29],
    [27, -32],
    [21, -36],
    [21, -29],
  ],
] as const;
/** The hold between the gunwales: a dark floor, and the bow ramp sloping down at its front. */
const HOLD = [
  [-20, 18],
  [20, 18],
  [20, -18],
  [-20, -18],
] as const;
const RAMP = [
  [-16, 27],
  [16, 27],
  [18, 19],
  [-18, 19],
] as const;
/** The bridge tower at the stern, and its visor (along the tower's front, just under its top). */
const TOWER = [
  [-12, -18],
  [12, -18],
  [15, -24],
  [15, -34],
  [-15, -34],
  [-15, -24],
] as const;
const VISOR = [
  [-10, -18.4],
  [10, -18.4],
  [12.4, -23.2],
  [11.2, -23.2],
  [9.2, -19.6],
  [-9.2, -19.6],
  [-11.2, -23.2],
  [-12.4, -23.2],
] as const;
/** The ram plate around its centre: a V of chamfered armour over the bow. */
const PLATE = [
  [0, 17],
  [20, 5],
  [21, -5],
  [15, -10],
  [-15, -10],
  [-21, -5],
  [-20, 5],
] as const;
/** A patch welded over a dent in the plate's left half. */
const DENT = [
  [-4, 3],
  [-12, -0.5],
  [-11, -5],
  [-4, -4],
] as const;
/** The plate's right warning light, along its upper front edge (mirrored for the left). */
const PLATE_LIGHT = [
  [1, 12.5],
  [15.5, 3.6],
  [15, 2.2],
  [1, 10.8],
] as const;
/** An armour plate over a pit beside the tower, around its centre. */
const PIT_PLATE = [
  [-2.6, -3],
  [2.6, -3],
  [2.6, 2.6],
  [-2.6, 3.4],
] as const;
/** A scorch across the starboard gunwale's bow end. */
const SCAR = [
  [-22.5, 11],
  [-26, 14],
  [-25.5, 18],
  [-23, 16.5],
  [-22, 14],
] as const;
/** A mortar's mounting plate on its sponson (an octagon, in units of the part's radius). */
const MOUNT = Array.from({ length: 8 }, (_, k) => {
  const a = (2 * Math.PI * (k + 0.5)) / 8;
  return [Math.sin(a), Math.cos(a)] as const;
});

/** The hull, the gunwales, the hold with its ramp and the bridge tower. */
function drawBody({ hull, neon }: EnemyParts): void {
  const deck = HULL_Y[2];
  hull.bevelSlab(BARGE_HULL, HULL_Y, [3, 2.5], H.base, {}, H.panel);
  neonBand(neon, BARGE_HULL, [-1.4, -0.4], [1.02, 1.02], ORANGE);
  for (const block of GUNWALE) {
    for (const wall of [block, flipX(block)]) {
      hull.bevelSlab(wall, [deck, deck, 10], [0, 1.8], H.base, {}, H.panel);
    }
  }
  hull.slab(HOLD, [deck, deck + 0.4], H.dark);
  hull.bevelSlab(RAMP, [-1, deck - 1, deck], [0, 0.8], H.panel, {}, H.dark);
  hull.bevelSlab(TOWER, [deck, deck, 14], [0, 2], H.base, {}, H.panel);
  neon.slab(VISOR, [11.2, 12.4], ORANGE);
}

/**
 * The hold, loaded unevenly: a closed hatch at the back, containers lashed to port (+X) beside
 * an empty bay, an open hatch at the front lit from inside, its cover folded up to starboard.
 */
function drawHold({ hull, neon }: EnemyParts): void {
  const floor = HULL_Y[2] + 0.4;
  hull.box([26, 0.6, 7], H.panel, { at: [0, floor, -11] });
  neon.box([27, 0.4, 0.6], ORANGE, { at: [0, floor + 0.1, -14.8] });
  for (const x of [-8, 0, 8]) seam(hull, [x, -14], [x, -8], [floor + 0.6, 0.6, 0.3], SHADE.edge);
  hull.box([9, 4, 6], H.panel, { at: [12, floor, 0] }, SHADE.edge);
  hull.box([7, 3, 6], SHADE.patch, { at: [3, floor, -0.5], yaw: 0.08 });
  hull.box([7, 2.6, 5], H.base, { at: [11.5, floor + 4, 0.5], yaw: -0.1 }, H.panel);
  hazard(hull, [-9, floor, 0], [10, 5], 5, 0);
  // The open hatch: a dark well with cargo lights, the cover leaning on the right gunwale.
  hull.box([22, 0.3, 6], SHADE.soot, { at: [0, floor, 11] });
  for (const x of [-7, 0, 7]) neon.box([3, 0.3, 0.6], ORANGE, { at: [x, floor + 0.3, 11] });
  hull.box([1.2, 7.5, 7], H.panel, { at: [-19.5, floor, 11], roll: -0.35 }, SHADE.edge);
}

/**
 * The machinery under the armour (phase 7 review): cogs, rams and lit conduits in the gaps
 * between the gunwales' blocks, and in the pits beside the tower, plated over unevenly.
 */
function drawMachinery({ hull, neon }: EnemyParts): void {
  const deck = HULL_Y[2];
  for (const s of SIDES) {
    glowLine(neon, [s * 21.5, deck + 0.6, 4.4], [s * 27, deck + 0.6, 4.4], 1.8, ORANGE);
    cog(hull, [s * 24.5, deck + 1.2, 8.2], 2.4, 7, s * 0.2);
    ram(hull, [s * 22, deck + 1.5, 1], [s * 22, deck + 3, 12], 1);
    glowLine(neon, [s * 21.5, deck + 0.6, -28.2], [s * 27, deck + 0.6, -28.2], 1.6, ORANGE);
    conduit(hull, [s * 21.5, deck + 1.8, -25], [s * 27, deck + 1.8, -25], 1.1, 2);
    cog(hull, [s * 18, deck, -21.5], 2.6, 8);
    cog(hull, [s * 18.6, deck, -26], 1.9, 6, 0.3);
    ram(hull, [s * 17, deck + 1, -33], [s * 19.5, deck + 4.5, -20], 1.1);
    conduit(hull, [s * 15.8, deck + 0.8, -19], [s * 15.8, deck + 0.8, -34], 0.7, 3);
    plate(hull, scaled(PIT_PLATE, 1, s * 18, -31), [deck, 3.6], H.base);
  }
  glowLine(neon, [17, deck + 0.4, -28.5], [20.5, deck + 0.4, -23.5], 0.6, ORANGE);
  // Starboard (-X) is plated over again, leaving a slot; port (+X) still shows its gears.
  plate(hull, scaled(PIT_PLATE, 0.9, -18, -23), [deck, 3.2], SHADE.patch);
}

/** A loading crane on the starboard (-X) gunwale, its boom swung over the hold. */
function drawCrane({ hull }: EnemyParts): void {
  const top = 10;
  hull.cylinder(1.6, 6, 6, H.panel, { at: [-24, top, -1] }, 1.2);
  const [ax, ay, az, bx, by, bz] = [-24, top + 6, -1, -11, top + 8, -7];
  const length = Math.hypot(bx - ax, by - ay, bz - az);
  hull.box([1.4, 1.4, length], H.base, {
    at: [(ax + bx) / 2, (ay + by) / 2 - 0.7, (az + bz) / 2],
    yaw: Math.atan2(bx - ax, bz - az),
    pitch: -Math.asin((by - ay) / length),
  });
  hull.box([0.3, by - 9, 0.3], H.dark, { at: [bx, 9, bz] });
  hull.box([1.8, 1.4, 1.8], SHADE.hazard, { at: [bx, 8.4, bz] });
}

/** The tower's roof: one funnel off to starboard, a radar dish and a mast to port, a vent. */
function drawTower(p: EnemyParts): void {
  const { hull } = p;
  const roof = 14;
  hull.box([3, 4, 3], H.panel, { at: [6, roof, -29] });
  dish(hull, [6, roof + 4, -29], 3.5, 0.5, 0.4);
  mast(p, [11, roof, -22], 8, ORANGE);
  hull.cylinder(2.8, 7, 8, H.panel, { at: [-8, roof, -28] }, 2.4);
  hull.cylinder(2.5, 0.4, 8, SHADE.soot, { at: [-8, roof + 7, -28] });
  hull.box([5.6, 0.6, 1], SHADE.hazard, { at: [-8, roof + 5, -25.6] });
  vent(hull, [0, roof, -25], [9, 4], 4, Math.PI / 2);
  seam(hull, [-12, -31.5], [12, -31.5], [roof, 0.6, 0.4], H.dark);
}

/** The deck's edges: running lights, bollards, hazard bands, a patched gunwale and a scar. */
function drawDeckEdges({ hull, neon }: EnemyParts): void {
  const [deck, top] = [HULL_Y[2], 10];
  for (const s of SIDES) {
    lamps(
      neon,
      [16, 2, -29].map((z): Vec3 => [s * 24.5, top, z]),
      1.2,
      ORANGE,
    );
    for (const z of [24, -37]) hull.cylinder(1.3, 1.8, 6, H.panel, { at: [s * 20, deck, z] }, 1.6);
    hazard(hull, [s * 24, top, 19.5], [3.2, 2], 3, s * 0.7);
    seam(hull, [s * 24.5, 2], [s * 24.5, -8], [top, 0.6, 0.3], H.dark);
  }
  hazard(hull, [0, deck, -36], [18, 2.2], 7, 0);
  plate(hull, rectAt(24.5, -15, 3.4, 9), [top, 0.5], SHADE.patch);
  seam(hull, [23, -11.5], [26, -11.5], [top + 0.5, 0.5, 0.3], SHADE.edge);
  seam(hull, [23, -18.5], [26, -18.5], [top + 0.5, 0.5, 0.3], SHADE.edge);
  plate(hull, SCAR, [top, 0.2], SHADE.soot);
}

/** A rectangle `w` by `d` centred on `(x, z)`. */
function rectAt(x: number, z: number, w: number, d: number): [number, number][] {
  return [
    [x - w / 2, z - d / 2],
    [x + w / 2, z - d / 2],
    [x + w / 2, z + d / 2],
    [x - w / 2, z + d / 2],
  ];
}

/**
 * P07-R05: the Breakwater, an armoured flying landing barge with orange neon: a long hull with
 * raised gunwales, a hold and a bow ramp, a bridge tower at the stern, a V-shaped ram plate over
 * its bow and two mortar turrets on its side sponsons.
 */
export function buildBreakwater(scene: Scene): EnemyModel {
  return buildBossModel(BREAKWATER, scene, ORANGE, {
    core: (p) => {
      drawBody(p);
      drawHold(p);
      drawMachinery(p);
      drawCrane(p);
      drawTower(p);
      drawDeckEdges(p);
      // The bow gun in the hold (the core's fans, bursts and rings).
      const gun = { radius: 7, barrels: 2, gap: 3, bore: 1.2, length: 6, neon: ORANGE };
      turret(p, [0, HULL_Y[2] + 0.4, 21], gun);
      for (const s of SIDES) {
        socket(p.hull, [s * 34, HULL_Y[2], -12], 8, 1);
        // The ram plate's brackets on the bow.
        p.hull.box([4, 3, 8], H.dark, { at: [s * 13, HULL_Y[2] - 1, 24] });
        p.reactor([s * 16, -0.5, -40], 3.4);
      }
      p.reactor([0, -0.5, -40], 3.8);
    },
    parts: { 'ram-plate': ramPlate, 'mortar-left': mortar, 'mortar-right': mortar },
  });
}

/** The ram plate (P07-R05): no weapon, a thick V of armour with orange warning lights. */
function ramPlate({ hull, neon }: EnemyParts, at: Vec3): void {
  const top = 9;
  hull.bevelSlab(PLATE, [-3, 1, top], [1.5, 4], H.panel, { at }, H.base);
  for (const light of [PLATE_LIGHT, flipX(PLATE_LIGHT)]) {
    const place = scaled(light, 1, at[0], at[2]);
    decal(neon, place, top + 0.05, ORANGE);
  }
  neonBand(neon, PLATE, [0.6, 1.8], [1.02, 1.02], ORANGE, { at });
  // A spine rib, bolted seams on the right half, a welded patch over a dent on the left.
  const on = (x: number, z: number): readonly [number, number] => [at[0] + x, at[2] + z];
  seam(hull, on(0, 11), on(0, -6), [top, 1.6, 0.8], SHADE.edge);
  for (const z of [3, -3]) seam(hull, on(3, z + 1), on(13, z - 1), [top, 0.6, 0.4], H.dark);
  plate(hull, scaled(DENT, 1, at[0], at[2]), [top, 0.6], SHADE.patch);
  hazard(hull, offset(at, 0, -3, -11), [16, 2], 6, 0);
}

/** A mortar turret (P07-R05): a mounting plate, a squat dome and a short, fat, raised barrel. */
function mortar(p: EnemyParts, at: Vec3): void {
  const r = BREAKWATER.stats.parts[1]?.radius ?? 13;
  const base = HULL_Y[2];
  p.hull.bevelSlab(
    scaled(MOUNT, r),
    [base - 1, base + 1, base + 3],
    [0.5, 1.5],
    H.base,
    { at },
    H.panel,
  );
  const s = Math.sign(at[0]);
  const gun = { radius: r, barrels: 1, gap: 0, bore: 3.6, length: 3, elevation: 0.6, neon: ORANGE };
  turret(p, offset(at, 0, base + 3, 0), { ...gun, hatch: s });
  if (s > 0) {
    // A ready rack of shells behind the port mortar.
    for (const a of [2.2, 2.6, 3, 3.4]) {
      const shell = offset(at, Math.sin(a) * 10.5, base + 3, Math.cos(a) * 10.5);
      p.hull.cylinder(1.1, 3, 6, SHADE.edge, { at: shell }, 0.6);
    }
  } else {
    // A fire-control box with its own antenna beside the starboard one.
    p.hull.box([3.5, 3, 4.5], H.panel, { at: offset(at, -9, base + 3, 3) }, SHADE.edge);
    mast(p, offset(at, -9, base + 6, 1.5), 5, ORANGE);
  }
}

import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { corners, pane, posts } from './polar-parts';
import { gableRoof, strut } from './jungle-parts';

// P09-R06: stilt villages, river ports and logging camps of World 3: bamboo and plank houses on
// stilts under thatch or corrugated roofs, with the neon trims of the future. Sizes in world
// units, standing on Y = 0; the front of a building faces -Z.

type Vec3 = readonly [number, number, number];

/** Height of the floors on stilts above the ground. */
const STILTS = 2.4;

/**
 * A stilt hut: a bamboo room on a plank deck on four stilts, under a steep thatched roof, a
 * ladder down to the ground, a lit window and a cyan neon trim under the front eave.
 */
export function buildStiltHut(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  posts(s, corners(3.4, 2.8), STILTS, C.woodDark, 0.45);
  s.box([8, 0.4, 7], C.wood, { at: [0, STILTS, -0.3] });
  s.box([6, 3.2, 4.6], C.bamboo, { at: [0, STILTS + 0.4, 0.4] });
  gableRoof(s, { size: [7.4, 6.6], y: STILTS + 3.4, rise: 3.2 }, C.thatch, C.bamboo, {
    at: [0, 0, 0.4],
  });
  strut(s, [-1.6, 0, -4.6], [-1.6, STILTS + 0.4, -3.6], [0.18, 0.18], C.woodDark);
  s.cylinder(0.08, 3.6, 3, C.metal, { at: [2.6, STILTS + 5.6, 1.6] });
  pane(l, [1.4, 1.1], [1.2, STILTS + 1.6, -1.96], L.window);
  l.box([7, 0.25, 0.25], L.cyan, { at: [0, STILTS + 3.2, -2.9] });
  l.box([0.4, 0.4, 0.4], L.red, { at: [2.6, STILTS + 9.2, 1.6] });
  return { structure: s.geometry, lights: l.geometry };
}

/**
 * A longhouse on stilts: a long plank house under a corrugated metal roof, a veranda along its
 * front, a water tank on legs at one end, a row of lit windows and a pink neon trim.
 */
export function buildLonghouse(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  const stilts = [-7, -2.4, 2.4, 7].flatMap((x): (readonly [number, number])[] => [
    [x, -3.8],
    [x, 3],
  ]);
  posts(s, stilts, STILTS, C.woodDark, 0.5);
  s.box([16.4, 0.4, 8.6], C.wood, { at: [0, STILTS, -0.4] });
  s.box([15, 3.6, 5.6], C.woodDark, { at: [0, STILTS + 0.4, 0.6] });
  gableRoof(s, { size: [16.6, 8.4], y: STILTS + 4, rise: 2.6 }, C.corrugated, C.wood, {
    at: [0, 0, 0.2],
  });
  s.cylinder(1.3, 2.6, 6, C.jungleMetal, { at: [9.2, STILTS + 0.4, 2] });
  posts(
    s,
    [
      [8.6, 1.4],
      [9.8, 2.6],
    ],
    STILTS,
    C.metalDark,
    0.3,
  );
  for (const x of [-5, -1, 3]) pane(l, [2, 1.3], [x, STILTS + 1.6, -2.26], L.window);
  l.box([15.6, 0.25, 0.25], L.pink, { at: [0, STILTS + 3.7, -3.9] });
  l.box([0.6, 0.6, 0.6], L.yellow, { at: [-7.6, STILTS + 3, -4.4] });
  return { structure: s.geometry, lights: l.geometry };
}

/** A log of radius `r`, `len` long along X from `at`, with pale cut ends (20 triangles). */
function log(s: SolidBuilder, at: Vec3, r: number, len: number): void {
  const place = { at, roll: -Math.PI / 2 };
  s.lathe(
    [
      [0, 0],
      [r, 0],
    ],
    5,
    C.logEnd,
    place,
    false,
  );
  s.lathe(
    [
      [r, 0],
      [r, len],
    ],
    5,
    C.log,
    place,
    false,
  );
  s.lathe(
    [
      [r, len],
      [0, len],
    ],
    5,
    C.logEnd,
    place,
    false,
  );
}

/** Radius of the felled logs. */
const LOG_R = 0.9;

/** A stack of logs three high (3, 2, 1) along X, from x = `x`, centred on z = `z`. */
function logStack(s: SolidBuilder, [x, z]: readonly [number, number], len: number): void {
  const rise = LOG_R * Math.sqrt(3);
  for (const [row, count] of [
    [0, 3],
    [1, 2],
    [2, 1],
  ] as const) {
    for (let i = 0; i < count; i++) {
      const across = (i - (count - 1) / 2) * 2 * LOG_R;
      log(s, [x, LOG_R + row * rise, z + across], LOG_R, len);
    }
  }
}

/**
 * A pile of felled logs: a stack three high held by stakes, a lone log, a stump and a lamp on a
 * post over the clearing.
 */
export function buildLogPile(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  logStack(s, [-5, -0.6], 10);
  posts(
    s,
    [
      [-5.6, -3.6],
      [5.6, 2.4],
    ],
    3.2,
    C.woodDark,
    0.35,
  );
  log(s, [-3.5, LOG_R, 3.6], LOG_R, 7);
  s.cylinder(1.2, 1, 6, C.log, { at: [4.4, 0, -3.4] });
  s.box([0.25, 6, 0.25], C.metalDark, { at: [5, 0, 4] });
  l.box([0.7, 0.4, 0.7], L.yellow, { at: [5, 6, 4] });
  return { structure: s.geometry, lights: l.geometry };
}

/**
 * A small boat moored along X at `at`: a hull pointed at its bow (+X), a plank deck and a small
 * cabin with a lit window.
 */
function boat(s: SolidBuilder, l: SolidBuilder, at: Vec3): void {
  const hull = [
    [-3.5, -1.3],
    [2.2, -1.3],
    [4, 0],
    [2.2, 1.3],
    [-3.5, 1.3],
  ] as const;
  s.bevelSlab(hull, [0, 0.9, 1.4], [0.6, 0], C.containerBlue, { at }, C.wood);
  s.box([2.4, 1.6, 2], C.white, { at: [at[0] - 1.2, at[1] + 1.4, at[2]] });
  pane(l, [1.2, 0.6], [at[0] - 1.2, at[1] + 2.2, at[2] - 1.06], L.window);
}

/**
 * A river jetty: a plank deck on posts running out over the water (-Z), a small boat moored
 * along it, a slewing crane with a crate on its hook, a shed with lit doors at the shore end.
 */
export function buildRiverDock(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  const deck = 1.6;
  posts(s, [...corners(1.8, 4.5), [-1.8, -10], [1.8, -10]], deck, C.woodDark, 0.4);
  s.box([4.4, 0.35, 15], C.wood, { at: [0, deck, -3.6] });
  boat(s, l, [-5.2, 0, -5.5]);
  // The crane: a mast on the deck, a jib over the boat, a cable and a crate.
  s.cylinder(0.5, 8, 4, C.signalOrange, { at: [1, deck, -7] });
  strut(s, [1, deck + 7.4, -7], [-6, deck + 8.4, -6.5], [0.35, 0.25], C.signalOrange, 4);
  strut(s, [-5.6, deck + 8.2, -6.5], [-5.6, deck + 4.4, -6.5], [0.06, 0.06], C.metalDark);
  s.box([1.4, 1.2, 1.4], C.containerRed, { at: [-5.6, deck + 3.2, -6.5] });
  s.box([7, 4, 5], C.corrugated, { at: [3, 0, 6] });
  gableRoof(s, { size: [7.6, 5.8], y: 4, rise: 1.4 }, C.rustDark, C.corrugated, {
    at: [3, 0, 6],
  });
  pane(l, [2.6, 2.2], [3, 0.4, 3.44], L.window);
  l.box([0.4, 2.4, 0.4], L.cyan, { at: [-0.4, 0.4, 3.4] });
  l.box([0.5, 0.5, 0.5], L.yellow, { at: [1.8, deck + 3, -10.8] });
  s.box([0.2, 3, 0.2], C.metalDark, { at: [1.8, deck + 0.35, -10.8] });
  return { structure: s.geometry, lights: l.geometry };
}

/**
 * A sawmill of a logging camp: an open shed under a rusty corrugated roof on posts, a log on
 * the saw bench, sawn planks stacked beside it, a stack of logs waiting, a smoking metal
 * chimney, and an office with lit windows.
 */
export function buildSawmill(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  posts(s, [...corners(6.5, 3.6), [0, -3.6], [0, 3.6]], 5.5, C.woodDark, 0.5);
  gableRoof(s, { size: [15, 9.4], y: 5.5, rise: 2.4 }, C.rustDark, C.woodDark);
  s.box([10, 1.2, 1.8], C.jungleMetal, { at: [-1, 0, 0] });
  log(s, [-6, 1.2 + LOG_R, 0], LOG_R, 9);
  s.box([4, 1.4, 2.6], C.logEnd, { at: [3, 0, -2.4] });
  logStack(s, [-5, 6.6], 9);
  s.box([5, 4, 4.4], C.wood, { at: [7.6, 0, 4.4] });
  gableRoof(s, { size: [5.6, 5.2], y: 4, rise: 1.6 }, C.corrugated, C.wood, {
    at: [7.6, 0, 4.4],
    yaw: Math.PI / 2,
  });
  s.cylinder(0.5, 9, 5, C.rust, { at: [-6, 0, -4.8] });
  s.cylinder(0.9, 2.2, 5, C.frost, { at: [-6, 9.2, -4.8] }, 1.4);
  pane(l, [2.2, 1.2], [7.6, 1.6, 2.16], L.window);
  l.box([0.5, 0.5, 0.5], L.yellow, { at: [0, 5.1, -3.6] });
  l.box([4.6, 0.25, 0.25], L.cyan, { at: [7.6, 3.6, 2.05] });
  return { structure: s.geometry, lights: l.geometry };
}

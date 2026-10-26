import { SolidBuilder, type SectionPoint } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { corners, pane } from './polar-parts';
import { strut } from './jungle-parts';
import { stain } from './volcanic-parts';

// P10-R08: the enemy's war factory on the caldera rim of 4-5 (vaulted hangars, launch pads,
// armoured towers) and the fortress city at the edge of the magma lake, in the game's darksynth
// style: soot-black armour and dark iron with red, cyan and orange neon (GD-60, GD-61). Sizes in
// world units, standing on Y = 0; the front faces -Z.

/** The hangar's vault, seen from its door: half a rounded arch. */
const VAULT: readonly SectionPoint[] = [
  [1, 0],
  [0.94, 0.45],
  [0.7, 0.82],
  [0.3, 1],
  [-0.3, 1],
  [-0.7, 0.82],
  [-0.94, 0.45],
  [-1, 0],
];
/** The hangar's half width, height and half length. */
const HANGAR = [8, 8, 11] as const;

/**
 * A war hangar: a long vault of dark armour plate, its great door at the front framed in red neon
 * and showing a dim lit interior, a blast wall, a control annexe with a cyan strip and an antenna
 * with a red light.
 */
export function buildWarHangar(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  const [w, h, d] = HANGAR;
  stain(s, [0, -4], 9, C.soot, 8);
  s.loft(
    VAULT,
    [
      [-d, w, 0, h],
      [d, w, 0, h],
    ],
    C.ironDark,
    {},
    { paint: (side) => (side === 3 ? C.iron : undefined) },
  );
  s.box([2 * w - 3, h - 2, 0.6], C.soot, { at: [0, 0, -d - 0.3] });
  l.box([0.3, h - 1.7, 0.3], L.red, { at: [-w + 1.3, 0, -d - 0.7] });
  l.box([0.3, h - 1.7, 0.3], L.red, { at: [w - 1.3, 0, -d - 0.7] });
  l.box([2 * w - 2.3, 0.3, 0.3], L.red, { at: [0, h - 1.9, -d - 0.7] });
  pane(l, [2 * w - 5, 1.2], [0, 0.2, -d - 0.62], L.windowDim);
  s.box([4, 4.4, 8], C.iron, { at: [w + 1.6, 0, 3] }, C.soot);
  l.box([0.2, 0.4, 6], L.cyan, { at: [w + 3.65, 3, 3] });
  s.box([0.3, 7, 0.3], C.metalDark, { at: [w + 1.6, 4.4, 5.5] });
  l.box([0.4, 0.4, 0.4], L.red, { at: [w + 1.6, 11.4, 5.5] });
  return { structure: s.geometry, lights: l.geometry };
}

/** The launch pad's half side, and its missile's height. */
const PAD = 9;
const MISSILE = 15;

/**
 * A launch pad: a square pad of dark armour with a cyan neon ring round the launch spot, a
 * missile standing on it (red-banded, finned), a lattice service tower with an arm to its nose,
 * a blast deflector, and red warning lights at the corners.
 */
export function buildLaunchPad(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([2 * PAD, 0.6, 2 * PAD], C.basalt, {}, C.ironDark);
  s.box([7, 0.4, 7], C.soot, { at: [0, 0.6, 0] });
  l.ring(4.2, 0.15, 12, L.cyan, { at: [0, 0.65, 0] });
  s.cylinder(1.1, MISSILE - 3, 6, C.ash, { at: [0, 1, 0] });
  s.ring(1.12, 1, 6, C.rustRed, { at: [0, MISSILE - 6, 0] });
  s.lathe(
    [
      [1.1, MISSILE - 2],
      [0, MISSILE + 1],
    ],
    6,
    C.ironDark,
  );
  for (const a of [0, Math.PI / 2, Math.PI, (3 * Math.PI) / 2]) {
    s.box([1.4, 2.4, 0.15], C.ironDark, { at: [Math.cos(a) * 1.3, 1, Math.sin(a) * 1.3], yaw: -a });
  }
  for (const [x, z] of corners(0.9, 0.9)) {
    strut(s, [x + 5, 0.6, z], [x * 0.6 + 5, MISSILE, z * 0.6], [0.2, 0.2], C.ironDark, 4);
  }
  s.box([4, 0.4, 0.5], C.rustRed, { at: [3, MISSILE - 4, 0] });
  s.box([6, 2.6, 1.2], C.iron, { at: [0, 0.6, 6.4] });
  for (const [x, z] of corners(PAD - 0.6, PAD - 0.6)) {
    l.box([0.5, 0.5, 0.5], L.red, { at: [x, 0.6, z] });
  }
  return { structure: s.geometry, lights: l.geometry };
}

/** The armoured tower's body: radius at each height. */
const TOWER = [
  [6, 0],
  [5, 4],
  [4, 14],
  [4.6, 16],
] as const;
const TOWER_TOP = 16;

/**
 * An armoured tower: a tapering eight-sided tower of soot-black armour with a flared top, slit
 * windows lit red, an orange neon ring, and a turret with twin barrels on its top.
 */
export function buildArmouredTower(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.lathe(TOWER, 8, C.ironDark, { yaw: Math.PI / 8 });
  s.box([5, 2.4, 5], C.iron, { at: [0, TOWER_TOP, 0], yaw: 0.4 }, C.soot);
  s.box([2.2, 1.6, 2.4], C.ironDark, { at: [0, TOWER_TOP + 2.4, -0.4] });
  for (const x of [-0.5, 0.5]) {
    strut(s, [x, TOWER_TOP + 3.2, -1.4], [x, TOWER_TOP + 3.8, -6], [0.25, 0.2], C.metalDark, 4);
  }
  l.ring(5.05, 0.3, 8, L.orange, { at: [0, 4.3, 0], yaw: Math.PI / 8 });
  for (const a of [0, Math.PI / 2, Math.PI, (3 * Math.PI) / 2]) {
    pane(l, [1.6, 0.4], [Math.sin(a) * 4.02, 11, -Math.cos(a) * 4.02], L.red, -a);
  }
  l.box([0.4, 0.4, 0.4], L.red, { at: [0, TOWER_TOP + 4, 0.6] });
  return { structure: s.geometry, lights: l.geometry };
}

/** The fortress block's masses: centre (x, z), size (w, h, d), colour. */
const BLOCKS = [
  [-6, 3, [10, 9, 12], C.ironDark],
  [6, -2, [10, 13, 10], C.basalt],
  [2, 8, [8, 6, 6], C.iron],
] as const;
/** The keep rising from the middle of the block: radius and height. */
const KEEP = [3, 22] as const;

/**
 * A fortress block: stepped masses of dark armour around a tall eight-sided keep, sloped
 * armour plates at its foot, rows of red slit windows, orange and cyan neon trims, red lights on
 * top of the keep.
 */
export function buildFortressBlock(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  for (const [x, z, [w, h, d], color] of BLOCKS) {
    s.box([w, h, d], color, { at: [x, 0, z] }, C.soot);
    l.box([w + 0.1, 0.3, d + 0.1], L.orange, { at: [x, h - 1, z] });
  }
  s.lathe(
    [
      [16, 0],
      [13, 3],
    ],
    4,
    C.basaltLight,
    { yaw: Math.PI / 4 },
    false,
  );
  const [r, h] = KEEP;
  s.cylinder(r, h, 8, C.ironDark, { at: [-1, 0, -1] }, r * 0.8);
  s.cylinder(r + 0.6, 1.4, 8, C.iron, { at: [-1, h, -1] });
  l.ring(r * 0.85, 0.4, 8, L.cyan, { at: [-1, h - 4, -1] });
  for (const [y, x] of [
    [5, -9],
    [5, -4],
    [8, 4],
    [8, 8],
  ] as const) {
    pane(l, [2.4, 0.5], [x, y, x < 0 ? -3.06 : -7.06], L.red);
  }
  l.box([0.5, 0.5, 0.5], L.red, { at: [-1, h + 1.4, -1] });
  return { structure: s.geometry, lights: l.geometry };
}

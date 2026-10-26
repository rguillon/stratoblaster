import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { leaf, strut, trunk } from './jungle-parts';
import { PLUME, plume, rock, stain } from './volcanic-parts';

// P10-R08: what grows and lies on World 4's ground: hardy grass tufts on the black islands, burnt
// dead trees and stumps on the ash plains, lava boulders, and the vents that smoke and steam,
// crusted rust red and sulphur yellow. Sizes in world units, standing on Y = 0.

/** The tufts of a grass clump: centre (x, z) and the turn of its first blade. */
const TUFTS = [
  [0, 0, 0],
  [1.5, 0.9, 1.1],
  [-1.3, 1.1, 2.3],
  [0.4, -1.5, 3.4],
] as const;
/** Blades per tuft, the length of the longest and how steeply they rise. */
const BLADES = 4;
const BLADE_LENGTH = 3.8;
const BLADE_RISE = -1.2;

/**
 * A clump of hardy grass on black rock: four tufts of tall, stiff blades in two dull greens
 * leaning out from a small basalt stone.
 */
export function buildHardyGrass(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  TUFTS.forEach(([x, z, turn], t) => {
    for (let i = 0; i < BLADES; i++) {
      const color = (i + t) % 2 === 0 ? C.hardyGrass : C.hardyGrassDark;
      const len = BLADE_LENGTH * (1 - 0.12 * ((i + t) % 3));
      const yaw = turn + (i / BLADES) * Math.PI * 2;
      leaf(s, [x, 0, z], [0.7, len], { yaw, pitch: BLADE_RISE + 0.08 * i }, color);
    }
  });
  rock(s, { at: [-0.6, -0.8], r: 0.9, h: 0.8 }, C.basalt);
  return { structure: s.geometry };
}

/** The burnt tree's broken branches: where they leave the trunk, and their charred tips. */
const BRANCHES = [
  [
    [0.1, 5.5, 0],
    [2.8, 8.6, 0.6],
  ],
  [
    [0, 6.6, 0.1],
    [-2.6, 9.2, -0.9],
  ],
  [
    [0.1, 7.6, 0],
    [1, 10.4, -2],
  ],
  [
    [-0.1, 4.2, 0],
    [-2.2, 5.6, 1.8],
  ],
  [
    [2, 7.8, 0.45],
    [3.4, 8.4, -0.6],
  ],
] as const;

/**
 * A burnt dead tree: a charred black trunk, leaning a little, with a few bare broken branches,
 * standing in a drift of grey ash.
 */
export function buildBurntTree(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  trunk(s, [0, 0, 0], [0.75, 0.25, 10.5], C.charcoal, 5, { roll: 0.04 });
  BRANCHES.forEach(([from, to], i) => {
    strut(s, from, to, [0.22, 0.08], i % 2 === 0 ? C.charred : C.charcoal);
  });
  strut(s, [0.3, 0.3, 0.2], [1.9, 0, 1.2], [0.3, 0.15], C.charcoal);
  strut(s, [-0.3, 0.3, -0.1], [-1.6, 0, -1.3], [0.3, 0.15], C.charcoal);
  stain(s, [0, 0], 2.6, C.ashDark, 6);
  return { structure: s.geometry };
}

/**
 * A burnt stump: a charred stub with one jagged split spike, a fallen black log beside it, roots
 * and a drift of ash.
 */
export function buildBurntStump(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  s.cylinder(1.1, 1.6, 6, C.charcoal, {}, 0.9);
  strut(s, [0.3, 1.5, 0.1], [0.5, 3.6, 0.3], [0.45, 0.05], C.charred);
  s.cylinder(0.5, 4.2, 5, C.charred, { at: [-1, 0.5, -1.4], roll: -Math.PI / 2, yaw: 0.5 });
  for (const [x, z] of [
    [1.6, 0.6],
    [-0.5, 1.7],
    [-1.4, -0.4],
  ] as const) {
    strut(s, [x * 0.4, 0.5, z * 0.4], [x, 0, z], [0.3, 0.12], C.charcoal);
  }
  stain(s, [0.2, 0.3], 2.2, C.ashDark, 6);
  return { structure: s.geometry };
}

/**
 * Lava boulders: a big black basalt block and two smaller ones, a thin crack of dim glowing slag
 * still hot in the big one.
 */
export function buildLavaBoulder(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  rock(s, { at: [0, 0], r: 2.4, h: 3.6, yaw: 0.3 }, C.basalt);
  rock(s, { at: [2.4, 1.3], r: 1.2, h: 1.6 }, C.basaltLight);
  rock(s, { at: [-2, 1.4], r: 1, h: 1.2 }, C.basalt);
  l.box([0.25, 1.7, 0.3], L.slagGlow, { at: [0.3, 0.3, -1.65], roll: 0.3 });
  return { structure: s.geometry, lights: l.geometry };
}

/** The stains of mineral crust around a vent: centre (x, z), radius, rust or sulphur. */
const VENT_STAINS = [
  [0, 0, 5, C.rustRed],
  [1.8, -1.6, 2.8, C.sulphur],
  [-2.2, 1.4, 2.2, C.sulphurDark],
  [-1, -2.6, 1.8, C.rustRed],
] as const;

/**
 * A smoking vent: a low cone of black cinders with an open crater glowing dimly in its throat,
 * crusted rust red and sulphur yellow around, a few blocks, and a slow smoke column.
 */
export function buildSmokingVent(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  for (const [x, z, r, color] of VENT_STAINS) stain(s, [x, z], r, color, 6, 0.05 + r * 0.004);
  s.lathe(
    [
      [3.6, 0],
      [2.2, 2.2],
      [1.3, 3.3],
      [0.8, 2.7],
    ],
    7,
    C.basalt,
    {},
    false,
  );
  s.lathe(
    [
      [1.3, 3.31],
      [0.9, 3.31],
    ],
    7,
    C.sulphur,
    {},
    false,
  );
  l.lathe(
    [
      [0.8, 2.7],
      [0, 2.75],
    ],
    7,
    L.slagGlow,
    {},
    false,
  );
  rock(s, { at: [3.2, 2.4], r: 0.8, h: 1 }, C.basaltLight);
  rock(s, { at: [-3.4, -1.6], r: 0.7, h: 0.8 }, C.basalt);
  return {
    structure: s.geometry,
    lights: l.geometry,
    plumes: [plume(PLUME.smoke, [0, 3.2, 0])],
  };
}

/** The sulphur vent's crusted chimneys: (x, z), radius, height, colour. */
const FUMAROLES = [
  [0, 0, 1.1, 3.6, C.sulphur],
  [1.6, 0.8, 0.8, 2.2, C.sulphurDark],
  [-1.3, 1.1, 0.7, 1.8, C.sulphur],
  [0.6, -1.5, 0.6, 1.4, C.rustRed],
] as const;

/**
 * A sulphur vent: a cluster of little crusted chimneys of bright sulphur on a yellow and rust
 * stain, the tallest sending up a column of steam.
 */
export function buildSulphurVent(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  stain(s, [0, 0], 3.6, C.sulphurDark, 7);
  stain(s, [1.4, -1.2], 2, C.rustRed, 5, 0.07);
  for (const [x, z, r, h, color] of FUMAROLES) {
    s.lathe(
      [
        [r, 0],
        [r * 0.55, h * 0.8],
        [r * 0.35, h],
      ],
      5,
      color,
      { at: [x, 0, z], yaw: x },
      false,
    );
  }
  return { structure: s.geometry, plumes: [plume(PLUME.steam, [0, 3.6, 0], 0.7)] };
}

/** Rocks around the hot spring's pool. */
const SPRING_ROCKS = [
  { at: [4.2, 2.2], r: 1.3, h: 3.2 },
  { at: [-4, 1.8], r: 1, h: 1.6 },
  { at: [-1.5, -4.4], r: 0.9, h: 1.2 },
] as const;

/**
 * A hot spring: a round pool of milky blue-green water in a rim of pale mineral crust, stained
 * rust and sulphur where it overflows, a few rocks, and steam rising off the water.
 */
export function buildHotSpring(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  stain(s, [1.6, -2.4], 3.2, C.rustRed, 6);
  stain(s, [-2.4, -1.6], 2.4, C.sulphurDark, 5, 0.07);
  s.lathe(
    [
      [4.6, 0],
      [4, 0.6],
      [3.3, 0.5],
    ],
    8,
    C.ashLight,
    {},
    false,
  );
  stain(s, [0, 0], 3.4, C.hotWater, 8, 0.35);
  for (const r of SPRING_ROCKS) rock(s, r, C.basalt);
  return { structure: s.geometry, plumes: [plume(PLUME.steam, [0, 0.4, 0])] };
}

/** The steam puffs over the disturbed water: (x, z), radius and height. */
const SEA_PUFFS = [
  [0, 0, 2, 3.4],
  [1.9, 1, 1.2, 2],
  [-1.6, 0.9, 1, 1.6],
] as const;

/**
 * Steam off the hot sea (Y = 0 is the water surface): a faint ring of disturbed pale water, low
 * puffs of steam boiling up from it, and a steam column rising above.
 */
export function buildSeaSteam(): PropGeometry {
  const s = new SolidBuilder();
  for (const [r0, r1, color] of [
    [4.2, 3.2, C.spray],
    [2.6, 1.8, C.steam],
  ] as const) {
    s.lathe(
      [
        [r0, 0.05],
        [r1, 0.1],
      ],
      8,
      color,
      {},
      false,
    );
  }
  for (const [x, z, r, h] of SEA_PUFFS) {
    s.lathe(
      [
        [r, 0],
        [r * 1.05, h * 0.45],
        [0, h],
      ],
      5,
      C.steam,
      { at: [x, 0, z] },
      false,
    );
  }
  return { structure: s.geometry, plumes: [plume(PLUME.steam, [0, 3, 0], 1.2)] };
}

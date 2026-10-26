import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { pane } from './polar-parts';
import { strut } from './jungle-parts';
import { PLUME, plume, stack, stain } from './volcanic-parts';

// P10-R08: the enemy's giant foundries of 4-4: smelters pouring molten metal, blast furnaces with
// glowing mouths, rows of smoking chimneys. Soot-black iron and rust, molten orange light and the
// enemy's neon (GD-60, GD-61). Sizes in world units, standing on Y = 0; the front faces -Z.

/** The smelter's crucibles of molten metal along its open front: x. */
const CRUCIBLES = [-7.5, -3, 1.5] as const;

/**
 * A smelter: a long soot-black shed with a sawtooth roof, three crucibles of molten metal along
 * its open front, a glowing channel running out of it, a hopper on legs, a tall smoking stack,
 * orange neon along the eaves.
 */
export function buildSmelter(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  stain(s, [0, 0], 14, C.soot, 8);
  s.box([20, 8, 10], C.ironDark, { at: [0, 0, 2] }, C.soot);
  for (const x of [-7.5, -2.5, 2.5, 7.5]) {
    s.face(
      [
        [x - 2.5, 8, -3],
        [x - 2.5, 8, 7],
        [x + 2.5, 10.5, 7],
        [x + 2.5, 10.5, -3],
      ],
      C.iron,
    );
    s.face(
      [
        [x + 2.5, 10.5, -3],
        [x + 2.5, 10.5, 7],
        [x + 2.5, 8, 7],
      ],
      C.soot,
    );
  }
  for (const x of CRUCIBLES) {
    s.cylinder(1.6, 2.2, 6, C.rustDark, { at: [x, 0, -4.6] }, 1.9);
    l.lathe(
      [
        [1.7, 2.1],
        [0, 2.2],
      ],
      6,
      L.molten,
      { at: [x, 0, -4.6] },
      false,
    );
  }
  l.box([14, 0.12, 1], L.furnace, { at: [-3, 0.06, -7] });
  pane(l, [16, 4], [-1, 0, -3.02], L.slagGlow);
  s.box([3.6, 3.4, 3.6], C.rustRed, { at: [7.5, 4.6, -4.6] });
  for (const dx of [-1.4, 1.4]) s.box([0.4, 4.6, 0.4], C.ironDark, { at: [7.5 + dx, 0, -4.6] });
  const smoke = stack(s, { at: [-8, 0, 5], r: 1.4, h: 17 }, C.iron, 6);
  l.box([20.2, 0.3, 0.2], L.orange, { at: [0, 7.6, -3.05] });
  l.box([0.5, 0.5, 0.5], L.red, { at: [-8, 17.2, 5] });
  return { structure: s.geometry, lights: l.geometry, plumes: [smoke] };
}

/** The blast furnace's tower: radius at each height. */
const FURNACE = [
  [4.2, 0],
  [4.6, 5],
  [3.6, 15],
  [2.4, 18],
] as const;
/** The hot-blast stoves beside it: (x, z), radius, height. */
const STOVES = [
  [8, 3, 2.2, 15],
  [8, -2.4, 2.2, 15],
  [3.5, 7.5, 2, 13],
] as const;

/**
 * A blast furnace: a tall tapering tower of dark iron bound with rust-red bands, its mouth at
 * the foot glowing white-hot, molten iron running from it down a channel, three domed stoves
 * beside it, a downcomer pipe to the top, smoke pouring from it, red lights.
 */
export function buildBlastFurnace(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  stain(s, [0, -2], 12, C.soot, 8);
  s.lathe(FURNACE, 8, C.ironDark, { at: [-2, 0, 0] }, false);
  s.ring(4.65, 0.8, 8, C.rustRed, { at: [-2, 5, 0] });
  s.cylinder(2.4, 3, 6, C.iron, { at: [-2, 18, 0] }, 1.6);
  for (const [x, z, r, h] of STOVES) {
    s.cylinder(r, h, 7, C.iron, { at: [x, 0, z] });
    s.lathe(
      [
        [r, h],
        [r * 0.6, h + 1.4],
        [0, h + 1.8],
      ],
      7,
      C.ironDark,
      { at: [x, 0, z] },
      false,
    );
  }
  strut(s, [-1, 20, 0], [8, 13, 0.3], [0.8, 0.8], C.rust, 5);
  // The glowing mouth at the foot, and the molten iron running out of it.
  pane(l, [3.4, 2.6], [-2, 0.4, -4.4], L.molten);
  l.box([1.4, 0.12, 6.6], L.furnace, { at: [-2, 0.05, -8] });
  s.box([3.6, 0.5, 7.4], C.slag, { at: [-2, 0, -8.2] });
  l.box([0.5, 0.5, 0.5], L.red, { at: [-2, 21.2, 0] });
  l.box([0.4, 0.4, 0.4], L.red, { at: [8, 16.9, 3] });
  return {
    structure: s.geometry,
    lights: l.geometry,
    plumes: [plume(PLUME.smoke, [-2, 21, 0], 1.3)],
  };
}

/** The chimneys of the row along X: x, radius and height. */
const CHIMNEYS = [
  [-9, 1.3, 22],
  [-3, 1.4, 25],
  [3, 1.3, 21],
  [9, 1.4, 24],
] as const;

/**
 * A row of chimneys: four tall soot-blackened stacks along a long boiler house of dark iron,
 * each smoking, a ladder of red aviation lights on the tallest, a strip of orange neon and glowing
 * fire doors along the front.
 */
export function buildChimneyRow(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  stain(s, [0, 0], 13, C.soot, 8);
  s.box([24, 6, 6], C.iron, { at: [0, 0, 1] }, C.soot);
  s.box([24.4, 1, 6.4], C.ironDark, { at: [0, 6, 1] });
  const plumes = CHIMNEYS.map(([x, r, h], i) =>
    stack(s, { at: [x, 7, 1], r, h: h - 7 }, i % 2 === 0 ? C.ironDark : C.rustDark, 6),
  );
  for (const [x, r, h] of CHIMNEYS) l.box([0.5, 0.5, 0.5], L.red, { at: [x + r * 0.7, h - 1, 1] });
  for (const x of [-9, -3, 3, 9]) pane(l, [2, 1.6], [x, 0.6, -2.02], L.furnace);
  l.box([24.2, 0.3, 0.2], L.orange, { at: [0, 5, -2.05] });
  return { structure: s.geometry, lights: l.geometry, plumes };
}

import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { corners, pane, posts } from './polar-parts';
import { strut } from './jungle-parts';
import { rock, stack, stain } from './volcanic-parts';

// P10-R08: the enemy's works on the cooled lava of 4-3: mining outposts, lava pumps drawing from
// a glowing basin, and heat collectors (arrays of dark panels round a glowing receiver). Dark
// iron, rust and soot, orange neon. Sizes in world units, standing on Y = 0; the front faces -Z.

/** The headframe's height, and the half spread of its legs at the foot. */
const HEADFRAME = 13;
const LEG_SPREAD = 2.2;

/**
 * A mining outpost: a dark iron headframe over the shaft with its wheel, a prefab block with a
 * strip of orange neon, ore bins, a conveyor ramp up to a hopper, a heap of black ore.
 */
export function buildMiningOutpost(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  stain(s, [0, 0], 10, C.basaltLight, 8);
  for (const [x, z] of corners(LEG_SPREAD, LEG_SPREAD)) {
    strut(s, [x - 5, 0, z], [x * 0.4 - 5, HEADFRAME, z * 0.4], [0.35, 0.25], C.ironDark, 4);
  }
  s.box([2.4, 0.6, 2.4], C.rustRed, { at: [-5, HEADFRAME, 0] });
  s.cylinder(1.6, 0.4, 8, C.iron, { at: [-5, HEADFRAME + 2.2, -0.2], pitch: Math.PI / 2 });
  s.box([7, 3.6, 5], C.iron, { at: [3.5, 0, 3.5] }, C.ironDark);
  s.box([3, 1.4, 2.6], C.ironDark, { at: [5, 3.6, 4] });
  strut(s, [-1, 0.4, -4.5], [5, 6, -4.5], [0.7, 0.7], C.rust, 4);
  s.box([3, 3, 3], C.rustRed, { at: [6, 4.4, -4.5] });
  s.lathe(
    [
      [2.6, 0],
      [0, 2.4],
    ],
    6,
    C.ore,
    { at: [-1, 0, -5.5] },
    false,
  );
  rock(s, { at: [7.5, 0.2], r: 1, h: 1.2 }, C.basalt);
  l.box([6.8, 0.3, 0.2], L.orange, { at: [3.5, 3, 0.9] });
  pane(l, [1.4, 0.8], [5, 4.1, 2.69], L.window);
  l.box([0.5, 0.5, 0.5], L.red, { at: [-5, HEADFRAME + 3.8, -0.2] });
  return { structure: s.geometry, lights: l.geometry };
}

/**
 * A lava pump: a heavy iron pump house on legs over a basin of glowing lava, two thick pipes
 * plunging into it, a glowing inspection hatch, a smoking stack and a red light.
 */
export function buildLavaPump(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  // The basin: a rim of black slag round a pool of lava (self-lit).
  s.lathe(
    [
      [6.2, 0],
      [5.6, 0.9],
      [4.8, 0.7],
    ],
    8,
    C.slag,
    { at: [0, 0, -2] },
    false,
  );
  l.lathe(
    [
      [4.8, 0.3],
      [0, 0.35],
    ],
    8,
    L.lava,
    { at: [0, 0, -2] },
    false,
  );
  posts(s, corners(3, 2.4), 3.2, C.ironDark, 0.7);
  s.box([7.4, 4.4, 6], C.iron, { at: [0, 3.2, 1.6] }, C.soot);
  s.box([8, 0.6, 6.6], C.ironDark, { at: [0, 3.2, 1.6] });
  for (const x of [-1.8, 1.8]) {
    strut(s, [x, 4.4, -0.8], [x * 1.1, 0.2, -3.6], [0.7, 0.7], C.rustDark, 6);
    l.cylinder(0.75, 0.4, 6, L.furnace, { at: [x * 1.1, 0.2, -3.6] });
  }
  const smoke = stack(s, { at: [2.4, 7.6, 3], r: 0.8, h: 4.4 }, C.ironDark, 5);
  pane(l, [1.6, 1], [-1.6, 5, -1.41], L.furnace);
  l.box([0.4, 0.4, 0.4], L.red, { at: [-2.8, 7.8, 3.6] });
  return { structure: s.geometry, lights: l.geometry, plumes: [{ ...smoke, scale: 0.6 }] };
}

/** Where the heat collector's panels stand (x, z); each is turned and tilted to the receiver. */
const PANELS = [
  [-6.5, -4],
  [-6.5, 1],
  [-2.5, -6.5],
  [3, -6.5],
  [6.5, -3],
  [6.5, 2.5],
] as const;
/** Height of the receiver at the top of the collector's tower. */
const RECEIVER = 12;

/**
 * A heat collector: an array of dark panels on low frames, each tilted towards a central tower,
 * the receiver at its top glowing with the heat they gather, orange neon round its foot.
 */
export function buildHeatCollector(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  stain(s, [0, 0], 9, C.basaltLight, 8);
  for (const [x, z] of PANELS) {
    const yaw = Math.atan2(-x, -z);
    s.box([0.4, 1, 0.4], C.ironDark, { at: [x, 0, z] });
    s.box([4, 0.3, 2.6], C.glassDark, { at: [x, 1, z], yaw, pitch: -0.45 }, C.solar);
  }
  s.cylinder(1.4, RECEIVER, 6, C.iron, {}, 0.9);
  s.cylinder(1.6, 0.6, 6, C.ironDark, { at: [0, RECEIVER + 2.4, 0] });
  l.cylinder(1.4, 2.4, 6, L.molten, { at: [0, RECEIVER, 0] });
  l.ring(1.5, 0.4, 6, L.orange, { at: [0, 0.6, 0] });
  return { structure: s.geometry, lights: l.geometry };
}

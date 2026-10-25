import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { cone, corners, pane, posts, snowCap, snowyGable } from './polar-parts';

// P08-R07: mining equipment on the glacier's edge (drill towers, conveyors, ore silos, cranes).
// Sizes in world units, standing on Y = 0.

/**
 * A drill tower: a tall yellow derrick tapering over a platform, a drill pipe down its middle,
 * a snowy machine shed beside it, work lights and a red light at the top.
 */
export function buildDrillTower(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([12, 2, 11], C.metalDark, {}, C.snowShade);
  s.cylinder(4, 24, 4, C.mineYellow, { at: [-1.5, 2, 0], yaw: Math.PI / 4 }, 1.1);
  s.box([3, 1.6, 3], C.metal, { at: [-1.5, 26, 0] }, C.snow);
  s.cylinder(0.5, 28, 4, C.metal, { at: [-1.5, 0, -0.1] });
  s.box([4.5, 4.5, 6], C.polarRed, { at: [3.6, 2, 1.5] });
  snowyGable(s, { size: [6.8, 5], y: 6.5, rise: 2 }, C.polarRed, {
    at: [3.6, 0, 1.5],
    yaw: Math.PI / 2,
  });
  pane(l, [2.6, 0.5], [3.6, 5.2, -1.56], L.yellow);
  pane(l, [6, 0.4], [0, 0.9, -5.56], L.yellow);
  l.box([0.7, 0.7, 0.7], L.red, { at: [-1.5, 28, -0.1] });
  return { structure: s.geometry, lights: l.geometry };
}

/** Feet of the trestles under the conveyor belt: x, and the belt's height there. */
const TRESTLES = [-6, 1, 8] as const;
const BELT_FROM: readonly [number, number] = [-12, 2.4];
const BELT_TO: readonly [number, number] = [11, 14];

/** The height of the conveyor belt above `x`. */
function beltHeight(x: number): number {
  const [x0, y0] = BELT_FROM;
  const [x1, y1] = BELT_TO;
  return y0 + ((x - x0) / (x1 - x0)) * (y1 - y0);
}

/** The head house at the top of the conveyor, on four legs, with a lit window. */
function headHouse(s: SolidBuilder, l: SolidBuilder): void {
  const x = 11.2;
  s.box([4, 4, 4.4], C.metal, { at: [x, 11.5, 0] });
  snowCap(s, [4.4, 4.8], [x, 15.5, 0]);
  const legs = corners(1.6, 1.8).map(([dx, z]) => [x + dx, z] as const);
  posts(s, legs, 11.5, C.metalDark, 0.5);
  pane(l, [2.4, 1], [x, 13.2, -2.26], L.window);
}

/**
 * A conveyor: a long belt rising on trestles from a hopper on the ground to a head house, with
 * a heap of dark ore beside the hopper and lights along the belt.
 */
export function buildConveyor(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  const [x0, y0] = BELT_FROM;
  const [x1, y1] = BELT_TO;
  const length = Math.hypot(x1 - x0, y1 - y0);
  const slope = Math.atan2(y1 - y0, x1 - x0);
  s.box(
    [length, 1, 2.4],
    C.mineYellow,
    { at: [(x0 + x1) / 2, (y0 + y1) / 2 - 0.5, 0], roll: slope },
    C.ore,
  );
  for (const x of TRESTLES) {
    posts(
      s,
      [
        [x, -1],
        [x, 1],
      ],
      beltHeight(x) - 0.4,
      C.metalDark,
      0.4,
    );
  }
  s.lathe(
    [
      [1.2, 0],
      [3, 3.2],
    ],
    4,
    C.metal,
    { at: [-11.5, 0, 0], yaw: Math.PI / 4 },
  );
  cone(s, 4, [0, 3.4], 6, C.ore, { at: [-8, 0, 4.5] });
  headHouse(s, l);
  for (const x of [-4, 4]) l.box([0.5, 0.5, 0.5], L.yellow, { at: [x, beltHeight(x) + 0.7, -1.4] });
  return { structure: s.geometry, lights: l.geometry };
}

/**
 * An ore silo: a tall round bin on legs over a cone hopper, under a snowy roof, with a smaller
 * bin beside it, a ladder cage up its front, and a lit ring.
 */
export function buildOreSilo(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  posts(s, corners(2.6, 2.6), 7, C.metalDark, 0.6);
  s.lathe(
    [
      [0, 3],
      [4, 7],
    ],
    8,
    C.metalDark,
    {},
    false,
  );
  s.cylinder(4, 13, 8, C.silver, { at: [0, 7, 0] });
  s.lathe(
    [
      [4.2, 20],
      [0, 22.4],
    ],
    8,
    C.snow,
  );
  s.cylinder(2.4, 12, 6, C.mineYellow, { at: [5.8, 0, 2] });
  cone(s, 2.6, [12, 1.6], 6, C.snow, { at: [5.8, 0, 2] });
  s.box([1, 21, 0.6], C.metalDark, { at: [0, 0, -4.2] });
  l.ring(4.05, 0.6, 8, L.cyan, { at: [0, 17, 0] });
  pane(l, [1.4, 1.2], [5.8, 1.2, -0.45], L.window);
  return { structure: s.geometry, lights: l.geometry };
}

/**
 * A mining crane: a tracked crawler with a yellow cab and engine house, a long boom raised over
 * the front, a hook hanging from its tip and a red light on it.
 */
export function buildMiningCrane(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  for (const x of [-3.2, 3.2]) s.box([2, 2, 10], C.metalDark, { at: [x, 0, 1] });
  s.box([7, 1, 7], C.metal, { at: [0, 2, 1.5] });
  s.box([6, 3.6, 5], C.mineYellow, { at: [0, 3, 3] }, C.snow);
  s.box([2.6, 3, 2.6], C.mineYellow, { at: [-1.8, 3, -0.6] }, C.snow);
  s.box([3, 2.4, 2.4], C.concreteDark, { at: [0, 3, 6.6] }, C.snow);
  // The boom, raised 55° towards the front, and the hook below its tip.
  s.box([1.2, 20, 1.2], C.mineYellow, { at: [1.4, 3.6, -0.5], pitch: -0.6 });
  s.box([0.2, 10, 0.2], C.metalDark, { at: [1.4, 9.8, -11.8] });
  s.box([1.2, 1, 1.2], C.metalDark, { at: [1.4, 9, -11.8] });
  pane(l, [1.8, 1.2], [-1.8, 4.4, -1.96], L.window);
  l.box([0.6, 0.6, 0.6], L.red, { at: [1.4, 20.2, -11.8] });
  return { structure: s.geometry, lights: l.geometry };
}

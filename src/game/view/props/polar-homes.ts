import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { corners, pane, posts, snowCap, snowyGable } from './polar-parts';

// P08-R07: futuristic northern homes (steep-roofed timber-and-metal chalets with neon trims and
// snow on the roofs, huts, heated domes). Sizes in world units, standing on Y = 0.

/**
 * A chalet: a timber body under a steep snowy roof, a metal-clad side wing, a glazed gable and a
 * cyan neon trim under the front eave.
 */
export function buildPolarChalet(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([11, 6, 9], C.timber, { at: [-1.5, 0, 0] });
  snowyGable(s, { size: [12.4, 10.6], y: 6, rise: 6.5 }, C.timber, { at: [-1.5, 0, 0] });
  s.box([5, 4.5, 7], C.metal, { at: [6.2, 0, 0.6] });
  snowCap(s, [5.4, 7.4], [6.2, 4.5, 0.6], 0.6);
  s.box([1.2, 3, 1.2], C.metalDark, { at: [-4, 9, 2] });
  snowCap(s, [1.5, 1.5], [-4, 12, 2], 0.4);
  pane(l, [5, 1.6], [-1.5, 2.2, -4.56], L.window);
  pane(l, [2.2, 2.2], [-7.56, 6.2, 0], L.window, Math.PI / 2);
  pane(l, [2.2, 1.4], [6.2, 1.8, -2.96], L.window);
  l.box([12, 0.3, 0.3], L.cyan, { at: [-1.5, 5.5, -4.8] });
  l.box([0.3, 0.3, 7.2], L.cyan, { at: [8.85, 4.2, 0.6] });
  return { structure: s.geometry, lights: l.geometry };
}

/**
 * A long chalet: a long timber house under a steep snowy roof, a cross wing with its own gable at
 * one end, a dark metal porch, a row of windows and a pink neon trim.
 */
export function buildLongChalet(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([18, 5, 8], C.timber, { at: [-1, 0, 1] });
  snowyGable(s, { size: [19.2, 9.6], y: 5, rise: 5.5 }, C.timber, { at: [-1, 0, 1] });
  s.box([6.5, 6.5, 10], C.metal, { at: [7, 0, 0] });
  snowyGable(s, { size: [10.6, 7.6], y: 6.5, rise: 6 }, C.metal, {
    at: [7, 0, 0],
    yaw: Math.PI / 2,
  });
  s.box([5, 0.4, 3], C.metalDark, { at: [-5, 3, -4.4] });
  posts(
    s,
    [
      [-7.2, -5.6],
      [-2.8, -5.6],
    ],
    3,
    C.metalDark,
    0.4,
  );
  for (const x of [-8, -4, 0]) pane(l, [2.2, 1.6], [x, 1.8, -3.06], L.window);
  pane(l, [3.4, 2], [7, 2.4, -5.06], L.window);
  l.box([18, 0.3, 0.3], L.pink, { at: [-1, 4.4, -3.3] });
  l.box([0.3, 0.3, 10.2], L.pink, { at: [10.4, 5.6, 0] });
  return { structure: s.geometry, lights: l.geometry };
}

/** A small hut on low stilts under a steep snowy roof, with a lit window and a mast light. */
export function buildIceHut(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  posts(s, corners(2.6, 2), 1.2, C.metalDark, 0.5);
  s.box([6, 3.4, 5], C.timber, { at: [0, 1.2, 0] }, C.snowShade);
  snowyGable(s, { size: [6.8, 6.2], y: 4.6, rise: 3.4 }, C.timber);
  s.box([1.6, 1.2, 0.8], C.metalDark, { at: [0, 0, -3] });
  s.cylinder(0.12, 6, 4, C.metal, { at: [2.4, 4.4, 1.4] });
  pane(l, [1.6, 1.1], [-1.2, 2.6, -2.56], L.window);
  l.box([0.5, 0.5, 0.5], L.red, { at: [2.4, 10.3, 1.4] });
  return { structure: s.geometry, lights: l.geometry };
}

/**
 * A heated dome: snow banked on its lower part, the top melted bare to dark glass panels, and a
 * glowing ring between them; an entrance tunnel at the front.
 */
export function buildHeatedDome(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  s.lathe(
    [
      [9.6, 0],
      [9.2, 2.6],
      [7.9, 5],
    ],
    10,
    C.snow,
    {},
    false,
  );
  s.lathe(
    [
      [7.6, 5.4],
      [5.4, 7.8],
      [2.6, 9.2],
      [0, 9.6],
    ],
    10,
    C.glassBlue,
    {},
    false,
  );
  // A dark band between snow and glass, behind the ring of light.
  s.lathe(
    [
      [7.9, 5],
      [7.6, 5.4],
    ],
    10,
    C.metalDark,
    {},
    false,
  );
  s.box([3.6, 3.4, 4], C.metal, { at: [0, 0, -8.6] }, C.snow);
  l.ring(7.95, 0.45, 10, L.yellow, { at: [0, 4.95, 0] });
  pane(l, [2, 2.4], [0, 0.3, -10.65], L.window);
  return { structure: s.geometry, lights: l.geometry };
}

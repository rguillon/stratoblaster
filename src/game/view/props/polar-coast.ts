import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { corners, pane, posts, snowCap, snowyGable } from './polar-parts';

// P08-R07: the cold coasts and harbours of World 2. Sizes in world units, standing on Y = 0.

/** Bands of the lighthouse tower: radius at the bottom of each band, its height and colour. */
const LIGHTHOUSE_BANDS = [
  [3.2, 0, C.white],
  [2.85, 5.5, C.polarRed],
  [2.5, 11, C.white],
  [2.15, 16.5, C.polarRed],
] as const;
const BAND_HEIGHT = 5.5;
const RADIUS_STEP = 0.35;

/**
 * A lighthouse: a tall tapering tower striped red and white, a gallery, a glowing lantern with a
 * beacon light, under a red cap; a keeper's hut at its foot.
 */
export function buildLighthouse(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  for (const [r, y, color] of LIGHTHOUSE_BANDS) {
    s.lathe(
      [
        [r, y],
        [r - RADIUS_STEP, y + BAND_HEIGHT],
      ],
      8,
      color,
      {},
      false,
    );
  }
  const top = BAND_HEIGHT * LIGHTHOUSE_BANDS.length;
  s.cylinder(2.9, 0.6, 8, C.metalDark, { at: [0, top, 0] }, 2.9);
  s.lathe(
    [
      [2.1, top + 3.4],
      [0, top + 5.4],
    ],
    8,
    C.polarRed,
  );
  l.cylinder(1.5, 2.8, 8, L.yellow, { at: [0, top + 0.6, 0] });
  l.box([0.6, 0.6, 0.6], L.red, { at: [0, top + 5.4, 0] });
  s.box([3.6, 3, 4], C.white, { at: [3.6, 0, 0.6] });
  snowyGable(s, { size: [4.4, 4.2], y: 3, rise: 2.2 }, C.white, {
    at: [3.6, 0, 0.6],
    yaw: Math.PI / 2,
  });
  pane(l, [1.4, 1], [3.9, 1.2, -1.46], L.window);
  return { structure: s.geometry, lights: l.geometry };
}

/**
 * A harbour crane: a portal on four legs carrying a turning tower, a cabin and a long jib over
 * the quay, with a counterweight behind and red lights on the jib.
 */
export function buildHarbourCrane(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  posts(s, corners(3.5, 3.5), 7, C.polarRed, 0.9);
  s.box([8, 1.4, 8], C.polarRed, { at: [0, 7, 0] });
  s.box([3.4, 5, 3.4], C.mineYellow, { at: [0, 8.4, 0] });
  s.box([4, 3, 4.6], C.mineYellow, { at: [0, 13.4, 1] }, C.snow);
  s.box([2.2, 2.4, 2], C.metalDark, { at: [-2, 13.4, -2.2] }, C.snow);
  // The jib, reaching over the water at the front, and the counterweight behind.
  s.box([1.2, 1.4, 14.5], C.mineYellow, { at: [0, 15.2, -5.25], pitch: 0.1 });
  s.box([0.8, 6, 0.8], C.metalDark, { at: [0, 16.4, 1.2] });
  s.box([3.6, 2.6, 2.6], C.concreteDark, { at: [0, 14.8, 6.8] }, C.snow);
  s.box([0.2, 8, 0.2], C.metalDark, { at: [0, 8.5, -11.8] });
  s.box([1.4, 0.8, 1.4], C.metalDark, { at: [0, 7.7, -11.8] });
  pane(l, [1.6, 1.2], [-2, 14.4, -3.25], L.window);
  l.box([0.6, 0.6, 0.6], L.red, { at: [0, 17.2, -12] });
  l.box([0.6, 0.6, 0.6], L.red, { at: [0, 22.4, 1.2] });
  return { structure: s.geometry, lights: l.geometry };
}

/**
 * A harbour fish store: a long warehouse of painted metal under a low snowy roof, with lit
 * loading doors on the quay side, an office at one end and crates stacked outside.
 */
export function buildFishStore(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([18, 7, 11], C.containerBlue, { at: [-1.5, 0, 1] });
  snowyGable(s, { size: [19, 12.2], y: 7, rise: 3 }, C.containerBlue, { at: [-1.5, 0, 1] });
  s.box([5, 5, 7], C.white, { at: [9.5, 0, 2] }, C.snowShade);
  snowCap(s, [5.4, 7.4], [9.5, 5, 2]);
  for (const x of [-7, -1.5, 4]) {
    s.box([3.6, 4, 0.3], C.metalDark, { at: [x, 0, -4.6] });
    pane(l, [3, 0.5], [x, 4.3, -4.8], L.yellow);
  }
  s.box([3, 2.4, 2.4], C.wood, { at: [-6, 0, -7.4] }, C.snow);
  s.box([2.4, 2.4, 2.4], C.containerRed, { at: [-2.8, 0, -7.6] }, C.snow);
  s.box([2.4, 2, 2.4], C.wood, { at: [-6, 2.4, -7.4] }, C.snow);
  pane(l, [2.4, 1.3], [9.5, 2.4, -1.56], L.window);
  l.box([5.2, 0.3, 0.3], L.cyan, { at: [9.5, 4.6, -1.7] });
  return { structure: s.geometry, lights: l.geometry };
}

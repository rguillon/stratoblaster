import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';

// P06-R06: futuristic desert homes and outposts. Sizes in world units, standing on Y = 0.

/** A low wall around the edge of a flat roof, `w × d`, on top of a block `h` high. */
function parapet(s: SolidBuilder, [w, h, d]: readonly [number, number, number], at = 0): void {
  const t = 0.8;
  s.box([w, 1, t], C.adobeDark, { at: [at, h, -d / 2 + t / 2] });
  s.box([w, 1, t], C.adobeDark, { at: [at, h, d / 2 - t / 2] });
  s.box([t, 1, d - 2 * t], C.adobeDark, { at: [at - w / 2 + t / 2, h, 0] });
  s.box([t, 1, d - 2 * t], C.adobeDark, { at: [at + w / 2 - t / 2, h, 0] });
}

/**
 * A thick-walled, flat-roofed block with a smaller upper floor, a row of tilted solar panels on
 * the roof and a cyan neon trim along the front.
 */
export function buildDesertHome(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([15, 6, 12], C.adobe, {}, C.adobeRoof);
  parapet(s, [15, 6, 12]);
  s.box([7, 4, 6], C.adobe, { at: [-3, 6, 2] }, C.adobeRoof);
  for (const x of [2.5, 5.5]) {
    s.box([2.6, 0.3, 4], C.solar, { at: [x, 7, -2], pitch: -0.45 });
  }
  l.box([15.2, 0.4, 0.4], L.cyan, { at: [0, 5.2, -6.2] });
  l.box([2.4, 1.4, 0.4], L.window, { at: [-4, 2, -6.2] });
  l.box([1.6, 1.2, 0.4], L.window, { at: [-3, 7.6, -1.2] });
  return { structure: s.geometry, lights: l.geometry };
}

/** A hut on short stilts under a pyramid thatch roof, with a lit window (islands, coast). */
export function buildBeachHut(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  for (const [x, z] of [
    [-3, -3],
    [3, -3],
    [-3, 3],
    [3, 3],
  ] as const) {
    s.box([0.6, 2, 0.6], C.woodDark, { at: [x, 0, z] });
  }
  s.box([8, 4, 8], C.wood, { at: [0, 2, 0] }, C.thatch);
  s.lathe(
    [
      [7.2, 6],
      [0, 10],
    ],
    4,
    C.thatch,
    { yaw: Math.PI / 4 },
  );
  l.box([2, 1.2, 0.3], L.window, { at: [0, 3.4, -4.1] });
  return { structure: s.geometry, lights: l.geometry };
}

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

/** A courtyard home: an L of thick walls around a yard, with a tall slotted wind catcher. */
export function buildWindcatcherHome(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([14, 5, 5], C.adobe, { at: [0, 0, 4] }, C.adobeRoof);
  s.box([5, 5, 9], C.adobe, { at: [-4.5, 0, -3] }, C.adobeRoof);
  s.box([8, 2, 0.8], C.adobeDark, { at: [2.5, 0, -6.6] });
  s.box([3.6, 13, 3.6], C.adobeDark, { at: [4.5, 0, 4] }, C.adobeRoof);
  for (const z of [-1.81, 1.81]) s.box([2.4, 3, 0.1], C.glassDark, { at: [4.5, 9, 4 + z] });
  l.box([3.8, 0.4, 3.8], L.pink, { at: [4.5, 13, 4] });
  l.box([14.2, 0.35, 0.35], L.pink, { at: [0, 4.6, 1.4] });
  l.box([1.8, 1.4, 0.4], L.window, { at: [-4.5, 1.8, -7.6] });
  return { structure: s.geometry, lights: l.geometry };
}

/** A water tower: a round tank under a cone, on four legs, with a red light on top. */
export function buildWaterTower(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  for (const [x, z] of [
    [-3, -3],
    [3, -3],
    [-3, 3],
    [3, 3],
  ] as const) {
    s.box([0.8, 10, 0.8], C.metalDark, { at: [x, 0, z] });
  }
  s.box([7, 0.6, 0.6], C.metalDark, { at: [0, 5, -3] });
  s.box([7, 0.6, 0.6], C.metalDark, { at: [0, 5, 3] });
  s.cylinder(5, 6, 8, C.white, { at: [0, 10, 0] });
  s.lathe(
    [
      [5.2, 16],
      [0, 18.5],
    ],
    8,
    C.metal,
  );
  l.ring(5.05, 0.5, 8, L.cyan, { at: [0, 12, 0] });
  l.box([0.9, 0.9, 0.9], L.red, { at: [0, 18.4, 0] });
  return { structure: s.geometry, lights: l.geometry };
}

/** A small solar farm: three rows of tilted panels on posts, and a control box. */
export function buildSolarFarm(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  for (const z of [-6, -1, 4]) {
    for (const x of [-6, 0, 6]) s.box([0.5, 2, 0.5], C.metalDark, { at: [x, 0, z] });
    s.box([16, 0.3, 3.6], C.solar, { at: [0, 2, z], pitch: -0.5 }, C.solar);
  }
  s.box([3, 3, 3], C.concrete, { at: [8.5, 0, 8] }, C.roof);
  l.box([1, 0.6, 0.3], L.cyan, { at: [8.5, 2, 6.4] });
  return { structure: s.geometry, lights: l.geometry };
}

/** A mine headframe: a tall A-frame tower with a lit winding wheel, over a shed. */
export function buildMineHeadframe(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([12, 5, 9], C.rust, { at: [0, 0, 4] }, C.roof);
  s.box([1, 20, 1], C.metalDark, { at: [-3, 0, -3], roll: -0.12 });
  s.box([1, 20, 1], C.metalDark, { at: [3, 0, -3], roll: 0.12 });
  s.box([1, 14, 1], C.metalDark, { at: [0, 0, 3] });
  s.box([1, 1, 7], C.metalDark, { at: [0, 13.5, 0] });
  s.box([7, 1, 1], C.metalDark, { at: [0, 10, -3] });
  s.box([3, 1.6, 2], C.metal, { at: [0, 19.5, -3] });
  l.ring(2.4, 0.4, 10, L.yellow, { at: [0, 21.6, -3], pitch: Math.PI / 2 });
  l.box([1, 1, 1], L.red, { at: [0, 21.4, -3] });
  l.box([4, 1.2, 0.4], L.window, { at: [-2, 2, -0.6] });
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

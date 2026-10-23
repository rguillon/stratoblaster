import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';

// P04-R04: technical / scientific installations. Sizes in world units, standing on Y = 0.

/** Radar dish on a mast above an equipment hut. */
export function buildRadarDish(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  s.box([10, 6, 10], C.metalDark, {}, C.roof);
  s.cylinder(1.2, 10, 6, C.metal, { at: [0, 6, 0] });
  const tilt = { at: [0, 15, 0] as const, pitch: -0.6 };
  s.lathe(
    [
      [0, 0],
      [5, 1.8],
      [9, 4.6],
    ],
    10,
    C.white,
    tilt,
  );
  s.cylinder(0.4, 6, 4, C.metal, tilt);
  l.box([1.2, 1.2, 1.2], L.cyan, { at: [0, 19, -2.8] });
  l.box([1, 1, 1], L.red, { at: [3, 6, 3] });
  return { structure: s.geometry, lights: l.geometry };
}

/** Tall lattice-like antenna mast with crossbars and red aviation lights. */
export function buildAntennaMast(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  s.box([7, 4, 5], C.concreteDark, { at: [5, 0, 0] }, C.roof);
  s.cylinder(3, 52, 4, C.metal, { yaw: Math.PI / 4 }, 0.5);
  for (const [y, w] of [
    [22, 10],
    [38, 7],
  ] as const) {
    s.box([w, 0.8, 0.8], C.metalDark, { at: [0, y, 0] });
    s.box([0.8, 0.8, w], C.metalDark, { at: [0, y, 0] });
  }
  for (const y of [30, 52]) l.box([1.4, 1.4, 1.4], L.red, { at: [0, y, 0] });
  return { structure: s.geometry, lights: l.geometry };
}

/** Observatory: a round building under a faceted dome, with a cyan ring. */
export function buildObservatory(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  s.cylinder(10, 8, 10, C.concrete);
  s.lathe(
    [
      [10, 8],
      [9.2, 12],
      [7, 15.5],
      [3.8, 17.6],
      [0, 18.4],
    ],
    10,
    C.white,
  );
  s.box([2.4, 9, 0.6], C.glass, { at: [0, 9.5, -8.4], pitch: 0.55 });
  l.ring(10.25, 0.7, 10, L.cyan, { at: [0, 6.6, 0] });
  return { structure: s.geometry, lights: l.geometry };
}

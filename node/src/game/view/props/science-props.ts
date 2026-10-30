import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';

// P04-R04: technical / scientific installations. Sizes in world units, standing on Y = 0.

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

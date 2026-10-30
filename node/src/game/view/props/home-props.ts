import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';

// P04-R04: futuristic homes. Sizes in world units, standing on Y = 0.

/** Two offset slabs with a cantilevered upper floor and lit window strips. */
export function buildCubeHome(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  s.box([16, 6, 12], C.white, {}, C.concreteDark);
  s.box([12, 5, 10], C.concreteDark, { at: [3, 6, 2] }, C.roof);
  l.box([10, 1.4, 0.4], L.window, { at: [-2, 2.6, -6.2] });
  l.box([8, 1.2, 0.4], L.window, { at: [3, 8.2, -3.2] });
  l.box([12.4, 0.4, 0.4], L.cyan, { at: [3, 11, -3.2] });
  return { structure: s.geometry, lights: l.geometry };
}

/** A low faceted dome with a ring of windows. */
export function buildDomeHome(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  s.lathe(
    [
      [9, 0],
      [8.6, 3],
      [6.6, 6.4],
      [3.5, 8.5],
      [0, 9.2],
    ],
    10,
    C.white,
  );
  s.box([3, 4, 3], C.concreteDark, { at: [0, 0, -8.6] });
  l.ring(8.75, 0.8, 10, L.cyan, { at: [0, 2.2, 0] });
  l.box([1.6, 2.6, 0.4], L.window, { at: [0, 0.4, -10.2] });
  return { structure: s.geometry, lights: l.geometry };
}

import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';

// P08-R07: the wind turbine of the farms of Worlds 1 and 2, the one World 2 prop still placed
// (moved out of the removed polar outposts, D-163). Sizes in world units, standing on Y = 0.

const BLADES = [0, (2 * Math.PI) / 3, (4 * Math.PI) / 3] as const;

/**
 * A wind turbine: a tall tapering mast on a pad, a nacelle at the top, and three long blades
 * facing the road, one pointing up; a red light on the nacelle.
 */
export function buildWindTurbine(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  s.box([5, 1, 5], C.concrete, {}, C.snow);
  s.cylinder(1, 30, 6, C.white, { at: [0, 1, 0] }, 0.55);
  s.box([1.8, 2, 5], C.white, { at: [0, 30.4, 0.6] }, C.snow);
  const hub: readonly [number, number, number] = [0, 31.4, -2.2];
  s.lathe(
    [
      [0.9, 0],
      [0, 1.4],
    ],
    5,
    C.white,
    { at: hub, pitch: -Math.PI / 2 },
  );
  for (const roll of BLADES) {
    s.box([0.9, 8.2, 0.3], C.white, { at: [0, 31.4, -2.4], roll });
  }
  l.box([0.5, 0.5, 0.5], L.red, { at: [0, 32.4, 2.4] });
  return { structure: s.geometry, lights: l.geometry };
}

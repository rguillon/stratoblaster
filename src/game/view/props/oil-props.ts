import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';

// P08-R07 (reviewer, 2026-10-27): the oil fields of World 2. Sizes in world units, on Y = 0.

/** Height of the walking beam's pivot on top of the Samson post. */
const PIVOT = 7.2;
/** Tilt of the walking beam: the horse head dipping towards the well. */
const TILT = -0.12;

/**
 * An oil pumpjack on a concrete pad: a yellow walking beam on an A-frame Samson post, its horse
 * head over the wellhead, a gearbox with two crank counterweights and the pitman arms at the
 * back, a small motor house, a yellow neon line along the beam and a red light on the post.
 */
export function buildPumpjack(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([12.5, 0.5, 5], C.concrete);
  // The Samson post: two legs leaning in to the pivot, braced at mid-height.
  for (const z of [-1, 1]) {
    s.box([0.5, PIVOT - 0.3, 0.5], C.metalDark, { at: [0, 0.5, z * 1.6], pitch: z * 0.2 });
  }
  s.box([0.4, 0.4, 2.6], C.metalDark, { at: [0, 3.6, 0] });
  // The walking beam and the horse head at its front end.
  s.box([10, 0.8, 0.7], C.mineYellow, { at: [0, PIVOT, 0], roll: TILT });
  s.box([1, 3.2, 1], C.mineYellow, { at: [5.2, PIVOT - 2.6, 0], roll: TILT });
  // The polished rod down to the wellhead.
  s.cylinder(0.15, 4.4, 4, C.silver, { at: [5.6, 0.5, 0] });
  s.box([1.4, 1.2, 1.4], C.metalDark, { at: [5.6, 0.5, 0] }, C.metal);
  // The gearbox, its crank counterweights and the pitman arms up to the beam's back end.
  s.box([2.2, 2.2, 1.6], C.metalDark, { at: [-3.4, 0.5, 0] }, C.metal);
  for (const z of [-1, 1]) {
    s.box([2.4, 2.8, 0.5], C.metal, { at: [-3.6, 0.9, z * 1.1] });
    s.box([0.3, 4.4, 0.3], C.metalDark, { at: [-4, 2.4, z * 0.6] });
  }
  // The motor house behind it.
  s.box([2.4, 2, 2.6], C.concreteDark, { at: [-5.4, 0.5, 0] }, C.roof);
  l.box([8.6, 0.2, 0.1], L.yellow, { at: [0.2, PIVOT + 0.3, 0.4], roll: TILT });
  l.box([0.6, 0.6, 0.6], L.red, { at: [0, PIVOT + 0.8, 0] });
  l.box([0.9, 0.6, 0.1], L.window, { at: [-5.4, 1.2, 1.35] });
  return { structure: s.geometry, lights: l.geometry };
}

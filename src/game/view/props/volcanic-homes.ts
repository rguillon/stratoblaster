import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { pane } from './polar-parts';
import { PLUME, ashRoof, plume, stack, stain } from './volcanic-parts';

// P10-R08: the ash-covered settlements along the road of 4-2: huts and houses of dark
// corrugated iron and grimy concrete, grey ash heaped on their roofs and drifted against their
// walls, small lit windows in the gloom. Sizes in world units, standing on Y = 0; the front
// faces -Z.

/** A drift of ash against a wall facing -Z: a wedge `w` wide, `h` high and `d` deep. */
function drift(
  s: SolidBuilder,
  [x, z]: readonly [number, number],
  [w, h, d]: readonly [number, number, number],
): void {
  const [x0, x1] = [x - w / 2, x + w / 2];
  s.face(
    [
      [x0, 0, z - d],
      [x0, h, z],
      [x1, h, z],
      [x1, 0, z - d],
    ],
    C.ashLight,
  );
  s.face(
    [
      [x0, 0, z],
      [x0, h, z],
      [x0, 0, z - d],
    ],
    C.ash,
  );
  s.face(
    [
      [x1, 0, z - d],
      [x1, h, z],
      [x1, 0, z],
    ],
    C.ash,
  );
}

/**
 * An ash hut: a small hut of dark corrugated iron, its roof under a thick coat of ash, ash
 * drifted against its front, a stove pipe, a water barrel, a lit window.
 */
export function buildAshHut(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  stain(s, [0, -1], 5.6, C.ashDark, 7);
  s.box([7, 3, 5], C.corrugated, {}, C.ironDark);
  ashRoof(s, { size: [7.8, 6.2], y: 3, rise: 1.8 }, C.corrugated);
  s.cylinder(0.3, 2.6, 5, C.ironDark, { at: [2.4, 3.6, 1.4] });
  drift(s, [-1.5, -2.5], [3.4, 1.2, 1.6]);
  s.cylinder(0.7, 1.4, 6, C.rustRed, { at: [4.3, 0, -1.6] });
  pane(l, [1.4, 0.9], [1.6, 1.4, -2.51], L.window);
  return {
    structure: s.geometry,
    lights: l.geometry,
    plumes: [plume(PLUME.smoke, [2.4, 6.2, 1.4], 0.35)],
  };
}

/**
 * An ash house: a two-storey house of grimy concrete with a lean-to of corrugated iron, both
 * roofs under thick ash, a soot-stained chimney smoking, ash drifts, rows of small lit windows.
 */
export function buildAshHouse(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  stain(s, [0, -1], 7.6, C.ashDark, 8);
  s.box([9, 6, 6], C.concreteDark, { at: [-1, 0, 0.5] });
  ashRoof(s, { size: [9.8, 7.2], y: 6, rise: 2.4 }, C.concreteDark, { at: [-1, 0, 0.5] });
  s.box([4, 3, 5], C.corrugated, { at: [5.5, 0, 1] }, C.ironDark);
  ashRoof(s, { size: [4.6, 5.8], y: 3, rise: 1.2 }, C.corrugated, {
    at: [5.5, 0, 1],
    yaw: Math.PI / 2,
  });
  const smoke = stack(s, { at: [-4, 6, 1.5], r: 0.7, h: 4 }, C.concreteDark, 4);
  drift(s, [-3, -2.5], [4, 1.4, 1.8]);
  drift(s, [5.5, -1.5], [3, 1, 1.4]);
  for (const x of [-3.5, -0.5, 1.8]) {
    pane(l, [1.2, 1], [x, 1.4, -2.51], L.window);
    pane(l, [1.2, 1], [x, 4, -2.51], x > 0 ? L.windowDim : L.window);
  }
  return {
    structure: s.geometry,
    lights: l.geometry,
    plumes: [{ ...smoke, scale: 0.4 }],
  };
}

import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';

// Phase 4 review: cars on the streets and main roads. Sizes in model units (drawn at half
// size), standing on Y = 0; the front faces +Z, the way they drive.

type Rgb = readonly [number, number, number];

/** Length of the headlight beams on the road, and their colour (dim, as the glow adds to it). */
const BEAM = 6;
const BEAM_LIGHT: Rgb = [0.4, 0.33, 0.18];

/** Kinds of cars: body length, width, height, cabin length and where it starts from the back. */
const SHAPES = {
  sedan: { length: 7, width: 3.2, height: 1.3, cabin: 3.4, back: 1.6 },
  van: { length: 7.6, width: 3.4, height: 2.8, cabin: 1.8, back: 5.2 },
  truck: { length: 10, width: 3.6, height: 3.4, cabin: 2.2, back: 7.6 },
} as const;
export type CarShape = keyof typeof SHAPES;

/** A flat quad facing up just above the road, `w × d`, centred at Z = `z`. */
function ground(l: SolidBuilder, [w, d]: readonly [number, number], z: number, color: Rgb): void {
  const [x0, x1, z0, z1, y] = [-w / 2, w / 2, z - d / 2, z + d / 2, 0.1];
  l.face(
    [
      [x0, y, z0],
      [x0, y, z1],
      [x1, y, z1],
      [x1, y, z0],
    ],
    color,
  );
}

/** A low-poly car: wheels, a body, a glass cabin, headlights with beams, and tail lights. */
export function buildCar(shape: CarShape, paint: Rgb): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder({ openBottoms: true });
  const { length, width, height, cabin, back } = SHAPES[shape];
  const z0 = -length / 2;
  s.box([width, height, length], paint, { at: [0, 0.4, 0] }, paint);
  s.box([width * 0.86, 1.1, cabin], C.glass, { at: [0, 0.4 + height, z0 + back + cabin / 2] });
  // Few triangles (hundreds of cars are in view): one block for the wheels, one strip for the
  // headlights and one for the tail lights.
  s.box([width + 0.2, 0.9, length - 1.6], C.metalDark);
  l.box([width * 0.8, 0.5, 0.2], L.window, { at: [0, 0.9, length / 2 + 0.1] });
  l.box([width * 0.8, 0.5, 0.2], L.red, { at: [0, 0.9, z0 - 0.1] });
  // The headlight beam on the road ahead, and a red glow behind: flat quads facing up.
  ground(l, [width * 0.9, BEAM], length / 2 + BEAM / 2 + 0.3, BEAM_LIGHT);
  ground(l, [width * 0.7, 1], z0 - 0.8, L.pinkDim);
  return { structure: s.geometry, lights: l.geometry };
}

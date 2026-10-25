import type { Placement, SolidBuilder } from '../../../render/geometry/solids';
import { PROP_COLORS as C } from '../../config/prop-look';

// P08-R07: shared parts of the World 2 props (steep snowy roofs, snow caps, flat window panes,
// stilts). Sizes in world units; the front of a prop faces -Z, towards the road.

type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

/** A steep gable roof: its size, eave height and rise; the ridge runs along X. */
export interface Gable {
  /** Length along X and depth along Z, overhangs included. */
  readonly size: readonly [w: number, d: number];
  /** Height of the eaves. */
  readonly y: number;
  /** Height of the ridge above the eaves. */
  readonly rise: number;
}

/**
 * A gable roof covered in snow (ridge along X): two snowy slopes over a dark metal sheet whose
 * edge shows under the snow, and two gable ends in `ends` (6 + 4 triangles).
 */
export function snowyGable(
  s: SolidBuilder,
  { size: [w, d], y, rise }: Gable,
  ends: Rgb,
  place: Placement = {},
): void {
  slopes(s, [w + 0.4, d + 0.5], y - 0.35, rise, C.metalDark, place);
  slopes(s, [w, d], y, rise, C.snow, place);
  const [x0, x1, z0, z1] = [-w / 2 + 0.2, w / 2 - 0.2, -d / 2 + 0.2, d / 2 - 0.2];
  const top = y + rise - 0.2;
  s.face(
    [
      [x0, y - 0.35, z0],
      [x0, y - 0.35, z1],
      [x0, top, 0],
    ],
    ends,
    place,
  );
  s.face(
    [
      [x1, y - 0.35, z1],
      [x1, y - 0.35, z0],
      [x1, top, 0],
    ],
    ends,
    place,
  );
}

/** The two slopes of a gable roof, ridge along X (4 triangles). */
function slopes(
  s: SolidBuilder,
  [w, d]: readonly [number, number],
  y: number,
  rise: number,
  color: Rgb,
  place: Placement,
): void {
  const [x0, x1, z0, z1] = [-w / 2, w / 2, -d / 2, d / 2];
  s.face(
    [
      [x0, y, z0],
      [x0, y + rise, 0],
      [x1, y + rise, 0],
      [x1, y, z0],
    ],
    color,
    place,
  );
  s.face(
    [
      [x1, y, z1],
      [x1, y + rise, 0],
      [x0, y + rise, 0],
      [x0, y, z1],
    ],
    color,
    place,
  );
}

/** A flat snowy cap `w × d` and `h` thick on a roof at `at`: white on top, shaded sides. */
export function snowCap(
  s: SolidBuilder,
  [w, d]: readonly [number, number],
  at: Vec3,
  h = 0.5,
  yaw = 0,
): void {
  s.box([w, h, d], C.snowShade, { at, yaw }, C.snow);
}

/**
 * A flat lit pane facing -Z (2 triangles), `w × h`, its bottom centre at `at`; turned by `yaw`
 * around its own centre for the other walls.
 */
export function pane(
  l: SolidBuilder,
  [w, h]: readonly [number, number],
  at: Vec3,
  color: Rgb,
  yaw = 0,
): void {
  l.face(
    [
      [-w / 2, 0, 0],
      [-w / 2, h, 0],
      [w / 2, h, 0],
      [w / 2, 0, 0],
    ],
    color,
    { at, yaw },
  );
}

/** Square posts `size` across and `h` high at each of `spots` (x, z). */
export function posts(
  s: SolidBuilder,
  spots: readonly (readonly [number, number])[],
  h: number,
  color: Rgb = C.metalDark,
  size = 0.6,
  y = 0,
): void {
  for (const [x, z] of spots) s.box([size, h, size], color, { at: [x, y, z] });
}

/** The four corners (±x, ±z) of a rectangle. */
export function corners(x: number, z: number): (readonly [number, number])[] {
  return [
    [-x, -z],
    [x, -z],
    [-x, z],
    [x, z],
  ];
}

/** A cone of `sides` facets, radius `r` at `y`, closing to a point `h` higher (no base). */
export function cone(
  s: SolidBuilder,
  r: number,
  [y, h]: readonly [number, number],
  sides: number,
  color: Rgb,
  place: Placement = {},
): void {
  s.lathe(
    [
      [r, y],
      [0, y + h],
    ],
    sides,
    color,
    place,
    false,
  );
}

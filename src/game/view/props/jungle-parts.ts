import type { Placement, SolidBuilder } from '../../../render/geometry/solids';
import { pane } from './polar-parts';

// P09-R06: shared parts of the World 3 props (round leafy crowns, thatched or corrugated gable
// roofs, decks on stilts, hanging vines). Sizes in world units; the front of a prop faces -Z.

type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

/** A round crown: its foot at `at`, its widest radius and its height. */
export interface Crown {
  readonly at: Vec3;
  readonly r: number;
  readonly h: number;
}

/**
 * A round, slightly flattened leafy crown (no bottom, never seen from above): a narrower foot,
 * the widest ring low down, then a domed top. `sides` facets around: 3 triangles each, or 5 when
 * `round` (a fuller dome, for the trees drawn alone).
 */
export function crown(
  s: SolidBuilder,
  { at, r, h }: Crown,
  color: Rgb,
  sides: number,
  round = false,
): void {
  const [x, y, z] = at;
  const dome = round
    ? ([
        [r * 0.6, y],
        [r, y + h * 0.35],
        [r * 0.72, y + h * 0.8],
        [0, y + h],
      ] as const)
    : ([
        [r * 0.62, y],
        [r, y + h * 0.4],
        [0, y + h],
      ] as const);
  s.lathe(dome, sides, color, { at: [x, 0, z] }, false);
}

/** A tapering trunk of `sides` facets from `at` up `h`, open at both ends (hidden in a crown). */
export function trunk(
  s: SolidBuilder,
  at: Vec3,
  [r0, r1, h]: readonly [number, number, number],
  color: Rgb,
  sides = 4,
  lean: Omit<Placement, 'at'> = {},
): void {
  s.lathe(
    [
      [r0, 0],
      [r1, h],
    ],
    sides,
    color,
    { ...lean, at },
    false,
  );
}

/** A gable roof: its size (overhangs included), eave height and rise; the ridge runs along X. */
export interface Roof {
  readonly size: readonly [w: number, d: number];
  readonly y: number;
  readonly rise: number;
}

/** A gable roof (ridge along X): two slopes in `color` and two gable ends in `ends` (6 triangles). */
export function gableRoof(
  s: SolidBuilder,
  { size: [w, d], y, rise }: Roof,
  color: Rgb,
  ends: Rgb,
  place: Placement = {},
): void {
  const [x0, x1, z0, z1] = [-w / 2, w / 2, -d / 2, d / 2];
  const top = y + rise;
  s.face(
    [
      [x0, y, z0],
      [x0, top, 0],
      [x1, top, 0],
      [x1, y, z0],
    ],
    color,
    place,
  );
  s.face(
    [
      [x1, y, z1],
      [x1, top, 0],
      [x0, top, 0],
      [x0, y, z1],
    ],
    color,
    place,
  );
  // The gable ends, a little inside the eaves.
  const [e0, e1] = [x0 + 0.4, x1 - 0.4];
  s.face(
    [
      [e0, y, z0 + 0.4],
      [e0, y, z1 - 0.4],
      [e0, top - 0.3, 0],
    ],
    ends,
    place,
  );
  s.face(
    [
      [e1, y, z1 - 0.4],
      [e1, y, z0 + 0.4],
      [e1, top - 0.3, 0],
    ],
    ends,
    place,
  );
}

/** A hip roof on a square `w × w` at `y`, `rise` high, closing to a point (4 triangles). */
export function hipRoof(
  s: SolidBuilder,
  w: number,
  [y, rise]: readonly [number, number],
  color: Rgb,
  place: Placement = {},
): void {
  s.lathe(
    [
      [w * Math.SQRT1_2, y],
      [0, y + rise],
    ],
    4,
    color,
    { ...place, yaw: (place.yaw ?? 0) + Math.PI / 4 },
    false,
  );
}

/**
 * Vines hanging down a wall facing -Z (turned by `yaw` for the other walls): `count` flat strips
 * in two moss greens, from `top` down by up to `drop`, spread along the wall by `spread`
 * (2 triangles each).
 */
export function vines(
  s: SolidBuilder,
  [x, top, z]: Vec3,
  [count, spread, drop]: readonly [number, number, number],
  colors: readonly [Rgb, Rgb],
  yaw = 0,
): void {
  for (let i = 0; i < count; i++) {
    const u = count === 1 ? 0 : (i / (count - 1) - 0.5) * spread;
    const len = drop * (1 - 0.25 * (i % 3));
    const [dx, dz] = [u * Math.cos(yaw), -u * Math.sin(yaw)];
    pane(s, [0.9, len], [x + dx, top - len, z + dz], i % 2 === 0 ? colors[0] : colors[1], yaw);
  }
}

/**
 * A straight thin prism of `sides` facets (open ends) from `from` to `to`: a stilt root, a
 * branch, a strut, a cable; `r` its radius at `from`, `tip` at `to` (2 triangles per facet).
 */
export function strut(
  s: SolidBuilder,
  from: Vec3,
  to: Vec3,
  [r, tip]: readonly [number, number],
  color: Rgb,
  sides = 3,
): void {
  const [dx, dy, dz] = [to[0] - from[0], to[1] - from[1], to[2] - from[2]];
  const across = Math.hypot(dx, dz);
  const length = Math.hypot(across, dy);
  // Roll tilts the prism's axis from +Y towards +X, then yaw turns it to its heading.
  s.lathe(
    [
      [r, 0],
      [tip, length],
    ],
    sides,
    color,
    { at: from, roll: -Math.atan2(across, dy), yaw: -Math.atan2(dz, dx) },
    false,
  );
}

/** How a flat leaf leaves its stem: its heading around Y and its droop (negative: rising). */
export interface LeafTurn {
  readonly yaw: number;
  readonly pitch: number;
}

/**
 * A flat pointed leaf `w` wide and `len` long from its stem at `at`, heading +Z turned by `turn`,
 * seen from both sides: a palm frond, a fern frond, a reed blade (4 triangles).
 */
export function leaf(
  s: SolidBuilder,
  at: Vec3,
  [w, len]: readonly [number, number],
  { yaw, pitch }: LeafTurn,
  color: Rgb,
): void {
  const outline: Vec3[] = [
    [0, 0, 0],
    [w / 2, 0, len * 0.4],
    [0, 0, len],
    [-w / 2, 0, len * 0.4],
  ];
  const place = { at, yaw, pitch };
  s.face(outline, color, place);
  s.face([...outline].reverse(), color, place);
}

import type { Placement, SolidBuilder } from '../../../render/geometry/solids';
import type { PropPlume } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C } from '../../config/prop-look';
import { gableRoof, type Roof } from './jungle-parts';

// P10-R08: shared parts of the World 4 props (mineral stains on the ground, ash-covered roofs,
// rough basalt rocks, smoking chimneys and stacks). Sizes in world units; the front of a prop
// faces -Z.

type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

/** The plume kinds the World 4 props send up (`PLUME_KINDS` of the engine). */
export const PLUME = { smoke: 'smoke', steam: 'steam' } as const;

/** A plume of `kind` rising from `at` (model space, scale 1), `scale` times its usual size. */
export function plume(kind: string, at: Vec3, scale?: number): PropPlume {
  return scale === undefined ? { kind, at } : { kind, at, scale };
}

/**
 * A flat stain on the ground (a mineral crust, an ash drift, a patch of soot): a polygon of
 * `sides` corners around (x, z), its radius `r`, a hair above the ground so it shows over the
 * terrain (`sides` - 2 triangles).
 */
export function stain(
  s: SolidBuilder,
  [x, z]: readonly [number, number],
  r: number,
  color: Rgb,
  sides = 6,
  y = 0.05,
): void {
  const corners = Array.from({ length: sides }, (_, i): Vec3 => {
    const a = ((sides - i) / sides) * Math.PI * 2 + x;
    // Every other corner a little in, so stains are ragged rather than round.
    const k = i % 2 === 0 ? 1 : 0.78;
    return [x + r * k * Math.cos(a), y, z + r * k * Math.sin(a)];
  });
  s.face(corners, color);
}

/** A rough rock: its foot at (x, z), its radius and height, facets turned by `yaw`. */
export interface Rock {
  readonly at: readonly [number, number];
  readonly r: number;
  readonly h: number;
  readonly yaw?: number;
}

/** A rough five-sided rock, widest low down, flat-topped (23 triangles). */
export function rock(s: SolidBuilder, { at: [x, z], r, h, yaw = 0 }: Rock, color: Rgb): void {
  s.lathe(
    [
      [r, 0],
      [r * 0.82, h * 0.55],
      [r * 0.35, h],
    ],
    5,
    color,
    { at: [x, 0, z], yaw: yaw + x },
  );
}

/**
 * A gable roof under a thick coat of grey ash (ridge along X): pale ash slopes over the dark metal
 * sheet whose edge shows under it, and gable ends in `ends` (12 triangles).
 */
export function ashRoof(s: SolidBuilder, roof: Roof, ends: Rgb, place: Placement = {}): void {
  const [w, d] = roof.size;
  gableRoof(
    s,
    { size: [w + 0.4, d + 0.5], y: roof.y - 0.3, rise: roof.rise },
    C.ironDark,
    ends,
    place,
  );
  gableRoof(s, roof, C.ashLight, C.ash, place);
}

/** A round stack: its foot, radius and height, and the colour of its sooty band at the top. */
export interface Stack {
  readonly at: Vec3;
  readonly r: number;
  readonly h: number;
}

/**
 * A round chimney stack of `sides` facets, slightly tapered, with a soot-black band at its top;
 * returns the smoke plume rising from it (about `4 × sides` triangles).
 */
export function stack(
  s: SolidBuilder,
  { at: [x, y, z], r, h }: Stack,
  color: Rgb,
  sides = 6,
  kind: string = PLUME.smoke,
): PropPlume {
  s.lathe(
    [
      [r, 0],
      [r * 0.82, h * 0.85],
    ],
    sides,
    color,
    { at: [x, y, z] },
    false,
  );
  s.lathe(
    [
      [r * 0.82, h * 0.85],
      [r * 0.8, h],
      [r * 0.55, h],
    ],
    sides,
    C.soot,
    { at: [x, y, z] },
    false,
  );
  return plume(kind, [x, y + h, z]);
}

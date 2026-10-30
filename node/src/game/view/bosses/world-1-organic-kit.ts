import type { OutlinePoint } from '../../../render/geometry/outline';
import {
  carapace,
  curve,
  organ,
  plate,
  ribs,
  segmentedBody,
  tendril,
  vein,
} from '../../../render/geometry/organic';
import type { Placement } from '../../../render/geometry/solids';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';

// P16-R05, P16-R06: the Cyber-Organic pieces of the World 1 boss models (living bodies with
// metal grafts). Logical pixels, nose +Z, Y up.

type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

/** Flesh shades (P16-R01). */
export const F = ENEMY_LOOK.flesh;
/** Hull shades of the grafts (P16-R01). */
export const M = ENEMY_LOOK.hull;
/** Rivets on the grafted plates: worn metal. */
const RIVET: Rgb = [0.24, 0.24, 0.27];

/** A creature's body along Z: a ridged shell on a swollen belly. */
export interface Hide {
  /** Z of its tail and nose, its half width, its belly and back heights. */
  readonly tail: number;
  readonly nose: number;
  readonly width: number;
  readonly bottom: number;
  readonly top: number;
  /** Number of segments (shell plates). */
  readonly segments: number;
  /** Shell colour and the darker seams between its plates. */
  readonly shell: readonly [Rgb, Rgb];
  /** Belly colour (a soft, swollen underside, a little wider than the shell). */
  readonly belly: Rgb;
  /** Its girth along the body (tail 0, nose 1). */
  readonly girth?: (t: number) => number;
  /** Where it sits. */
  readonly at?: Vec3;
}

/** Draws a {@link Hide}: a swollen belly in flesh, a carapace over it, both in `flesh`. */
export function hide({ flesh }: EnemyParts, h: Hide): void {
  const place: Placement = { at: h.at ?? [0, 0, 0] };
  const body = {
    tail: h.tail,
    nose: h.nose,
    segments: h.segments,
    ...(h.girth ? { girth: h.girth } : {}),
  };
  const mid = (h.bottom + h.top) / 2;
  segmentedBody(
    flesh,
    { ...body, width: h.width, bottom: h.bottom, top: mid, pinch: 0.15 },
    h.belly,
    place,
  );
  carapace(flesh, { ...body, width: h.width * 0.92, bottom: mid - 1, top: h.top }, h.shell, place);
}

/** A glowing vein along the back from `from` to `to`, bowed up by `bow`, with `branches` off it. */
export function spine(
  { vein: glow }: EnemyParts,
  from: Vec3,
  to: Vec3,
  { width = 1.2, bow = 2, color }: { width?: number; bow?: number; color: Rgb },
): void {
  vein(glow, curve(from, to, [0, bow, 0], 4), width, color);
}

/** A vein from `from` to `to`, bowed by `bow`. */
export function veinLine(
  p: EnemyParts,
  from: Vec3,
  to: Vec3,
  bow: Vec3,
  width: number,
  color: Rgb,
): void {
  vein(p.vein, curve(from, to, bow, 3), width, color);
}

/** Bone ribs arching over a back at each Z of `zs`. */
export function ribCage(
  { flesh }: EnemyParts,
  zs: readonly number[],
  arch: { halfWidth: number; y: number; height: number; thickness: number },
  color: Rgb = F.bone,
  place: Placement = {},
): void {
  ribs(flesh, zs, arch, color, place);
}

/** A tentacle, sinew or limb of flesh from `from` to `to`, bowed by `bow`, `r` thick at its root. */
export function tentacle(
  { flesh }: EnemyParts,
  from: Vec3,
  to: Vec3,
  bow: Vec3,
  [r0, r1]: readonly [number, number],
  color: Rgb = F.sinew,
  sides = 4,
): void {
  tendril(flesh, curve(from, to, bow, 4), [r0, r1], sides, color);
}

/** A gland: a lit bulb on a flesh bed, `r` across, at `at`. */
export function gland(p: EnemyParts, at: Vec3, r: number, glow: Rgb, bed: Rgb = F.crimson): void {
  organ(p.flesh, r * 1.5, 6, bed, { at }, 0.35);
  organ(p.vein, r, 5, glow, { at: [at[0], at[1] + r * 0.6, at[2]] }, 0.6);
}

/** A swollen organ of `r` at `at` (squashed by `stretch`), `sides` facets round. */
export function sac(
  p: EnemyParts,
  at: Vec3,
  r: number,
  color: Rgb,
  { stretch = 0.6, sides = 7, yaw = 0 }: { stretch?: number; sides?: number; yaw?: number } = {},
): void {
  organ(p.flesh, r, sides, color, { at, yaw }, stretch);
}

/** A grafted armour plate of `outline` (around `at`), `[y0, y1]` thick, riveted. */
export function graft(
  p: EnemyParts,
  outline: readonly OutlinePoint[],
  [y0, y1]: readonly [number, number],
  at: Vec3,
  { color = M.panel, yaw = 0 }: { color?: Rgb; yaw?: number } = {},
): void {
  plate(p.hull, outline, [y0, y1], [color, RIVET], { at, yaw });
}

/** A regular polygon of `n` corners and radius `r` (a plate outline), stretched by `[sx, sz]`. */
export function polygon(
  n: number,
  r: number,
  [sx, sz]: readonly [number, number] = [1, 1],
): OutlinePoint[] {
  return Array.from({ length: n }, (_, k): OutlinePoint => {
    const a = (2 * Math.PI * (k + 0.5)) / n;
    return [Math.sin(a) * r * sx, Math.cos(a) * r * sz];
  });
}

/**
 * An armoured growth (P16-R05): what a destroyable part is drawn as, a swollen flesh mound of
 * `r` around `at`, a vein ring at its foot and grafted armour on its crown, so it reads as one
 * clear target.
 */
export function growth(
  p: EnemyParts,
  at: Vec3,
  r: number,
  glow: Rgb,
  {
    flesh = F.crimson,
    height = 0.45,
    armour = true,
  }: { flesh?: Rgb; height?: number; armour?: boolean } = {},
): void {
  organ(p.flesh, r, 8, flesh, { at, yaw: Math.PI / 8 }, height);
  p.vein.ring(r * 0.9, r * 0.06, 8, glow, {
    at: [at[0], at[1] + r * 0.15, at[2]],
    yaw: Math.PI / 8,
  });
  if (armour)
    graft(p, polygon(6, r * 0.62), [r * height * 0.75, r * height * 0.95], at, { color: M.base });
}

/**
 * A fleshy skirt (a mantle, a fin fold) of `outline` from `y0` to `y1`, its rim lined by a vein,
 * tinted `color`.
 */
export function mantle(
  p: EnemyParts,
  outline: readonly OutlinePoint[],
  [y0, y1]: readonly [number, number],
  color: Rgb,
  rim?: Rgb,
): void {
  p.flesh.bevelSlab(outline, [y0, (y0 + y1) / 2, y1], [1.5, 2.5], color);
  if (!rim) return;
  const ring = [...outline, outline[0] ?? [0, 0]];
  const y = (y0 + y1) / 2 + 0.2;
  vein(
    p.vein,
    ring.map(([x, z]): Vec3 => [x * 1.005, y, z * 1.005]),
    0.9,
    rim,
  );
}

/** The outline `outline` scaled by `k` around the origin, then moved by `[dx, dz]`. */
export function scaleOutline(
  outline: readonly OutlinePoint[],
  k: number,
  dx = 0,
  dz = 0,
): OutlinePoint[] {
  return outline.map(([x, z]): OutlinePoint => [x * k + dx, z * k + dz]);
}

/** A row of `count` teeth or barbs of bone along X at `at`, `size` long, pointing along `dir`. */
export function barbs(
  { flesh }: EnemyParts,
  at: Vec3,
  { count, spacing, size, dir }: { count: number; spacing: number; size: number; dir: Vec3 },
  color: Rgb = F.bone,
): void {
  for (let i = 0; i < count; i++) {
    const x = at[0] + (i - (count - 1) / 2) * spacing;
    const root: Vec3 = [x, at[1], at[2]];
    const tip: Vec3 = [x + dir[0] * size, at[1] + dir[1] * size, at[2] + dir[2] * size];
    tendril(flesh, [root, tip], [size * 0.25, 0], 3, color);
  }
}

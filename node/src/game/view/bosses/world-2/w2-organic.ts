import type { OutlinePoint } from '../../../../render/geometry/outline';
import {
  carapace,
  curve,
  organ,
  plate,
  tendril,
  vein,
  type SegmentedBody,
} from '../../../../render/geometry/organic';
import type { SolidBuilder } from '../../../../render/geometry/solids';
import { ENEMY_LOOK } from '../../../config/enemy-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';

// P16-R05, R06: the Cyber-Organic pieces of the World 2 bosses (ice world): pale, cold flesh with
// crystals of frost grown through it, bone, and metal grafts. Logical pixels, nose +Z, Y up.
type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

const F = ENEMY_LOOK.flesh;
const M = ENEMY_LOOK.hull;

/** The World 2 flesh shades: cold teal and purple, bone, and the ice grown through them. */
export const ICE_FLESH = {
  teal: F.teal,
  purple: F.purple,
  crimson: F.crimson,
  sinew: F.sinew,
  bone: F.bone,
  membrane: F.membrane,
  /** Rimed flesh: a frosted, pale teal (top faces). */
  rime: [0.13, 0.17, 0.19] as Rgb,
  /** Crystals of ice grown through the flesh. */
  crystal: [0.15, 0.19, 0.24] as Rgb,
  /** The seams between shell plates. */
  seam: [0.02, 0.04, 0.05] as Rgb,
};

/** Metal shades for the grafts. */
export const GRAFT = { base: M.base, panel: M.panel, dark: M.dark };

/** A shell over a swollen body (P16-R01): teal plates with dark seams. */
export function shell(b: SolidBuilder, body: SegmentedBody, color: Rgb = ICE_FLESH.teal): void {
  carapace(b, body, [color, ICE_FLESH.seam]);
}

/**
 * A cluster of ice crystals grown from the flesh at `at`: `n` thin four-sided spikes, `size` long,
 * fanning out upwards, uneven.
 */
export function crystals(b: SolidBuilder, at: Vec3, size: number, n = 3): void {
  for (let k = 0; k < n; k++) {
    const a = (2 * Math.PI * k) / n + size;
    const len = size * (0.7 + 0.3 * ((k * 7) % 3));
    b.cylinder(
      len * 0.2,
      len,
      4,
      ICE_FLESH.crystal,
      {
        at,
        pitch: 0.5 * Math.cos(a),
        roll: 0.5 * Math.sin(a),
      },
      0,
    );
  }
}

/** A row of spikes of ice along a back, from `from` to `to`, `size` tall. */
export function spineRow(b: SolidBuilder, from: Vec3, to: Vec3, n: number, size: number): void {
  for (let i = 0; i < n; i++) {
    const t = n === 1 ? 0.5 : i / (n - 1);
    const at: Vec3 = [
      from[0] + (to[0] - from[0]) * t,
      from[1] + (to[1] - from[1]) * t,
      from[2] + (to[2] - from[2]) * t,
    ];
    b.cylinder(
      size * 0.25,
      size * (0.8 + 0.4 * (i % 2)),
      4,
      ICE_FLESH.crystal,
      { at, pitch: -0.4 },
      0,
    );
  }
}

/** A sinew from `from` to `to`, bowed by `bow`, thinning from `r` to half of it. */
export function sinew(
  b: SolidBuilder,
  from: Vec3,
  to: Vec3,
  r: number,
  color: Rgb = ICE_FLESH.sinew,
  bow: Vec3 = [0, r, 0],
): void {
  tendril(b, curve(from, to, bow, 3), [r, r * 0.5], 4, color);
}

/** A glowing vein from `from` to `to`, bowed upwards. */
export function glowVein(p: EnemyParts, from: Vec3, to: Vec3, width: number, glow: Rgb): void {
  vein(p.vein, curve(from, to, [0, width, 0], 3), width, glow);
}

/** A gland: a lit bulb of `radius` on `at`, in a ring of flesh. */
export function gland(
  p: EnemyParts,
  at: Vec3,
  radius: number,
  glow: Rgb,
  rim: Rgb = ICE_FLESH.purple,
): void {
  p.flesh.ring(radius * 1.3, radius * 0.6, 6, rim, { at });
  organ(p.vein, radius, 5, glow, { at }, 0.6);
}

/**
 * A destroyable growth (P16-R05): a swollen organ of `radius` on `at`, a metal armour plate on its
 * top, crystals on its flank and a gland lit `glow`. Its outline stays clear: one bulb.
 */
export function armouredOrgan(
  p: EnemyParts,
  at: Vec3,
  radius: number,
  glow: Rgb,
  { color = ICE_FLESH.purple, height = 0.5 }: { color?: Rgb; height?: number } = {},
): void {
  const [x, y, z] = at;
  organ(p.flesh, radius, 6, color, { at: [x, y - radius * 0.2, z] }, height);
  const r = radius * 0.55;
  const top = y - radius * 0.2 + radius * 2 * height * 0.8;
  const hex: OutlinePoint[] = Array.from({ length: 6 }, (_, k): OutlinePoint => {
    const a = (2 * Math.PI * (k + 0.5)) / 6;
    return [Math.sin(a) * r, Math.cos(a) * r];
  });
  plate(p.hull, hex, [0, radius * 0.18], [GRAFT.base, GRAFT.panel], { at: [x, top, z] });
  crystals(p.flesh, [x + radius * 0.6, y + radius * 0.4, z - radius * 0.3], radius * 0.5, 2);
  gland(p, [x - radius * 0.55, y + radius * 0.5, z + radius * 0.35], radius * 0.18, glow);
}

/** Flesh tendrils hanging off `at` outwards along `dir` (x, z), `n` of them, `length` long. */
export function fringe(
  b: SolidBuilder,
  at: Vec3,
  [dx, dz]: readonly [number, number],
  n: number,
  length: number,
  color: Rgb = ICE_FLESH.sinew,
): void {
  for (let i = 0; i < n; i++) {
    const s = (i - (n - 1) / 2) * 0.5;
    const tip: Vec3 = [at[0] + (dx - dz * s) * length, at[1] - 1, at[2] + (dz + dx * s) * length];
    tendril(b, curve(at, tip, [0, 1.5, 0], 2), [length * 0.12, 0], 3, color);
  }
}

/** Icicles of `ICE_FLESH.crystal` under every `every`-th corner of `outline`, at height `y`. */
export function iceTeeth(
  b: SolidBuilder,
  outline: readonly OutlinePoint[],
  y: number,
  every: number,
): void {
  outline.forEach(([x, z], i) => {
    if (i % every !== 0) return;
    const length = 2.5 + (i % 3);
    b.cylinder(
      length * 0.22,
      length,
      4,
      ICE_FLESH.crystal,
      {
        at: [x * 0.97, y, z * 0.97],
        pitch: Math.PI,
      },
      0,
    );
  });
}

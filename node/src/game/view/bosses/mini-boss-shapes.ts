import type { OutlinePoint } from '../../../render/geometry/outline';
import type { Placement, SolidBuilder } from '../../../render/geometry/solids';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';

// P07-R05: pieces shared by the World 1 mini boss models. Logical pixels, nose +Z, Y up.
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** Hull shades (dark metal, tinted towards the boss's neon colour by its material). */
export const H = ENEMY_LOOK.hull;
/** Hull shades beyond `ENEMY_LOOK.hull`: worn edges, weathered patches, hazard paint, soot. */
export const SHADE = {
  /** Worn, lighter metal: plate edges, new repair plates. */
  edge: [0.24, 0.24, 0.27] as Rgb,
  /** Weathered, slightly warm metal: old patches. */
  patch: [0.14, 0.12, 0.1] as Rgb,
  /** Faded hazard paint. */
  hazard: [0.36, 0.3, 0.08] as Rgb,
  /** Burnt metal: scars and exhaust soot. */
  soot: [0.025, 0.025, 0.03] as Rgb,
};

/** Charge lights are drawn white: their material tints them with the boss's neon colour. */
export const WHITE: Rgb = [1, 1, 1];
/** A quarter turn: pitched by it, a lathe's axis (+Y) points along +Z, to the nose. */
export const QUARTER = Math.PI / 2;

/** `at` moved by `[dx, dy, dz]`. */
export function offset(
  [x, y, z]: readonly [number, number, number],
  dx: number,
  dy: number,
  dz: number,
): Vec3 {
  return [x + dx, y + dy, z + dz];
}

/** The outline scaled by `k` around the origin, then moved by `[dx, dz]`. */
export function scaled(
  outline: readonly OutlinePoint[],
  k: number,
  dx = 0,
  dz = 0,
): OutlinePoint[] {
  return outline.map(([x, z]): OutlinePoint => [x * k + dx, z * k + dz]);
}

/** Twice the signed area of an outline in (x, z): positive when counter-clockwise. */
function doubleArea(outline: readonly OutlinePoint[]): number {
  return outline.reduce((sum, [x1, z1], i) => {
    const [x2, z2] = outline[(i + 1) % outline.length] ?? [x1, z1];
    return sum + x1 * z2 - x2 * z1;
  }, 0);
}

/**
 * An open band of light around an outline (centred on the origin): from the outline scaled
 * `k0` at height `y0` to the outline scaled `k1` at `y1`, facing out. A neon ring under a rim
 * that, unlike a slab, hides nothing inside the hull (glow layers draw lights without occluders).
 */
export function neonBand(
  builder: SolidBuilder,
  outline: readonly OutlinePoint[],
  [y0, y1]: readonly [number, number],
  [k0, k1]: readonly [number, number],
  color: Rgb,
  place: Placement = {},
): void {
  const ring = doubleArea(outline) > 0 ? [...outline] : [...outline].reverse();
  ring.forEach(([px, pz], i) => {
    const [qx, qz] = ring[(i + 1) % ring.length] ?? [px, pz];
    builder.face(
      [
        [px * k0, y0, pz * k0],
        [px * k1, y1, pz * k1],
        [qx * k1, y1, qz * k1],
        [qx * k0, y0, qz * k0],
      ],
      color,
      place,
    );
  });
}

/** A gun turret: its size, barrels and where they point. */
export interface TurretSpec {
  /** Radius of the turret (about its part's hit radius). */
  readonly radius: number;
  /** Number of barrels side by side, and the gap between their axes. */
  readonly barrels: number;
  readonly gap: number;
  /** Barrel radius and length past the housing's front. */
  readonly bore: number;
  readonly length: number;
  /** Turn of the turret around +Y (radians, 0 = barrels to the nose) and barrel elevation. */
  readonly yaw?: number;
  readonly elevation?: number;
  /** Colour of the neon ring around its base. */
  readonly neon: Rgb;
  /** Which side of the dome its hatch is on (+1: +X, -1: -X; default +1). */
  readonly hatch?: number;
  /** What its muzzles fire (`EnemyParts.muzzle`), `gun` by default. */
  readonly fires?: string;
}

/** The turret's domed, faceted housing (a lathe profile, in units of its radius). */
const TURRET_DOME = [
  [0.95, 0],
  [1, 0.12],
  [0.82, 0.32],
  [0.5, 0.46],
  [0, 0.5],
] as const;

/**
 * A gun turret centred on `at` (P07-R05): a faceted dome, a neon ring around its foot and its
 * barrels pointing along `yaw`, a charge light at every muzzle.
 */
export function turret(
  { hull, neon, charge, muzzle }: EnemyParts,
  at: Vec3,
  spec: TurretSpec,
): void {
  const r = spec.radius;
  const yaw = spec.yaw ?? 0;
  const dome = TURRET_DOME.map(([u, v]) => [u * r * 0.8, v * r] as const);
  hull.lathe(dome, 8, H.panel, { at, yaw: yaw + Math.PI / 8 });
  neon.ring(r * 0.84, r * 0.08, 8, spec.neon, {
    at: offset(at, 0, r * 0.05, 0),
    yaw: yaw + Math.PI / 8,
  });
  const pitch = QUARTER - (spec.elevation ?? 0);
  const length = spec.length + r * 0.5;
  for (let i = 0; i < spec.barrels; i++) {
    const across = (i - (spec.barrels - 1) / 2) * spec.gap;
    const foot: Vec3 = [across, r * 0.28, r * 0.3];
    const barrel = { at: turned(at, foot, 0, pitch, yaw), pitch, yaw };
    hull.cylinder(spec.bore, length, 6, H.dark, barrel, spec.bore * 0.85);
    const light = { at: turned(at, foot, length, pitch, yaw), pitch, yaw };
    charge.cylinder(spec.bore * 1.05, spec.bore * 0.6, 6, WHITE, light);
    muzzle(turned(at, foot, length + spec.bore * 0.6, pitch, yaw), spec.fires);
  }
  dressing(hull, at, spec);
}

/** The turret's dressing: a mantlet over the barrels' roots, a hatch off to one side, a vent. */
function dressing(hull: SolidBuilder, at: Vec3, spec: TurretSpec): void {
  const r = spec.radius;
  const yaw = spec.yaw ?? 0;
  const put = (x: number, y: number, z: number): Vec3 => {
    const [dx, dy, dz] = yawed([x, y, z], yaw);
    return offset(at, dx, dy, dz);
  };
  const width = (spec.barrels - 1) * spec.gap + spec.bore * 4;
  hull.box([width, r * 0.3, r * 0.4], H.dark, { at: put(0, r * 0.12, r * 0.5), yaw }, H.panel);
  const side = spec.hatch ?? 1;
  hull.cylinder(r * 0.17, r * 0.07, 6, SHADE.edge, {
    at: put(side * r * 0.24, r * 0.44, -r * 0.18),
  });
  hull.box([r * 0.55, r * 0.08, r * 0.14], H.dark, { at: put(0, r * 0.36, -r * 0.5), yaw });
  hull.box([r * 0.55, r * 0.08, r * 0.06], SHADE.edge, { at: put(0, r * 0.4, -r * 0.5), yaw });
}

/** Turns `[x, y, z]` by `yaw` around +Y. */
function yawed([x, y, z]: readonly [number, number, number], yaw: number): Vec3 {
  return [x * Math.cos(yaw) + z * Math.sin(yaw), y, -x * Math.sin(yaw) + z * Math.cos(yaw)];
}

/**
 * Where a barrel standing on `foot` (around the turret's centre `at`), pitched and yawed, is
 * `along` its axis: its base (0) or its muzzle (its length).
 */
function turned(at: Vec3, foot: Vec3, along: number, pitch: number, yaw: number): Vec3 {
  const axis = yawed([0, along * Math.cos(pitch), along * Math.sin(pitch)], yaw);
  const [fx, fy, fz] = yawed(foot, yaw);
  return offset(at, fx + axis[0], fy + axis[1], fz + axis[2]);
}

/** A dark round socket on the core where a part was mounted (left once the part is gone). */
export function socket(hull: SolidBuilder, at: Vec3, radius: number, height: number): void {
  hull.cylinder(radius, height, 8, H.dark, { at, yaw: Math.PI / 8 }, radius * 0.85);
}

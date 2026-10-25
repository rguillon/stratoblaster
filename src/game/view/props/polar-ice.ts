import type { OutlinePoint } from '../../../render/geometry/outline';
import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { cone } from './polar-parts';

// P08-R07: ice floating on the cold sea of 2-1 (floes, icebergs) and a weather buoy. Their Y = 0
// is the water line: they float on it and never reach below it.

type Vec3 = readonly [number, number, number];
/** A tilted block of a pressure ridge: its size, where it stands, its roll and yaw. */
type RidgeBlock = readonly [size: Vec3, at: Vec3, roll: number, yaw: number];

/** Draws the blocks of ice of a pressure ridge, pushed up and tilted, snow on their tops. */
function ridge(s: SolidBuilder, blocks: readonly RidgeBlock[]): void {
  for (const [size, at, roll, yaw] of blocks) s.box(size, C.ice, { at, roll, yaw }, C.snow);
}

/** A flat lid of open water or melt on a floe, just above its top at `y`. */
function pool(s: SolidBuilder, outline: readonly OutlinePoint[], y: number): void {
  s.slab(outline, [y, y + 0.05], C.iceDeep);
}

const SMALL_FLOE: readonly OutlinePoint[] = [
  [-5.2, -1.4],
  [-3.4, -4.4],
  [0.6, -5.4],
  [4.4, -3.2],
  [5.6, 0.8],
  [3, 4.6],
  [-1.6, 5],
  [-4.6, 2.6],
];

/**
 * A small ice floe: a flat irregular white plate about 1.2 thick, a pressure ridge of tilted
 * blocks pushed up across it, and a few loose chunks.
 */
export function buildSmallFloe(): PropGeometry {
  const s = new SolidBuilder();
  s.slab(SMALL_FLOE, [0, 1.2], C.iceBlue, {}, C.snow);
  ridge(s, [
    [[2.2, 2.4, 1.6], [-1.4, 0.8, 0.6], 0.35, 0.4],
    [[1.8, 2.3, 1.5], [0.6, 0.8, 0.2], -0.3, 0.2],
    [[1.4, 1.6, 1.2], [2.4, 0.9, -0.5], 0.2, 0.9],
  ]);
  s.box([1.2, 0.7, 1], C.ice, { at: [-2.6, 1.2, -2.4], yaw: 0.6 }, C.snow);
  s.box([1, 0.5, 0.8], C.ice, { at: [-5, 0, -3.2], yaw: 0.3 }, C.snow);
  return { structure: s.geometry };
}

const LARGE_FLOE: readonly OutlinePoint[] = [
  [-13, -3],
  [-10, -9],
  [-3, -12.4],
  [5, -11],
  [11.5, -6],
  [13.2, 1],
  [10, 8],
  [3, 12],
  [-5, 11],
  [-11.4, 6],
];
const DRIFT: readonly OutlinePoint[] = [
  [-8, 2],
  [-4, -2],
  [2, -1],
  [6, 3],
  [3, 7],
  [-5, 7],
];
const MELT_POOL: readonly OutlinePoint[] = [
  [3, -8],
  [7, -7],
  [8, -3.6],
  [4.6, -3],
  [2.4, -5],
];

/**
 * A large ice floe: a wide irregular plate with a snow drift on it, a blue melt pool, a long
 * pressure ridge and loose chunks around its edge.
 */
export function buildLargeFloe(): PropGeometry {
  const s = new SolidBuilder();
  s.slab(LARGE_FLOE, [0, 1.4], C.iceBlue, {}, C.snow);
  s.slab(DRIFT, [1.4, 2.2], C.snowShade, {}, C.snow);
  pool(s, MELT_POOL, 1.4);
  ridge(s, [
    [[2.6, 2.8, 2], [-9, 1, -5], 0.3, 0.5],
    [[2.4, 3, 1.8], [-6.6, 1, -6.4], -0.25, 0.4],
    [[2.2, 2.6, 2], [-4.2, 1, -7.6], 0.35, 0.6],
    [[2, 2, 1.6], [-1.8, 1, -8.6], -0.2, 0.3],
  ]);
  s.box([2, 0.8, 1.6], C.ice, { at: [14, 0, -2], yaw: 0.4 }, C.snow);
  s.box([1.6, 0.7, 1.4], C.ice, { at: [-6, 0, 12.4], yaw: 1.1 }, C.snow);
  return { structure: s.geometry };
}

const BERG_BASE: readonly OutlinePoint[] = [
  [-10, -2],
  [-6, -8.6],
  [2, -9.6],
  [8.8, -5],
  [10, 2],
  [5, 8.4],
  [-4, 8.8],
  [-9, 4.6],
];
const BERG_TOP: readonly OutlinePoint[] = [
  [-6, -1],
  [-2.6, -5.4],
  [3.4, -4.6],
  [6, 0.6],
  [2.8, 5.4],
  [-3.6, 4.6],
];

/**
 * An iceberg: a wide faceted block of white-blue ice with sloping sides, a taller block on it
 * and a sharp peak, snow on the flats.
 */
export function buildIceberg(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  s.bevelSlab(BERG_BASE, [0, 1.2, 6], [-0.6, 2.2], C.iceBlue, {}, C.snow);
  s.bevelSlab(BERG_TOP, [6, 6, 15], [0, 2.4], C.ice, { at: [-0.6, 0, 0.4] }, C.snow);
  cone(s, 3, [14.6, 7.4], 5, C.ice, { at: [-1.6, 0, 1.2] });
  cone(s, 2.6, [5.6, 4.2], 5, C.iceBlue, { at: [5.4, 0, -3.2] });
  return { structure: s.geometry };
}

/**
 * A weather buoy: an orange float with a white band, a short mast with a solar panel and
 * instruments, and a light on top.
 */
export function buildWeatherBuoy(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  s.lathe(
    [
      [1.8, 0],
      [2.1, 0.7],
      [1.9, 1.4],
      [1.2, 1.9],
    ],
    8,
    C.signalOrange,
  );
  s.ring(2.12, 0.3, 8, C.white, { at: [0, 0.6, 0] });
  s.cylinder(0.5, 4.4, 4, C.metal, { at: [0, 1.9, 0], yaw: Math.PI / 4 }, 0.18);
  s.box([1.4, 0.15, 1], C.solar, { at: [0, 4, -0.4], pitch: -0.5 });
  s.box([1.6, 0.15, 0.15], C.metalDark, { at: [0, 5.4, 0] });
  l.box([0.5, 0.5, 0.5], L.yellow, { at: [0, 6.3, 0] });
  return { structure: s.geometry, lights: l.geometry };
}

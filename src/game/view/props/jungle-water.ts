import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { corners, pane, posts } from './polar-parts';
import { gableRoof, leaf, strut } from './jungle-parts';

// P09-R06: what stands on the jungle's water (Y = 0 is the water surface): reed clumps, lily
// pads, fishing platforms on stilts, and the waterfalls where a river drops over a cliff.

type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

/** A cattail: a thin stalk from the water up to `top`, a brown seed head near its tip. */
function cattail(s: SolidBuilder, [x, z]: readonly [number, number], top: Vec3): void {
  strut(s, [x, 0, z], top, [0.12, 0.08], C.reed);
  const [tx, ty, tz] = top;
  s.cylinder(0.28, 1, 4, C.cattail, { at: [tx, ty - 1.4, tz] });
}

/** Blades of the reed clump: where each rises from, its heading and its lean (negative: up). */
const BLADES = [
  [0.4, 0.2, 0, -1.25],
  [-0.6, 0.5, 1.2, -1.3],
  [0.9, -0.7, 2.3, -1.2],
  [-0.2, -1, 3.1, -1.35],
  [-1.3, -0.3, 4, -1.2],
  [1.4, 0.8, 4.9, -1.3],
  [0, 1.4, 5.6, -1.25],
  [-1, 1.2, 0.8, -1.15],
  [1.2, -1.5, 3.6, -1.3],
] as const;

/** A clump of reeds standing in the water: tall pointed blades in two greens and four cattails. */
export function buildReeds(): PropGeometry {
  const s = new SolidBuilder();
  BLADES.forEach(([x, z, yaw, pitch], i) => {
    leaf(s, [x, 0, z], [0.8, 4.6], { yaw, pitch }, i % 2 === 0 ? C.reed : C.moss);
  });
  cattail(s, [0.2, -0.3], [0.6, 4.9, -0.5]);
  cattail(s, [-0.8, 0.6], [-1.3, 4.4, 0.9]);
  cattail(s, [1, 0.4], [1.6, 4, 0.7]);
  cattail(s, [-0.3, -1.2], [-0.5, 3.8, -1.9]);
  return { structure: s.geometry };
}

/** The pads of a lily patch: centre (x, z), radius and colour. */
const PADS: readonly (readonly [number, number, number, Rgb])[] = [
  [0, 0, 1.6, C.lilyPad],
  [2.4, 1, 1.2, C.moss],
  [-2.2, 1.3, 1.4, C.lilyPad],
  [1, -2.4, 1.3, C.canopyLight],
  [-1.6, -2, 1.1, C.lilyPad],
  [3, -1.6, 0.9, C.moss],
  [-3.3, -0.6, 0.9, C.canopyLight],
];

/**
 * A patch of lily pads floating flat on the water, a pink flower opening on the largest, and a
 * few cattails and bare stalks standing out of the water among them.
 */
export function buildLilyPads(): PropGeometry {
  const s = new SolidBuilder();
  for (const [x, z, r, color] of PADS) {
    s.lathe(
      [
        [r, 0],
        [0, 0.15],
      ],
      6,
      color,
      { at: [x, 0, z] },
      false,
    );
  }
  s.lathe(
    [
      [0.25, 0.1],
      [0.8, 0.7],
      [0.3, 0.5],
      [0, 0.6],
    ],
    5,
    C.lilyFlower,
    { at: [0.2, 0, 0.1] },
    false,
  );
  cattail(s, [2.6, 2.4], [2.9, 4.2, 2.8]);
  cattail(s, [-2.8, 2.6], [-3.1, 3.7, 3]);
  strut(s, [-0.4, 0, 3], [-0.2, 3.4, 3.3], [0.1, 0.06], C.reed);
  strut(s, [3.4, 0, 0.6], [3.6, 3.2, 0.4], [0.1, 0.06], C.reed);
  return { structure: s.geometry };
}

/** Height of the fishing platform's deck above the water. */
const DECK = 2.6;

/**
 * A small fishing platform on stilts over the water: a plank deck with a thatched shed, a rack
 * with a net hung out to dry, a ladder down to the water, and a lamp on a post.
 */
export function buildFishingPlatform(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  posts(s, [...corners(4.2, 3), [0, -3], [0, 3]], DECK, C.woodDark, 0.5);
  s.box([9.4, 0.4, 7], C.wood, { at: [0, DECK, 0] });
  s.box([4, 2.8, 3.6], C.bamboo, { at: [2, DECK + 0.4, 1.2] });
  gableRoof(s, { size: [5, 4.8], y: DECK + 3.2, rise: 1.8 }, C.thatch, C.bamboo, {
    at: [2, 0, 1.2],
  });
  // The net rack at the front: two poles, a bar, and the net hung from it.
  posts(
    s,
    [
      [-4, -3.2],
      [-0.6, -3.2],
    ],
    3.4,
    C.woodDark,
    0.3,
    DECK + 0.4,
  );
  s.box([3.8, 0.25, 0.25], C.woodDark, { at: [-2.3, DECK + 3.6, -3.2] });
  s.face(
    [
      [-3.9, DECK + 1, -3.3],
      [-3.9, DECK + 3.6, -3.3],
      [-0.7, DECK + 3.6, -3.3],
      [-0.7, DECK + 1, -3.3],
    ],
    C.metalDark,
  );
  strut(s, [-4.6, 0, -1], [-4.6, DECK + 0.4, -1], [0.15, 0.15], C.woodDark);
  s.box([0.2, 4.2, 0.2], C.metalDark, { at: [4.2, DECK + 0.4, -3.2] });
  pane(l, [1.2, 1], [2.6, DECK + 1.4, -0.66], L.window);
  l.box([0.6, 0.6, 0.6], L.yellow, { at: [4.2, DECK + 4.6, -3.2] });
  return { structure: s.geometry, lights: l.geometry };
}

/** Half width of the waterfall's ledge along X, and its half depth along Z. */
const FALL_HALF = 44;
const LEDGE_HALF = 14;
/** Height of the upper river's surface on top of the ledge. */
const LIP = 14;
/** Strips of the falling water, alternating foam and spray, across the river. */
const STRIPS = 8;
/** Half width of the falling sheet, between the rocks at both ends. */
const SHEET_HALF = 33;

/** Rocks at the ends of the ledge and in the falls: centre (x, z), radius, height. */
const ROCKS = [
  [-39, -4, 5, 19],
  [-37, -11, 3.5, 9],
  [38.5, -3, 5.5, 18],
  [36.5, 8, 5, 16],
  [-38, 8, 5, 16.5],
] as const;

/** Spray puffs at the foot of the falls: x, radius and height. */
const PUFFS = [
  [-28, 2.6, 4],
  [-19, 3, 5],
  [-9.5, 2.8, 4.4],
  [0, 3, 5.4],
  [9.5, 2.7, 4.6],
  [19, 3, 5],
  [28, 2.4, 3.6],
] as const;

/** One band of the falling sheet, from (top, zTop) down to (bottom, zBottom), in strips. */
function sheetBand(
  s: SolidBuilder,
  [top, zTop]: readonly [number, number],
  [bottom, zBottom]: readonly [number, number],
  shift: number,
): void {
  const step = (2 * SHEET_HALF) / STRIPS;
  for (let i = 0; i < STRIPS; i++) {
    const [x0, x1] = [-SHEET_HALF + i * step, -SHEET_HALF + (i + 1) * step];
    s.face(
      [
        [x0, bottom, zBottom],
        [x0, top, zTop],
        [x1, top, zTop],
        [x1, bottom, zBottom],
      ],
      (i + shift) % 2 === 0 ? C.foam : C.spray,
    );
  }
}

/**
 * A waterfall across a river (its width along X): a mossy rock ledge from X = -44 to 44 and
 * Z = -14 to 14 with the upper river's water on top at 14 high, a white sheet of falling water
 * on its downstream face (-Z) curling over the lip down to the lower river, white spray puffs at
 * its foot, and big rocks at both ends.
 */
export function buildWaterfall(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  s.box([2 * FALL_HALF - 2, LIP, 2 * LEDGE_HALF], C.mossStoneDark, {}, C.riverWater);
  // A band of foam where the water speeds up over the lip.
  s.box([2 * SHEET_HALF, 0.3, 3], C.spray, { at: [0, LIP, -LEDGE_HALF + 1.5] }, C.foam);
  sheetBand(s, [LIP + 0.3, -LEDGE_HALF], [LIP - 2.5, -LEDGE_HALF - 1.2], 0);
  sheetBand(s, [LIP - 2.5, -LEDGE_HALF - 1.2], [0, -LEDGE_HALF - 2], 1);
  for (const [x, z, r, h] of ROCKS) {
    s.lathe(
      [
        [r, 0],
        [r * 0.85, h * 0.6],
        [r * 0.35, h],
      ],
      5,
      h > LIP ? C.mossStone : C.mossStoneDark,
      { at: [x, 0, z], yaw: x * 0.1 },
    );
  }
  PUFFS.forEach(([x, r, h], i) => {
    s.lathe(
      [
        [r, 0],
        [r * 1.05, h * 0.45],
        [0, h],
      ],
      5,
      i % 2 === 0 ? C.foam : C.spray,
      { at: [x, 0, -LEDGE_HALF - 1.8] },
      false,
    );
  });
  return { structure: s.geometry };
}

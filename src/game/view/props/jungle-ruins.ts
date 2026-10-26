import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { pane } from './polar-parts';
import { crown, hipRoof, vines } from './jungle-parts';

// P09-R06: the overgrown temple ruins of 3-3 (stepped pyramids, statues, shrines, causeways):
// grey-green mossy stone, moss on every ledge, vines down the walls, and the violet neon the
// enemy added when it moved in. Sizes in world units, standing on Y = 0; the front faces -Z.

type Rgb = readonly [number, number, number];

/** Moss greens of the vines. */
const VINES: readonly [Rgb, Rgb] = [C.moss, C.mossDark];

/** The pyramid's tiers: half side and height of each, bottom to top. */
const TIERS = [
  [15, 3.6],
  [12.4, 3.4],
  [9.8, 3.4],
  [7.4, 3.2],
] as const;
/** Height of the pyramid's top platform, where the shrine stands. */
const SUMMIT = TIERS.reduce((sum, [, h]) => sum + h, 0);

/**
 * The front staircase of the pyramid: a sloping paved ramp from the ground in front of the
 * bottom tier up to the summit, with its two sides (4 triangles).
 */
function staircase(s: SolidBuilder, half: number, [z0, z1]: readonly [number, number]): void {
  s.face(
    [
      [-half, 0, z0],
      [-half, SUMMIT, z1],
      [half, SUMMIT, z1],
      [half, 0, z0],
    ],
    C.paving,
  );
  s.face(
    [
      [-half, 0, z0],
      [-half, 0, z1],
      [-half, SUMMIT, z1],
    ],
    C.mossStoneDark,
  );
  s.face(
    [
      [half, 0, z1],
      [half, 0, z0],
      [half, SUMMIT, z1],
    ],
    C.mossStoneDark,
  );
}

/**
 * An overgrown stepped pyramid: four mossy stone tiers, a paved staircase up its front, vines
 * down the tiers, trees rooted on its ledges, and a shrine on the summit whose doorway the enemy
 * lit with violet neon, with a mast and a red light.
 */
export function buildStepPyramid(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  let y = 0;
  TIERS.forEach(([half, h], i) => {
    s.box(
      [2 * half, h, 2 * half],
      i % 2 === 0 ? C.mossStone : C.mossStoneDark,
      { at: [0, y, 0] },
      C.moss,
    );
    vines(s, [-half * 0.55, y + h, -half - 0.05], [3, half * 0.4, h * 0.9], VINES);
    vines(s, [half * 0.6, y + h, -half - 0.05], [2, half * 0.25, h * 0.8], VINES);
    y += h;
  });
  staircase(s, 2.6, [-19, -(TIERS.at(-1)?.[0] ?? 0)]);
  crown(s, { at: [-11, 3.6, 8], r: 3.4, h: 3.6 }, C.canopy, 5);
  crown(s, { at: [9, 7, -5], r: 2.8, h: 3 }, C.canopyLight, 5);
  crown(s, { at: [5, 10.4, 6.5], r: 2.6, h: 3 }, C.canopyDark, 5);
  s.box([7, 4.2, 7], C.mossStoneDark, { at: [0, SUMMIT, 0.6] });
  hipRoof(s, 8.2, [SUMMIT + 4.2, 2.6], C.mossStone, { at: [0, 0, 0.6] });
  s.cylinder(0.15, 7, 3, C.metalDark, { at: [2.6, SUMMIT + 4.2, 3] });
  pane(l, [2.4, 3], [0, SUMMIT, -2.96], L.violet);
  l.box([7.4, 0.3, 0.3], L.violet, { at: [0, SUMMIT + 4, -2.85] });
  l.box([0.5, 0.5, 0.5], L.red, { at: [2.6, SUMMIT + 11.2, 3] });
  return { structure: s.geometry, lights: l.geometry };
}

/**
 * A stone statue of a seated jungle god on a mossy plinth: legs folded, hands on its knees, a
 * tall headdress; the enemy fitted its eyes with glowing violet lenses.
 */
export function buildTempleStatue(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([7, 2, 7], C.mossStoneDark, {}, C.moss);
  s.box([5.6, 2, 3.6], C.mossStone, { at: [0, 2, -0.8] });
  s.box([3.6, 5, 2.6], C.mossStone, { at: [0, 4, 0.6] });
  for (const x of [-2.1, 2.1]) s.box([0.9, 3.6, 1], C.mossStoneDark, { at: [x, 4, -0.6] });
  s.box([2.8, 2.8, 2.4], C.mossStone, { at: [0, 9, 0.4] });
  s.box([3.6, 3, 0.8], C.mossStoneDark, { at: [0, 11.6, 1.2] }, C.moss);
  vines(s, [1, 9, -0.82], [2, 1.2, 3.2], VINES);
  vines(s, [-1.6, 2, -3.52], [2, 2.6, 1.8], VINES);
  l.box([0.6, 0.4, 0.2], L.violet, { at: [-0.65, 10.4, -0.85] });
  l.box([0.6, 0.4, 0.2], L.violet, { at: [0.65, 10.4, -0.85] });
  return { structure: s.geometry, lights: l.geometry };
}

/** Pillars of the shrine: (x, z), height; the short ones are broken. */
const PILLARS = [
  [-4.4, -3, 7],
  [-1.5, -3, 7],
  [1.5, -3, 3.5],
  [4.4, -3, 6],
  [-4.4, 2.6, 5],
  [4.4, 2.6, 7],
] as const;

/**
 * A ruined shrine: a paved platform with a broken colonnade, a lintel still lying across two
 * pillars, a fallen block, vines and a mossy tree; an enemy relay box on it with a violet light.
 */
export function buildRuinShrine(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([12, 1, 9.4], C.mossStoneDark, {}, C.paving);
  for (const [x, z, h] of PILLARS) s.cylinder(0.75, h, 5, C.mossStone, { at: [x, 1, z] });
  s.box([4.8, 1, 1.8], C.mossStone, { at: [-2.95, 8, -3] }, C.moss);
  s.box([2.4, 1.6, 1.8], C.mossStone, { at: [2.6, 1, 0.6], yaw: 0.5 }, C.moss);
  vines(s, [-2.95, 8, -3.95], [3, 3, 3.6], VINES);
  crown(s, { at: [4.8, 4.5, 2.4], r: 2.6, h: 3.2 }, C.canopy, 5);
  s.box([1.8, 1.6, 1.4], C.jungleMetal, { at: [-1.6, 1, 2] });
  l.box([1.4, 0.3, 0.2], L.violet, { at: [-1.6, 2, 1.25] });
  l.box([0.4, 0.4, 0.4], L.red, { at: [1.5, 4.5, -3] });
  return { structure: s.geometry, lights: l.geometry };
}

/** Length of a causeway piece along X: pieces are laid end to end every 15. */
const CAUSEWAY_LENGTH = 15;
/** Height of the causeway's deck. */
const CAUSEWAY_DECK = 3.4;

/**
 * A piece of a raised stone causeway, exactly 15 long along X (x = -7.5 to 7.5): a paved deck
 * with low parapets on two mossy piers, vines down its sides.
 */
export function buildCauseway(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const half = CAUSEWAY_LENGTH / 2;
  for (const x of [-half / 2, half / 2]) {
    s.box([2.6, CAUSEWAY_DECK, 5], C.mossStoneDark, { at: [x, 0, 0] });
  }
  s.box([CAUSEWAY_LENGTH, 1, 6.4], C.mossStone, { at: [0, CAUSEWAY_DECK, 0] }, C.paving);
  for (const z of [-2.9, 2.9]) {
    s.box([CAUSEWAY_LENGTH, 0.8, 0.6], C.mossStone, { at: [0, CAUSEWAY_DECK + 1, z] }, C.moss);
  }
  vines(s, [-1, CAUSEWAY_DECK + 1, -3.25], [3, 6, 2.6], VINES);
  vines(s, [1.5, CAUSEWAY_DECK + 1, 3.25], [2, 5, 2.2], VINES, Math.PI);
  return { structure: s.geometry };
}

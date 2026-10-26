import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C } from '../../config/prop-look';
import { cone } from './polar-parts';
import { crown, leaf, strut, trunk, type Crown } from './jungle-parts';

// P09-R06: the vegetation of World 3: the canopy (packed broadleaf crowns, drawn by the thousand,
// so the lightest of all), emergent trees, palms, giant ferns, mangroves on stilt roots, twisted
// swamp trees. Sizes in world units, standing on Y = 0 (the water level for the mangrove).

type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

/**
 * The crowns of a canopy patch: foot, radius, height, colour and facets. Five crowns in five
 * greens, the tallest in the middle, packed so neighbouring patches close over the ground.
 */
const CLUSTER: readonly (readonly [Crown, Rgb, number])[] = [
  [{ at: [0, 12, 0], r: 8, h: 9.5 }, C.canopy, 7],
  [{ at: [-7, 8.5, 3.5], r: 6.5, h: 8.5 }, C.canopyDark, 6],
  [{ at: [6.5, 10, 4.5], r: 6, h: 9 }, C.canopyLight, 6],
  [{ at: [3, 7.5, -7], r: 6.5, h: 8.5 }, C.canopyBlue, 6],
  [{ at: [-5, 6.5, -6], r: 5.5, h: 7.5 }, C.canopyYellow, 6],
];

/**
 * A patch of canopy: five big round, slightly flattened crowns in several greens, 14 to 22 high,
 * on short trunks hidden under them (111 triangles).
 */
export function buildCanopyCluster(): PropGeometry {
  const s = new SolidBuilder();
  for (const [c, color, sides] of CLUSTER) crown(s, c, color, sides);
  for (const [{ at }] of CLUSTER.slice(0, 3)) {
    trunk(s, [at[0], 0, at[2]], [0.9, 0.6, at[1] + 1], C.jungleBark, 3);
  }
  return { structure: s.geometry };
}

/**
 * An emergent tree rising out of the canopy: a tall pale trunk on buttress roots, a branch, and
 * a big round crown with two side lobes, about 26 high.
 */
export function buildCanopyCrown(): PropGeometry {
  const s = new SolidBuilder();
  trunk(s, [0, 0, 0], [1.3, 0.7, 17], C.jungleBark, 5);
  for (const a of [0.4, 2.5, 4.6]) {
    strut(s, [2.4 * Math.cos(a), 0, 2.4 * Math.sin(a)], [0, 4, 0], [0.5, 0.2], C.jungleBark);
  }
  strut(s, [0, 12, 0], [3.4, 15.5, 1], [0.45, 0.3], C.jungleBark);
  crown(s, { at: [0, 15, 0], r: 6.5, h: 11 }, C.canopy, 8, true);
  crown(s, { at: [3.6, 13.5, 1.6], r: 4, h: 6 }, C.canopyLight, 6);
  crown(s, { at: [-3.2, 14, -2], r: 3.8, h: 6 }, C.canopyDark, 6);
  return { structure: s.geometry };
}

/** Fronds of a palm crown at `top`: `count` long drooping leaves in two greens. */
function fronds(
  s: SolidBuilder,
  top: Vec3,
  count: number,
  [len, droop]: readonly [number, number],
) {
  for (let i = 0; i < count; i++) {
    const turn = { yaw: (2 * Math.PI * i) / count + 0.2, pitch: droop + (i % 2) * 0.25 };
    leaf(s, top, [1.8, len], turn, i % 2 === 0 ? C.palmLeaf : C.fern);
  }
}

/** A jungle palm: a slender bent trunk with a crown of long drooping fronds, about 12 high. */
export function buildJunglePalm(): PropGeometry {
  const s = new SolidBuilder();
  strut(s, [0, 0, 0], [0.8, 6, 0], [0.6, 0.5], C.palmTrunk, 5);
  strut(s, [0.8, 6, 0], [0.9, 11.6, 0.4], [0.5, 0.4], C.palmTrunk, 5);
  cone(s, 0.7, [11.2, 1.2], 4, C.palmTrunk);
  fronds(s, [0.9, 11.8, 0.4], 8, [5.2, 0.35]);
  return { structure: s.geometry };
}

/** A giant fern: a ring of tall fronds rising and arching out, a lower ring of spreading ones. */
export function buildGiantFern(): PropGeometry {
  const s = new SolidBuilder();
  cone(s, 0.8, [0, 1.6], 4, C.jungleBark);
  for (let i = 0; i < 7; i++) {
    const yaw = (2 * Math.PI * i) / 7;
    leaf(s, [0, 0.8, 0], [2, 7.5], { yaw, pitch: -0.75 }, i % 2 === 0 ? C.fern : C.canopyLight);
  }
  for (let i = 0; i < 5; i++) {
    const yaw = (2 * Math.PI * (i + 0.5)) / 5;
    leaf(s, [0, 0.5, 0], [2.2, 6], { yaw, pitch: -0.25 }, C.canopy);
  }
  return { structure: s.geometry };
}

/** Headings of the mangrove's stilt roots around its trunk, radians. */
const ROOTS = [0.3, 1.35, 2.4, 3.4, 4.4, 5.4] as const;

/**
 * A mangrove standing in shallow water (Y = 0 is the water level): a short trunk held up by six
 * arching stilt roots, under a wide dark crown.
 */
export function buildMangrove(): PropGeometry {
  const s = new SolidBuilder();
  for (const a of ROOTS) {
    const [c, n] = [Math.cos(a), Math.sin(a)];
    const knee: Vec3 = [3.4 * c, 3, 3.4 * n];
    strut(s, [4.3 * c, 0, 4.3 * n], knee, [0.3, 0.25], C.swampBark);
    strut(s, knee, [0.5 * c, 5, 0.5 * n], [0.25, 0.4], C.swampBark);
  }
  trunk(s, [0, 4.5, 0], [0.7, 0.5, 4], C.swampBark, 5);
  crown(s, { at: [0, 7, 0], r: 5, h: 5.5 }, C.canopyDark, 7, true);
  crown(s, { at: [1.8, 8.5, -1.2], r: 3, h: 4.5 }, C.canopyBlue, 5);
  return { structure: s.geometry };
}

/**
 * A twisted swamp tree: a crooked trunk in three bends, bare branches, two sparse dark crowns
 * and beards of grey-green moss hanging from the branches.
 */
export function buildSwampTree(): PropGeometry {
  const s = new SolidBuilder();
  const bends: readonly Vec3[] = [
    [0, -0.1, 0],
    [0.9, 3.5, 0.3],
    [-0.4, 6.5, -0.4],
    [0.6, 9.5, 0.2],
  ];
  bends.slice(1).forEach((to, i) => {
    const from = bends[i] ?? to;
    strut(s, from, to, [0.8 - i * 0.18, 0.62 - i * 0.18], C.swampBark, 4);
  });
  const tips: readonly Vec3[] = [
    [3.6, 8.6, 1.2],
    [-3.4, 9.4, -0.6],
    [0.4, 11, -3.2],
  ];
  for (const tip of tips) {
    strut(s, [0.3, 7.5, 0], tip, [0.35, 0.15], C.swampBark);
    // A moss beard hanging from each branch tip, an upside-down cone.
    s.lathe(
      [
        [0, tip[1] - 3.2],
        [0.7, tip[1] - 0.2],
      ],
      3,
      C.hangingMoss,
      { at: [tip[0] * 0.85, 0, tip[2] * 0.85] },
      false,
    );
  }
  crown(s, { at: [2.4, 9.2, 0.8], r: 2.4, h: 2.6 }, C.mossDark, 5);
  crown(s, { at: [-1.6, 10, -1.2], r: 2.8, h: 2.8 }, C.mossDark, 5);
  return { structure: s.geometry };
}

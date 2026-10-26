import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { windowBands } from './city-props';
import { pane } from './polar-parts';
import { crown, hipRoof, strut, trunk } from './jungle-parts';

// P09-R06: the canopy city of 3-5: tree-top outposts built round giant trunks, and towers rising
// out of the canopy linked by sky bridges, trees on their roofs. Lit windows and neon for the
// night. Sizes in world units, standing on Y = 0; the front faces -Z.

type Rgb = readonly [number, number, number];

/** Heights of the tree-top outpost's two platforms round the trunk. */
const LOW_DECK = 10;
const HIGH_DECK = 16.5;
/** Headings of the struts under the lower platform, radians. */
const BRACES = [0.4, 2, 3.6, 5.2] as const;

/** A hut on a platform: a plank room under a hip roof, a lit window on its front (-Z). */
function hut(
  s: SolidBuilder,
  l: SolidBuilder,
  [x, y, z]: readonly [number, number, number],
  w: number,
): void {
  s.box([w, 2.6, w], C.wood, { at: [x, y, z] });
  hipRoof(s, w + 1, [y + 2.6, 1.8], C.thatch, { at: [x, 0, z] });
  pane(l, [w * 0.45, 0.9], [x, y + 1, z - w / 2 - 0.06], L.window);
}

/**
 * A tree-top outpost: a giant trunk with a round platform part way up, braced underneath, two
 * huts on it, a smaller lookout platform higher up, the tree's crown above, a ladder, and at
 * night a cyan neon rim and lit windows.
 */
export function buildTreetopPlatform(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  trunk(s, [0, 0, 0], [2.4, 1.5, 20], C.jungleBark, 6);
  for (const a of BRACES) {
    const [c, n] = [Math.cos(a), Math.sin(a)];
    strut(s, [1.9 * c, LOW_DECK - 4, 1.9 * n], [6 * c, LOW_DECK, 6 * n], [0.3, 0.3], C.woodDark);
  }
  s.cylinder(7, 0.6, 8, C.wood, { at: [0, LOW_DECK, 0], yaw: Math.PI / 8 });
  s.cylinder(3.6, 0.5, 6, C.wood, { at: [0, HIGH_DECK, 0] });
  hut(s, l, [-3.4, LOW_DECK + 0.6, -2.4], 3.4);
  hut(s, l, [3.2, LOW_DECK + 0.6, 2], 3);
  hut(s, l, [1.2, HIGH_DECK + 0.5, -1.6], 2.2);
  strut(s, [4.8, 0, -4.4], [4.6, LOW_DECK, -4.2], [0.15, 0.15], C.woodDark);
  crown(s, { at: [0, 19, 0], r: 6.5, h: 7.5 }, C.canopy, 7, true);
  crown(s, { at: [-4.2, 17.5, 3.4], r: 3.4, h: 4 }, C.canopyLight, 5);
  l.ring(7.05, 0.3, 8, L.cyan, { at: [0, LOW_DECK + 0.15, 0], yaw: Math.PI / 8 });
  l.ring(3.65, 0.25, 6, L.yellowDim, { at: [0, HIGH_DECK + 0.1, 0] });
  return { structure: s.geometry, lights: l.geometry };
}

/** A tower of the sky-bridge group: centre (x, z), half side, height, facade. */
type Tower = readonly [x: number, z: number, half: number, h: number, facade: Rgb];

const TOWERS: readonly Tower[] = [
  [-7.5, -5, 4, 30, C.glassGreen],
  [7.5, -4, 4.2, 40, C.glassDark],
  [0, 8.5, 3.8, 24, C.mossStoneDark],
];
/** The sky bridges: the towers they link (indices) and their height. */
const BRIDGES = [
  [0, 1, 22],
  [1, 2, 17],
  [0, 2, 12],
] as const;

/** A sky bridge between two towers at height `y`: a glazed tube with a lit strip along it. */
function skyBridge(s: SolidBuilder, l: SolidBuilder, a: Tower, b: Tower, y: number): void {
  const [dx, dz] = [b[0] - a[0], b[1] - a[1]];
  const length = Math.hypot(dx, dz);
  const place = {
    at: [(a[0] + b[0]) / 2, y, (a[1] + b[1]) / 2] as const,
    yaw: -Math.atan2(dz, dx),
  };
  s.box([length - 2, 2, 2.4], C.glassBlue, place, C.metal);
  l.box([length - 2.4, 0.3, 2.6], L.pinkDim, { ...place, at: [place.at[0], y - 0.3, place.at[2]] });
}

/**
 * Towers linked by sky bridges: three slender towers of glass and old stone rising out of the
 * canopy, glazed bridges between them at different heights, trees growing on their roofs, rows
 * of lit windows and neon bridge strips.
 */
export function buildSkyBridgeTowers(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  for (const [x, z, half, h, facade] of TOWERS) {
    s.box([2 * half, h, 2 * half], facade, { at: [x, 0, z] }, C.moss);
    windowBands(l, [2 * half, 2 * half], [6, h - 2], 6.5, 1.4, L.windowDim, [x, z]);
    crown(s, { at: [x - half * 0.3, h, z + half * 0.2], r: half * 0.75, h: 3.4 }, C.canopy, 5);
    crown(s, { at: [x + half * 0.45, h, z - half * 0.4], r: half * 0.5, h: 2.6 }, C.canopyLight, 5);
  }
  for (const [i, j, y] of BRIDGES) {
    const [a, b] = [TOWERS[i], TOWERS[j]];
    if (a && b) skyBridge(s, l, a, b, y);
  }
  l.box([0.5, 0.5, 0.5], L.red, { at: [10.9, 40, -7.4] });
  return { structure: s.geometry, lights: l.geometry };
}

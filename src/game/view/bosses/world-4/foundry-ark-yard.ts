import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { rod } from '../final-boss-greebles';
import { seam } from '../mini-boss-greebles';
import { H, SHADE } from '../mini-boss-shapes';
import { ARK_ORANGE, DECK_TOP, MOLTEN, RUST, SOOT } from './foundry-ark-parts';

// P10-R11, 4-4: the Foundry Ark's yard, the heavy industry on its deck around the furnace: casting
// sheds with lit windows, ore wagons on their rails, pipe runs, molten seams between the plates.
// Model space: logical pixels, nose +Z, Y up; drawn for the right side (+X) and mirrored.
type Vec3 = [number, number, number];

/** The casting sheds along the deck's sides (right side): centre, width, length, height. */
const SHEDS = [
  [38, -62, 14, 22, 9],
  [42, 0, 10, 20, 7],
] as const;
/** The ore wagons on the rails between the furnace and the battery (centre along Z). */
const WAGONS = [42, 56] as const;
/** The deck plates' molten seams (right side): glowing cracks where the plates meet. */
const SEAMS: readonly (readonly [OutlinePoint, OutlinePoint])[] = [
  [
    [22, 30],
    [46, 52],
  ],
  [
    [20, -36],
    [26, -84],
  ],
  [
    [50, -30],
    [56, 6],
  ],
];
/** The pipe runs from the furnace to the chimney row (right side): from, bend, to. */
const PIPE: readonly Vec3[] = [
  [14, DECK_TOP + 8, 14],
  [20, DECK_TOP + 6, 28],
  [17, DECK_TOP + 6, 42],
];

/** A casting shed: a long block with a sawtooth roof, a row of furnace-lit windows. */
function shed(
  { hull, neon }: EnemyParts,
  s: number,
  [x, z, w, d, h]: readonly [number, number, number, number, number],
): void {
  hull.box([w, h, d], H.base, { at: [s * x, DECK_TOP, z] }, RUST);
  for (const dz of [-d / 3, 0, d / 3]) {
    hull.box([w * 0.9, 2, 2], H.panel, { at: [s * x, DECK_TOP + h, z + dz], roll: s * 0.35 });
  }
  neon.box([0.4, 1.2, d * 0.8], ARK_ORANGE, { at: [s * (x - w / 2 - 0.2), DECK_TOP + h / 2, z] });
}

/** An ore wagon on the rails, heaped with glowing ore. */
function wagon({ hull, neon }: EnemyParts, z: number): void {
  hull.box([7, 3.2, 10], H.dark, { at: [0, DECK_TOP + 0.6, z] }, SHADE.edge);
  neon.box([5, 0.6, 7.6], MOLTEN, { at: [0, DECK_TOP + 3.6, z] });
  hull.box([5.4, 1, 3], SOOT, { at: [0, DECK_TOP + 4, z] });
}

/** The yard on the deck: sheds, wagons, pipe runs and glowing seams between the plates. */
export function drawYard(p: EnemyParts): void {
  const { hull, neon } = p;
  for (const s of SIDES) {
    for (const spec of SHEDS) shed(p, s, spec);
    for (const [[ax, az], [bx, bz]] of SEAMS) {
      seam(neon, [s * ax, az], [s * bx, bz], [DECK_TOP, 0.5, 0.15], MOLTEN);
    }
    const side = PIPE.map(([x, y, z]): Vec3 => [s * x, y, z]);
    side.slice(1).forEach((b, i) => {
      const a = side[i];
      if (a) rod(hull, a, b, 1.3, H.panel);
    });
  }
  for (const z of WAGONS) wagon(p, z);
}

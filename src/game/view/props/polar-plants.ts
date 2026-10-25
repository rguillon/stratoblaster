import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C } from '../../config/prop-look';
import { cone } from './polar-parts';

// P08-R07: the snowy vegetation of World 2. Sizes in world units, standing on Y = 0.

/** A snow-covered pine: a short trunk under three dark green tiers, each with a white cap. */
export function buildSnowPine(): PropGeometry {
  const s = new SolidBuilder();
  s.cylinder(0.6, 2.6, 5, C.bark, {}, 0.45);
  const tiers = [
    [3.7, 2, 6],
    [3, 5, 5.5],
    [2.1, 8, 5],
  ] as const;
  tiers.forEach(([r, y, h], i) => {
    s.lathe(
      [
        [r, y],
        [0, y + h],
      ],
      6,
      i === 1 ? C.pine : C.pineDark,
    );
    // The snow sits on the upper half of each tier, a little proud of the needles.
    cone(s, r * 0.58, [y + h * 0.45, h * 0.55 + 0.25], 6, i === 0 ? C.snowShade : C.snow);
  });
  return { structure: s.geometry };
}

/** A bare frosted tree: a pale leaning trunk with a few upturned branches tipped with frost. */
export function buildFrostedTree(): PropGeometry {
  const s = new SolidBuilder();
  s.cylinder(0.45, 9, 5, C.frostDark, { roll: 0.04 }, 0.18);
  const branches = [
    [3, 0.6, 0],
    [4.6, 0.7, 2.2],
    [6, 0.65, 4.1],
    [7.2, 0.55, 1.2],
  ] as const;
  for (const [y, lean, yaw] of branches) {
    s.box([0.28, 3, 0.28], C.frost, { at: [0, y, 0], roll: lean, yaw });
    // A tuft of frost at the tip of each branch.
    const reach = 2.8 * Math.sin(lean);
    const top = y + 2.8 * Math.cos(lean);
    s.lathe(
      [
        [0, top - 0.5],
        [0.55, top],
        [0, top + 0.6],
      ],
      4,
      C.snow,
      { at: [-reach * Math.cos(yaw), 0, reach * Math.sin(yaw)] },
    );
  }
  return { structure: s.geometry };
}

/** A low, round snowy bush: two dark green mounds under thick snow. */
export function buildSnowyBush(): PropGeometry {
  const s = new SolidBuilder();
  s.lathe(
    [
      [2.4, 0],
      [2.5, 1.2],
      [1.8, 2.4],
    ],
    6,
    C.pineDark,
    {},
    false,
  );
  s.lathe(
    [
      [2, 2.1],
      [1.4, 3],
      [0, 3.5],
    ],
    6,
    C.snow,
    {},
    false,
  );
  s.lathe(
    [
      [1.4, 0],
      [1.5, 0.9],
      [0.9, 1.6],
      [0, 2],
    ],
    5,
    C.snowShade,
    { at: [1.6, 0, -0.9] },
    false,
  );
  return { structure: s.geometry };
}

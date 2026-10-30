import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C } from '../../config/prop-look';

// P06-R06: desert and coast vegetation. Sizes in world units, standing on Y = 0.

/** Fronds of a palm: `count` long thin leaves leaning out and down from the crown. */
function fronds(s: SolidBuilder, top: readonly [number, number, number], count: number): void {
  for (let i = 0; i < count; i++) {
    const yaw = (2 * Math.PI * i) / count + 0.3;
    const color = i % 2 === 0 ? C.palmLeaf : C.leafDark;
    s.box([1.6, 0.25, 7], color, { at: top, yaw, pitch: 0.35 });
  }
}

/** A palm tree: a slightly bent ringed trunk with a crown of drooping fronds. */
export function buildPalmTree(): PropGeometry {
  const s = new SolidBuilder();
  s.cylinder(0.8, 6, 5, C.palmTrunk, { roll: 0.08 }, 0.65);
  s.cylinder(0.65, 6, 5, C.palmTrunk, { at: [-0.45, 5.9, 0], roll: 0.18 }, 0.5);
  fronds(s, [-1.5, 11.6, 0], 7);
  return { structure: s.geometry };
}

/** A dry, scraggly bush: two low olive and straw-coloured mounds. */
export function buildDryBush(): PropGeometry {
  const s = new SolidBuilder();
  s.lathe(
    [
      [2.6, 0],
      [2.4, 1.4],
      [1.2, 2.8],
      [0, 3.4],
    ],
    5,
    C.dryLeaf,
  );
  s.lathe(
    [
      [1.6, 0],
      [1.4, 1],
      [0, 1.8],
    ],
    4,
    C.dryLeafDark,
    { at: [2.2, 0, -1.4] },
  );
  return { structure: s.geometry };
}

/** A cactus-like plant: a tall ribbed column with two raised arms. */
export function buildCactus(): PropGeometry {
  const s = new SolidBuilder();
  s.cylinder(1.1, 10, 6, C.cactus, {}, 0.8);
  s.box([3, 0.9, 0.9], C.cactus, { at: [1.6, 4, 0] });
  s.cylinder(0.6, 4, 5, C.cactus, { at: [3, 4, 0] }, 0.45);
  s.box([2.4, 0.8, 0.8], C.cactus, { at: [-1.4, 6, 0] });
  s.cylinder(0.55, 3, 5, C.cactus, { at: [-2.5, 6, 0] }, 0.4);
  return { structure: s.geometry };
}

import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C } from '../../config/prop-look';

// P04-R04: dead trees, a leafless trunk with a few bare branches. Sizes in world units.

/** Branch: a thin tapered cylinder leaning `lean` radians from vertical, turned by `yaw`. */
function branch(s: SolidBuilder, y: number, length: number, lean: number, yaw: number): void {
  s.cylinder(0.5, length, 4, C.woodDark, { at: [0, y, 0], roll: lean, yaw }, 0.12);
}

/** Tall dead tree with three branches. */
export function buildDeadTree(): PropGeometry {
  const s = new SolidBuilder();
  s.cylinder(1.2, 16, 5, C.wood, {}, 0.45);
  branch(s, 7, 7, 0.9, 0.3);
  branch(s, 10, 6, 0.8, 2.4);
  branch(s, 12.5, 5, 0.7, 4.3);
  return { structure: s.geometry };
}

/** Short dead tree with a bent trunk forking at the top. */
export function buildForkedTree(): PropGeometry {
  const s = new SolidBuilder();
  s.cylinder(1.1, 7, 5, C.wood, { roll: 0.15 }, 0.8);
  s.cylinder(0.8, 6, 5, C.wood, { at: [-1, 6.8, 0], roll: 0.5 }, 0.2);
  s.cylinder(0.7, 5, 5, C.wood, { at: [-1, 6.8, 0], roll: -0.55, yaw: 0.6 }, 0.15);
  branch(s, 4, 4, 1.1, 3.6);
  return { structure: s.geometry };
}

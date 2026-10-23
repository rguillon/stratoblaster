import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C } from '../../config/prop-look';

// Phase 4 review: living trees for the green section. Sizes in world units, standing on Y = 0.

/** Conifer: a short trunk under three stacked cones. */
export function buildConifer(): PropGeometry {
  const s = new SolidBuilder();
  s.cylinder(0.7, 3, 5, C.bark, {}, 0.5);
  const tiers = [
    [4.2, 2.5, 7],
    [3.4, 5.5, 6.5],
    [2.4, 8.5, 6],
  ] as const;
  tiers.forEach(([radius, y, height], i) => {
    s.lathe(
      [
        [radius, y],
        [0, y + height],
      ],
      6,
      i === 1 ? C.leaf : C.leafDark,
    );
  });
  return { structure: s.geometry };
}

/** Broadleaf tree: a trunk under a faceted round crown. */
export function buildBroadleafTree(): PropGeometry {
  const s = new SolidBuilder();
  s.cylinder(0.9, 5, 5, C.bark, {}, 0.6);
  s.lathe(
    [
      [0, 3.8],
      [4.2, 5.5],
      [5.2, 8.5],
      [3.8, 11.5],
      [0, 12.8],
    ],
    7,
    C.leaf,
  );
  return { structure: s.geometry };
}

/** A low, round bush in two tones. */
export function buildBush(): PropGeometry {
  const s = new SolidBuilder();
  s.lathe(
    [
      [3.2, 0],
      [3.4, 1.6],
      [2.2, 3.4],
      [0, 4],
    ],
    6,
    C.leafLight,
  );
  s.lathe(
    [
      [2, 0],
      [2.1, 1.2],
      [1.2, 2.6],
      [0, 3],
    ],
    5,
    C.leafDark,
    { at: [2.6, 0, 1.2] },
  );
  return { structure: s.geometry };
}

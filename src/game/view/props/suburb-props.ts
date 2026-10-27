import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { gableRoof } from './jungle-parts';

// P09-R06 (reviewer's rework, 2026-10-27): the homes of World 3, from the workers' flats by the
// factories to the houses of the garden suburbs. Small buildings only. Sizes in world units, on
// Y = 0; the front faces -Z.

/**
 * A house: two floors of pale render under a red tile roof, a chimney, a flat-roofed garage at
 * its side, lit windows and a cyan neon line under the eaves.
 */
export function buildSuburbHouse(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  const house = { at: [-1.5, 0, 0] } as const;
  s.box([9, 6, 7], C.render, house);
  gableRoof(s, { size: [10, 8.2], y: 6, rise: 3 }, C.tileRoof, C.render, house);
  s.box([1, 3, 1], C.brick, { at: [1, 7, 1.2] });
  s.box([4, 3, 6], C.renderWarm, { at: [5, 0, 0.5] }, C.roof);
  l.box([2, 1.4, 0.2], L.window, { at: [-3.5, 1.4, -3.6] });
  l.box([2, 1.2, 0.2], L.window, { at: [-3.5, 4, -3.6] });
  l.box([2, 1.2, 0.2], L.window, { at: [0.5, 4, -3.6] });
  l.box([9.2, 0.2, 0.2], L.cyan, { at: [-1.5, 5.8, -3.65] });
  return { structure: s.geometry, lights: l.geometry };
}

/**
 * A row of four narrow terraced houses under one slate roof, each a step higher than the last
 * on alternate sides, brick and render by turns, a lit door and windows in each.
 */
export function buildRowHouses(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  for (const [i, x] of [-7.5, -2.5, 2.5, 7.5].entries()) {
    const h = i % 2 === 0 ? 6 : 6.6;
    s.box([5, h, 7], i % 2 === 0 ? C.brick : C.renderWarm, { at: [x, 0, 0] });
    l.box([0.9, 1.6, 0.2], L.window, { at: [x - 1.4, 0, -3.6] });
    l.box([1.6, 1.1, 0.2], L.window, { at: [x + 0.8, 3.8, -3.6] });
  }
  gableRoof(s, { size: [20.6, 8], y: 6.6, rise: 2.4 }, C.slateRoof, C.brick);
  for (const x of [-5, 5]) s.box([0.8, 2.4, 0.8], C.brick, { at: [x, 8, 0] });
  return { structure: s.geometry, lights: l.geometry };
}

/**
 * A small block of flats by the factories: three floors of render on a brick ground floor, a
 * flat roof with a water tank, balcony slabs and lit window strips, a yellow neon sign.
 */
export function buildWalkUp(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([14, 3, 9], C.brick);
  s.box([14, 7, 9], C.render, { at: [0, 3, 0] }, C.roof);
  s.box([3, 2, 3], C.concreteDark, { at: [3.5, 10, 1] }, C.metal);
  for (const y of [3.2, 6.6]) {
    s.box([12, 0.4, 1.4], C.concreteDark, { at: [0, y, -5.1] });
    l.box([11, 1.1, 0.2], L.windowDim, { at: [0, y + 1.3, -4.6] });
  }
  l.box([3, 1.6, 0.2], L.window, { at: [-3, 0.6, -4.6] });
  l.box([4, 0.6, 0.2], L.yellow, { at: [3, 2.2, -4.65] });
  return { structure: s.geometry, lights: l.geometry };
}

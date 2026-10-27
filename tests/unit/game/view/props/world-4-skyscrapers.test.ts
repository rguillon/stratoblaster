import { describe, expect, it } from 'vitest';
import {
  CITY_VARIANTS,
  SKYSCRAPER_VARIANTS,
  variantId,
} from '../../../../../src/game/config/building-families';
import { WORLD_4_PROPS } from '../../../../../src/game/config/world-4/city-props';
import { PROP_MODELS } from '../../../../../src/game/view/props/prop-models';
import type { ColoredGeometry } from '../../../../../src/render/geometry/gradient-shapes';

const EMPTY: ColoredGeometry = { positions: [0, 0, 0], indices: [], colors: [] };
const model = (id: string) => PROP_MODELS[id]?.() ?? { structure: EMPTY, lights: EMPTY };
const coords = (geo: ColoredGeometry, axis: number) =>
  geo.positions.filter((_, i) => i % 3 === axis);
const top = (id: string) => Math.max(...coords(model(id).structure, 1));
const triangles = (id: string) => {
  const { structure, lights = EMPTY } = model(id);
  return (structure.indices.length + lights.indices.length) / 3;
};

// The skyscrapers of World 4's downtown (reviewer's rework, 2026-10-27).
describe('World 4 skyscrapers (P10-R08, rework)', () => {
  const SKYSCRAPERS = Array.from({ length: SKYSCRAPER_VARIANTS }, (_, i) =>
    variantId('skyscraper', i + 1),
  );
  const CITY_TOWERS = Array.from({ length: CITY_VARIANTS }, (_, i) =>
    variantId('city-tower', i + 1),
  );

  it('P10-R08: each skyscraper stays under the 600-triangle cap of the buildings made of parts', () => {
    for (const id of SKYSCRAPERS) expect(triangles(id), id).toBeLessThan(600);
  });

  it('P10-R08: each skyscraper is taller than every city tower, and they differ from one variant to the next', () => {
    const tallestTower = Math.max(...CITY_TOWERS.map(top));
    for (const id of SKYSCRAPERS) expect(top(id), id).toBeGreaterThan(tallestTower);
    const shapes = new Set(
      SKYSCRAPERS.map((id) => JSON.stringify(model(id).structure.positions.slice(0, 60))),
    );
    expect(shapes.size).toBe(SKYSCRAPER_VARIANTS);
  });

  it('P10-R08: each building of World 4 fits in its footprint at its largest scale, lights included', () => {
    for (const kind of WORLD_4_PROPS.groups.flatMap((g) => g.kinds)) {
      const { structure, lights = EMPTY } = model(kind.id);
      const reach = (geo: ColoredGeometry) => {
        const zs = coords(geo, 2);
        return Math.max(0, ...coords(geo, 0).map((x, i) => Math.hypot(x, zs[i] ?? 0)));
      };
      const largest = Math.max(reach(structure), reach(lights)) * kind.scale[1];
      expect(largest, kind.id).toBeLessThanOrEqual(kind.footprint + 1e-9);
    }
  });
});

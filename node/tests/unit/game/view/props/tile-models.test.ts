import { describe, expect, it } from 'vitest';
import {
  BUILDING_MARGIN,
  LOT_MODELS,
  TILE,
  TILE_GROUPS,
  TILE_MODELS,
} from '../../../../../src/game/config/tile-buildings';
import { PROP_COLORS, PROP_LIGHTS } from '../../../../../src/game/config/prop-look';
import { PROP_MODELS } from '../../../../../src/game/view/props/prop-models';
import { buildTileModel } from '../../../../../src/game/view/props/tile-models';
import { SILHOUETTE_COUNT } from '../../../../../src/game/view/props/tile-towers';

// Phase 15: the models made for the grid of tiles.

const sorted = ([a, b]: readonly [number, number]): [number, number] => [
  Math.min(a, b),
  Math.max(a, b),
];

describe('models made for the grid (phase 15)', () => {
  it.each(TILE_MODELS.map((m) => [m.id, m] as const))(
    'P15-R07: %s stays inside its tiles, less the margin, at every height',
    (_, model) => {
      const { structure, lights } = buildTileModel(model);
      const positions = [...structure.positions, ...(lights?.positions ?? [])];
      const [hw, hd] = model.tiles.map((n) => (n * TILE.size) / 2 - BUILDING_MARGIN);
      for (let i = 0; i < positions.length; i += 3) {
        expect(Math.abs(positions[i] ?? 0)).toBeLessThanOrEqual((hw ?? 0) + 1e-6);
        expect(Math.abs(positions[i + 2] ?? 0)).toBeLessThanOrEqual((hd ?? 0) + 1e-6);
        expect(positions[i + 1] ?? 0).toBeGreaterThanOrEqual(-1e-6);
      }
    },
  );

  it('P15-R09: every group of the districts has its models, footprints and a non-square one', () => {
    for (const [id, group] of Object.entries(TILE_GROUPS)) {
      const models = group.models;
      expect(new Set(models.map((m) => m.id)).size, id).toBeGreaterThanOrEqual(5);
      const footprints = new Set(models.map((m) => sorted(m.tiles).join('x')));
      expect(footprints.size, id).toBeGreaterThanOrEqual(3);
      expect(
        models.some((m) => m.tiles[0] !== m.tiles[1]),
        id,
      ).toBe(true);
      const [min, max] = [sorted(group.range[0]), sorted(group.range[1])];
      for (const m of models) {
        const [a, b] = sorted(m.tiles);
        expect(a >= min[0] && b >= min[1] && a <= max[0] && b <= max[1], m.id).toBe(true);
      }
    }
  });

  it('P15-R09: lots from 1 × 1 to 2 × 2: a car park, a yard, a plaza and a park', () => {
    expect(LOT_MODELS.length).toBeGreaterThanOrEqual(4);
    expect(new Set(LOT_MODELS.map((m) => m.archetype))).toEqual(
      new Set(['carPark', 'yard', 'plaza', 'park']),
    );
    for (const m of LOT_MODELS) expect(Math.max(...m.tiles)).toBeLessThanOrEqual(2);
  });

  it('P15-R09: every model is registered, lit for the night levels, in the props colours (P14-R02)', () => {
    const colors = new Set(
      [...Object.values(PROP_COLORS), ...Object.values(PROP_LIGHTS)].map((c) => c.join()),
    );
    for (const m of TILE_MODELS) {
      expect(PROP_MODELS[m.id], m.id).toBeDefined();
      const { structure, lights } = buildTileModel(m);
      expect(lights?.indices.length ?? 0, m.id).toBeGreaterThan(0);
      for (const geo of [structure, lights]) {
        for (let i = 0; i < (geo?.colors.length ?? 0); i += 4) {
          const rgb = (geo?.colors.slice(i, i + 3) ?? []).join();
          expect(colors.has(rgb), `${m.id} ${rgb}`).toBe(true);
        }
      }
    }
  });

  it('Phase 15 (reviewer, 2026-10-28): the city buildings of a group each have their own silhouette', () => {
    const city = new Set(['midrise', 'office', 'tower', 'skyscraper']);
    for (const [id, group] of Object.entries(TILE_GROUPS)) {
      const shapes = group.models
        .filter((m) => city.has(m.archetype))
        .map((m) => (m.seed - 1) % SILHOUETTE_COUNT);
      expect(new Set(shapes).size, id).toBe(shapes.length);
    }
  });
});

import { describe, expect, it } from 'vitest';
import { CAR_IDS } from '../../../../../src/game/config/cars';
import { WORLD_1_PROPS, WORLD_1_PROP_IDS } from '../../../../../src/game/config/world-1/props';
import { WORLD_2_PROPS } from '../../../../../src/game/config/world-2/props';
import { PROP_MODELS } from '../../../../../src/game/view/props/prop-models';
import {
  BUILDING_MARGIN,
  TILE,
  TILE_GROUPS,
  TILE_MODELS,
} from '../../../../../src/game/config/tile-buildings';
import { ROAD_KIT_MODELS } from '../../../../../src/game/view/props/road-kit';
import type { ColoredGeometry } from '../../../../../src/render/geometry/gradient-shapes';

function extent(geo: ColoredGeometry) {
  const xs = geo.positions.filter((_, i) => i % 3 === 0);
  const ys = geo.positions.filter((_, i) => i % 3 === 1);
  const zs = geo.positions.filter((_, i) => i % 3 === 2);
  const radius = Math.max(...xs.map((x, i) => Math.hypot(x, zs[i] ?? 0)));
  return { bottom: Math.min(...ys), top: Math.max(...ys), radius };
}

/** Triangles of a prop model, its structure and its lights. */
const triangles = (id: string) => {
  const model = PROP_MODELS[id]?.();
  return ((model?.structure.indices.length ?? 0) + (model?.lights?.indices.length ?? 0)) / 3;
};
/** Triangles of the heaviest hand-made Level Zero prop, before Level Zero was removed (D-031). */
const heaviest = 336;

/** Ids of the models of a building group made for the grid of tiles (phase 15). */
const tileIds = (group: keyof typeof TILE_GROUPS): string[] =>
  TILE_GROUPS[group].models.map((m) => m.id);

describe('prop models', () => {
  it('Phase 15 (reviewer, 2026-10-28): every model but the road kit spans whole tiles less the margin, centred', () => {
    for (const [id, build] of Object.entries(PROP_MODELS)) {
      if (id in ROAD_KIT_MODELS) continue;
      const { positions } = build().structure;
      for (const axis of [0, 2]) {
        const vs = positions.filter((_, i) => i % 3 === axis);
        const [lo, hi] = [Math.min(...vs), Math.max(...vs)];
        const tiles = (hi - lo + 2 * BUILDING_MARGIN) / TILE.size;
        expect(Math.abs(tiles - Math.round(tiles)), `${id} axis ${String(axis)}`).toBeLessThan(
          1e-6,
        );
        expect(Math.abs(lo + hi), id).toBeLessThan(1e-6);
      }
    }
  });

  it('P04-R04: the model count (only the models a level places, reviewer 2026-10-28)', () => {
    // 8 shared models (trees, antenna, two homes), 9 for World 1 (the wind turbine included),
    // 6 cars; phase 15: the models of the grid of tiles and the road kit.
    expect(Object.keys(PROP_MODELS)).toHaveLength(
      8 + 9 + 6 + TILE_MODELS.length + Object.keys(ROAD_KIT_MODELS).length,
    );
  });

  it('P06-R06: desert homes, outposts, farms and plants, as light as the Level Zero props (D-031)', () => {
    for (const id of Object.values(WORLD_1_PROP_IDS)) {
      expect(PROP_MODELS[id], id).toBeDefined();
      expect(triangles(id), id).toBeLessThanOrEqual(heaviest);
    }
    const expected = {
      'desert-homes': tileIds('desertHomes'),
      outposts: tileIds('outposts'),
      farms: ['farmhouse', 'greenhouse', 'grain-silos', 'wind-turbine'],
    };
    for (const [group, kinds] of Object.entries(expected)) {
      const ids = WORLD_1_PROPS.groups.find((g) => g.id === group)?.kinds.map((k) => k.id);
      expect(ids, group).toEqual(expect.arrayContaining(kinds));
    }
    expect(WORLD_1_PROPS.trees.map((t) => t.id)).toEqual(
      expect.arrayContaining(['dry-bush', 'palm-tree', 'cactus', 'dead-tree', 'broadleaf-tree']),
    );
  });

  // The road kit is flat: see `road-kit.test.ts`.
  it.each(Object.entries(PROP_MODELS).filter(([id]) => !(id in ROAD_KIT_MODELS)))(
    'P04-R04: %s is low-poly and stands on the ground',
    (id, build) => {
      const { structure, lights } = build();
      const { bottom, top } = extent(structure);
      // A leaning trunk may sink a little into the ground, never float above it.
      expect(bottom).toBeLessThanOrEqual(1e-9);
      expect(bottom).toBeGreaterThan(-0.5);
      // Cars are smaller than the buildings and trees.
      const car = (Object.values(CAR_IDS) as string[]).includes(id);
      expect(top, id).toBeGreaterThan(car ? 2 : 3);
      expect(structure.indices.length / 3).toBeLessThan(600);
      expect((lights?.indices.length ?? 0) / 3).toBeLessThan(600);
      expect(structure.colors).toHaveLength((structure.positions.length / 3) * 4);
      if (lights) expect(lights.indices.length).toBeGreaterThan(0);
    },
  );

  it('P04-R04, P06-R06: each building fits in its footprint at its largest scale, so neighbours do not overlap', () => {
    const groups = WORLD_1_PROPS.groups;
    for (const kind of groups.flatMap((g) => g.kinds)) {
      const model = PROP_MODELS[kind.id];
      if (!model) throw new Error(`no model for ${kind.id}`);
      const largest = extent(model().structure).radius * kind.scale[1];
      expect(largest, kind.id).toBeLessThanOrEqual(kind.footprint);
    }
  });
});

describe('World 2 prop models', () => {
  it('P08-R07 (rework, 2026-10-27): desert homes and outposts, mines, oil, refineries and factories', () => {
    const kinds = new Set(WORLD_2_PROPS.groups.flatMap((g) => g.kinds.map((k) => k.id)));
    // Phase 15: the models made for the grid of tiles, by group.
    for (const id of [
      ...tileIds('desertHomes'),
      ...tileIds('outposts'),
      ...tileIds('mines'),
      ...tileIds('oil'),
      ...tileIds('refinery'),
      ...tileIds('industrial'),
      ...tileIds('heavyIndustry'),
    ])
      expect(kinds.has(id), id).toBe(true);
    expect(WORLD_2_PROPS.trees.map((t) => t.id)).toEqual(
      expect.arrayContaining(['cactus', 'dry-bush', 'palm-tree', 'dead-tree']),
    );
    expect(WORLD_2_PROPS.floating).toBeUndefined();
  });

  it('P08-R07: each building fits in its footprint at its largest scale', () => {
    for (const kind of WORLD_2_PROPS.groups.flatMap((g) => g.kinds)) {
      const model = PROP_MODELS[kind.id];
      if (!model) throw new Error(`no model for ${kind.id}`);
      const largest = extent(model().structure).radius * kind.scale[1];
      expect(largest, kind.id).toBeLessThanOrEqual(kind.footprint + 1e-9);
    }
  });
});

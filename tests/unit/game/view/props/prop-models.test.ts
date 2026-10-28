import { describe, expect, it } from 'vitest';
import {
  INDUSTRIAL_VARIANTS,
  JUNGLE_VARIANTS,
  POLAR_VARIANTS,
  variantId,
  type PartFamily,
} from '../../../../../src/game/config/building-families';
import { CAR_IDS } from '../../../../../src/game/config/cars';
import { LEVEL_ZERO } from '../../../../../src/game/sim/scenery-levels';
import { WORLD_1_PROPS, WORLD_1_PROP_IDS } from '../../../../../src/game/config/world-1/props';
import { WORLD_2_PROP_IDS, WORLD_2_PROPS } from '../../../../../src/game/config/world-2/props';
import { WORLD_3_PROP_IDS } from '../../../../../src/game/config/world-3/props';
import { PROP_MODELS } from '../../../../../src/game/view/props/prop-models';
import { TILE_GROUPS, TILE_MODELS } from '../../../../../src/game/config/tile-buildings';
import { ROAD_KIT_MODELS } from '../../../../../src/game/view/props/road-kit';
import type { ColoredGeometry } from '../../../../../src/render/geometry/gradient-shapes';

function extent(geo: ColoredGeometry) {
  const xs = geo.positions.filter((_, i) => i % 3 === 0);
  const ys = geo.positions.filter((_, i) => i % 3 === 1);
  const zs = geo.positions.filter((_, i) => i % 3 === 2);
  const radius = Math.max(...xs.map((x, i) => Math.hypot(x, zs[i] ?? 0)));
  return { bottom: Math.min(...ys), top: Math.max(...ys), radius };
}

const PROP_GROUPS = {
  industrial: [
    'factory',
    'storage-tanks',
    'warehouse',
    'cooling-tower',
    'container-yard',
    'refinery',
  ],
  science: ['radar-dish', 'antenna-mast', 'observatory'],
  homes: ['cube-home', 'dome-home', 'stilt-pod'],
};

/** Triangles of a prop model, its structure and its lights. */
const triangles = (id: string) => {
  const model = PROP_MODELS[id]?.();
  return ((model?.structure.indices.length ?? 0) + (model?.lights?.indices.length ?? 0)) / 3;
};
/** The heaviest hand-made Level Zero prop (the range of the earlier props, D-031). */
const heaviest = Math.max(
  ...[...PROP_GROUPS.industrial, ...PROP_GROUPS.science, ...PROP_GROUPS.homes].map(triangles),
);

const variants = (kind: string) =>
  Array.from({ length: INDUSTRIAL_VARIANTS }, (_, i) => variantId(kind as PartFamily, i + 1));

/** Ids of the models of a building group made for the grid of tiles (phase 15). */
const tileIds = (group: keyof typeof TILE_GROUPS): string[] =>
  TILE_GROUPS[group].models.map((m) => m.id);

describe('prop models', () => {
  it('P04-R04 + review: industrial, technical / scientific, homes, city buildings and trees', () => {
    const ids = (group: string) =>
      LEVEL_ZERO.props.groups.find((g) => g.id === group)?.kinds.map((k) => k.id) ?? [];
    for (const [group, kinds] of Object.entries(PROP_GROUPS)) {
      expect(ids(group)).toEqual(expect.arrayContaining(kinds));
    }
    expect(ids('industrial')).toEqual(expect.arrayContaining(variants('industrial-complex')));
    // P15-R09: the industrial zone and the city centre are filled with models made for the grid.
    expect(ids('heavy-industry')).toEqual(tileIds('heavyIndustry'));
    expect(ids('city')).toEqual(tileIds('city'));
    const trees = LEVEL_ZERO.props.trees.map((t) => t.id);
    expect(trees).toEqual(['dead-tree', 'forked-tree', 'conifer', 'broadleaf-tree', 'bush']);
    // 17 hand-made models, 12 more for World 1 (phase 6, farms added in review), 5 families of 16
    // buildings made of parts, and 6 cars; for World 2 (phase 8), 22 hand-made models and 3
    // families of 8; for World 3 (phase 9), 29 hand-made models and 2 families of 8; for World 4
    // (phase 10), 31 hand-made volcanic models, removed (reviewer, 2026-10-28). Phase 15: the
    // models of the grid of tiles and the road kit replace 4 World 1 models, 4 families of parts,
    // the pumpjack, the World 3 homes and the World 4 skyscrapers.
    expect(Object.keys(PROP_MODELS)).toHaveLength(
      17 +
        8 +
        16 +
        6 +
        22 +
        24 +
        29 +
        16 +
        TILE_MODELS.length +
        Object.keys(ROAD_KIT_MODELS).length,
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

  it('P04 review: buildings with a square plan fit in it', () => {
    for (const kind of LEVEL_ZERO.props.groups.flatMap((g) => g.kinds)) {
      if (kind.frontage === undefined) continue;
      const positions = PROP_MODELS[kind.id]?.().structure.positions ?? [];
      const across = positions.filter((_, i) => i % 3 !== 1).map(Math.abs);
      expect(Math.max(...across), kind.id).toBeLessThanOrEqual(kind.frontage + 1);
    }
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
    const groups = [...LEVEL_ZERO.props.groups, ...WORLD_1_PROPS.groups];
    for (const kind of groups.flatMap((g) => g.kinds)) {
      const model = PROP_MODELS[kind.id];
      if (!model) throw new Error(`no model for ${kind.id}`);
      const largest = extent(model().structure).radius * kind.scale[1];
      expect(largest, kind.id).toBeLessThanOrEqual(kind.footprint);
    }
  });

  it('P04 review: buildings made of parts differ from one variant to the next', () => {
    for (const kind of ['industrial-complex']) {
      const shapes = new Set(
        variants(kind).map((id) =>
          JSON.stringify(PROP_MODELS[id]?.().structure.positions.slice(0, 30)),
        ),
      );
      expect(shapes.size, kind).toBe(variants(kind).length);
    }
  });
});

describe('World 2 prop models', () => {
  const polar = (family: PartFamily) =>
    Array.from({ length: POLAR_VARIANTS }, (_, i) => variantId(family, i + 1));

  it('P08-R07: every new prop is as light as the hand-made props of the earlier levels (D-031)', () => {
    for (const id of Object.values(WORLD_2_PROP_IDS)) {
      expect(PROP_MODELS[id], id).toBeDefined();
      expect(triangles(id), id).toBeLessThanOrEqual(heaviest);
    }
  });

  it('P08-R07 (rework, 2026-10-27): desert homes and outposts, mines, oil pumpjacks, refineries and factories; no frozen prop', () => {
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
    const frozen = new Set<string>(Object.values(WORLD_2_PROP_IDS));
    for (const id of [...kinds, ...WORLD_2_PROPS.trees.map((t) => t.id)])
      expect(frozen.has(id), id).toBe(false);
    expect(WORLD_2_PROPS.floating).toBeUndefined();
  });

  it('P08-R07: each building fits in its footprint at its largest scale', () => {
    // Buildings only: the plants are World 1's, whose footprints space their trunks (P06-R06).
    for (const kind of WORLD_2_PROPS.groups.flatMap((g) => g.kinds)) {
      const model = PROP_MODELS[kind.id];
      if (!model) throw new Error(`no model for ${kind.id}`);
      const largest = extent(model().structure).radius * kind.scale[1];
      expect(largest, kind.id).toBeLessThanOrEqual(kind.footprint + 1e-9);
    }
  });

  it('P08-R07: the polar buildings made of parts differ from one variant to the next', () => {
    for (const family of ['polar-tower', 'polar-block', 'mining-complex'] as const) {
      const shapes = new Set(
        polar(family).map((id) =>
          JSON.stringify(PROP_MODELS[id]?.().structure.positions.slice(0, 30)),
        ),
      );
      expect(shapes.size, family).toBe(POLAR_VARIANTS);
    }
  });

  it('P08-R03: the pipeline is one piece every 15 units along its line', () => {
    const { positions } = PROP_MODELS.pipeline?.().structure ?? { positions: [] };
    const xs = positions.filter((_, i) => i % 3 === 0);
    expect(Math.min(...xs)).toBeCloseTo(-15 / 2, 1);
    expect(Math.max(...xs)).toBeCloseTo(15 / 2, 1);
  });
});

describe('World 3 props (P09-R06)', () => {
  const jungle = (family: PartFamily) =>
    Array.from({ length: JUNGLE_VARIANTS }, (_, i) => variantId(family, i + 1));
  const CANOPY = [WORLD_3_PROP_IDS.canopyCluster, WORLD_3_PROP_IDS.canopyCrown];

  it('P09-R06: each new prop stays under the triangle budget; the canopy crowns lighter still', () => {
    for (const id of Object.values(WORLD_3_PROP_IDS)) {
      expect(PROP_MODELS[id], id).toBeDefined();
      // The dam spans the whole lake: one set piece, within the props' 600-triangle cap.
      const budget = id === WORLD_3_PROP_IDS.dam ? 600 : heaviest;
      expect(triangles(id), id).toBeLessThanOrEqual(budget);
    }
    for (const id of CANOPY) expect(triangles(id), id).toBeLessThanOrEqual(heaviest / 2.5);
    for (const id of [...jungle('canopy-tower'), ...jungle('canopy-block')])
      expect(triangles(id), id).toBeLessThan(600);
  });

  it('P09-R06: the canopy city buildings made of parts differ from one variant to the next', () => {
    for (const family of ['canopy-tower', 'canopy-block'] as const) {
      const shapes = new Set(
        jungle(family).map((id) =>
          JSON.stringify(PROP_MODELS[id]?.().structure.positions.slice(0, 30)),
        ),
      );
      expect(shapes.size, family).toBe(JUNGLE_VARIANTS);
    }
  });

  it('P09-R06: the causeway and the swamp pipeline are 15 long, as their lines lay them', () => {
    for (const id of [WORLD_3_PROP_IDS.causeway, WORLD_3_PROP_IDS.swampPipeline]) {
      const xs = (PROP_MODELS[id]?.().structure.positions ?? []).filter((_, i) => i % 3 === 0);
      expect(Math.min(...xs), id).toBeCloseTo(-7.5, 1);
      expect(Math.max(...xs), id).toBeCloseTo(7.5, 1);
    }
  });
});

import { describe, expect, it } from 'vitest';
import {
  CITY_VARIANTS,
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
import * as W4 from '../../../../../src/game/config/world-4/props';
import { PLUME_KINDS } from '../../../../../src/config/plumes';
import { PROP_MODELS } from '../../../../../src/game/view/props/prop-models';
import type { ColoredGeometry } from '../../../../../src/render/geometry/gradient-shapes';
import type { PropRules } from '../../../../../src/core/scenery/scenery-level';

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

/** The kinds of `rules` that need room: its buildings, plants and floating props. */
const placedKinds = ({ groups, trees, floating }: PropRules) => [
  ...groups.flatMap((g) => g.kinds),
  ...trees,
  ...(floating?.kinds ?? []),
];
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
  Array.from({ length: kind.startsWith('city') ? CITY_VARIANTS : INDUSTRIAL_VARIANTS }, (_, i) =>
    variantId(kind as PartFamily, i + 1),
  );

describe('prop models', () => {
  it('P04-R04 + review: industrial, technical / scientific, homes, city buildings and trees', () => {
    const ids = (group: string) =>
      LEVEL_ZERO.props.groups.find((g) => g.id === group)?.kinds.map((k) => k.id) ?? [];
    for (const [group, kinds] of Object.entries(PROP_GROUPS)) {
      expect(ids(group)).toEqual(expect.arrayContaining(kinds));
    }
    expect(ids('industrial')).toEqual(expect.arrayContaining(variants('industrial-complex')));
    // Review: the industrial zone and the city centre are filled by large buildings made of parts.
    expect(ids('heavy-industry')).toEqual(
      expect.arrayContaining([
        ...variants('industrial-plant'),
        ...variants('industrial-works'),
        ...variants('industrial-complex'),
      ]),
    );
    expect(ids('city')).toEqual(
      expect.arrayContaining([...variants('city-block'), ...variants('city-tower')]),
    );
    const trees = LEVEL_ZERO.props.trees.map((t) => t.id);
    expect(trees).toEqual(['dead-tree', 'forked-tree', 'conifer', 'broadleaf-tree', 'bush']);
    // 17 hand-made models, 12 more for World 1 (phase 6, farms added in review), 5 families of 16
    // buildings made of parts, and 6 cars; for World 2 (phase 8), 22 hand-made models and 3
    // families of 8; for World 3 (phase 9), 29 hand-made models and 2 families of 8; for World 4
    // (phase 10), 31 hand-made models; the World 2 pumpjack and the 3 World 3 homes (reviewer's
    // reworks, 2026-10-27).
    expect(Object.keys(PROP_MODELS)).toHaveLength(
      17 + 12 + 80 + 6 + 22 + 24 + 29 + 16 + 31 + 1 + 3,
    );
  });

  it('P06-R06: desert homes, outposts, farms and plants, as light as the Level Zero props (D-031)', () => {
    for (const id of Object.values(WORLD_1_PROP_IDS)) {
      expect(PROP_MODELS[id], id).toBeDefined();
      expect(triangles(id), id).toBeLessThanOrEqual(heaviest);
    }
    const expected = {
      'desert-homes': ['desert-home', 'windcatcher-home'],
      outposts: ['water-tower', 'solar-farm', 'antenna-mast'],
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

  it.each(Object.entries(PROP_MODELS))(
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
    for (const kind of [
      'industrial-complex',
      'industrial-works',
      'industrial-plant',
      'city-tower',
      'city-block',
    ]) {
      const shapes = new Set(
        variants(kind).map((id) =>
          JSON.stringify(PROP_MODELS[id]?.().structure.positions.slice(0, 30)),
        ),
      );
      expect(shapes.size, kind).toBe(variants(kind).length);
    }
  });

  it('P04 review: big city buildings are made of lots of different heights, not one square', () => {
    for (const id of variants('city-block')) {
      const ys = PROP_MODELS[id]?.().structure.positions.filter((_, i) => i % 3 === 1) ?? [];
      // Several roofs: tall towers next to lower slabs or wings.
      expect(new Set(ys.map((y) => Math.round(y))).size, id).toBeGreaterThan(3);
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
    for (const id of [
      'desert-home',
      'solar-farm',
      'mine-headframe',
      'oil-pumpjack',
      'refinery',
      'storage-tanks',
      'factory',
      'cooling-tower',
      variantId('industrial-plant', 1),
      variantId('industrial-works', 1),
    ])
      expect(kinds.has(id), id).toBe(true);
    expect(WORLD_2_PROPS.trees.map((t) => t.id)).toEqual(
      expect.arrayContaining(['cactus', 'dry-bush', 'palm-tree', 'dead-tree']),
    );
    const frozen = new Set<string>(
      Object.values(WORLD_2_PROP_IDS).filter((id) => id !== WORLD_2_PROP_IDS.pumpjack),
    );
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

describe('World 4 props (P10-R08)', () => {
  const W = W4.WORLD_4_PROP_IDS;
  const { groups, trees, floating } = W4.WORLD_4_PROPS;
  const ids = (rules: readonly { readonly id: string }[]) => rules.map((r) => r.id);
  const xs = (id: string) =>
    (PROP_MODELS[id]?.().structure.positions ?? []).filter((_, i) => i % 3 === 0);
  const FAR = { structure: { positions: [Infinity], indices: [], colors: [] }, lights: undefined };
  /** How far a model reaches from its centre, its lights (furnace mouths, neon) included. */
  const reach = (id: string) => {
    const { structure, lights = structure } = PROP_MODELS[id]?.() ?? FAR;
    return Math.max(extent(structure).radius, extent(lights).radius);
  };

  it('P10-R08: each new prop stays under the triangle budget; each group and scatter has rules', () => {
    for (const id of Object.values(W)) expect(triangles(id), id).toBeLessThanOrEqual(heaviest);
    expect(ids(groups)).toEqual(expect.arrayContaining(Object.values(W4.WORLD_4_GROUPS)));
    expect(ids(trees)).toEqual(expect.arrayContaining(Object.values(W4.VOLCANIC_SCATTER).flat()));
    expect(ids(floating?.kinds ?? [])).toContain(W.seaSteam);
  });

  it('P10-R08: each building, plant and floating prop fits in its footprint at its largest scale', () => {
    for (const kind of placedKinds(W4.WORLD_4_PROPS)) {
      expect(reach(kind.id) * kind.scale[1], kind.id).toBeLessThanOrEqual(kind.footprint);
    }
  });

  it('P10-R08: vents, wells, chimneys, furnaces and cooling towers send up smoke or steam', () => {
    const vents = [W.smokingVent, W.sulphurVent, W.seaSteam, W.hotSpring, W.geothermalWell];
    for (const id of [...vents, W.coolingTower, W.powerPlant, W.smelter, W.blastFurnace]) {
      const model = PROP_MODELS[id]?.();
      expect(model?.plumes?.length, id).toBeGreaterThan(0);
      for (const { kind, at } of model?.plumes ?? []) {
        expect(PLUME_KINDS[kind], id).toBeDefined();
        expect(Math.hypot(at[0], at[2]), id).toBeLessThanOrEqual(reach(id));
      }
    }
    expect(PROP_MODELS[W.chimneyRow]?.().plumes?.length).toBeGreaterThanOrEqual(3);
  });

  it('P10-R08: pipeline and track pieces are laid end to end; ore wagons ride on the track', () => {
    for (const id of [W.pipeline, W.railLine]) {
      expect(Math.min(...xs(id)), id).toBeCloseTo(-W4.LINE_PIECE_LENGTH / 2, 1);
      expect(Math.max(...xs(id)), id).toBeCloseTo(W4.LINE_PIECE_LENGTH / 2, 1);
    }
    const [rail, wagons] = W4.railWithWagons({ x: 0, amplitude: 40, wavelength: 3000 });
    expect([rail?.kind, wagons?.kind, wagons?.path]).toEqual([W.railLine, W.oreWagon, rail?.path]);
    expect(wagons?.drift).toMatchObject({ x: 0, z: expect.any(Number) as number });
    // Each wagon stands centred on a track piece, and wagons never touch one another.
    expect((W4.ORE_WAGON_SPACING / 2 - W4.LINE_PIECE_LENGTH / 2) % W4.LINE_PIECE_LENGTH).toBe(0);
    expect(2 * Math.max(...xs(W.oreWagon).map(Math.abs))).toBeLessThan(W4.ORE_WAGON_SPACING);
  });
});

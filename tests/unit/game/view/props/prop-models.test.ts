import { describe, expect, it } from 'vitest';
import {
  CITY_VARIANTS,
  INDUSTRIAL_VARIANTS,
  variantId,
  type PartFamily,
} from '../../../../../src/game/config/building-families';
import { CAR_IDS } from '../../../../../src/game/config/cars';
import { LEVEL_ZERO } from '../../../../../src/game/sim/scenery-levels';
import { WORLD_1_PROPS, WORLD_1_PROP_IDS } from '../../../../../src/game/config/world-1/props';
import { PROP_MODELS } from '../../../../../src/game/view/props/prop-models';
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
    expect(LEVEL_ZERO.props.trees.map((t) => t.id)).toEqual([
      'dead-tree',
      'forked-tree',
      'conifer',
      'broadleaf-tree',
      'bush',
    ]);
    // 17 hand-made models, 9 more for World 1 (phase 6), 5 families of 16 buildings made of
    // parts, and 6 cars.
    expect(Object.keys(PROP_MODELS)).toHaveLength(17 + 9 + 5 * 16 + 6);
  });

  it('P06-R06: desert homes, outposts and plants, as light as the Level Zero props (D-031)', () => {
    const triangles = (id: string) => {
      const model = PROP_MODELS[id]?.();
      return ((model?.structure.indices.length ?? 0) + (model?.lights?.indices.length ?? 0)) / 3;
    };
    const handMade = PROP_GROUPS.industrial.concat(PROP_GROUPS.science, PROP_GROUPS.homes);
    const heaviest = Math.max(...handMade.map(triangles));
    for (const id of Object.values(WORLD_1_PROP_IDS)) {
      expect(PROP_MODELS[id], id).toBeDefined();
      expect(triangles(id), id).toBeLessThanOrEqual(heaviest);
    }
    const desert = WORLD_1_PROPS.groups
      .find((g) => g.id === 'desert-homes')
      ?.kinds.map((k) => k.id);
    expect(desert).toEqual(expect.arrayContaining(['desert-home', 'windcatcher-home']));
    const outposts = WORLD_1_PROPS.groups.find((g) => g.id === 'outposts')?.kinds.map((k) => k.id);
    expect(outposts).toEqual(expect.arrayContaining(['water-tower', 'solar-farm', 'antenna-mast']));
    expect(WORLD_1_PROPS.trees.map((t) => t.id)).toEqual(
      expect.arrayContaining(['dry-bush', 'palm-tree', 'cactus', 'dead-tree']),
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

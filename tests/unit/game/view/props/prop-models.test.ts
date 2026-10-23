import { describe, expect, it } from 'vitest';
import { LEVEL_ZERO } from '../../../../../src/game/sim/scenery-levels';
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
  industrial: ['factory', 'storage-tanks', 'warehouse', 'cooling-tower'],
  science: ['radar-dish', 'antenna-mast', 'observatory'],
  homes: ['cube-home', 'dome-home', 'stilt-pod'],
};

describe('prop models', () => {
  it('P04-R04: industrial buildings, technical / scientific installations, homes and dead trees', () => {
    for (const [group, kinds] of Object.entries(PROP_GROUPS)) {
      const rule = LEVEL_ZERO.props.groups.find((g) => g.id === group);
      expect(rule?.kinds.map((k) => k.id)).toEqual(kinds);
    }
    expect(LEVEL_ZERO.props.trees.map((t) => t.id)).toEqual(['dead-tree', 'forked-tree']);
    expect(Object.keys(PROP_MODELS)).toHaveLength(12);
  });

  it.each(Object.entries(PROP_MODELS))(
    'P04-R04: %s is low-poly and stands on the ground',
    (_, build) => {
      const { structure, lights } = build();
      const { bottom, top } = extent(structure);
      // A leaning trunk may sink a little into the ground, never float above it.
      expect(bottom).toBeLessThanOrEqual(1e-9);
      expect(bottom).toBeGreaterThan(-0.5);
      expect(top).toBeGreaterThan(5);
      expect(structure.indices.length / 3).toBeLessThan(600);
      expect(structure.colors).toHaveLength((structure.positions.length / 3) * 4);
      if (lights) expect(lights.indices.length).toBeGreaterThan(0);
    },
  );

  it('P04-R04: each building fits in its footprint at its largest scale, so neighbours do not overlap', () => {
    for (const kind of LEVEL_ZERO.props.groups.flatMap((g) => g.kinds)) {
      const model = PROP_MODELS[kind.id];
      if (!model) throw new Error(`no model for ${kind.id}`);
      const largest = extent(model().structure).radius * kind.scale[1];
      expect(largest, kind.id).toBeLessThanOrEqual(kind.footprint);
    }
  });
});

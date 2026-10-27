import { describe, expect, it } from 'vitest';
import { WORLD_3_PROP_IDS, WORLD_3_PROPS } from '../../../../../src/game/config/world-3/props';
import { PROP_MODELS } from '../../../../../src/game/view/props/prop-models';
import type { ColoredGeometry } from '../../../../../src/render/geometry/gradient-shapes';

/** How far a model reaches from its centre, and its top. */
function extent(geo: ColoredGeometry) {
  const xs = geo.positions.filter((_, i) => i % 3 === 0);
  const ys = geo.positions.filter((_, i) => i % 3 === 1);
  const zs = geo.positions.filter((_, i) => i % 3 === 2);
  const radius = Math.max(...xs.map((x, i) => Math.hypot(x, zs[i] ?? 0)));
  return { top: Math.max(...ys), radius };
}

/** Triangles of a prop model, its structure and its lights. */
const triangles = (id: string) => {
  const model = PROP_MODELS[id]?.();
  return ((model?.structure.indices.length ?? 0) + (model?.lights?.indices.length ?? 0)) / 3;
};

// The World 3 props since the reviewer's rework (2026-10-27); the jungle props are tested in
// `prop-models.test.ts`.
const EMPTY: ColoredGeometry = { positions: [0, 0, 0], indices: [], colors: [] };
describe('World 3 homes (P09-R06, rework)', () => {
  const W = WORLD_3_PROP_IDS;
  const HOMES = [W.suburbHouse, W.rowHouses, W.walkUp];

  it('P09-R06: each home is as light as the hand-made Level Zero props (D-031)', () => {
    const LEVEL_ZERO = ['factory', 'storage-tanks', 'warehouse', 'cooling-tower', 'container-yard'];
    const heaviest = Math.max(
      ...[...LEVEL_ZERO, 'refinery', 'radar-dish', 'antenna-mast', 'observatory'].map(triangles),
      ...['cube-home', 'dome-home', 'stilt-pod'].map(triangles),
    );
    for (const id of HOMES) expect(triangles(id), id).toBeLessThanOrEqual(heaviest);
  });

  it('P09-R06 (rework, 2026-10-27): factories, docks and workshops, then flats, terraces, houses and farms; no tower, no jungle prop', () => {
    const groups = new Map(WORLD_3_PROPS.groups.map((g) => [g.id, g.kinds.map((k) => k.id)]));
    const kinds = new Set([...groups.values()].flat());
    for (const id of [W.suburbHouse, W.rowHouses, W.walkUp, 'factory', 'farmhouse'])
      expect(kinds.has(id), id).toBe(true);
    const homes = new Set<string>([W.suburbHouse, W.rowHouses, W.walkUp]);
    const jungleProps = new Set<string>(Object.values(W).filter((id) => !homes.has(id)));
    const towers = /(city|canopy|polar)-(tower|block)/;
    for (const id of [...kinds, ...WORLD_3_PROPS.trees.map((t) => t.id)]) {
      expect(jungleProps.has(id), id).toBe(false);
      expect(towers.test(id), id).toBe(false);
    }
    expect(WORLD_3_PROPS.floating).toBeUndefined();
    // The homes of the suburbs and villages are small: lower than a factory.
    const height = (id: string) => extent(PROP_MODELS[id]?.().structure ?? EMPTY).top;
    for (const id of groups.get('w3-villages') ?? [])
      expect(height(id), id).toBeLessThanOrEqual(height('factory'));
  });

  it('P09-R06: each building fits in its footprint at its largest scale', () => {
    // Buildings only: the plants are Level Zero's, whose footprints space their trunks (P04-R04).
    for (const kind of WORLD_3_PROPS.groups.flatMap((g) => g.kinds)) {
      const model = PROP_MODELS[kind.id];
      if (!model) throw new Error(`no model for ${kind.id}`);
      const largest = extent(model().structure).radius * kind.scale[1];
      expect(largest, kind.id).toBeLessThanOrEqual(kind.footprint + 1e-9);
    }
  });
});

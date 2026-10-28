import { describe, expect, it } from 'vitest';
import { HeightField } from '../../../../src/core/scenery/height-field';
import { PropPlacer } from '../../../../src/core/scenery/prop-placement';
import { levelRoads, type Road } from '../../../../src/core/scenery/road-network';
import { runoutStart, withRunout } from '../../../../src/core/scenery/scenery-level';
import { GAME } from '../../../../src/game/index';
import { SAMPLE_SCENERY_LEVEL } from '../../../fixtures/sample-scenery';

// Reviewer, 2026-10-28: the roads and buildings of a level's runout are generated after the rest.

describe('the runout (reviewer, 2026-10-28)', () => {
  const scenery = GAME.gameLevels.find((l) => l.id === '4-4')?.scenery;
  if (!scenery) throw new Error('no level 4-4');
  const level = withRunout(scenery, 60);
  const from = runoutStart(level) ?? 0;
  // Phase 15: on a grid of tiles, the row where the runout starts is the one on the tile there.
  const tile = level.roads.tiles?.size;
  const row = tile ? (Math.round(from / tile - 0.5) + 0.5) * tile : from;
  const field = new HeightField(level);
  const streetsAt = (roads: readonly Road[], z: number) =>
    roads.filter((r) => r.points.every((p) => Math.abs(p.z - z) < 1e-6));

  it('starts where the level ends, at its length without the runout', () => {
    expect(from).toBeCloseTo(field.length - 60 * level.scrollSpeed);
    expect(runoutStart(scenery)).toBeUndefined();
  });

  it('its streets are laid apart, going on from a full row where it starts', () => {
    const network = levelRoads(field, level.roads, level.seed, { runoutFrom: from });
    const before = network.roads;
    expect(before.every((r) => r.points.every((p) => p.z <= row + 1e-6))).toBe(true);
    expect(streetsAt(before, row).length).toBeGreaterThan(0);
    const added = network.addRunout();
    expect(added.length).toBeGreaterThan(50);
    expect(network.roads).toEqual([...before, ...added]);
    // The list of roads is a new one: the one before stays as it was.
    expect(network.roads).not.toBe(before);
    for (const road of added) {
      expect(road.points.every((p) => p.z >= row - 1e-6)).toBe(true);
      // A column starting at the row ends on it (or off the screen), never in the open.
      const start = road.points.find((p) => Math.abs(p.z - row) < 1e-6);
      if (start && Math.abs(start.x) < level.roads.offscreenX) {
        const onRow = streetsAt(before, row).some((r) => {
          const xs = r.points.map((p) => p.x);
          return start.x >= Math.min(...xs) && start.x <= Math.max(...xs);
        });
        expect(onRow).toBe(true);
      }
    }
    expect(network.addRunout()).toEqual([]);
  });

  it('without a runout, every street is laid at once', () => {
    const network = levelRoads(field, level.roads, level.seed);
    expect(network.roads.some((r) => r.points.some((p) => p.z > row + 1))).toBe(true);
    expect(network.addRunout()).toEqual([]);
  });

  it('only the roads are kept for the main thread (not the slots and blocks)', () => {
    const network = levelRoads(field, level.roads, level.seed, { runoutFrom: from });
    expect(Object.keys(network.snapshot())).toEqual(['roads']);
    const made = levelRoads(field, level.roads, level.seed, { made: network.snapshot() });
    expect(made.roads).toEqual(network.roads);
    expect(made.slots).toEqual([]);
  });

  it("reviewer, 2026-10-28: the runout's buildings are placed after the others, once", () => {
    const level = withRunout(SAMPLE_SCENERY_LEVEL, 30);
    const from = runoutStart(level) ?? 0;
    const field = new HeightField(level);
    const roads = levelRoads(field, level.roads, level.seed, { runoutFrom: from });
    const p = new PropPlacer(field, level.props, level.seed, roads);
    const all = { xMin: -500, xMax: 500, zMin: -1000, zMax: field.length + 4000 };
    const before = p.snapshot().buildings;
    // Away from where it starts, nothing stands in the runout yet.
    expect(before.every((b) => b.placement.z < from + 50)).toBe(true);
    roads.addRunout();
    const added = p.placeRunout();
    expect(added.length).toBeGreaterThan(0);
    expect(added.every((b) => b.placement.z > from - 50)).toBe(true);
    expect(p.placeRunout()).toEqual([]);
    expect(p.place(all).length).toBeGreaterThan(0);
    // Without a runout, there is nothing to add.
    const without = levelRoads(field, level.roads, level.seed);
    expect(new PropPlacer(field, level.props, level.seed, without).placeRunout()).toEqual([]);
  });
});

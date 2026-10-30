import { describe, expect, it } from 'vitest';
import { HeightField } from '../../../../src/core/scenery/height-field';
import { PropPlacer } from '../../../../src/core/scenery/prop-placement';
import { RoadNetwork, type Road } from '../../../../src/core/scenery/road-network';
import {
  roadPieces,
  roadTiles,
  tileKey,
  type RoadPiece,
} from '../../../../src/core/scenery/road-tiles';
import type { PropKindRule, SceneryLevel } from '../../../../src/core/scenery/scenery-level';
import { packBlock, type PackSite } from '../../../../src/core/scenery/tile-packing';
import { Traffic } from '../../../../src/core/scenery/traffic';
import { SAMPLE_SCENERY_LEVEL } from '../../../fixtures/sample-scenery';

// Phase 15: the districts on a grid of tiles, with the sample game (ENG-145).

const TILE = { size: 10, sidewalk: 2 };
const kind = (id: string, w: number, d: number): PropKindRule => ({
  id,
  weight: 1,
  footprint: (Math.hypot(w, d) * TILE.size) / 2,
  scale: [1, 1],
  tiles: [w, d],
});

/** The sample level, flat, as one district on tiles, with buildings of whole tiles. */
const LEVEL: SceneryLevel = {
  ...SAMPLE_SCENERY_LEVEL,
  sections: SAMPLE_SCENERY_LEVEL.sections.map((s) => ({
    ...s,
    relief: { ...s.relief, base: 10, amplitude: 0.5 },
    streets: { rows: [40, 70], columns: [40, 70], links: 0.6 },
  })),
  roads: {
    ...SAMPLE_SCENERY_LEVEL.roads,
    offscreenX: 200,
    dual: { width: 12, mainRoads: 0, avenues: 0.3 },
    boulevards: [{ lanes: 3, width: 30, share: 0.15 }],
    tiles: TILE,
  },
  props: {
    ...SAMPLE_SCENERY_LEVEL.props,
    groups: [
      {
        id: 'blocks',
        weight: 1,
        kinds: [kind('a', 1, 1), kind('b', 1, 2), kind('c', 2, 3), kind('d', 2, 2)],
      },
    ],
    lots: [kind('lot', 1, 1)],
  },
};
const RANGE = { zMin: -200, zMax: 600 };

function ground(seed = 3) {
  const field = new HeightField(LEVEL);
  const roads = new RoadNetwork(field, LEVEL.roads, seed, RANGE);
  const placer = new PropPlacer(field, LEVEL.props, seed, roads);
  return { field, roads, placer, pieces: roadPieces(roads.roads, TILE) };
}

const onScreen = (x: number): boolean => Math.abs((x + 0.5) * TILE.size) < LEVEL.roads.offscreenX;
const STEPS = [
  [0, 1],
  [1, 0],
  [0, -1],
  [-1, 0],
] as const;

/** The tiles just past each open side of `p`, with the side's number. */
function beyond(p: RoadPiece): [number, number, number][] {
  return p.sides.flatMap((s, i) => {
    if (!s) return [];
    const [dx, dz] = STEPS[i] ?? [0, 0];
    return Array.from({ length: s.size }, (_, k): [number, number, number] =>
      dz !== 0
        ? [p.x + s.offset + k, dz > 0 ? p.z + p.size : p.z - 1, i]
        : [dx > 0 ? p.x + p.size : p.x - 1, p.z + s.offset + k, i],
    );
  });
}

describe('streets on tiles (phase 15)', () => {
  const { roads, placer, pieces } = ground();
  const streets = roads.roads.filter((r) => r.kind === 'street');

  it('P15-R01: every street covers whole tiles, and no tile is covered twice', () => {
    expect(streets.length).toBeGreaterThan(5);
    for (const s of streets) {
      const [a, b] = [s.points[0], s.points.at(-1)];
      if (!a || !b) continue;
      const across = a.z === b.z ? a.z : a.x;
      const n = s.width / TILE.size;
      expect(Number.isInteger(n), String(s.width)).toBe(true);
      // Its edges are on tile edges.
      expect((across - s.width / 2) / TILE.size).toBeCloseTo(
        Math.round((across - s.width / 2) / TILE.size),
      );
    }
    const seen = new Set<number>();
    for (const p of pieces) {
      for (let i = 0; i < p.size; i++) {
        for (let j = 0; j < p.size; j++) {
          const k = tileKey(p.x + i, p.z + j);
          expect(seen.has(k)).toBe(false);
          seen.add(k);
        }
      }
    }
  });

  it('P15-R01: the same seed gives the same streets and buildings', () => {
    const again = ground();
    expect(again.roads.roads).toEqual(roads.roads);
    expect(again.placer.snapshot()).toEqual(placer.snapshot());
  });

  it('P15-R02: a street is N tiles wide for N lanes each way', () => {
    for (const s of streets) expect(s.lanes * TILE.size).toBe(s.width);
    expect(streets.some((s) => s.lanes === 3)).toBe(true);
  });

  it('P15-R05: every open side on screen meets another piece; X and T junctions both occur', () => {
    const tiles = roadTiles(pieces);
    for (const p of pieces) {
      for (const [x, z] of beyond(p)) {
        const inside = z * TILE.size > RANGE.zMin + 20 && (z + 1) * TILE.size < RANGE.zMax - 20;
        if (onScreen(x) && inside) expect(tiles.has(tileKey(x, z)), JSON.stringify(p)).toBe(true);
      }
    }
    expect(pieces.some((p) => p.kind === 'cross')).toBe(true);
    expect(pieces.some((p) => p.kind === 'tee')).toBe(true);
  });

  it('P15-R04: a narrower road never goes on with a wider one ending on it, and turns are of one size', () => {
    for (const p of pieces.filter((q) => q.adapter && Math.abs((q.x + q.size / 2) * 10) < 180)) {
      expect(p.kind).not.toBe('turn');
      const sizes = p.sides.flatMap((s) => (s ? [s.size] : []));
      // The wide road (the piece's size) goes on through it.
      expect(sizes.filter((s) => s === p.size)).toHaveLength(2);
    }
  });

  it('P15-R07, R08: buildings stand on whole tiles off the roads, at quarter turns, facing a street they touch', () => {
    const tiles = roadTiles(pieces);
    const buildings = placer.snapshot().buildings;
    expect(buildings.length).toBeGreaterThan(20);
    const taken = new Set<number>();
    for (const b of buildings) {
      const w = (2 * b.halfX) / TILE.size;
      const d = (2 * b.halfZ) / TILE.size;
      const x0 = b.placement.x / TILE.size - w / 2;
      const z0 = b.placement.z / TILE.size - d / 2;
      expect(x0).toBeCloseTo(Math.round(x0));
      expect(z0).toBeCloseTo(Math.round(z0));
      expect(b.placement.scale).toBe(1);
      const quarter = b.placement.rotation / (Math.PI / 2);
      expect(quarter).toBeCloseTo(Math.round(quarter));
      for (let i = 0; i < w; i++) {
        for (let j = 0; j < d; j++) {
          const k = tileKey(Math.round(x0) + i, Math.round(z0) + j);
          expect(tiles.has(k)).toBe(false);
          expect(taken.has(k)).toBe(false);
          taken.add(k);
        }
      }
    }
  });
});

describe('packing a block (phase 15)', () => {
  const site = (road: (x: number, z: number) => boolean): PackSite => ({
    free: (x, z) => !road(x, z),
    road,
    kindsAt: () => [kind('big', 2, 3), kind('small', 1, 1)],
    random: (k) => ((k * 7919) % 101) / 101,
  });

  it('P15-R08: covers about the density asked for, never past the block, facing the street', () => {
    // A 6 × 6 block with a street along its low Z side (row -1).
    const block = { x0: 0, x1: 6, z0: 0, z1: 6 };
    for (const density of [1, 0.5]) {
      const spots: { x: number; z: number; w: number; d: number; rotation: number }[] = [];
      const taken = new Set<number>();
      const s = site((_, z) => z === -1);
      packBlock({ ...s, free: (x, z) => !taken.has(tileKey(x, z)) }, block, density, (spot) => {
        spots.push(spot);
        for (let i = 0; i < spot.w; i++)
          for (let j = 0; j < spot.d; j++) taken.add(tileKey(spot.x + i, spot.z + j));
      });
      expect(Math.abs(taken.size / 36 - density)).toBeLessThanOrEqual(0.1);
      for (const spot of spots) {
        expect(spot.x >= 0 && spot.z >= 0 && spot.x + spot.w <= 6 && spot.z + spot.d <= 6).toBe(
          true,
        );
        // Those on the street face it (-Z: no turn).
        if (spot.z === 0) expect(spot.rotation).toBe(0);
      }
    }
  });
});

describe('cars on streets with sidewalks (phase 15)', () => {
  it('P15-R11: car lanes keep inside the roadway, off the sidewalks', () => {
    const road: Road = {
      index: 0,
      kind: 'street',
      width: 20,
      lanes: 2,
      // One chance of a car per point: a point every 10.
      points: Array.from({ length: 41 }, (_, i) => ({ x: 5, z: i * 10, width: 20 })),
    };
    const rules = {
      kinds: ['car'],
      density: 1,
      lift: 0,
      scale: 1,
      length: 4,
      speed: [10, 10] as const,
    };
    const traffic = new Traffic([road], () => 0, { ...rules, sidewalk: TILE.sidewalk }, 1);
    const cars = traffic.at(1, { xMin: -100, xMax: 100, zMin: 0, zMax: 400 });
    expect(cars.length).toBeGreaterThan(5);
    for (const car of cars) expect(Math.abs(car.x - 5)).toBeLessThanOrEqual(10 - TILE.sidewalk);
    expect(cars.some((c) => Math.abs(c.x - 5) > 4)).toBe(true);
  });
});

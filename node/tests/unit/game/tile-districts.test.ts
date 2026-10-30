import { describe, expect, it } from 'vitest';
import { HeightField } from '../../../src/core/scenery/height-field';
import { PropPlacer } from '../../../src/core/scenery/prop-placement';
import { levelRoads } from '../../../src/core/scenery/road-network';
import {
  roadPieces,
  roadTiles,
  tileKey,
  type RoadPiece,
} from '../../../src/core/scenery/road-tiles';
import type { PropKindRule, SceneryLevel } from '../../../src/core/scenery/scenery-level';
import type { Block } from '../../../src/core/scenery/street-grid';
import { TileGround } from '../../../src/core/scenery/tile-packing';
import { Traffic } from '../../../src/core/scenery/traffic';
import { CAR_RULES } from '../../../src/game/config/cars';
import { TILE } from '../../../src/game/config/tile-buildings';
import { GAME_LEVELS } from '../../../src/game/sim/levels';

// Phase 15: the districts of one level of each world, on the grid of tiles.

const LEVELS: readonly SceneryLevel[] = [
  ...['1-5', '2-5', '3-3', '4-5'].map((id) => {
    const level = GAME_LEVELS.find((l) => l.id === id)?.scenery;
    if (!level) throw new Error(`no level ${id}`);
    return level;
  }),
];

const STEPS = [
  [0, 1],
  [1, 0],
  [0, -1],
  [-1, 0],
] as const;

/** The tiles just past each open side of `p`. */
function beyond(p: RoadPiece): [number, number][] {
  return p.sides.flatMap((s, i) => {
    if (!s) return [];
    const [dx, dz] = STEPS[i] ?? [0, 0];
    return Array.from({ length: s.size }, (_, k): [number, number] =>
      dz !== 0
        ? [p.x + s.offset + k, dz > 0 ? p.z + p.size : p.z - 1]
        : [dx > 0 ? p.x + p.size : p.x - 1, p.z + s.offset + k],
    );
  });
}

interface Tiled {
  readonly k: PropKindRule;
  readonly x: number;
  readonly z: number;
  readonly w: number;
  readonly d: number;
}

interface SectionStats {
  free: number;
  covered: number;
  readonly footprints: Map<string, number>;
}

/** The block tiles fit to build on of each section, and how many of them buildings cover. */
function sectionStats(
  level: SceneryLevel,
  field: HeightField,
  blocks: readonly Block[],
  road: ReadonlySet<number>,
  [tiled, lots]: readonly [readonly Tiled[], ReadonlySet<string>],
): Map<string, SectionStats> {
  const t = TILE.size;
  const ground = new TileGround(field, TILE, level.props);
  const sections = new Map<string, SectionStats>();
  const blockTiles = new Map<number, SectionStats>();
  const count = (x: number, z: number): void => {
    if (road.has(tileKey(x, z)) || !ground.fit(x, z)) return;
    const name = field.sectionAt((z + 0.5) * t).section.name;
    let s = sections.get(name);
    if (!s) sections.set(name, (s = { free: 0, covered: 0, footprints: new Map() }));
    s.free++;
    blockTiles.set(tileKey(x, z), s);
  };
  for (const b of blocks) {
    for (let x = Math.round(b.xMin / t); x < Math.round(b.xMax / t); x++) {
      for (let z = Math.round(b.zMin / t); z < Math.round(b.zMax / t); z++) count(x, z);
    }
  }
  for (const { k, x, z, w, d } of tiled) {
    const s = blockTiles.get(tileKey(x, z));
    if (!s) continue;
    s.covered += w * d;
    if (lots.has(k.id)) continue;
    const key = [w, d].sort().join('x');
    s.footprints.set(key, (s.footprints.get(key) ?? 0) + 1);
  }
  return sections;
}

describe.each(LEVELS.map((l) => [l.id, l] as const))('level %s on tiles (phase 15)', (_, level) => {
  const field = new HeightField(level);
  const roads = levelRoads(field, level.roads, level.seed);
  const placer = new PropPlacer(field, level.props, level.seed, roads);
  const t = TILE.size;
  const pieces = roadPieces(roads.roads, TILE);
  const road = roadTiles(pieces);
  const onScreen = (x: number, z: number): boolean =>
    Math.abs((x + 0.5) * t) < level.roads.offscreenX && z * t > 0 && z * t < field.length;
  const kinds = new Map(
    [...level.props.groups.flatMap((g) => g.kinds), ...(level.props.lots ?? [])].map((k) => [
      k.id,
      k,
    ]),
  );
  const lots = new Set((level.props.lots ?? []).map((k) => k.id));
  const tiled = placer.snapshot().buildings.flatMap((b) => {
    const k = kinds.get(b.placement.kind);
    // Packed on the grid: a few homes of the same kinds are still scattered away from the
    // streets, with a round footprint.
    const whole = (half: number) => Math.abs((2 * half) / t - Math.round((2 * half) / t)) < 1e-6;
    if (!k?.tiles || !whole(b.halfX) || !whole(b.halfZ)) return [];
    const [w, d] = [Math.round((2 * b.halfX) / t), Math.round((2 * b.halfZ) / t)];
    const [x, z] = [Math.round(b.placement.x / t - w / 2), Math.round(b.placement.z / t - d / 2)];
    return [{ b, k, x, z, w, d }];
  });

  it('P15-R01: the road pieces and the buildings of whole tiles never share a tile', () => {
    expect(pieces.length).toBeGreaterThan(100);
    expect(road.size).toBe(pieces.reduce((n, p) => n + p.size * p.size, 0));
    const taken = new Set<number>();
    for (const { x, z, w, d } of tiled) {
      for (let i = 0; i < w; i++) {
        for (let j = 0; j < d; j++) {
          const key = tileKey(x + i, z + j);
          expect(road.has(key)).toBe(false);
          expect(taken.has(key)).toBe(false);
          taken.add(key);
        }
      }
    }
  });

  it('P15-R04, R05: open sides on screen meet another piece; no turn joins two sizes', () => {
    let unmatched = 0;
    for (const p of pieces) {
      for (const [x, z] of beyond(p)) if (onScreen(x, z) && !road.has(tileKey(x, z))) unmatched++;
      if (p.adapter && onScreen(p.x, p.z)) expect(p.kind).not.toBe('turn');
    }
    expect(unmatched).toBe(0);
    expect(pieces.some((p) => p.kind === 'cross')).toBe(true);
    expect(pieces.some((p) => p.kind === 'tee')).toBe(true);
  });

  it('P15-R06: no winding road or path runs onto a district street, so none ends there with a gap', () => {
    for (const r of roads.roads.filter((q) => q.kind !== 'street')) {
      for (const p of r.points) {
        const [x, z] = [Math.floor(p.x / t), Math.floor(p.z / t)];
        if (Math.abs(p.x) < level.roads.offscreenX) expect(road.has(tileKey(x, z))).toBe(false);
      }
    }
  });

  it('P15-R07: buildings stand on their tiles at scale 1, turned by quarter turns', () => {
    expect(tiled.length).toBeGreaterThan(100);
    for (const { b, k, w, d } of tiled) {
      expect(b.placement.scale).toBe(1);
      const quarter = b.placement.rotation / (Math.PI / 2);
      expect(quarter).toBeCloseTo(Math.round(quarter));
      const [kw, kd] = k.tiles ?? [0, 0];
      const turned = Math.round(quarter) % 2 !== 0;
      expect([w, d]).toEqual(turned ? [kd, kw] : [kw, kd]);
    }
  });

  it('P15-R08: buildings touching a street face it', () => {
    const along = (
      x: number,
      z: number,
      w: number,
      d: number,
      [dx, dz]: readonly [number, number],
    ) =>
      dz !== 0
        ? Array.from({ length: w }, (_, i) => road.has(tileKey(x + i, dz < 0 ? z - 1 : z + d)))
        : Array.from({ length: d }, (_, j) => road.has(tileKey(dx < 0 ? x - 1 : x + w, z + j)));
    for (const { b, x, z, w, d } of tiled) {
      if (!STEPS.some((s) => along(x, z, w, d, s).some(Boolean))) continue;
      const front = [-Math.sin(b.placement.rotation), -Math.cos(b.placement.rotation)] as const;
      const step = [Math.round(front[0]), Math.round(front[1])] as const;
      expect(along(x, z, w, d, step).some(Boolean)).toBe(true);
    }
  });

  it('P15-R08: each section fills its density of block tiles, with mixed footprints', () => {
    const sections = sectionStats(level, field, roads.blocks, road, [tiled, lots]);
    for (const [name, s] of sections) {
      const density = level.sections.find((q) => q.name === name)?.buildingDensity ?? 0;
      if (s.free < 200) continue;
      expect(Math.abs(s.covered / s.free - density), name).toBeLessThanOrEqual(0.1);
      const counts = [...s.footprints.values()];
      const total = counts.reduce((a, b) => a + b, 0);
      expect(s.footprints.size, name).toBeGreaterThanOrEqual(3);
      expect(Math.max(...counts) / total, name).toBeLessThanOrEqual(0.6);
    }
  });

  it('P15-R11: cars drive on the roadway of the streets, never on a sidewalk', () => {
    const streets = roads.roads.filter((r) => r.kind === 'street').slice(0, 200);
    const traffic = new Traffic(streets, () => 0, CAR_RULES, level.seed);
    const cars = traffic.at(3, { xMin: -1000, xMax: 1000, zMin: 0, zMax: field.length });
    expect(cars.length).toBeGreaterThan(10);
    for (const car of cars) {
      const [x, z] = [Math.floor(car.x / t), Math.floor(car.z / t)];
      expect(road.has(tileKey(x, z))).toBe(true);
      // Within the roadway of a street: at least the sidewalk's width from the edge of its tiles
      // (at a crossing, of either street).
      const onRoadway = (q: (typeof streets)[number]) => {
        const [a, b] = [q.points[0], q.points.at(-1)];
        if (!a || !b) return false;
        const [lo, hi] = a.z === b.z ? [a.x, b.x] : [a.z, b.z];
        const along = a.z === b.z ? car.x : car.z;
        const off = a.z === b.z ? Math.abs(car.z - a.z) : Math.abs(car.x - a.x);
        return (
          along >= Math.min(lo, hi) - 1e-6 &&
          along <= Math.max(lo, hi) + 1e-6 &&
          off <= q.width / 2 - TILE.sidewalk + 1e-6
        );
      };
      expect(streets.some(onRoadway)).toBe(true);
    }
  });
});

import { describe, expect, it } from 'vitest';
import type { GameLevel } from '../../../../src/core/content/game-level';
import { levelLength, type TerrainSection } from '../../../../src/core/scenery/scenery-level';
import { QUIET_BEFORE_BOSS } from '../../../../src/game/config/world-1/bosses';
import { MORNING_MIST } from '../../../../src/game/config/world-3/looks';
import {
  JUNGLE_PLANTS,
  WORLD_3_FLOATING,
  WORLD_3_PROPS,
} from '../../../../src/game/config/world-3/props';
import { PLAN_3_1 } from '../../../../src/game/config/world-3/waves';
import { composeBeats } from '../../../../src/game/config/world-2/waves';
import { ENEMY_KINDS } from '../../../../src/game/sim/enemy-kinds';
import { LEVELS } from '../../../../src/game/sim/levels';
import { WORLD_2 } from '../../../../src/game/sim/world-2';
import { WORLD_3 } from '../../../../src/game/sim/world-3';
import { SCENERY_BINDINGS } from '../../../../src/game/view/scenery-bindings';
import { at } from '../../../helpers/at';
import { buildingCount, levelMetrics, waterShares } from '../../../helpers/level-metrics';

const level = (id: string): GameLevel => {
  const found = [...WORLD_2, ...WORLD_3].find((l) => l.id === id);
  if (!found) throw new Error(`no level ${id}`);
  return found;
};

const increasing = (values: readonly number[]) =>
  values.every((v, i) => i === 0 || v > (values[i - 1] ?? 0));

const METRICS = WORLD_3.map(levelMetrics);
const lookOf = (id: string) => SCENERY_BINDINGS.looks[level(id).scenery.id];

/** A sea section: a coast, or open water whose ground lies under the water level. */
const isSea = (s: TerrainSection) => s.shore !== undefined || s.relief.base < 0;

/** Plants and what grows or stands on the water: not buildings. */
const PLANTS = new Set([
  ...WORLD_3_PROPS.trees.map((t) => t.id),
  ...WORLD_3_FLOATING.kinds.map((k) => k.id),
]);

describe('World 3', () => {
  it('P09-R01: five playable levels, 3-1 to 3-5, all unlocked; worlds 4 and 5 stay locked', () => {
    expect(WORLD_3.map((l) => l.id)).toEqual(['3-1', '3-2', '3-3', '3-4', '3-5']);
    const row = LEVELS.levels.filter((l) => l.world === 3);
    expect(row.map((l) => [l.id, l.unlocked])).toEqual(WORLD_3.map((l) => [l.id, true]));
    expect(LEVELS.levels.filter((l) => l.world > 3).every((l) => !l.unlocked)).toBe(true);
    // 3-1 comes right after 2-5 in the grid (completing 2-5 highlights it); after 3-5 comes a
    // locked level, so 3-5 stays highlighted.
    const ids = LEVELS.levels.map((l) => l.id);
    expect(ids.indexOf('3-1')).toBe(ids.indexOf('2-5') + 1);
    expect(LEVELS.levels[ids.indexOf('3-5') + 1]?.unlocked).toBe(false);
  });

  it('P09-R02: each level lasts about 5 minutes (290 to 310 s) at its ground speed', () => {
    for (const game of WORLD_3) {
      const seconds = levelLength(game.scenery) / game.scenery.scrollSpeed;
      expect(seconds, game.id).toBeGreaterThanOrEqual(290);
      expect(seconds, game.id).toBeLessThanOrEqual(310);
    }
    expect(WORLD_3.map((l) => l.scenery.scrollSpeed)).toEqual([70, 60, 55, 60, 60]);
  });

  it('P09-R03: 3-1 has a sea section, at most 30 % of it sea; 3-2 to 3-5 have none', () => {
    const first = at(WORLD_3, 0);
    expect(first.scenery.sections.some(isSea)).toBe(true);
    expect(waterShares(first, isSea).sea).toBeGreaterThan(0);
    expect(waterShares(first, isSea).sea).toBeLessThanOrEqual(0.3);
    const seconds = (sections: readonly TerrainSection[]) =>
      sections.reduce((sum, s) => sum + s.seconds, 0);
    const sections = first.scenery.sections;
    expect(seconds(sections.filter(isSea)) / seconds(sections)).toBeLessThanOrEqual(0.3);
    for (const game of WORLD_3.slice(1)) {
      expect(game.scenery.sections.filter(isSea), game.id).toEqual([]);
      expect(waterShares(game, isSea).sea, game.id).toBe(0);
    }
  });

  it('P09-R03: every level has some river, lake or swamp water', () => {
    for (const game of WORLD_3)
      expect(waterShares(game, isSea).inland, game.id).toBeGreaterThan(0.02);
    // Rivers cut below the water level, the swamps, the lake and the pools.
    const has = (id: string, test: (s: TerrainSection) => boolean) =>
      level(id).scenery.sections.some(test);
    for (const id of ['3-1', '3-2', '3-3', '3-5'])
      expect(
        has(id, (s) => (s.channel?.floor ?? 0) < 0),
        id,
      ).toBe(true);
    expect(has('3-4', (s) => s.relief.base < 4 && (s.floatDensity ?? 0) > 0)).toBe(true);
    expect(has('3-5', (s) => (s.lakes?.level ?? 0) < 0)).toBe(true);
  });

  it('P09-R03: the number of buildings goes up from 3-1 to 3-5 (fixed seed)', () => {
    expect(increasing(WORLD_3.map((l) => buildingCount(l, PLANTS)))).toBe(true);
  });

  it('P09-R03: each level begins on the kind of ground the previous one ended on', () => {
    const first = (id: string) => at(level(id).scenery.sections, 0);
    const last = (id: string) => level(id).scenery.sections.at(-1);
    for (const [prev, next] of [
      ['3-1', '3-2'],
      ['3-2', '3-3'],
      ['3-3', '3-4'],
      ['3-4', '3-5'],
    ] as const) {
      expect(first(next).relief, next).toEqual(last(prev)?.relief);
    }
    expect(first('3-2').channel).toEqual(last('3-1')?.channel);
    expect(last('3-5')?.groups).toEqual(['canopy-centre']);
    // The delta's sea, the waterfalls of 3-3, the swamp pipelines and the dam of 3-4.
    expect(first('3-1').relief.base).toBeLessThan(-20);
    expect(
      level('3-3').scenery.props.landmarks?.filter((l) => l.kind === 'waterfall').length,
    ).toBeGreaterThanOrEqual(2);
    expect(level('3-4').scenery.props.lines?.every((l) => l.overWater)).toBe(true);
    expect(level('3-4').scenery.props.landmarks?.map((l) => l.kind)).toContain('giant-dam');
    // The rainforest's canopy: the densest trees of the world.
    const rainforest = level('3-2').scenery.sections;
    expect(rainforest.filter((s) => s.treeDensity >= 1).length).toBeGreaterThanOrEqual(2);
    expect(rainforest.some((s) => s.trees?.includes(at(JUNGLE_PLANTS.rainforest, 0)))).toBe(true);
  });

  /** The sky script of level `id`; fails when it has none. */
  const script = (id: string) => {
    const found = lookOf(id)?.atmosphere;
    if (!found) throw new Error(`no sky script for ${id}`);
    return found;
  };
  const rain = (strength: number) => ({ kind: 'rain', strength });
  const changes = (id: string) => script(id).changes ?? [];

  it('P09-R04: 3-1 a morning mist lifting over the first half; 3-2 a shower over its middle third', () => {
    expect(script('3-1').start).toEqual({
      timeOfDay: 'morning',
      clouds: [0.3, 0.2],
      mist: { fog: 0.4, white: MORNING_MIST.white },
    });
    expect(changes('3-1').map((c) => [c.from, c.to, c.look])).toEqual([
      [0, 150, { timeOfDay: 'morning', clouds: [0.3, 0.2] }],
    ]);
    expect(script('3-2').start).toMatchObject({ timeOfDay: 'midday', clouds: [0.5, 0.3] });
    expect(script('3-2').start.weather).toBeUndefined();
    // Green-tinted ambient under the canopy.
    const tint = script('3-2').start.tint ?? [1, 1, 1];
    expect(tint[1]).toBeGreaterThan(Math.max(tint[0], tint[2]));
    expect(changes('3-2').map((c) => [c.from, c.to, c.look.weather])).toEqual([
      [92, 108, rain(0.4)],
      [192, 208, undefined],
    ]);
  });

  it('P09-R04: 3-3 a thunderstorm building over the first quarter, with lightning', () => {
    expect(script('3-3').start).toMatchObject({ timeOfDay: 'afternoon', clouds: [0.5, 0.5] });
    expect(script('3-3').start.weather).toBeUndefined();
    expect(changes('3-3').map((c) => [c.from, c.to, c.look])).toEqual([
      [
        0,
        75,
        { timeOfDay: 'afternoon', clouds: [0.9, 0.9], storm: 1, weather: rain(0.8), lightning: 1 },
      ],
    ]);
  });

  it('P09-R04: 3-4 a rainy dusk; 3-5 a rainy night clearing before the final boss', () => {
    expect(script('3-4').start).toEqual({
      timeOfDay: 'dusk',
      clouds: [0.6, 0.4],
      weather: rain(0.3),
    });
    expect(changes('3-4')).toEqual([]);
    expect(script('3-5').start).toEqual({
      timeOfDay: 'night',
      clouds: [0.6, 0.4],
      weather: rain(0.5),
    });
    // The rain stops and the clouds open before the final boss (300 s; the ground runs ahead of
    // the level after the mini boss's fight).
    const [clearing] = changes('3-5');
    expect(clearing?.look).toEqual({ timeOfDay: 'night', clouds: [0.2, 0.1] });
    expect(clearing?.to).toBeLessThan(300);
  });

  it('P09-R07: each wave script uses only its level’s kinds; 3-2 to 3-5 use all eleven', () => {
    const kinds = (id: string) => [...new Set(level(id).waves.map((w) => w.kind))].sort();
    expect(kinds('3-1')).toEqual(['gnat', 'hornet', 'scout', 'splitter', 'strafer', 'weaver']);
    for (const id of ['3-2', '3-3', '3-4', '3-5'])
      expect(kinds(id), id).toEqual(ENEMY_KINDS.map((k) => k.id).sort());
    // Each level's lead kinds come often.
    const count = (id: string, kind: string) =>
      level(id).waves.filter((w) => w.kind === kind).length;
    expect(count('3-2', 'hornet')).toBeGreaterThan(count('3-2', 'scout'));
    expect(count('3-3', 'spinner') + count('3-3', 'rocketeer')).toBeGreaterThan(
      count('3-3', 'scout'),
    );
    expect(count('3-4', 'carrier')).toBeGreaterThan(count('3-3', 'carrier'));
    expect(count('3-5', 'bulwark')).toBeGreaterThan(count('3-4', 'bulwark'));
  });

  it('P09-R07: the waves are deterministic: same distances, same enemies, twice', () => {
    expect(composeBeats(PLAN_3_1)).toEqual(composeBeats(PLAN_3_1));
    expect(levelMetrics(level('3-2'))).toEqual(METRICS[1]);
  });

  it('P09-R08: enemies, HP per minute and the peak on screen go up strictly from 3-1 to 3-5', () => {
    expect(increasing(METRICS.map((m) => m.perMinute))).toBe(true);
    expect(increasing(METRICS.map((m) => m.healthPerMinute))).toBe(true);
    expect(increasing(METRICS.map((m) => m.peak))).toBe(true);
    const factors = WORLD_3.map((l) => l.difficulty);
    for (let i = 1; i < factors.length; i++) {
      expect(at(factors, i).bulletSpeed).toBeGreaterThanOrEqual(at(factors, i - 1).bulletSpeed);
      expect(at(factors, i).fireRate).toBeGreaterThanOrEqual(at(factors, i - 1).fireRate);
    }
    expect(factors.map((f) => f.bulletSpeed)).toEqual([1, 1.05, 1.1, 1.2, 1.25]);
    expect(factors.map((f) => f.fireRate)).toEqual([1, 1.05, 1.1, 1.2, 1.25]);
  });

  it('P09-R08: 3-1 is at least as hard as 2-3, and 3-5 harder than 2-5', () => {
    const [w23, w25] = [levelMetrics(level('2-3')), levelMetrics(level('2-5'))];
    const [w31, w35] = [at(METRICS, 0), at(METRICS, 4)];
    expect(w31.perMinute).toBeGreaterThanOrEqual(w23.perMinute);
    expect(w31.healthPerMinute).toBeGreaterThanOrEqual(w23.healthPerMinute);
    expect(w31.peak).toBeGreaterThanOrEqual(w23.peak);
    expect(w35.perMinute).toBeGreaterThan(w25.perMinute);
    expect(w35.healthPerMinute).toBeGreaterThan(w25.healthPerMinute);
    expect(w35.peak).toBeGreaterThan(w25.peak);
    const d = (id: string) => level(id).difficulty;
    expect(d('3-1').bulletSpeed).toBeGreaterThanOrEqual(d('2-3').bulletSpeed);
    expect(d('3-1').fireRate).toBeGreaterThanOrEqual(d('2-3').fireRate);
    expect(d('3-5').bulletSpeed).toBeGreaterThan(d('2-5').bulletSpeed);
    expect(d('3-5').fireRate).toBeGreaterThan(d('2-5').fireRate);
  });

  it('P09-R08: in each level, the second half has more enemy HP than the first', () => {
    for (const [i, m] of METRICS.entries())
      expect(m.secondHalf, WORLD_3[i]?.id).toBeGreaterThan(m.firstHalf);
  });

  it('P09-R09: a mini boss at the middle of each level and a final boss at its end, no wave before them', () => {
    for (const game of WORLD_3) {
      const length = levelLength(game.scenery);
      expect(
        game.bosses?.map((b) => [b.rank, b.at]),
        game.id,
      ).toEqual([
        ['mini', length / 2],
        ['final', length],
      ]);
      const quiet = QUIET_BEFORE_BOSS * game.scenery.scrollSpeed;
      for (const boss of game.bosses ?? []) {
        expect(game.waves.filter((w) => w.at > boss.at - quiet && w.at <= boss.at)).toEqual([]);
      }
    }
  });
});

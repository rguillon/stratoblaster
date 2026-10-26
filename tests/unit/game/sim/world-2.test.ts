import { describe, expect, it } from 'vitest';
import type { GameLevel } from '../../../../src/core/content/game-level';
import { levelLength } from '../../../../src/core/scenery/scenery-level';
import { resolveSky } from '../../../../src/core/scenery/sky-look';
import { QUIET_BEFORE_BOSS } from '../../../../src/game/config/world-1/bosses';
import { WORLD_2_FLOATING, WORLD_2_PROP_IDS } from '../../../../src/game/config/world-2/props';
import { composeBeats, PLAN_2_1 } from '../../../../src/game/config/world-2/waves';
import { FIRST_KINDS } from '../../../../src/game/sim/enemy-kinds';
import { LEVELS } from '../../../../src/game/sim/levels';
import { WORLD_1 } from '../../../../src/game/sim/world-1';
import { WORLD_2 } from '../../../../src/game/sim/world-2';
import { SCENERY_BINDINGS } from '../../../../src/game/view/scenery-bindings';
import { at } from '../../../helpers/at';
import { buildingCount, levelMetrics, seaShare } from '../../../helpers/level-metrics';

const level = (id: string): GameLevel => {
  const found = [...WORLD_1, ...WORLD_2].find((l) => l.id === id);
  if (!found) throw new Error(`no level ${id}`);
  return found;
};

const increasing = (values: readonly number[]) =>
  values.every((v, i) => i === 0 || v > (values[i - 1] ?? 0));

const METRICS = WORLD_2.map(levelMetrics);
const lookOf = (id: string) => SCENERY_BINDINGS.looks[level(id).scenery.id];

/** Plants and the lone huts and masts scattered like plants: not buildings. */
const PLANTS = new Set([
  WORLD_2_PROP_IDS.snowPine,
  WORLD_2_PROP_IDS.frostedTree,
  WORLD_2_PROP_IDS.snowyBush,
  ...WORLD_2_FLOATING.kinds.map((k) => k.id),
]);

describe('World 2', () => {
  it('P08-R01: five playable levels, 2-1 to 2-5, all unlocked', () => {
    expect(WORLD_2.map((l) => l.id)).toEqual(['2-1', '2-2', '2-3', '2-4', '2-5']);
    const row = LEVELS.levels.filter((l) => l.world === 2);
    expect(row.map((l) => [l.id, l.unlocked])).toEqual(WORLD_2.map((l) => [l.id, true]));
    // 2-1 comes right after 1-5 in the grid: completing 1-5 highlights it.
    const ids = LEVELS.levels.map((l) => l.id);
    expect(ids.indexOf('2-1')).toBe(ids.indexOf('1-5') + 1);
  });

  it('P08-R02: each level lasts about 5 minutes (290 to 310 s) at its ground speed', () => {
    for (const game of WORLD_2) {
      const seconds = levelLength(game.scenery) / game.scenery.scrollSpeed;
      expect(seconds, game.id).toBeGreaterThanOrEqual(290);
      expect(seconds, game.id).toBeLessThanOrEqual(310);
    }
    expect(WORLD_2.map((l) => l.scenery.scrollSpeed)).toEqual([70, 65, 60, 55, 60]);
  });

  it('P08-R03: the share over the sea goes down from 2-1 to 2-2; 2-3 to 2-5 have no sea', () => {
    const [first, second] = WORLD_2.map(seaShare);
    expect(first).toBeGreaterThanOrEqual(0.8);
    expect(second).toBeLessThanOrEqual(0.5);
    expect(second).toBeLessThan(first ?? 0);
    for (const id of ['2-3', '2-4', '2-5']) {
      const { scenery } = level(id);
      expect(scenery.sea, id).toBeUndefined();
      expect(
        scenery.sections.some((s) => s.shore),
        id,
      ).toBe(false);
    }
  });

  it('P08-R03: the number of buildings goes up from 2-1 to 2-5 (fixed seed)', () => {
    expect(increasing(WORLD_2.map((l) => buildingCount(l, PLANTS)))).toBe(true);
  });

  it('P08-R03: each level begins on the kind of ground the previous one ended on', () => {
    const first = (id: string) => at(level(id).scenery.sections, 0);
    const last = (id: string) => level(id).scenery.sections.at(-1);
    // 2-1's coast and 2-2's start, the snowy hills of 2-2 and the tundra's edge, the lakes, the
    // mine fields.
    expect(first('2-2').shore).toEqual(last('2-1')?.shore);
    expect(first('2-3').relief).toEqual(last('2-2')?.relief);
    expect(first('2-4').lakes).toEqual(last('2-3')?.lakes);
    expect(first('2-5').relief).toEqual(last('2-4')?.relief);
    expect(last('2-5')?.groups).toEqual(['polar-city']);
    // Fjords, frozen lakes, a glacier with crevasses, ice floating on the sea of 2-1.
    expect(level('2-2').scenery.sections.some((s) => s.channel && s.channel.floor < 0)).toBe(true);
    expect(level('2-3').scenery.sections.some((s) => s.lakes)).toBe(true);
    expect(level('2-3').scenery.props.lines?.length).toBe(1);
    expect(level('2-4').scenery.sections.some((s) => s.crevasses)).toBe(true);
    expect(level('2-1').scenery.sections.some((s) => (s.floatDensity ?? 0) > 0)).toBe(true);
  });

  /** The sky script of level `id`; fails when it has none. */
  const script = (id: string) => {
    const found = lookOf(id)?.atmosphere;
    if (!found) throw new Error(`no sky script for ${id}`);
    return found;
  };
  const snow = (strength: number) => ({ kind: 'snow', strength });
  const changes = (id: string) => script(id).changes ?? [];

  it('P08-R04, P08-R06: 2-1 at dawn; 2-2 a clear morning, light snow over its second half', () => {
    expect(script('2-1').start).toEqual({ timeOfDay: 'dawn', clouds: [0.25, 0.15] });
    expect(changes('2-1')).toEqual([]);
    expect(script('2-2').start).toEqual({ timeOfDay: 'morning', clouds: [0.2, 0.3] });
    expect(changes('2-2').map((c) => [c.from, c.look.weather])).toEqual([[150, snow(0.2)]]);
  });

  it('P08-R04, P08-R06: 2-3 overcast with snow; 2-4 a blizzard over its second half', () => {
    expect(script('2-3').start).toMatchObject({
      timeOfDay: 'midday',
      clouds: [0.8, 0.6],
      weather: snow(0.4),
    });
    expect(script('2-4').start).toMatchObject({
      timeOfDay: 'afternoon',
      clouds: [0.9, 0.8],
      weather: snow(0.5),
    });
    // A blizzard over the second half (from 150 s), clearing for the final boss (at 300 s).
    expect(changes('2-4').map((c) => [c.to, c.look.weather])).toEqual([
      [150, snow(1)],
      [292, snow(0.3)],
    ]);
  });

  it('P08-R04, P08-R06: 2-5 dusk to night over its first third, with an aurora', () => {
    expect(script('2-5').start).toMatchObject({ timeOfDay: 'dusk', clouds: [0.3, 0.2] });
    expect(changes('2-5').map((c) => [c.from, c.to, c.look])).toEqual([
      [0, 100, { timeOfDay: 'night', clouds: [0.1, 0.05], aurora: 1 }],
    ]);
  });

  it('P08-R04: the clouds follow the time of day: pink-orange dawn, dark grey storm, blue-grey night', () => {
    const base = { fog: { start: 1000, end: 2600 }, cloudOpacity: [0.75, 0.5] };
    const sky = (id: string) =>
      resolveSky(lookOf(id)?.atmosphere?.start ?? { timeOfDay: 'midday', clouds: [0, 0] }, base);
    const [r, , b] = sky('2-1').clouds[0]?.color ?? [0, 0, 0];
    expect(r).toBeGreaterThan(b);
    expect(Math.max(...(sky('2-4').clouds[0]?.color ?? [1]))).toBeLessThan(0.5);
    expect(sky('2-4').fog.end).toBeLessThan(sky('2-3').fog.end);
  });

  it('P08-R08: each wave script uses only its level’s kinds; 2-3 to 2-5 use all eleven first kinds, none of the new ones (P05-R24)', () => {
    const kinds = (id: string) => [...new Set(level(id).waves.map((w) => w.kind))].sort();
    expect(kinds('2-1')).toEqual(['gnat', 'hornet', 'scout', 'strafer', 'weaver']);
    expect(kinds('2-2')).toEqual([...kinds('2-1'), 'lancer', 'splitter'].sort());
    for (const id of ['2-3', '2-4', '2-5'])
      expect(kinds(id), id).toEqual(FIRST_KINDS.map((k) => k.id).sort());
  });

  it('P08-R08: the waves are deterministic: same distances, same enemies, twice', () => {
    expect(composeBeats(PLAN_2_1)).toEqual(composeBeats(PLAN_2_1));
    expect(levelMetrics(level('2-2'))).toEqual(METRICS[1]);
  });

  it('P08-R09: enemies, HP per minute and the peak on screen go up strictly from 2-1 to 2-5', () => {
    expect(increasing(METRICS.map((m) => m.perMinute))).toBe(true);
    expect(increasing(METRICS.map((m) => m.healthPerMinute))).toBe(true);
    expect(increasing(METRICS.map((m) => m.peak))).toBe(true);
    const factors = WORLD_2.map((l) => l.difficulty);
    for (let i = 1; i < factors.length; i++) {
      expect(at(factors, i).bulletSpeed).toBeGreaterThanOrEqual(at(factors, i - 1).bulletSpeed);
      expect(at(factors, i).fireRate).toBeGreaterThanOrEqual(at(factors, i - 1).fireRate);
    }
    expect(factors.map((f) => f.bulletSpeed)).toEqual([0.9, 0.95, 1, 1.1, 1.15]);
  });

  it('P08-R09: 2-1 is at least as hard as 1-3, and 2-5 harder than 1-5', () => {
    const [w13, w15] = [levelMetrics(level('1-3')), levelMetrics(level('1-5'))];
    const [w21, w25] = [at(METRICS, 0), at(METRICS, 4)];
    expect(w21.perMinute).toBeGreaterThanOrEqual(w13.perMinute);
    expect(w21.healthPerMinute).toBeGreaterThanOrEqual(w13.healthPerMinute);
    expect(w25.perMinute).toBeGreaterThan(w15.perMinute);
    expect(w25.healthPerMinute).toBeGreaterThan(w15.healthPerMinute);
    const d = (id: string) => level(id).difficulty;
    expect(d('2-1').bulletSpeed).toBeGreaterThanOrEqual(d('1-3').bulletSpeed);
    expect(d('2-1').fireRate).toBeGreaterThanOrEqual(d('1-3').fireRate);
    expect(d('2-5').bulletSpeed).toBeGreaterThan(d('1-5').bulletSpeed);
    expect(d('2-5').fireRate).toBeGreaterThan(d('1-5').fireRate);
  });

  it('P08-R09: in each level, the second half has more enemy HP than the first', () => {
    for (const [i, m] of METRICS.entries())
      expect(m.secondHalf, WORLD_2[i]?.id).toBeGreaterThan(m.firstHalf);
  });

  it('P08-R10: a mini boss at the middle of each level and a final boss at its end, no wave before them', () => {
    for (const game of WORLD_2) {
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

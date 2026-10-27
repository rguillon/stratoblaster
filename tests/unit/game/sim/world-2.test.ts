import { describe, expect, it } from 'vitest';
import type { GameLevel } from '../../../../src/core/content/game-level';
import { levelLength } from '../../../../src/core/scenery/scenery-level';
import { QUIET_BEFORE_BOSS } from '../../../../src/game/config/world-1/bosses';
import { TRANSITION } from '../../../../src/game/config/world-2/scenery';
import { WORLD_2_GROUPS, WORLD_2_PROPS } from '../../../../src/game/config/world-2/props';
import { composeBeats, PLAN_2_1 } from '../../../../src/game/config/world-2/waves';
import { FIRST_KINDS } from '../../../../src/game/sim/enemy-kinds';
import { LEVELS } from '../../../../src/game/sim/levels';
import { WORLD_1 } from '../../../../src/game/sim/world-1';
import { WORLD_2 } from '../../../../src/game/sim/world-2';
import { SCENERY_BINDINGS } from '../../../../src/game/view/scenery-bindings';
import { at } from '../../../helpers/at';
import { levelMetrics, propCounts } from '../../../helpers/level-metrics';

const level = (id: string): GameLevel => {
  const found = [...WORLD_1, ...WORLD_2].find((l) => l.id === id);
  if (!found) throw new Error(`no level ${id}`);
  return found;
};

const increasing = (values: readonly number[]) =>
  values.every((v, i) => i === 0 || v > (values[i - 1] ?? 0));

const METRICS = WORLD_2.map(levelMetrics);
const lookOf = (id: string) => SCENERY_BINDINGS.looks[level(id).scenery.id];

/** Plants: not buildings. */
const PLANTS = new Set(WORLD_2_PROPS.trees.map((t) => t.id));

/** How much of a level a ground cover covers: its shares weighted by the sections' time. */
const cover = (game: GameLevel, kind: 'lush' | 'sandy' | 'paved') =>
  game.scenery.sections.reduce((sum, s) => sum + s.seconds * (s.surface?.[kind] ?? 0), 0);

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

  it('P08-R03: no World 2 level has a sea or a shore (reworked, 2026-10-27)', () => {
    for (const game of WORLD_2) {
      expect(game.scenery.sea, game.id).toBeUndefined();
      expect(
        game.scenery.sections.some((s) => s.shore),
        game.id,
      ).toBe(false);
    }
  });

  it('P08-R03: the sand gives way to pavement from 2-1 to 2-5', () => {
    for (const id of ['2-1', '2-2'])
      expect(cover(level(id), 'sandy'), id).toBeGreaterThan(cover(level(id), 'paved'));
    for (const id of ['2-4', '2-5'])
      expect(cover(level(id), 'paved'), id).toBeGreaterThan(cover(level(id), 'sandy'));
    expect(increasing(WORLD_2.map((l) => -cover(l, 'sandy')))).toBe(true);
    expect(increasing(WORLD_2.map((l) => cover(l, 'paved')))).toBe(true);
  });

  it('P08-R03: the industry comes in slowly: none in 2-1, heavy industry only at the end of 2-5', () => {
    const groups = (id: string) => new Set(level(id).scenery.sections.flatMap((s) => s.groups));
    for (const g of [WORLD_2_GROUPS.industrial, WORLD_2_GROUPS.heavyIndustry])
      expect(groups('2-1').has(g), g).toBe(false);
    expect(groups('2-1').has(WORLD_2_GROUPS.mines)).toBe(true);
    expect(groups('2-3').has(WORLD_2_GROUPS.oil)).toBe(true);
    expect(level('2-5').scenery.sections.at(-1)?.groups).toEqual([WORLD_2_GROUPS.heavyIndustry]);
  });

  it('P08-R03: props and buildings go up from 2-1 to 2-5, and from each first half to the second (fixed seed)', () => {
    const counts = WORLD_2.map((l) => propCounts(l, PLANTS));
    expect(increasing(counts.map((c) => c.all))).toBe(true);
    expect(increasing(counts.map((c) => c.buildings))).toBe(true);
    for (const [i, c] of counts.entries())
      expect(c.secondHalf, at(WORLD_2, i).id).toBeGreaterThan(c.firstHalf);
  });

  it('P08-R03: each level begins on the ground the previous one ended on; slow transitions', () => {
    for (const [i, next] of WORLD_2.slice(1).entries()) {
      const { sections } = at(WORLD_2, i).scenery;
      const [last, first] = [at(sections, sections.length - 1), at(next.scenery.sections, 0)];
      expect(first.relief, next.id).toEqual(last.relief);
      expect(first.surface, next.id).toEqual(last.surface);
      expect(first.groups, next.id).toEqual(last.groups);
    }
    for (const game of WORLD_2) {
      expect(game.scenery.transition, game.id).toBe(TRANSITION);
      expect(game.scenery.transition, game.id).toBeGreaterThan(at(WORLD_1, 0).scenery.transition);
      // Each section is longer than the blend, so the blends never overlap.
      for (const s of game.scenery.sections)
        expect(s.seconds * game.scenery.scrollSpeed, s.name).toBeGreaterThan(TRANSITION);
    }
  });

  /** The sky script of level `id`; fails when it has none. */
  const script = (id: string) => {
    const found = lookOf(id)?.atmosphere;
    if (!found) throw new Error(`no sky script for ${id}`);
    return found;
  };

  it('P08-R04, P08-R06: a time of day per level, fixed within it: three days, dusk, night', () => {
    expect(WORLD_2.map((l) => script(l.id).start)).toEqual([
      { timeOfDay: 'morning', clouds: [0.15, 0.1] },
      { timeOfDay: 'midday', clouds: [0.2, 0.15] },
      { timeOfDay: 'afternoon', clouds: [0.25, 0.2], storm: 0.15 },
      { timeOfDay: 'dusk', clouds: [0.35, 0.25], storm: 0.3 },
      { timeOfDay: 'night', clouds: [0.4, 0.3], storm: 0.35 },
    ]);
    for (const game of WORLD_2) expect(script(game.id).changes ?? [], game.id).toEqual([]);
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

import { describe, expect, it } from 'vitest';
import type { GameLevel } from '../../../../src/core/content/game-level';
import { levelLength, type TerrainSection } from '../../../../src/core/scenery/scenery-level';
import { QUIET_BEFORE_BOSS } from '../../../../src/game/config/world-1/bosses';
import { TRANSITION } from '../../../../src/game/config/world-2/scenery';
import { MORNING_MIST } from '../../../../src/game/config/world-3/looks';
import { WORLD_3_GROUPS, WORLD_3_PROPS } from '../../../../src/game/config/world-3/props';
import { PLAN_3_1 } from '../../../../src/game/config/world-3/waves';
import { composeBeats } from '../../../../src/game/config/world-2/waves';
import { FIRST_KINDS } from '../../../../src/game/sim/enemy-kinds';
import { ELITE_KINDS } from '../../../../src/game/sim/elite-kinds';
import { VETERAN_KINDS } from '../../../../src/game/sim/veteran-kinds';
import { LEVELS } from '../../../../src/game/sim/levels';
import { WORLD_2 } from '../../../../src/game/sim/world-2';
import { WORLD_3 } from '../../../../src/game/sim/world-3';
import { SCENERY_BINDINGS } from '../../../../src/game/view/scenery-bindings';
import { at } from '../../../helpers/at';
import { levelMetrics, propCounts, waterShares } from '../../../helpers/level-metrics';

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

/** Plants: not buildings. */
const PLANTS = new Set(WORLD_3_PROPS.trees.map((t) => t.id));

/** How much of a level a ground cover covers: its shares weighted by the sections' time. */
const cover = (game: GameLevel, kind: 'lush' | 'paved') =>
  game.scenery.sections.reduce((sum, s) => sum + s.seconds * (s.surface?.[kind] ?? 0), 0);

describe('World 3', () => {
  it('P09-R01: five playable levels, 3-1 to 3-5, all unlocked', () => {
    expect(WORLD_3.map((l) => l.id)).toEqual(['3-1', '3-2', '3-3', '3-4', '3-5']);
    const row = LEVELS.levels.filter((l) => l.world === 3);
    expect(row.map((l) => [l.id, l.unlocked])).toEqual(WORLD_3.map((l) => [l.id, true]));
    // 3-1 comes right after 2-5 in the grid (completing 2-5 highlights it); after 3-5 comes
    // 4-1 (P10-R01).
    const ids = LEVELS.levels.map((l) => l.id);
    expect(ids.indexOf('3-1')).toBe(ids.indexOf('2-5') + 1);
    expect(LEVELS.levels[ids.indexOf('3-5') + 1]?.id).toBe('4-1');
  });

  it('P09-R02: each level lasts about 5 minutes (290 to 310 s) at its ground speed', () => {
    for (const game of WORLD_3) {
      const seconds = levelLength(game.scenery) / game.scenery.scrollSpeed;
      expect(seconds, game.id).toBeGreaterThanOrEqual(290);
      expect(seconds, game.id).toBeLessThanOrEqual(310);
    }
    expect(WORLD_3.map((l) => l.scenery.scrollSpeed)).toEqual([70, 60, 55, 60, 60]);
  });

  it('P09-R03: no open sea in World 3, canals and rivers allowed (reviewer, 2026-10-27)', () => {
    for (const game of WORLD_3) {
      expect(game.scenery.sections.filter(isSea), game.id).toEqual([]);
      expect(waterShares(game, isSea).sea, game.id).toBe(0);
      for (const s of game.scenery.sections) {
        expect(s.relief.base, `${game.id} ${s.name}`).toBeGreaterThan(game.scenery.sea?.level ?? 0);
        expect(s.floatDensity ?? 0, `${game.id} ${s.name}`).toBe(0);
      }
      expect(game.scenery.props.floating, game.id).toBeUndefined();
    }
  });

  it('P09-R03: every level has some canal, river or pond water', () => {
    for (const game of WORLD_3) {
      expect(waterShares(game, isSea).inland, game.id).toBeGreaterThan(0.02);
      expect(
        game.scenery.sections.some((s) => (s.channel?.floor ?? 0) < 0),
        game.id,
      ).toBe(true);
    }
    expect(level('3-5').scenery.sections.some((s) => (s.lakes?.level ?? 0) < 0)).toBe(true);
  });

  it('P09-R03: the concrete gives way to grass from 3-1 to 3-5', () => {
    for (const id of ['3-1', '3-2', '3-3'])
      expect(cover(level(id), 'paved'), id).toBeGreaterThan(cover(level(id), 'lush'));
    for (const id of ['3-4', '3-5'])
      expect(cover(level(id), 'lush'), id).toBeGreaterThan(cover(level(id), 'paved'));
    expect(increasing(WORLD_3.map((l) => -cover(l, 'paved')))).toBe(true);
    expect(increasing(WORLD_3.map((l) => cover(l, 'lush')))).toBe(true);
  });

  it('P09-R03: from the factories to the homes: no industry in 3-4 and 3-5, garden villages only at the end', () => {
    const groups = (id: string) => new Set(level(id).scenery.sections.flatMap((s) => s.groups));
    const G = WORLD_3_GROUPS;
    const industry = [G.heavyIndustry, G.industrial, G.docks, G.workshops];
    expect(groups('3-1').has(G.heavyIndustry)).toBe(true);
    for (const id of ['3-4', '3-5'])
      for (const g of industry) expect(groups(id).has(g), `${id} ${g}`).toBe(false);
    for (const g of [G.suburbs, G.villages]) expect(groups('3-1').has(g), g).toBe(false);
    expect(level('3-5').scenery.sections.at(-1)?.groups).toEqual([G.villages]);
  });

  it('P09-R03: props and buildings go up from 3-1 to 3-5, and from each first half to the second (fixed seed)', () => {
    const counts = WORLD_3.map((l) => propCounts(l, PLANTS));
    expect(increasing(counts.map((c) => c.all))).toBe(true);
    expect(increasing(counts.map((c) => c.buildings))).toBe(true);
    for (const [i, c] of counts.entries())
      expect(c.secondHalf, at(WORLD_3, i).id).toBeGreaterThan(c.firstHalf);
  });

  it('P09-R03: each level begins on the ground the previous one ended on, 3-1 on 2-5’s; slow transitions', () => {
    const levels = [level('2-5'), ...WORLD_3];
    for (const [i, next] of levels.slice(1).entries()) {
      const { sections } = at(levels, i).scenery;
      const [last, first] = [at(sections, sections.length - 1), at(next.scenery.sections, 0)];
      expect(first.relief, next.id).toEqual(last.relief);
      expect(first.surface, next.id).toEqual(last.surface);
      expect(first.streets, next.id).toEqual(last.streets);
      if (i > 0) expect(first.groups, next.id).toEqual(last.groups);
      if (i > 0) expect(first.channel, next.id).toEqual(last.channel);
    }
    for (const game of WORLD_3) {
      expect(game.scenery.transition, game.id).toBe(TRANSITION);
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
    // No green canopy tint since the rework (reviewer, 2026-10-27).
    expect(script('3-2').start).toEqual({ timeOfDay: 'midday', clouds: [0.5, 0.3] });
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

  it('P09-R07, P05-R24: each wave script uses only its level’s kinds; 3-2 to 3-5 use all eleven first kinds; a veteran kind more at each level', () => {
    const kinds = (id: string) => [...new Set(level(id).waves.map((w) => w.kind))].sort();
    const veterans = (n: number) => VETERAN_KINDS.slice(0, n).map((k) => k.id);
    expect(kinds('3-1')).toEqual(
      ['gnat', 'hornet', 'scout', 'splitter', 'strafer', 'weaver', ...veterans(1)].sort(),
    );
    // Wasps, then Mortars, Minelayers, Mantises and Phantoms.
    const order = ['wasp', 'mortar', 'minelayer', 'mantis', 'phantom'];
    for (const [i, id] of ['3-2', '3-3', '3-4', '3-5'].entries())
      expect(kinds(id), id).toEqual(
        [...FIRST_KINDS.map((k) => k.id), ...order.slice(0, i + 2)].sort(),
      );
    // No elite kind before World 4.
    for (const game of WORLD_3)
      expect(kinds(game.id).some((k) => ELITE_KINDS.some((e) => e.id === k))).toBe(false);
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

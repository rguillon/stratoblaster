import { describe, expect, it } from 'vitest';
import type { GameLevel } from '../../../../src/core/content/game-level';
import { levelLength, type TerrainSection } from '../../../../src/core/scenery/scenery-level';
import { QUIET_BEFORE_BOSS } from '../../../../src/game/config/world-1/bosses';
import {
  ASH_BROWN,
  ASH_LIGHT,
  ASH_PINK,
  ERUPTION_RED,
  FURNACE_GLOW,
  LAVA_GLOW,
  SMOKE_HAZE,
} from '../../../../src/game/config/world-4/looks';
import { WORLD_4_FLOATING, WORLD_4_PROPS } from '../../../../src/game/config/world-4/props';
import { PLAN_4_1 } from '../../../../src/game/config/world-4/waves';
import { composeBeats } from '../../../../src/game/config/world-2/waves';
import { FIRST_KINDS } from '../../../../src/game/sim/enemy-kinds';
import { ELITE_KINDS } from '../../../../src/game/sim/elite-kinds';
import { VETERAN_KINDS } from '../../../../src/game/sim/veteran-kinds';
import { LEVELS } from '../../../../src/game/sim/levels';
import { WORLD_3 } from '../../../../src/game/sim/world-3';
import { WORLD_4 } from '../../../../src/game/sim/world-4';
import { SCENERY_BINDINGS } from '../../../../src/game/view/scenery-bindings';
import { at } from '../../../helpers/at';
import { buildingCount, levelMetrics, seaShare } from '../../../helpers/level-metrics';

const level = (id: string): GameLevel => {
  const found = [...WORLD_3, ...WORLD_4].find((l) => l.id === id);
  if (!found) throw new Error(`no level ${id}`);
  return found;
};

const increasing = (values: readonly number[]) =>
  values.every((v, i) => i === 0 || v > (values[i - 1] ?? 0));

const METRICS = WORLD_4.map(levelMetrics);
const lookOf = (id: string) => SCENERY_BINDINGS.looks[level(id).scenery.id];

/** A sea section: a coast, or open water whose ground lies under the water level. */
const isSea = (s: TerrainSection) => s.shore !== undefined || s.relief.base < 0;

/** Share of a level's ground covered by lava: under its liquid level, if its look makes it lava. */
const lavaShare = (id: string) => (lookOf(id)?.sea.lava ? seaShare(level(id)) : 0);

/** Plants, rocks and what floats on the sea: not buildings. */
const SCATTER = new Set([
  ...WORLD_4_PROPS.trees.map((t) => t.id),
  ...WORLD_4_FLOATING.kinds.map((k) => k.id),
]);

const ash = (strength: number) => ({ kind: 'ash', strength });
const embers = (strength: number) => ({ kind: 'embers', strength });

describe('World 4', () => {
  it('P10-R01: five playable levels, 4-1 to 4-5, all unlocked, the last row of the grid', () => {
    expect(WORLD_4.map((l) => l.id)).toEqual(['4-1', '4-2', '4-3', '4-4', '4-5']);
    const row = LEVELS.levels.filter((l) => l.world === 4);
    expect(row.map((l) => [l.id, l.unlocked])).toEqual(WORLD_4.map((l) => [l.id, true]));
    // 4-1 comes right after 3-5 in the grid (completing 3-5 highlights it); 4-5 is the last
    // level, so it stays highlighted.
    const ids = LEVELS.levels.map((l) => l.id);
    expect(ids.indexOf('4-1')).toBe(ids.indexOf('3-5') + 1);
    expect(ids.at(-1)).toBe('4-5');
    expect(LEVELS.levels.every((l) => l.unlocked)).toBe(true);
  });

  it('P10-R02: each level lasts about 5 minutes (290 to 310 s) at its ground speed', () => {
    for (const game of WORLD_4) {
      const seconds = levelLength(game.scenery) / game.scenery.scrollSpeed;
      expect(seconds, game.id).toBeGreaterThanOrEqual(290);
      expect(seconds, game.id).toBeLessThanOrEqual(310);
    }
    expect(WORLD_4.map((l) => l.scenery.scrollSpeed)).toEqual([70, 65, 60, 55, 55]);
  });

  it('P10-R03: 4-1 is mostly sea (≥ 70 %); 4-2 to 4-5 have no sea section', () => {
    const first = at(WORLD_4, 0);
    const seconds = (sections: readonly TerrainSection[]) =>
      sections.reduce((sum, s) => sum + s.seconds, 0);
    const sections = first.scenery.sections;
    expect(seconds(sections.filter(isSea)) / seconds(sections)).toBeGreaterThanOrEqual(0.7);
    expect(seaShare(first)).toBeGreaterThanOrEqual(0.7);
    expect(lookOf('4-1')?.sea.lava).toBeUndefined();
    for (const game of WORLD_4.slice(1))
      expect(game.scenery.sections.filter(isSea), game.id).toEqual([]);
  });

  it('P10-R03: no lava in 4-1 and 4-2; the lava’s share of the ground goes up from 4-3 to 4-5', () => {
    expect(lavaShare('4-1')).toBe(0);
    expect(lavaShare('4-2')).toBe(0);
    expect(seaShare(level('4-2'))).toBe(0);
    const shares = ['4-3', '4-4', '4-5'].map(lavaShare);
    expect(increasing(shares)).toBe(true);
    // About 10 %, 20 % and 35 % (tunable values).
    expect(at(shares, 0)).toBeGreaterThan(0.05);
    expect(at(shares, 2)).toBeGreaterThan(0.25);
  });

  it('P10-R03: the number of buildings goes up from 4-1 to 4-4 (fixed seed)', () => {
    const counts = WORLD_4.slice(0, 4).map((l) => buildingCount(l, SCATTER));
    expect(increasing(counts)).toBe(true);
  });

  it('P10-R03: each level begins on the kind of ground the previous one ended on', () => {
    const first = (id: string) => at(level(id).scenery.sections, 0);
    const last = (id: string) => level(id).scenery.sections.at(-1);
    for (const [prev, next] of [
      ['4-1', '4-2'],
      ['4-2', '4-3'],
      ['4-3', '4-4'],
      ['4-4', '4-5'],
    ] as const) {
      expect(first(next).relief, next).toEqual(last(prev)?.relief);
    }
    // 4-5 ends on the magma lake, which the final fight's runout repeats.
    expect(lavaShare('4-5')).toBeGreaterThan(lavaShare('4-4'));
  });

  /** The sky script of level `id`; fails when it has none. */
  const script = (id: string) => {
    const found = lookOf(id)?.atmosphere;
    if (!found) throw new Error(`no sky script for ${id}`);
    return found;
  };
  const changes = (id: string) => script(id).changes ?? [];

  it('P10-R04: 4-1 a red dawn behind a smoke haze; 4-2 an ash-dark midday with falling ash', () => {
    expect(script('4-1').start).toEqual({
      timeOfDay: 'dawn',
      clouds: [0.4, 0.3],
      cloudTint: ASH_PINK,
      mist: SMOKE_HAZE,
    });
    expect(changes('4-1')).toEqual([]);
    expect(script('4-2').start).toEqual({
      timeOfDay: 'midday',
      clouds: [0.9, 0.9],
      cloudTint: ASH_BROWN,
      tint: ASH_LIGHT,
      weather: ash(0.5),
    });
    expect(changes('4-2')).toEqual([]);
    // Brown-grey clouds; a dim, yellowish light.
    expect(ASH_BROWN[2]).toBeLessThan(ASH_BROWN[0]);
    expect(ASH_LIGHT[2]).toBeLessThan(ASH_LIGHT[1]);
  });

  it('P10-R04: 4-3 a dusk giving way to the lava’s glow, with embers', () => {
    expect(script('4-3').start).toEqual({
      timeOfDay: 'dusk',
      clouds: [0.5, 0.4],
      storm: 0.5,
      underglow: { color: LAVA_GLOW, strength: 0.25 },
      weather: embers(0.4),
    });
    expect(changes('4-3').map((c) => [c.from, c.to, c.look])).toEqual([
      [
        60,
        280,
        {
          timeOfDay: 'night',
          clouds: [0.5, 0.4],
          storm: 0.5,
          underglow: { color: LAVA_GLOW, strength: 0.8 },
          weather: embers(0.4),
        },
      ],
    ]);
  });

  it('P10-R04: 4-4 a furnace-lit night with ash and embers; 4-5 the eruption growing to the final boss', () => {
    expect(script('4-4').start).toEqual({
      timeOfDay: 'night',
      clouds: [0.6, 0.5],
      storm: 0.6,
      underglow: { color: FURNACE_GLOW, strength: 0.7 },
      weather: ash(0.3),
      secondWeather: embers(0.3),
    });
    expect(changes('4-4')).toEqual([]);
    expect(script('4-5').start).toEqual({
      timeOfDay: 'night',
      clouds: [0.7, 0.6],
      underglow: { color: ERUPTION_RED, strength: 0.6 },
      weather: embers(0.6),
    });
    // The final boss comes at 300 s of the level, the ground ahead of it after the mini boss's
    // chase: the eruption is at its strongest by then.
    expect(changes('4-5').map((c) => [c.from, c.to, c.look])).toEqual([
      [
        180,
        300,
        {
          timeOfDay: 'night',
          clouds: [0.7, 0.6],
          underglow: { color: ERUPTION_RED, strength: 1 },
          weather: embers(1),
        },
      ],
    ]);
  });

  it('P10-R05: the lava levels’ liquid is lava, flowing down the screen', () => {
    for (const id of ['4-3', '4-4', '4-5']) {
      const sea = lookOf(id)?.sea;
      expect(sea?.lava, id).toBeDefined();
      expect(sea?.drift[1], id).toBeGreaterThan(0);
      expect(level(id).scenery.sea, id).toBeDefined();
    }
  });

  it('P10-R09, P05-R24: each wave script uses all eleven first kinds and the five veterans; the elites come in level by level', () => {
    const kinds = (id: string) => [...new Set(level(id).waves.map((w) => w.kind))].sort();
    const first = FIRST_KINDS.map((k) => k.id);
    const veterans = VETERAN_KINDS.map((k) => k.id);
    // Hydras and Orbiters first, then Scissors, Hives and Juggernauts.
    const order = ['hydra', 'orbiter', 'scissor', 'hive', 'juggernaut'];
    const elites = (n: number) => order.slice(0, n);
    expect([...order].sort()).toEqual(ELITE_KINDS.map((k) => k.id).sort());
    const expected = { '4-1': 2, '4-2': 3, '4-3': 4, '4-4': 5, '4-5': 5 };
    for (const [id, n] of Object.entries(expected))
      expect(kinds(id), id).toEqual([...first, ...veterans, ...elites(n)].sort());
    const count = (id: string, kind: string) =>
      level(id).waves.filter((w) => w.kind === kind).length;
    const leads: [string, string[]][] = [
      ['4-1', ['weaver', 'strafer']],
      ['4-2', ['splitter', 'spinner']],
      ['4-3', ['lancer', 'rocketeer']],
      ['4-4', ['carrier', 'bulwark']],
    ];
    for (const [id, lead] of leads) {
      const own = lead.reduce((sum, kind) => sum + count(id, kind), 0);
      const elsewhere = lead.reduce((sum, kind) => sum + count('3-3', kind), 0);
      expect(own, id).toBeGreaterThan(elsewhere * 0.9);
    }
  });

  it('P10-R09: the waves are deterministic: same distances, same enemies, twice', () => {
    expect(composeBeats(PLAN_4_1)).toEqual(composeBeats(PLAN_4_1));
    expect(levelMetrics(level('4-2'))).toEqual(METRICS[1]);
  });

  it('P10-R10: enemies, HP per minute and the peak on screen go up strictly from 4-1 to 4-5', () => {
    expect(increasing(METRICS.map((m) => m.perMinute))).toBe(true);
    expect(increasing(METRICS.map((m) => m.healthPerMinute))).toBe(true);
    expect(increasing(METRICS.map((m) => m.peak))).toBe(true);
    const factors = WORLD_4.map((l) => l.difficulty);
    expect(factors.map((f) => f.bulletSpeed)).toEqual([1.1, 1.15, 1.2, 1.3, 1.35]);
    expect(factors.map((f) => f.fireRate)).toEqual([1.1, 1.15, 1.2, 1.3, 1.35]);
  });

  it('P10-R10: 4-1 is at least as hard as 3-3, and 4-5 harder than 3-5', () => {
    const [w33, w35] = [levelMetrics(level('3-3')), levelMetrics(level('3-5'))];
    const [w41, w45] = [at(METRICS, 0), at(METRICS, 4)];
    expect(w41.perMinute).toBeGreaterThanOrEqual(w33.perMinute);
    expect(w41.healthPerMinute).toBeGreaterThanOrEqual(w33.healthPerMinute);
    expect(w41.peak).toBeGreaterThanOrEqual(w33.peak);
    expect(w45.perMinute).toBeGreaterThan(w35.perMinute);
    expect(w45.healthPerMinute).toBeGreaterThan(w35.healthPerMinute);
    expect(w45.peak).toBeGreaterThan(w35.peak);
    const d = (id: string) => level(id).difficulty;
    expect(d('4-1').bulletSpeed).toBeGreaterThanOrEqual(d('3-3').bulletSpeed);
    expect(d('4-1').fireRate).toBeGreaterThanOrEqual(d('3-3').fireRate);
    expect(d('4-5').bulletSpeed).toBeGreaterThan(d('3-5').bulletSpeed);
    expect(d('4-5').fireRate).toBeGreaterThan(d('3-5').fireRate);
  });

  it('P10-R10: in each level, the second half has more enemy HP than the first', () => {
    for (const [i, m] of METRICS.entries())
      expect(m.secondHalf, WORLD_4[i]?.id).toBeGreaterThan(m.firstHalf);
  });

  it('P10-R11: a mini boss at the middle of each level and a final boss at its end, no wave before them', () => {
    for (const game of WORLD_4) {
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

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
import { TRANSITION } from '../../../../src/game/config/world-2/scenery';
import { WORLD_4_GROUPS, WORLD_4_PROPS } from '../../../../src/game/config/world-4/city-props';
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
import { PROP_MODELS } from '../../../../src/game/view/props/prop-models';
import { levelMetrics, placedProps, waterShares } from '../../../helpers/level-metrics';

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

/** Plants: not buildings. */
const PLANTS = new Set(WORLD_4_PROPS.trees.map((t) => t.id));

/** How much of a level a ground cover covers: its shares weighted by the sections' time. */
const cover = (game: GameLevel, kind: 'lush' | 'paved') =>
  game.scenery.sections.reduce((sum, s) => sum + s.seconds * (s.surface?.[kind] ?? 0), 0);

/** The top of a prop model, at scale 1. */
const top = (id: string) =>
  Math.max(...(PROP_MODELS[id]?.().structure.positions ?? [0]).filter((_, i) => i % 3 === 1));

/**
 * The mean height of the buildings placed over a level (its own seed), over the whole level and
 * over each half.
 */
function buildingHeights(game: GameLevel) {
  const { placed, length } = placedProps(game);
  const buildings = placed.filter((p) => !PLANTS.has(p.kind));
  const tops = new Map<string, number>();
  const height = (kind: string) => tops.get(kind) ?? tops.set(kind, top(kind)).get(kind) ?? 0;
  const mean = (ps: typeof buildings) =>
    ps.reduce((sum, p) => sum + height(p.kind) * p.scale, 0) / ps.length;
  return {
    all: mean(buildings),
    firstHalf: mean(buildings.filter((p) => p.z < length / 2)),
    secondHalf: mean(buildings.filter((p) => p.z >= length / 2)),
    tallest: Math.max(...buildings.map((p) => height(p.kind) * p.scale)),
  };
}

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

  it('P10-R03: no sea, no lava and no river in World 4: only buildings and roads (reviewer, 2026-10-28)', () => {
    for (const game of WORLD_4) {
      expect(game.scenery.sections.filter(isSea), game.id).toEqual([]);
      expect(lookOf(game.id)?.sea.lava, game.id).toBeUndefined();
      expect(game.scenery.props.floating, game.id).toBeUndefined();
      expect(waterShares(game, isSea).sea, game.id).toBe(0);
      expect(waterShares(game, isSea).inland, game.id).toBe(0);
      for (const section of game.scenery.sections) {
        expect(section.channel, section.name).toBeUndefined();
        expect(section.treeDensity, section.name).toBe(0);
      }
    }
  });

  it('no sea plane under the ground, where it never showed (reviewer, 2026-10-28)', () => {
    for (const game of WORLD_4) expect(game.scenery.sea, game.id).toBeUndefined();
  });

  it('the flat ground casts no shadows (reviewer, 2026-10-28)', () => {
    for (const game of WORLD_4) expect(lookOf(game.id)?.terrain.castsShadows, game.id).toBe(false);
  });

  it('P10-R03: concrete everywhere, no grass (reviewer, 2026-10-28)', () => {
    for (const game of WORLD_4) expect(cover(game, 'lush'), game.id).toBe(0);
  });

  it('P10-R03: from the houses to the skyscrapers: no tower in 4-1 and 4-2, no skyscraper before 4-4, skyscrapers only at the end', () => {
    const G = WORLD_4_GROUPS;
    const groups = (id: string) => new Set(level(id).scenery.sections.flatMap((s) => s.groups));
    expect(at(level('4-1').scenery.sections, 0).groups).toEqual([G.villages]);
    for (const id of ['4-1', '4-2'])
      for (const g of [G.towers, G.skyscrapers, G.downtown])
        expect(groups(id).has(g), `${id} ${g}`).toBe(false);
    expect(groups('4-3').has(G.skyscrapers)).toBe(false);
    expect(groups('4-4').has(G.skyscrapers)).toBe(true);
    expect(level('4-5').scenery.sections.at(-1)?.groups).toEqual([G.downtown]);
    const downtown = WORLD_4_PROPS.groups.find((g) => g.id === G.downtown)?.kinds ?? [];
    expect(downtown.every((k) => k.id.startsWith('skyscraper-'))).toBe(true);
  });

  it('P10-R03: the buildings grow taller from 4-1 to 4-5, and from each first half to the second (fixed seed)', () => {
    const heights = WORLD_4.map(buildingHeights);
    expect(increasing([buildingHeights(level('3-5')).all, ...heights.map((h) => h.all)])).toBe(
      true,
    );
    for (const [i, h] of heights.entries())
      expect(h.secondHalf, at(WORLD_4, i).id).toBeGreaterThan(h.firstHalf);
    // The skyscrapers stand at least twice as tall as Level Zero's tallest city tower (86.8 high
    // at scale 0.5; the tower was removed in phase 15).
    expect(at(heights, 4).tallest).toBeGreaterThan(2 * 86.8 * 0.5);
  });

  it('P10-R03: each level begins on the ground the previous one ended on, 4-1 on 3-5’s; slow transitions', () => {
    const levels = [level('3-5'), ...WORLD_4];
    for (const [i, next] of levels.slice(1).entries()) {
      const { sections } = at(levels, i).scenery;
      const [last, first] = [at(sections, sections.length - 1), at(next.scenery.sections, 0)];
      expect(first.streets, next.id).toEqual(last.streets);
      expect(first.groups, next.id).toEqual(last.groups);
      // 3-5 has grass and a river; World 4 is all concrete (reviewer, 2026-10-28).
      if (i === 0) continue;
      expect(first.relief, next.id).toEqual(last.relief);
      expect(first.surface, next.id).toEqual(last.surface);
    }
    for (const game of WORLD_4) {
      expect(game.scenery.transition, game.id).toBe(TRANSITION);
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
  const changes = (id: string) => script(id).changes ?? [];

  it('World 4 is lit as brightly as midday allows, its windows and cars on (reviewer, 2026-10-28)', () => {
    for (const game of WORLD_4) {
      const sky = script(game.id);
      for (const look of [sky.start, ...(sky.changes ?? []).map((c) => c.look)])
        expect(look, game.id).toMatchObject({
          timeOfDay: 'midday',
          groundLights: 1.5,
          brightness: 1.3,
        });
    }
  });

  it('P10-R04: 4-1 a red dawn behind a smoke haze; 4-2 an ash-dark midday with falling ash', () => {
    expect(script('4-1').start).toMatchObject({
      timeOfDay: 'midday',
      clouds: [0, 0],
      cloudTint: ASH_PINK,
      mist: SMOKE_HAZE,
    });
    expect(changes('4-1')).toEqual([]);
    expect(script('4-2').start).toMatchObject({
      timeOfDay: 'midday',
      clouds: [0, 0],
      cloudTint: ASH_BROWN,
      tint: ASH_LIGHT,
      weather: ash(0.5),
    });
    expect(changes('4-2')).toEqual([]);
    // No clouds (reviewer, 2026-10-28); a dim, yellowish light.
    expect(ASH_BROWN[2]).toBeLessThan(ASH_BROWN[0]);
    expect(ASH_LIGHT[2]).toBeLessThan(ASH_LIGHT[1]);
  });

  it('P10-R04: 4-3 a dusk giving way to the city’s glow, with embers', () => {
    expect(script('4-3').start).toMatchObject({
      timeOfDay: 'midday',
      clouds: [0, 0],
      storm: 0.5,
      underglow: { color: LAVA_GLOW, strength: 0.25 },
      weather: embers(0.4),
    });
    expect(changes('4-3').map((c) => [c.from, c.to, c.look])).toMatchObject([
      [
        60,
        280,
        {
          timeOfDay: 'midday',
          clouds: [0, 0],
          storm: 0.5,
          underglow: { color: LAVA_GLOW, strength: 0.8 },
          weather: embers(0.4),
        },
      ],
    ]);
  });

  it('P10-R04: 4-4 a night lit by the towers, with ash and embers; 4-5 the eruption growing to the final boss', () => {
    expect(script('4-4').start).toMatchObject({
      timeOfDay: 'midday',
      clouds: [0, 0],
      storm: 0.6,
      underglow: { color: FURNACE_GLOW, strength: 0.7 },
      weather: ash(0.3),
      secondWeather: embers(0.3),
    });
    expect(changes('4-4')).toEqual([]);
    expect(script('4-5').start).toMatchObject({
      timeOfDay: 'midday',
      clouds: [0, 0],
      underglow: { color: ERUPTION_RED, strength: 0.6 },
      weather: embers(0.6),
    });
    // The final boss comes at 300 s of the level, the ground ahead of it after the mini boss's
    // chase: the eruption is at its strongest by then.
    expect(changes('4-5').map((c) => [c.from, c.to, c.look])).toMatchObject([
      [
        180,
        300,
        {
          timeOfDay: 'midday',
          clouds: [0, 0],
          underglow: { color: ERUPTION_RED, strength: 1 },
          weather: embers(1),
        },
      ],
    ]);
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

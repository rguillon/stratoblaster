import { describe, expect, it } from 'vitest';
import type { GameLevel } from '../../../../src/core/content/game-level';
import { HeightField } from '../../../../src/core/scenery/height-field';
import { PropPlacer } from '../../../../src/core/scenery/prop-placement';
import { levelRoads } from '../../../../src/core/scenery/road-network';
import { levelLength } from '../../../../src/core/scenery/scenery-level';
import { LevelRun } from '../../../../src/core/systems/level-run';
import { WORLD_1_PROPS } from '../../../../src/game/config/world-1/props';
import { PLAYER_WEAPONS } from '../../../../src/game/config/player-weapons';
import { QUIET_BEFORE_BOSS } from '../../../../src/game/config/world-1/bosses';
import {
  WAVES_1_1,
  WORLD_1_FILLERS,
  fill,
  quietBefore,
  waveScript,
} from '../../../../src/game/config/world-1/waves';
import { ENEMY_KINDS, FIRST_KINDS } from '../../../../src/game/sim/enemy-kinds';
import { LEVELS } from '../../../../src/game/sim/levels';
import { WORLD_1 } from '../../../../src/game/sim/world-1';
import { SCENERY_BINDINGS } from '../../../../src/game/view/scenery-bindings';
import { at } from '../../../helpers/at';

const level = (id: string): GameLevel => {
  const found = WORLD_1.find((l) => l.id === id);
  if (!found) throw new Error(`no level ${id}`);
  return found;
};

/** Whether every value is greater than the one before it. */
const increasing = (values: readonly number[]) =>
  values.every((v, i) => i === 0 || v > (values[i - 1] ?? 0));

/**
 * What a level throws at the player, measured by playing it through without shooting (so the
 * numbers do not depend on the player): enemies spawned, their total health, the most on screen
 * at once, and the health spawned in each half of the level. Its waves only: its bosses (P07),
 * which would wait to be destroyed, are left out.
 */
function measure(game: GameLevel) {
  const weapon = PLAYER_WEAPONS[0];
  const run = new LevelRun({
    screen: { width: 480, height: 640 },
    level: { ...game, bosses: [] },
    kinds: ENEMY_KINDS,
    weapon,
    weaponLevel: 1,
    ship: { start: { x: 240, y: 90 }, maxSpeed: 100, accelerationSeconds: 0.08, muzzleOffset: 20 },
    bounds: { minY: 30, maxY: 440, centerX: 240, halfWidthAt: () => 140 },
    cullMargin: 80,
    maxEnemyAge: 40,
    endWait: 10,
    seed: 606,
  });
  let [peak, firstHalf] = [0, -1];
  const still = { move: { x: 0, y: 0 }, fire: false };
  while (run.phase !== 'complete') {
    run.step(1 / 60, still);
    peak = Math.max(peak, run.enemies.onScreen);
    if (firstHalf < 0 && run.track.time >= run.track.duration / 2) {
      firstHalf = run.enemies.spawnedHealth;
    }
  }
  const { spawned, spawnedHealth } = run.enemies;
  return { spawned, health: spawnedHealth, peak, firstHalf, secondHalf: spawnedHealth - firstHalf };
}

const METRICS = WORLD_1.map(measure);

/** Share of the ground under the playfield that is under the sea. */
function seaShare(game: GameLevel): number {
  const { scenery } = game;
  if (!scenery.sea) return 0;
  const field = new HeightField(scenery);
  let [wet, all] = [0, 0];
  for (let z = 0; z < field.length; z += 20) {
    for (let x = -240; x <= 240; x += 20) {
      all++;
      if (field.height(x, z) < scenery.sea.level) wet++;
    }
  }
  return wet / all;
}

const PLANTS = new Set([
  'dead-tree',
  'forked-tree',
  'palm-tree',
  'dry-bush',
  'cactus',
  'bush',
  'broadleaf-tree',
  'conifer',
]);

/** Props placed over the whole level with its own seed: all, buildings, and in each half. */
function props(game: GameLevel) {
  const { scenery } = game;
  const field = new HeightField(scenery);
  const placer = new PropPlacer(
    field,
    scenery.props,
    scenery.seed,
    levelRoads(field, scenery.roads, scenery.seed),
  );
  const placed = placer.place({ xMin: -400, xMax: 400, zMin: 0, zMax: field.length });
  const firstHalf = placed.filter((p) => p.z < field.length / 2).length;
  return {
    all: placed.length,
    buildings: placed.filter((p) => !PLANTS.has(p.kind)).length,
    firstHalf,
    secondHalf: placed.length - firstHalf,
  };
}

/** How much of a level each ground cover covers: its shares weighted by the sections' time. */
function cover(game: GameLevel, kind: 'lush' | 'sandy' | 'paved'): number {
  return game.scenery.sections.reduce((sum, s) => sum + s.seconds * (s.surface?.[kind] ?? 0), 0);
}

describe('World 1', () => {
  it('P06-R01: has five playable levels, 1-1 to 1-5, all unlocked in the level select', () => {
    expect(WORLD_1.map((l) => l.id)).toEqual(['1-1', '1-2', '1-3', '1-4', '1-5']);
    const row = LEVELS.levels.filter((l) => l.world === 1);
    expect(row.map((l) => [l.id, l.unlocked])).toEqual(WORLD_1.map((l) => [l.id, true]));
  });

  it('P06-R04: each level lasts about 4 minutes (230 to 250 s) at its ground speed', () => {
    for (const game of WORLD_1) {
      const seconds = levelLength(game.scenery) / game.scenery.scrollSpeed;
      expect(seconds, game.id).toBeGreaterThanOrEqual(230);
      expect(seconds, game.id).toBeLessThanOrEqual(250);
    }
    expect(WORLD_1.map((l) => l.scenery.scrollSpeed)).toEqual([70, 65, 60, 60, 60]);
  });

  it('P06-R05: the share over the sea goes down from 1-1 to 1-3; 1-3 to 1-5 have no sea', () => {
    const shares = WORLD_1.map(seaShare);
    expect(shares[0]).toBeGreaterThanOrEqual(0.8);
    expect(shares[1]).toBeLessThanOrEqual(0.5);
    expect(increasing(shares.slice(0, 3).map((s) => -s))).toBe(true);
    for (const id of ['1-3', '1-4', '1-5']) {
      const { scenery } = level(id);
      expect(scenery.sea, id).toBeUndefined();
      expect(
        scenery.sections.some((s) => s.shore),
        id,
      ).toBe(false);
    }
  });

  it('P06-R05: 1-1 is sea until its last 30 s, where the first coast comes', () => {
    const sections = level('1-1').scenery.sections;
    const coast = sections.findIndex((s) => s.shore);
    expect(coast).toBe(sections.length - 1);
    expect(sections[coast]?.seconds).toBe(30);
    expect(sections.slice(0, coast).every((s) => s.relief.base < 0)).toBe(true);
  });

  it('P06-R05: grass covers 1-2 and 1-3 the most, sand covers 1-4 and 1-5 more than grass', () => {
    for (const id of ['1-2', '1-3']) {
      expect(cover(level(id), 'lush'), id).toBeGreaterThan(cover(level(id), 'sandy'));
      expect(cover(level(id), 'lush'), id).toBeGreaterThan(cover(level(id), 'paved'));
    }
    for (const id of ['1-4', '1-5']) {
      expect(cover(level(id), 'sandy'), id).toBeGreaterThan(cover(level(id), 'lush'));
    }
  });

  it('P06-R05: props and buildings go up from 1-1 to 1-5, and from each first half to the second (fixed seed)', () => {
    const counts = WORLD_1.map(props);
    expect(increasing(counts.map((c) => c.all))).toBe(true);
    expect(increasing(counts.map((c) => c.buildings))).toBe(true);
    for (const [i, c] of counts.entries()) {
      expect(c.secondHalf, at(WORLD_1, i).id).toBeGreaterThan(c.firstHalf);
    }
  });

  it('P06-R05: each level begins on the kind of ground the previous one ended on', () => {
    for (const [i, next] of WORLD_1.slice(1).entries()) {
      const { sections } = at(WORLD_1, i).scenery;
      const [last, first] = [at(sections, sections.length - 1), at(next.scenery.sections, 0)];
      expect(first.relief, next.id).toEqual(last.relief);
      expect(first.surface, next.id).toEqual(last.surface);
      expect(first.shore, next.id).toEqual(last.shore);
    }
    // 1-2 starts on the green coast where 1-1 ended, 1-3 on the farmland, 1-4 on the dry
    // grassland, and 1-5 on the desert outskirts; it ends on the sand, in a desert town.
    expect(at(level('1-2').scenery.sections, 0).shore).toBeDefined();
    expect(at(level('1-3').scenery.sections, 0).surface).toEqual({ lush: 1 });
    expect(at(level('1-4').scenery.sections, 0).surface).toEqual({ lush: 0.2 });
    expect(at(level('1-5').scenery.sections, 0).groups).toContain('desert-homes');
    const end = level('1-5').scenery.sections.at(-1);
    expect(end?.groups).toEqual(['desert-homes']);
    expect(end?.surface?.sandy).toBeGreaterThan(0.5);
  });

  it('P06-R06: the green levels have farms and villages; the dry ones sand, dunes and desert homes', () => {
    for (const id of ['1-2', '1-3']) {
      const groups = level(id).scenery.sections.flatMap((s) => s.groups ?? []);
      expect(groups, id).toEqual(expect.arrayContaining(['farms', 'villages']));
    }
    for (const id of ['1-4', '1-5']) {
      const { sections } = level(id).scenery;
      expect(
        sections.some((s) => s.groups?.includes('desert-homes')),
        id,
      ).toBe(true);
    }
    expect(level('1-4').scenery.sections.some((s) => s.dunes)).toBe(true);
    // Reviewer, 2026-10-27: no factory and no city in World 1, they are for other worlds.
    const groups = WORLD_1.flatMap((l) => l.scenery.sections.flatMap((s) => s.groups ?? []));
    for (const kept of ['industrial', 'heavy-industry', 'city']) expect(groups).not.toContain(kept);
    expect(level('1-4').scenery.sections.some((s) => s.channel)).toBe(true);
    expect(WORLD_1.every((l) => l.scenery.props === WORLD_1_PROPS)).toBe(true);
    for (const game of WORLD_1) {
      const look = SCENERY_BINDINGS.looks[game.scenery.id];
      expect(look?.terrain.sand, game.id).toBeDefined();
      expect(look?.terrain.lush, game.id).toBe(SCENERY_BINDINGS.looks['world-1-1']?.terrain.lush);
    }
  });

  it('P06-R10: the sun is highest in 1-1 (midday) and lower in each level after it', () => {
    const elevations = WORLD_1.map(
      (l) => SCENERY_BINDINGS.looks[l.scenery.id]?.sun.elevationDeg ?? 0,
    );
    expect(at(elevations, 0)).toBeGreaterThanOrEqual(65);
    expect(increasing(elevations.map((e) => -e))).toBe(true);
  });

  it('P06-R07: each level only uses the kinds it introduces and those of the levels before', () => {
    const kinds = (id: string) => new Set(level(id).waves.map((w) => w.kind));
    const sorted = (id: string) => [...kinds(id)].sort();
    expect(sorted('1-1')).toEqual(['gnat', 'hornet', 'scout', 'strafer']);
    expect(sorted('1-2')).toEqual([...sorted('1-1'), 'splitter', 'weaver'].sort());
    expect(sorted('1-3')).toEqual([...sorted('1-2'), 'carrier', 'spinner'].sort());
    expect(sorted('1-4')).toEqual([...sorted('1-3'), 'lancer', 'rocketeer'].sort());
    expect(sorted('1-5')).toEqual(FIRST_KINDS.map((k) => k.id).sort());
  });

  it('P06-R07: waves are triggered by distance, the same every time', () => {
    const speed = level('1-1').scenery.scrollSpeed;
    const filler = WORLD_1_FILLERS['1-1'];
    if (!filler) throw new Error('no filler for 1-1');
    const length = levelLength(level('1-1').scenery);
    const script = waveScript(speed, fill(WAVES_1_1, filler));
    expect(level('1-1').waves).toEqual(
      quietBefore(script, [length / 2, length], QUIET_BEFORE_BOSS * speed),
    );
    expect(level('1-1').waves[0]?.at).toBe(at(WAVES_1_1, 0)[0] * speed);
    expect(measure(level('1-2'))).toEqual(METRICS[1]);
  });

  it('P06-R08: enemy count, total enemy HP and peak on screen go up strictly from 1-1 to 1-5', () => {
    expect(increasing(METRICS.map((m) => m.spawned))).toBe(true);
    expect(increasing(METRICS.map((m) => m.health))).toBe(true);
    expect(increasing(METRICS.map((m) => m.peak))).toBe(true);
    // Tunable values, with the density raised by 50 % (D-044) and the lulls filled (D-051) in
    // review: about 280 enemies in 1-1, the fewest at once; at least 15 at once in 1-5.
    expect(METRICS[0]?.spawned).toBeLessThanOrEqual(300);
    expect(METRICS[0]?.peak).toBeLessThanOrEqual(18);
    expect(METRICS[4]?.peak).toBeGreaterThanOrEqual(15);
  });

  it('phase 6 review: filler groups leave no long lull, and 1-1 gets only kinds that do not shoot', () => {
    for (const game of WORLD_1) {
      const times = [...game.waves]
        .map((w) => w.at / game.scenery.scrollSpeed)
        .sort((a, b) => a - b);
      // The quiet stretches before the bosses (P07-R06) are left out.
      const bosses = (game.bosses ?? []).map((b) => b.at / game.scenery.scrollSpeed);
      const quiet = (t0: number, t1: number) =>
        bosses.some((b) => t0 <= b && t1 >= b - QUIET_BEFORE_BOSS);
      const lulls = times
        .slice(1)
        .map((t, i) => [times[i] ?? 0, t] as const)
        .filter(([t0, t1]) => !quiet(t0, t1))
        .map(([t0, t1]) => t1 - t0);
      const filler = WORLD_1_FILLERS[game.id];
      expect(Math.max(...lulls), game.id).toBeLessThanOrEqual(
        (filler?.maxGap[0] ?? 0) * 1.5 + 1e-9,
      );
    }
    const written = new Set(WAVES_1_1.map((beat) => beat[0]));
    const fillers = level('1-1').waves.filter((w) => !written.has(w.at / 70));
    expect(fillers.length).toBeGreaterThan(20);
    expect(new Set(fillers.map((w) => w.kind))).toEqual(new Set(['hornet', 'gnat']));
  });

  it('phase 6 review: the waves bring 50 % more groups than written, never on top of each other', () => {
    const written = waveScript(70, WAVES_1_1, 1);
    const denser = level('1-1').waves;
    const groups = (script: typeof written) => script.reduce((n, w) => n + w.count, 0);
    expect(groups(denser)).toBeGreaterThanOrEqual(Math.floor(groups(written) * 1.5));
    for (const wave of denser) {
      if (wave.count > 1)
        expect(wave.interval > 0 || (wave.spread ?? 0) !== 0, wave.kind).toBe(true);
    }
  });

  it('P06-R08: the bullet speed and fire rate factors never go down from 1-1 to 1-5', () => {
    const factors = WORLD_1.map((l) => l.difficulty);
    for (let i = 1; i < factors.length; i++) {
      const [before, now] = [at(factors, i - 1), at(factors, i)];
      expect(now.bulletSpeed).toBeGreaterThanOrEqual(before.bulletSpeed);
      expect(now.fireRate).toBeGreaterThanOrEqual(before.fireRate);
      expect(now.bulletSpeed + now.fireRate).toBeGreaterThan(before.bulletSpeed + before.fireRate);
    }
    expect(factors.map((f) => f.bulletSpeed)).toEqual([0.8, 0.85, 0.9, 1, 1.1]);
  });

  it('P07-R06: each level has a mini boss at its middle and a final boss at its end', () => {
    for (const game of WORLD_1) {
      const length = levelLength(game.scenery);
      expect(
        game.bosses?.map((b) => [b.rank, b.at]),
        game.id,
      ).toEqual([
        ['mini', length / 2],
        ['final', length],
      ]);
    }
  });

  it('P07-R06: no wave starts in the 10 s before each boss', () => {
    for (const game of WORLD_1) {
      const quiet = QUIET_BEFORE_BOSS * game.scenery.scrollSpeed;
      for (const boss of game.bosses ?? []) {
        const near = game.waves.filter((w) => w.at > boss.at - quiet && w.at <= boss.at);
        expect(near, `${game.id} ${boss.rank}`).toEqual([]);
      }
    }
  });

  it('P07-R03: the scenery is drawn past the end of each level for the final fight', () => {
    expect(WORLD_1.map((l) => l.runout)).toEqual([150, 80, 30, 70, 75]);
  });

  it('P06-R08: in each level, the second half has more enemy HP than the first', () => {
    for (const [i, m] of METRICS.entries()) {
      expect(m.secondHalf, WORLD_1[i]?.id).toBeGreaterThan(m.firstHalf);
    }
  });
});

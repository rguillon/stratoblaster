import { describe, expect, it } from 'vitest';
import type { GameLevel } from '../../../../src/core/content/game-level';
import { HeightField } from '../../../../src/core/scenery/height-field';
import { PropPlacer } from '../../../../src/core/scenery/prop-placement';
import { levelRoads } from '../../../../src/core/scenery/road-network';
import { levelLength } from '../../../../src/core/scenery/scenery-level';
import { LevelRun } from '../../../../src/core/systems/level-run';
import { WORLD_1_PROPS } from '../../../../src/game/config/world-1/props';
import { PLAYER_WEAPONS } from '../../../../src/game/config/player-weapons';
import { WAVES_1_1, waveScript } from '../../../../src/game/config/world-1/waves';
import { ENEMY_KINDS } from '../../../../src/game/sim/enemy-kinds';
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
 * at once, and the health spawned in each half of the level.
 */
function measure(game: GameLevel) {
  const weapon = PLAYER_WEAPONS[0];
  const run = new LevelRun({
    screen: { width: 480, height: 640 },
    level: game,
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

const PLANTS = new Set(['dead-tree', 'forked-tree', 'palm-tree', 'dry-bush', 'cactus', 'bush']);

/** Buildings placed over the whole level, with its own seed. */
function buildings(game: GameLevel): number {
  const { scenery } = game;
  const field = new HeightField(scenery);
  const placer = new PropPlacer(
    field,
    scenery.props,
    scenery.seed,
    levelRoads(field, scenery.roads, scenery.seed),
  );
  const area = { xMin: -400, xMax: 400, zMin: 0, zMax: field.length };
  return placer.place(area).filter((p) => !PLANTS.has(p.kind)).length;
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

  it('P06-R05: the number of buildings goes up from 1-1 to 1-5 (fixed seed)', () => {
    const counts = WORLD_1.map(buildings);
    expect(increasing(counts)).toBe(true);
  });

  it('P06-R05: each level begins on the kind of ground the previous one ended on', () => {
    const first = (id: string) => at(level(id).scenery.sections, 0);
    const last = (id: string) => {
      const { sections } = level(id).scenery;
      return at(sections, sections.length - 1);
    };
    // 1-2 starts on the coast where 1-1 ended,
    expect(last('1-1').shore).toBeDefined();
    expect(first('1-2').shore).toEqual(last('1-1').shore);
    // 1-3 on the sand and rock 1-2 ended on,
    expect(first('1-3').relief).toEqual(last('1-2').relief);
    expect(first('1-3').surface).toEqual(last('1-2').surface);
    // 1-4 in the open desert (dunes) 1-3 ended on,
    expect(last('1-3').dunes).toBeDefined();
    expect(first('1-4').dunes).toBeDefined();
    // and 1-5 on flat desert at the edge of the industry 1-4 ended on.
    expect(last('1-4').groups).toEqual(['heavy-industry']);
    expect(first('1-5').dunes).toBeUndefined();
    expect(first('1-5').relief.amplitude).toBeLessThanOrEqual(10);
    expect(first('1-5').surface).toMatchObject({ sandy: 1 });
    expect(last('1-5').groups).toEqual(['city']);
  });

  it('P06-R06: the desert levels are sand with dunes, and use the desert homes and outposts', () => {
    for (const id of ['1-3', '1-4', '1-5']) {
      const { sections } = level(id).scenery;
      expect(
        sections.some((s) => (s.surface?.sandy ?? 0) > 0),
        id,
      ).toBe(true);
      expect(
        sections.some((s) => s.groups?.includes('desert-homes')),
        id,
      ).toBe(true);
    }
    expect(level('1-3').scenery.sections.some((s) => s.dunes)).toBe(true);
    expect(level('1-3').scenery.sections.some((s) => s.channel)).toBe(true);
    expect(WORLD_1.every((l) => l.scenery.props === WORLD_1_PROPS)).toBe(true);
    for (const game of WORLD_1) {
      expect(SCENERY_BINDINGS.looks[game.scenery.id]?.terrain.sand, game.id).toBeDefined();
    }
  });

  it('P06-R07: each level only uses the kinds it introduces and those of the levels before', () => {
    const kinds = (id: string) => new Set(level(id).waves.map((w) => w.kind));
    const sorted = (id: string) => [...kinds(id)].sort();
    expect(sorted('1-1')).toEqual(['gnat', 'hornet', 'scout', 'strafer']);
    expect(sorted('1-2')).toEqual([...sorted('1-1'), 'splitter', 'weaver'].sort());
    expect(sorted('1-3')).toEqual([...sorted('1-2'), 'carrier', 'spinner'].sort());
    expect(sorted('1-4')).toEqual([...sorted('1-3'), 'lancer', 'rocketeer'].sort());
    expect(sorted('1-5')).toEqual(ENEMY_KINDS.map((k) => k.id).sort());
  });

  it('P06-R07: waves are triggered by distance, the same every time', () => {
    const speed = level('1-1').scenery.scrollSpeed;
    expect(level('1-1').waves).toEqual(waveScript(speed, WAVES_1_1));
    expect(level('1-1').waves[0]?.at).toBe(at(WAVES_1_1, 0)[0] * speed);
    expect(measure(level('1-2'))).toEqual(METRICS[1]);
  });

  it('P06-R08: enemy count, total enemy HP and peak on screen go up strictly from 1-1 to 1-5', () => {
    expect(increasing(METRICS.map((m) => m.spawned))).toBe(true);
    expect(increasing(METRICS.map((m) => m.health))).toBe(true);
    expect(increasing(METRICS.map((m) => m.peak))).toBe(true);
    // Tunable values, with the density raised by 50 % in review (D-044): about 90 enemies in
    // 1-1, the fewest at once; at least 15 at once in 1-5.
    expect(METRICS[0]?.spawned).toBeLessThanOrEqual(1.5 * 60 * 1.4);
    expect(METRICS[0]?.peak).toBeLessThanOrEqual(12);
    expect(METRICS[4]?.peak).toBeGreaterThanOrEqual(15);
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

  it('P06-R08: in each level, the second half has more enemy HP than the first', () => {
    for (const [i, m] of METRICS.entries()) {
      expect(m.secondHalf, WORLD_1[i]?.id).toBeGreaterThan(m.firstHalf);
    }
  });
});

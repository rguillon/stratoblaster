import { describe, expect, it } from 'vitest';
import { at } from '../../../helpers/at';
import type { GameLevel } from '../../../../src/core/content/game-level';
import type { LevelBoss } from '../../../../src/core/systems/boss-fights';
import {
  LevelRun,
  type LevelControls,
  type LevelRunOptions,
} from '../../../../src/core/systems/level-run';
import type { Wave } from '../../../../src/core/systems/wave-runner';
import { SAMPLE_GAME } from '../../../fixtures/sample-game';
import { SAMPLE_BOSS_KINDS } from '../../../fixtures/sample-boss';
import { SAMPLE_ENEMY_KINDS } from '../../../fixtures/sample-enemies';
import { SAMPLE_SCENERY_LEVEL } from '../../../fixtures/sample-scenery';

const top = { side: 'top', position: 0.5 } as const;
const STILL: LevelControls = { move: { x: 0, y: 0 }, fire: false };
/** The sample level is 20 s long at 20 units/s: the mini boss at 5 s, the final boss at its end. */
const BOSSES: readonly LevelBoss[] = [
  { kind: 'big-cube', rank: 'mini', at: 100 },
  { kind: 'big-cube', rank: 'final', at: 400 },
];

const level = (waves: readonly Wave[], bosses = BOSSES): GameLevel => ({
  id: 'a',
  scenery: SAMPLE_SCENERY_LEVEL,
  waves,
  difficulty: { bulletSpeed: 1, fireRate: 1 },
  bosses,
});

function newRun(waves: readonly Wave[] = [], overrides: Partial<LevelRunOptions> = {}): LevelRun {
  const [weapon] = SAMPLE_GAME.playerWeapons;
  if (!weapon) throw new Error('no weapon');
  return new LevelRun({
    screen: SAMPLE_GAME.screen,
    level: level(waves),
    kinds: SAMPLE_ENEMY_KINDS,
    weapon,
    weaponLevel: 1,
    weapons: SAMPLE_GAME.playerWeapons,
    ship: { start: { x: 150, y: 50 }, maxSpeed: 100, accelerationSeconds: 0.05, muzzleOffset: 10 },
    bounds: { minY: 20, maxY: 300, centerX: 150, halfWidthAt: () => 120 },
    cullMargin: 40,
    maxEnemyAge: 60,
    endWait: 10,
    seed: 3,
    bossKinds: SAMPLE_BOSS_KINDS,
    bossRules: SAMPLE_GAME.bossFights,
    ...overrides,
  });
}

function play(run: LevelRun, seconds: number, controls = STILL): void {
  for (let i = 0; i < Math.round(seconds * 60) && run.phase !== 'complete'; i++) {
    run.step(1 / 60, controls);
  }
}

/** Destroys the boss being fought (its parts, then its core) and waits for its death blasts. */
function defeat(run: LevelRun): void {
  for (let i = 0; i < 3; i++) {
    run.breakBossPart();
    play(run, 0.1);
  }
  play(run, 1.2);
}

describe('LevelRun with bosses', () => {
  it('P07-R06: the mini boss arrives at its distance; no wave starts while it is fought', () => {
    const run = newRun([{ at: 120, kind: 'dropper', count: 1, interval: 0, entry: top }]);
    play(run, 5.1);
    expect(run.fights.rank).toBe('mini');
    expect(run.enemies.enemies).toHaveLength(1);
    play(run, 20);
    // The wave at 120 would have come at 6 s: the level waits during the fight (P07-R03).
    expect(run.track.progress).toBeCloseTo(100, 0);
    expect(run.enemies.enemies).toHaveLength(1);
    defeat(run);
    expect(run.fights.active).toBe(false);
    play(run, 1.1);
    expect(run.enemies.enemies.some((e) => e.model === 'cube' && e.points === 7)).toBe(true);
  });

  it('P07-R03: the ground scrolls at the boss speed during the fight', () => {
    const run = newRun();
    play(run, 5.1);
    play(run, 2);
    expect(run.track.speedFactor).toBeCloseTo(0.5);
    const before = run.track.distance;
    play(run, 1);
    expect(run.track.distance - before).toBeCloseTo(10, 0);
  });

  it('P07-R06: the level ends once its final boss is destroyed, not at the end of the scroll', () => {
    const run = newRun();
    play(run, 5.1);
    defeat(run);
    play(run, 30);
    expect(run.track.ended).toBe(true);
    expect(run.fights.rank).toBe('final');
    expect(run.phase).toBe('playing');
    expect(run.track.held).toBe(true);
    defeat(run);
    play(run, 1 / 60);
    expect(run.phase).toBe('complete');
    expect(run.result).toMatchObject({ outcome: 'complete', destroyed: 2, spawned: 2 });
  });

  it('P07-R06: touching a boss part hurts the player; the part loses no health', () => {
    const run = newRun([], { hull: SAMPLE_GAME.hull });
    play(run, 5.1);
    play(run, 3);
    const boss = run.fights.boss;
    if (!boss) throw new Error('no boss');
    // Fly up into the gun (on the left of the boss).
    const gun = at(boss.parts, 0);
    run.ship.x = gun.x;
    run.ship.y = gun.y;
    run.step(1 / 60, STILL);
    expect(run.hits[0]?.kind).toBe('collision');
    expect(gun.health).toBe(gun.maxHealth);
  });

  it('P07-R07: a destroyed part drops a bonus from its own chance, the core of a boss too', () => {
    const run = newRun([], { bonuses: SAMPLE_GAME.bonuses });
    play(run, 5.1);
    play(run, 3);
    const boss = run.fights.boss;
    if (!boss) throw new Error('no boss');
    // The gun has a chance of 1, the plate of 0; the game's rule (no drops) does not apply.
    at(boss.parts, 0).health = 0;
    play(run, 0.1);
    expect(run.bonuses?.dropped).toBe(1);
    at(boss.parts, 1).health = 0;
    play(run, 0.1);
    expect(run.bonuses?.dropped).toBe(1);
    boss.core.health = 0;
    play(run, 1.2);
    expect(run.bonuses?.dropped).toBe(2);
  });

  it('P07-R08: destroying the mini boss saves a checkpoint; the game over result carries it', () => {
    const run = newRun([], { hull: SAMPLE_GAME.hull });
    play(run, 5.1);
    run.shots.select(at(SAMPLE_GAME.playerWeapons, 0), 2);
    defeat(run);
    expect(run.checkpoint).toMatchObject({ progress: 100, bossesPassed: 1 });
    expect(run.checkpoint?.weapons).toEqual({ weapon: 'pea', levels: { pea: 2 } });
    expect(run.result.checkpoint).toBeUndefined();
    const hull = run.hull;
    if (!hull) throw new Error('no hull');
    hull.lives = 1;
    hull.health = 1;
    hull.invincible = 0;
    // A Dropper comes at the ship until it is hit.
    run.enemies.add(
      ...at(SAMPLE_ENEMY_KINDS, 0).spawn({ width: 300, height: 400, random: () => 0.5 }),
    );
    play(run, 10);
    expect(run.phase).toBe('over');
    expect(run.result.checkpoint).toEqual(run.checkpoint);
  });

  it('P07-R08: a run from the checkpoint starts after the mini boss, with the saved weapons', () => {
    const checkpoint = {
      progress: 100,
      bossesPassed: 1,
      weapons: { weapon: 'ray', levels: { ray: 2, pea: 2 } },
    };
    const run = newRun([], { checkpoint, hull: SAMPLE_GAME.hull });
    expect(run.track.progress).toBe(100);
    expect(run.shots.weapon.id).toBe('ray');
    expect(run.shots.level).toBe(2);
    expect(run.hull?.lives).toBe(SAMPLE_GAME.hull.lives);
    play(run, 2);
    expect(run.fights.active).toBe(false);
    run.arsenal.switchWeapon();
    expect([run.shots.weapon.id, run.shots.level]).toEqual(['pea', 2]);
    // A later game over still offers the same checkpoint.
    expect(run.checkpoint).toBe(checkpoint);
  });

  it('P06-R09, P07-R09: seeking to a boss brings it in; seeking during a fight drops it', () => {
    const run = newRun();
    run.seek(400 / 20);
    play(run, 1 / 60);
    expect(run.fights.rank).toBe('final');
    run.seek(2);
    expect(run.fights.active).toBe(false);
    expect(run.enemies.enemies).toHaveLength(0);
    play(run, 3.2);
    expect(run.fights.rank).toBe('mini');
  });

  it('P06-R03: without a final boss, the level still ends with its scroll', () => {
    const run = newRun([], { level: level([], [{ kind: 'big-cube', rank: 'mini', at: 100 }]) });
    play(run, 5.1);
    defeat(run);
    play(run, 40);
    expect(run.phase).toBe('complete');
  });
});

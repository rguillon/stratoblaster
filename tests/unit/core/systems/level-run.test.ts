import { describe, expect, it } from 'vitest';
import type { GameLevel } from '../../../../src/core/content/game-level';
import {
  Enemy,
  type EnemyKindDefinition,
  type EnemySpawnArea,
} from '../../../../src/core/entities/enemy';
import {
  LevelRun,
  type LevelControls,
  type LevelRunOptions,
} from '../../../../src/core/systems/level-run';
import type { Wave } from '../../../../src/core/systems/wave-runner';
import { SAMPLE_GAME } from '../../../fixtures/sample-game';
import { SAMPLE_ENEMY_KINDS } from '../../../fixtures/sample-enemies';
import { SAMPLE_SCENERY_LEVEL } from '../../../fixtures/sample-scenery';

/** An enemy that hovers at the top of the screen and never leaves. */
class Hover extends Enemy {
  constructor(x: number, y: number) {
    super(x, y, { model: 'cube', radius: 10, health: 1000, points: 1 });
  }

  override update(): void {
    // stays put
  }
}

const KINDS: readonly EnemyKindDefinition[] = [
  ...SAMPLE_ENEMY_KINDS,
  { id: 'hover', name: 'Hover', spawn: (area) => [new Hover(area.width / 2, area.height - 50)] },
];

const top = { side: 'top', position: 0.5 } as const;

/** A 20 s sample level (20 units/s, 400 long) with `waves`. */
const level = (waves: readonly Wave[]): GameLevel => ({
  id: 'a',
  scenery: SAMPLE_SCENERY_LEVEL,
  waves,
  difficulty: { bulletSpeed: 1, fireRate: 1 },
});

const STILL: LevelControls = { move: { x: 0, y: 0 }, fire: false };

function newRun(
  waves: readonly Wave[],
  endWait = 10,
  inView?: (x: number, y: number) => boolean,
  weapons?: LevelRunOptions['weapons'],
  overrides: Partial<LevelRunOptions> = {},
): LevelRun {
  const [weapon] = SAMPLE_GAME.playerWeapons;
  if (!weapon) throw new Error('no weapon');
  return new LevelRun({
    screen: SAMPLE_GAME.screen,
    level: level(waves),
    kinds: KINDS,
    weapon,
    weaponLevel: 2,
    ship: { start: { x: 150, y: 50 }, maxSpeed: 100, accelerationSeconds: 0.05, muzzleOffset: 10 },
    bounds: { minY: 20, maxY: 300, centerX: 150, halfWidthAt: () => 120 },
    cullMargin: 40,
    maxEnemyAge: 60,
    endWait,
    seed: 3,
    ...(inView ? { inView } : {}),
    ...(weapons ? { weapons } : {}),
    ...overrides,
  });
}

/** Steps `run` at 60 Hz for `seconds` (or until it is complete). */
function play(run: LevelRun, seconds: number, controls = STILL): void {
  for (let i = 0; i < Math.round(seconds * 60) && run.phase !== 'complete'; i++) {
    run.step(1 / 60, controls);
  }
}

describe('LevelRun', () => {
  it('P06-R02: the ship moves with the controls and stays inside the playfield', () => {
    const run = newRun([]);
    play(run, 1, { move: { x: 1, y: 0 }, fire: false });
    expect(run.ship.x).toBeGreaterThan(200);
    play(run, 5, { move: { x: 1, y: 0 }, fire: false });
    expect(run.ship.x).toBe(270);
    expect(run.shots.muzzleX).toBe(270);
    expect(run.shots.muzzleY).toBe(run.ship.y + 10);
  });

  it('P06-R02: shooting an enemy until it has no health left blows it up and removes it', () => {
    const run = newRun([{ at: 0, kind: 'dropper', count: 1, interval: 0, entry: top }]);
    let blasts = 0;
    for (let i = 0; i < 5 * 60; i++) {
      run.step(1 / 60, { move: { x: 0, y: 0 }, fire: true });
      blasts += run.blasts.filter((b) => b.kind === 'enemy').length;
    }
    expect(run.shots.weapon.id).toBe('pea');
    expect(run.enemies.kills).toBe(1);
    expect(blasts).toBe(1);
    expect(run.enemies.enemies).toHaveLength(0);
  });

  it('P06-R02 (review): only enemies on screen can be shot, so none blows up out of sight', () => {
    const above = [{ at: 0, kind: 'hover', count: 1, interval: 0, entry: top }] as const;
    // The Hover waits 50 px under the top edge: in view by default…
    const seen = newRun(above);
    play(seen, 6, { move: { x: 0, y: 0 }, fire: true });
    expect(seen.enemies.enemies[0]?.health).toBeLessThan(1000);
    // …but out of a view that stops 100 px under the top edge.
    const hidden = newRun(above, 10, (_x, y) => y <= 300);
    play(hidden, 6, { move: { x: 0, y: 0 }, fire: true });
    expect(hidden.enemies.enemies[0]?.health).toBe(1000);
    expect(hidden.shots.totalDamage).toBe(0);
  });

  it('phase 6 review: enemies come in from the top only where the ship can reach at the bottom', () => {
    const areas: EnemySpawnArea[] = [];
    const probe: EnemyKindDefinition = {
      id: 'probe',
      name: 'Probe',
      spawn: (area) => {
        areas.push(area);
        return [];
      },
    };
    const waves = [{ at: 0, kind: 'probe', count: 1, interval: 0, entry: top }] as const;
    const run = newRun(waves, 10, undefined, undefined, {
      kinds: [...KINDS, probe],
      // Narrower at the bottom, as with a tilted camera.
      bounds: { minY: 20, maxY: 300, centerX: 150, halfWidthAt: (y) => (y < 100 ? 90 : 140) },
    });
    play(run, 1);
    expect(areas.map((a) => a.topRange)).toEqual([[60, 240]]);
  });

  it('phase 6 review: a bonus picked up raises the weapon in use, which keeps its level', () => {
    const [pea, ray] = SAMPLE_GAME.playerWeapons;
    if (!pea || !ray) throw new Error('two weapons expected');
    const bonuses = { chance: { perHealth: 0, min: 1, max: 1 }, fallSpeed: 100, pickupRadius: 15 };
    const run = newRun([], 10, undefined, [pea, ray], { weaponLevel: 1, bonuses });
    const dropOnShip = () => {
      const { x, y } = run.ship;
      run.bonuses?.drop([{ id: 1, x, y: y + 20, radius: 5, health: 0, maxHealth: 10 }]);
      play(run, 1);
    };
    dropOnShip();
    expect(run.shots.level).toBe(2);
    expect(run.bonuses?.collected).toBe(1);
    // No further than the weapon's last level.
    dropOnShip();
    expect(run.shots.level).toBe(pea.levels.length);
    // The ray starts at the starting level; the pea gets its level back.
    play(run, 0.1, { ...STILL, switchWeapon: true });
    expect([run.shots.weapon, run.shots.level]).toEqual([ray, 1]);
    play(run, 0.1, { ...STILL, switchWeapon: true });
    expect([run.shots.weapon, run.shots.level]).toEqual([pea, pea.levels.length]);
    // Without bonus rules, none.
    expect(newRun([]).bonuses).toBeUndefined();
  });

  it('phase 6 review: destroyed enemies drop bonuses', () => {
    const always = { chance: { perHealth: 0, min: 1, max: 1 }, fallSpeed: 0, pickupRadius: 1 };
    const fragile: EnemyKindDefinition = {
      id: 'fragile',
      name: 'Fragile',
      spawn: (area) => {
        const enemy = new Hover(area.width / 2, area.height - 50);
        enemy.health = 0.5;
        return [enemy];
      },
    };
    const waves = [{ at: 0, kind: 'fragile', count: 1, interval: 0, entry: top }] as const;
    const run = newRun(waves, 10, undefined, undefined, {
      kinds: [...KINDS, fragile],
      bonuses: always,
    });
    // Shots fly at 100 px/s, the enemy is 300 px up.
    play(run, 5, { move: { x: 0, y: 0 }, fire: true });
    expect(run.enemies.kills).toBe(1);
    expect(run.bonuses?.dropped).toBe(1);
    expect(run.bonuses?.bonuses[0]?.x).toBeCloseTo(150);
  });

  it('GD-20..GD-22: enemy shots hurt the ship, which blinks invincible; out of lives, game over', () => {
    const hull = {
      lives: 2,
      invincibleSeconds: 1,
      hitRadius: 5,
      damage: { bullet: 60, missile: 60, laser: 60, collision: 60 },
      ramDamage: 10,
    };
    const ship = { start: { x: 150, y: 50 }, maxSpeed: 100, accelerationSeconds: 0.05 };
    const run = newRun([], 10, undefined, undefined, {
      hull,
      ship: { ...ship, muzzleOffset: 10, maxHealth: 100 },
    });
    const shoot = () => {
      run.enemies.shots.fireBullet(run.ship.x, run.ship.y, 0, { speed: 0, radius: 2, style: 's' });
    };
    shoot();
    play(run, 1 / 60);
    expect(run.hits).toEqual([{ kind: 'bullet', x: 150, y: 50, event: 'hit' }]);
    expect([run.hull?.health, run.hull?.lives]).toEqual([40, 2]);
    // Invincible: another bullet goes through, harmless, until the second is over.
    shoot();
    play(run, 0.5);
    expect(run.hull?.health).toBe(40);
    play(run, 0.6);
    expect([run.hull?.health, run.hull?.lives]).toEqual([100, 1]);
    expect(run.phase).toBe('playing');
    // The last life: two more hits.
    for (const event of ['hit', 'gameOver']) {
      play(run, 1.1);
      shoot();
      play(run, 1 / 60);
      expect(run.hits.map((h) => h.event)).toEqual([event]);
    }
    expect(run.phase).toBe('over');
    expect(run.result.outcome).toBe('over');
    // The ship is gone: it neither moves nor shoots; seeking does nothing.
    play(run, 1, { move: { x: 1, y: 0 }, fire: true });
    expect(run.ship.x).toBe(150);
    expect(run.shots.firing).toBe(false);
    run.seek(5);
    expect(run.phase).toBe('over');
    // Without hull rules, nothing hurts.
    expect(newRun([]).hull).toBeUndefined();
  });

  it('phase 6 review: switching cycles through the weapons, each at the starting level', () => {
    const [pea, ray] = SAMPLE_GAME.playerWeapons;
    if (!pea || !ray) throw new Error('missing weapons');
    const fire = (switchWeapon: boolean) => ({ move: { x: 0, y: 0 }, fire: true, switchWeapon });
    // Without a list, the starting weapon is the only one.
    const single = newRun([]);
    single.step(1 / 60, fire(true));
    expect(single.shots.weapon).toBe(pea);
    const both = newRun([], 10, undefined, [pea, ray]);
    both.step(1 / 60, fire(false));
    expect(both.shots.activeCount).toBeGreaterThan(0);
    both.step(1 / 60, fire(true));
    expect(both.shots.weapon).toBe(ray);
    expect(both.shots.level).toBe(2);
    expect(both.shots.beam.length).toBeGreaterThan(0);
    // Shots already in flight keep flying.
    expect(both.shots.activeCount).toBeGreaterThan(0);
    both.step(1 / 60, fire(true));
    expect(both.shots.weapon).toBe(pea);
  });

  it('P06-R07: the waves come as the level scrolls past their distance', () => {
    const run = newRun([{ at: 200, kind: 'dropper', count: 1, interval: 0, entry: top }]);
    play(run, 9.9);
    expect(run.enemies.spawned).toBe(0);
    play(run, 0.2);
    expect(run.enemies.spawned).toBe(1);
  });

  it('P06-R03: no enemy comes after the end of the scroll; the level completes once they are gone', () => {
    const run = newRun([
      { at: 0, kind: 'dropper', count: 1, interval: 0, entry: top },
      { at: 380, kind: 'pair', count: 3, interval: 1.5, entry: top },
    ]);
    play(run, 20.1);
    expect(run.track.ended).toBe(true);
    expect(run.phase).toBe('clearing');
    expect(run.enemies.spawned).toBe(3);
    play(run, 30);
    expect(run.enemies.spawned).toBe(3);
    expect(run.phase).toBe('complete');
    expect(run.track.time).toBe(20);
    expect(run.result).toEqual({ levelId: 'a', destroyed: 0, spawned: 3, outcome: 'complete' });
  });

  it('P06-R03: the level completes at most `endWait` seconds after the end of the scroll', () => {
    const run = newRun([{ at: 300, kind: 'hover', count: 1, interval: 0, entry: top }], 4);
    play(run, 23.9);
    expect(run.phase).toBe('clearing');
    play(run, 0.2);
    expect(run.phase).toBe('complete');
    expect(run.enemies.enemies).toHaveLength(1);
    const before = run.ship.y;
    run.step(1 / 60, { move: { x: 0, y: 1 }, fire: true });
    expect(run.ship.y).toBe(before);
  });

  it('P06-R07: the same level played twice gives the same run', () => {
    const waves: Wave[] = [
      { at: 0, kind: 'pair', count: 2, interval: 0.7, entry: top },
      { at: 100, kind: 'dropper', count: 3, interval: 0.4, entry: top },
    ];
    const [a, b] = [newRun(waves), newRun(waves)];
    const fire = { move: { x: 0.5, y: 0.2 }, fire: true };
    play(a, 12, fire);
    play(b, 12, fire);
    expect(a.result).toEqual(b.result);
    expect(a.enemies.enemies.map((e) => [e.x, e.y])).toEqual(
      b.enemies.enemies.map((e) => [e.x, e.y]),
    );
  });

  it('P06-R09: seeking skips the waves before that time and clears the screen', () => {
    const run = newRun([
      { at: 0, kind: 'dropper', count: 1, interval: 0, entry: top },
      { at: 100, kind: 'dropper', count: 1, interval: 0, entry: top },
      { at: 300, kind: 'pair', count: 1, interval: 0, entry: top },
    ]);
    play(run, 1, { move: { x: 0, y: 0 }, fire: true });
    expect(run.enemies.enemies).toHaveLength(1);
    run.seek(10);
    expect(run.track.time).toBe(10);
    expect(run.enemies.enemies).toHaveLength(0);
    expect(run.shots.activeCount).toBe(0);
    play(run, 6);
    expect(run.enemies.spawned).toBe(3);
    run.seek(30);
    expect(run.track.ended).toBe(true);
    play(run, 1 / 60);
    expect(run.phase).toBe('complete');
  });

  it('rejects a wave script with an unknown enemy kind', () => {
    expect(() => newRun([{ at: 0, kind: 'nope', count: 1, interval: 0, entry: top }])).toThrow(
      /unknown enemy kind/,
    );
  });
});

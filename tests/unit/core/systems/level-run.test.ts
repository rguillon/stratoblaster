import { describe, expect, it } from 'vitest';
import type { GameLevel } from '../../../../src/core/content/game-level';
import { Enemy, type EnemyKindDefinition } from '../../../../src/core/entities/enemy';
import { LevelRun, type LevelControls } from '../../../../src/core/systems/level-run';
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
    expect(run.result).toEqual({ levelId: 'a', destroyed: 0, spawned: 3 });
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

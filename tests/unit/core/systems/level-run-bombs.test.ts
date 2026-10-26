import { describe, expect, it } from 'vitest';
import type { LevelRun } from '../../../../src/core/systems/level-run';
import { BOMB, BOMBS, level, newRun, play, SAFE, Still } from '../../../helpers/score-run';

describe('LevelRun bombs (P11-R05)', () => {
  it('P11-R05: a level starts with the starting bombs; one bomb destroys the small enemies and hurts the big ones', () => {
    const run = newRun();
    expect(run.bombs?.count).toBe(3);
    const small = [0, 1, 2, 3, 4].map((i) => new Still(60 + i * 40, 250, 10, 50));
    const big = new Still(150, 300, 200, 500);
    run.enemies.add(...small, big);
    play(run, 1 / 60, BOMB);
    expect(run.bombs?.count).toBe(2);
    expect(big.health).toBe(100);
    play(run, 1 / 60);
    expect(run.enemies.kills).toBe(5);
    expect(run.enemies.enemies).toEqual([big]);
  });

  it('P11-R05: enemies off screen are not hurt', () => {
    const run = newRun();
    const away = new Still(150, 480, 10, 50);
    run.enemies.add(away);
    play(run, 1 / 60, BOMB);
    expect(away.health).toBe(10);
  });

  it('P11-R05: a bomb clears the enemy bullets, missiles and lasers, and keeps the ship safe', () => {
    const run = newRun();
    const { shots } = run.enemies;
    shots.fireBullet(150, 200, Math.PI, { speed: 10, radius: 2, style: 's' });
    shots.fireMissile(100, 200, Math.PI, {
      speed: 10,
      radius: 3,
      health: 5,
      turnRateDeg: 0,
      homingSeconds: 0,
      style: 's',
    });
    const owner = new Still(150, 350, 1000, 0);
    run.enemies.add(owner);
    shots.fireLaser(owner, { warningSeconds: 0.1, firingSeconds: 2, width: 6, style: 's' });
    expect(shots.count).toBe(3);
    play(run, 1 / 60, BOMB);
    expect(shots.count).toBe(0);
    // While it lasts, a bullet on the ship does nothing.
    shots.fireBullet(run.ship.x, run.ship.y, 0, { speed: 0, radius: 2, style: 's' });
    play(run, 0.5);
    expect(run.hull?.health).toBe(100);
    play(run, 0.6);
    shots.fireBullet(run.ship.x, run.ship.y, 0, { speed: 0, radius: 2, style: 's' });
    play(run, 1 / 60);
    expect(run.hull?.lives).toBe(2);
  });

  it('P11-R05: holding the bomb key sets off one bomb only; with none left nothing happens', () => {
    const run = newRun();
    // The controls give `bomb` once per press: held, it is set on one step only.
    play(run, 1 / 60, BOMB);
    play(run, 3);
    expect(run.bombs?.count).toBe(2);
    // A press during a bomb does nothing.
    play(run, 1 / 60, BOMB);
    play(run, 0.5, BOMB);
    expect(run.bombs?.count).toBe(1);
    play(run, 1);
    play(run, 1 / 60, BOMB);
    play(run, 1.1);
    expect(run.bombs?.count).toBe(0);
    const enemy = new Still(150, 250, 10, 50);
    run.enemies.add(enemy);
    play(run, 1 / 60, BOMB);
    expect(enemy.health).toBe(10);
    expect(run.bombs?.fired).toBe(3);
  });

  it('P11-R05: a lost life tops the bombs back up to the starting count, not above', () => {
    const hit = (run: LevelRun): void => {
      run.enemies.shots.fireBullet(run.ship.x, run.ship.y, 0, { speed: 0, radius: 2, style: 's' });
      play(run, 1 / 60);
      play(run, 1.1);
    };
    const low = newRun();
    play(low, 1 / 60, BOMB);
    play(low, 1.1);
    play(low, 1 / 60, BOMB);
    play(low, 1.1);
    expect(low.bombs?.count).toBe(1);
    hit(low);
    expect([low.hull?.lives, low.bombs?.count]).toEqual([2, 3]);
    const high = newRun();
    high.bombs?.add();
    expect(high.bombs?.count).toBe(4);
    hit(high);
    expect(high.bombs?.count).toBe(4);
  });

  it('P11-R05: a shielded boss core takes no bomb damage; its parts do', () => {
    const run = newRun({
      level: level([{ kind: 'big-cube', rank: 'final', at: 0 }]),
      bombs: { ...BOMBS, damage: 5 },
      hull: SAFE,
    });
    play(run, 1.5);
    const boss = run.fights.boss;
    if (!boss) throw new Error('no boss');
    expect(boss.coreShielded).toBe(true);
    const core = boss.coreHealth;
    play(run, 1 / 60, BOMB);
    expect(boss.parts.map((p) => p.health)).toEqual([15, 5]);
    expect(boss.coreHealth).toBe(core);
  });
});

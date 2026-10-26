import { describe, expect, it } from 'vitest';
import type { LevelBoss } from '../../../../src/core/systems/boss-fights';
import type { LevelRun } from '../../../../src/core/systems/level-run';
import { Dropper } from '../../../fixtures/sample-enemies';
import {
  BOMB,
  BOMBS,
  defeat,
  HULL,
  level,
  newRun,
  NO_DROP,
  play,
  SAFE,
  STILL,
  Still,
} from '../../../helpers/score-run';

describe('LevelRun score (P11-R01, R04)', () => {
  it('P11-R01: an enemy destroyed by a shot scores its points', () => {
    const run = newRun();
    run.enemies.add(new Still(150, 150, 1, 50));
    expect(run.score).toBe(0);
    play(run, 2, { ...STILL, fire: true });
    expect(run.enemies.kills).toBe(1);
    expect(run.score).toBe(50);
    expect(run.result.score).toBe(50);
  });

  it('P11-R01: an enemy destroyed by ramming it, or by a bomb, scores too', () => {
    const rammed = newRun();
    rammed.enemies.add(new Still(150, 50, 10, 30));
    play(rammed, 0.1);
    expect(rammed.score).toBe(30);
    const bombed = newRun();
    bombed.enemies.add(new Still(150, 250, 10, 40));
    play(bombed, 1 / 60, BOMB);
    play(bombed, 0.1);
    expect(bombed.score).toBe(40);
  });

  it('P11-R01: an enemy that leaves the screen alive scores nothing', () => {
    const run = newRun();
    run.enemies.add(new Dropper(40, 300));
    play(run, 6);
    expect(run.enemies.enemies).toHaveLength(0);
    expect(run.score).toBe(0);
  });

  it('P11-R01: each boss part destroyed scores its share, the core the boss points', () => {
    const run = newRun({
      level: level([{ kind: 'scored-cube', rank: 'final', at: 0 }]),
      hull: SAFE,
    });
    play(run, 1.5);
    expect(run.fights.active).toBe(true);
    run.breakBossPart();
    play(run, 0.1);
    expect(run.score).toBe(10);
    run.breakBossPart();
    play(run, 0.1);
    expect(run.score).toBe(20);
    run.breakBossPart();
    play(run, 1.2);
    expect(run.score).toBe(120);
  });

  it('P11-R04: the checkpoint keeps the score; a run from it starts with that score', () => {
    const mini: LevelBoss = { kind: 'scored-cube', rank: 'mini', at: 100 };
    const run = newRun({ level: level([mini]), hull: SAFE });
    play(run, 5.1);
    run.enemies.add(new Still(150, 100, 0, 500));
    play(run, 1 / 60);
    defeat(run);
    expect(run.checkpoint?.score).toBe(620);
    run.enemies.add(new Still(150, 100, 0, 900));
    play(run, 1 / 60);
    expect(run.score).toBe(1520);
    const checkpoint = run.checkpoint;
    if (!checkpoint) throw new Error('no checkpoint');
    const resumed = newRun({ level: level([mini]), checkpoint });
    expect(resumed.score).toBe(620);
    expect(resumed.bombs?.count).toBe(BOMBS.start);
  });
});

describe('LevelRun life and bomb bonuses (P11-R07)', () => {
  const pick = (run: LevelRun, kind: 'life' | 'bomb'): void => {
    run.bonuses?.place(kind, { x: run.ship.x, y: run.ship.y + 5 });
    play(run, 1 / 60);
  };

  it('P11-R07: a life bonus adds a life; at the most, it scores its points instead', () => {
    const run = newRun({ hull: { ...HULL, lives: 2 } });
    pick(run, 'life');
    expect(run.hull?.lives).toBe(3);
    pick(run, 'life');
    pick(run, 'life');
    expect(run.hull?.lives).toBe(5);
    expect(run.score).toBe(0);
    pick(run, 'life');
    expect(run.hull?.lives).toBe(5);
    expect(run.score).toBe(5000);
  });

  it('P11-R07: a bomb bonus adds a bomb; at the most, it scores its points instead', () => {
    const run = newRun();
    pick(run, 'bomb');
    pick(run, 'bomb');
    expect(run.bombs?.count).toBe(5);
    pick(run, 'bomb');
    expect(run.bombs?.count).toBe(5);
    expect(run.score).toBe(2000);
  });

  it('P11-R07: the mini boss drops a life bonus where its core was', () => {
    const run = newRun({ level: level([{ kind: 'big-cube', rank: 'mini', at: 100 }]), hull: SAFE });
    play(run, 5.1);
    const boss = run.fights.boss;
    defeat(run);
    const life = run.bonuses?.bonuses.find((b) => b.kind === 'life');
    expect(life?.x).toBeCloseTo(boss?.x ?? NaN);
    // The final boss drops none.
    const final = newRun({
      level: level([{ kind: 'big-cube', rank: 'final', at: 0 }]),
      hull: SAFE,
    });
    play(final, 1.5);
    defeat(final);
    expect(final.bonuses?.bonuses.some((b) => b.kind === 'life')).toBe(false);
  });

  it('P11-R07: enemies drop life and bomb bonuses with their chances, the same each time', () => {
    const kindsDropped = (): string[] => {
      const run = newRun({
        bonuses: {
          ...NO_DROP,
          chance: { perHealth: 0, min: 0.5, max: 0.5 },
          special: { life: 0.2, bomb: 0.3 },
        },
      });
      for (let i = 0; i < 40; i++) {
        run.enemies.add(new Still(150, 250, 0, 1));
        play(run, 1 / 60);
      }
      return run.bonuses?.bonuses.map((b) => b.kind) ?? [];
    };
    const kinds = kindsDropped();
    expect(kinds).toEqual(kindsDropped());
    expect(kinds).toContain('life');
    expect(kinds).toContain('bomb');
    expect(kinds).toContain('weapon');
    expect(kinds.length).toBeLessThanOrEqual(40);
  });
});

import { describe, expect, it } from 'vitest';
import { createRng } from '../../../../src/core/math/rng';
import { BOMB_RULES } from '../../../../src/game/config/bombs';
import { BONUS_RULES } from '../../../../src/game/config/bonuses';
import { HULL_RULES } from '../../../../src/game/config/hull';
import { MENU_TEXTS } from '../../../../src/game/config/menu-texts';
import { bossPartPoints, SCORING } from '../../../../src/game/config/scoring';
import { BOSS_DESIGNS } from '../../../../src/game/sim/boss-kinds';
import { ENEMY_KINDS } from '../../../../src/game/sim/enemy-kinds';

const AREA = { width: 480, height: 640 };

describe('scoring, lives and bombs of the game (P11)', () => {
  it('P11-R01: a kind with more health never scores less than a kind with half its health', () => {
    const roster = ENEMY_KINDS.flatMap((kind) => kind.spawn({ ...AREA, random: createRng(1) }));
    expect(roster.length).toBeGreaterThanOrEqual(ENEMY_KINDS.length);
    for (const a of roster) {
      for (const b of roster) {
        if (b.maxHealth * 2 <= a.maxHealth) expect(a.points).toBeGreaterThanOrEqual(b.points);
      }
    }
  });

  it('P11-R01: each boss part scores 10 % of its boss, rounded to 10; the core the boss points', () => {
    expect(bossPartPoints(10_000)).toBe(1000);
    expect(bossPartPoints(3500)).toBe(350);
    expect(bossPartPoints(4567)).toBe(460);
    for (const { stats } of BOSS_DESIGNS) {
      expect(stats.partPoints).toBe(bossPartPoints(stats.points));
      expect(stats.points).toBeGreaterThan(0);
    }
  });

  it('P11-R05: 3 bombs at the start, no limit (reviewer, 2026-10-28), 100 damage, 1 s; it destroys every World 1 kind up to the Rocketeer', () => {
    expect(BOMB_RULES).toEqual({ start: 3, damage: 100, seconds: 1 });
    const health = (name: string): number => {
      const kind = ENEMY_KINDS.find((k) => k.name === name);
      return kind?.spawn({ ...AREA, random: createRng(1) })[0]?.maxHealth ?? Infinity;
    };
    for (const name of [
      'Gnat',
      'Hornet',
      'Scout',
      'Strafer',
      'Weaver',
      'Spinner',
      'Lancer',
      'Rocketeer',
    ]) {
      expect(health(name)).toBeLessThanOrEqual(BOMB_RULES.damage);
    }
  });

  it('P11-R07: lives without limit (reviewer, 2026-10-28); life 1 %, bomb 3 %; at a most they would score 5 000 and 2 000', () => {
    expect([HULL_RULES.lives, HULL_RULES.maxLives]).toEqual([3, undefined]);
    expect(BONUS_RULES.special).toEqual({ life: 0.01, bomb: 0.03 });
    expect(BONUS_RULES.overflowPoints).toEqual(SCORING.overflow);
    expect(SCORING.overflow).toEqual({ life: 5000, bomb: 2000 });
  });

  it('P11-R02: the score shows 7 digits, zero-padded, the high score after HI', () => {
    expect(MENU_TEXTS.hudScore(0)).toBe('0000000');
    expect(MENU_TEXTS.hudHighScore(12_340)).toBe('HI 0012340');
    expect(MENU_TEXTS.hudBomb(3)).toBe('Bomb 3');
    expect(MENU_TEXTS.newHighScore).toBe('New high score!');
  });
});

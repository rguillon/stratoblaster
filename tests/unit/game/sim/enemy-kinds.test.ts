import { describe, expect, it } from 'vitest';
import { validateEnemyKinds } from '../../../../src/core/entities/enemy';
import { createRng } from '../../../../src/core/math/rng';
import { ENEMY_CONFIG } from '../../../../src/game/config/enemies';
import { ENEMY_KINDS } from '../../../../src/game/sim/enemy-kinds';
import { ENEMY_MODELS } from '../../../../src/game/view/enemies/enemy-models';

const AREA = { width: 480, height: 640 };

describe('ENEMY_KINDS', () => {
  it('P05-R01..R10: are the 10 enemies of the spec, in its order', () => {
    expect(() => {
      validateEnemyKinds(ENEMY_KINDS);
    }).not.toThrow();
    expect(ENEMY_KINDS.map((k) => k.name)).toEqual([
      'Gnat',
      'Hornet',
      'Scout',
      'Strafer',
      'Weaver',
      'Spinner',
      'Lancer',
      'Rocketeer',
      'Bulwark',
      'Splitter',
    ]);
  });

  it('P05-R01: a Gnat group is 5 Gnats', () => {
    const group = ENEMY_KINDS[0]?.spawn({ ...AREA, random: createRng(1) }) ?? [];
    expect(group).toHaveLength(ENEMY_CONFIG.gnat.groupSize);
  });

  it('P05-R11: every kind appears outside the playfield, with a model and its points', () => {
    for (const kind of ENEMY_KINDS) {
      for (const seed of [1, 2, 3]) {
        for (const enemy of kind.spawn({ ...AREA, random: createRng(seed) })) {
          const outside = enemy.y > AREA.height || enemy.x < 0 || enemy.x > AREA.width;
          expect(outside, kind.id).toBe(true);
          expect(ENEMY_MODELS[enemy.model], enemy.model).toBeTypeOf('function');
          expect(enemy.points).toBeGreaterThan(0);
        }
      }
    }
  });

  it('GD-50: tougher enemies score more points', () => {
    const stats = Object.values(ENEMY_CONFIG).map((c) => c.stats);
    for (const a of stats) {
      for (const b of stats) {
        if (a.health > b.health) expect(a.points).toBeGreaterThanOrEqual(b.points);
      }
    }
  });
});

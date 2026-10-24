import { describe, expect, it } from 'vitest';
import { validateEnemyKinds } from '../../../../src/core/entities/enemy';
import { createRng } from '../../../../src/core/math/rng';
import { ENEMY_CONFIG } from '../../../../src/game/config/enemies';
import { ENEMY_KINDS } from '../../../../src/game/sim/enemy-kinds';
import { ENEMY_MODELS } from '../../../../src/game/view/enemies/enemy-models';

const AREA = { width: 480, height: 640 };

describe('ENEMY_KINDS', () => {
  it('P05-R01..R10, P05-R12: are the 11 enemies of the spec, in its order', () => {
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
      'Carrier',
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

  it('P06-R07: a wave places the kinds that come from the top at its entry position', () => {
    const entry = { side: 'top', position: 0.25 } as const;
    for (const id of [
      'hornet',
      'scout',
      'weaver',
      'spinner',
      'lancer',
      'rocketeer',
      'bulwark',
      'carrier',
    ]) {
      const kind = ENEMY_KINDS.find((k) => k.id === id);
      for (const seed of [1, 2]) {
        const [enemy] = kind?.spawn({ ...AREA, random: createRng(seed), entry }) ?? [];
        expect(enemy?.x, id).toBe(120);
        expect(enemy?.y, id).toBeGreaterThan(AREA.height);
      }
    }
    // Positions are kept away from the corners.
    const scout = ENEMY_KINDS.find((k) => k.id === 'scout');
    const [edge] =
      scout?.spawn({ ...AREA, random: createRng(1), entry: { side: 'top', position: 0 } }) ?? [];
    expect(edge?.x).toBeCloseTo(0.08 * AREA.width);
  });

  it('P06-R07: a Strafer comes in from the side and at the height of its entry', () => {
    const strafer = ENEMY_KINDS.find((k) => k.id === 'strafer');
    const spawn = (side: 'left' | 'right') =>
      strafer?.spawn({ ...AREA, random: createRng(1), entry: { side, position: 0.75 } })[0];
    expect(spawn('left')?.x).toBeLessThan(0);
    expect(spawn('right')?.x).toBeGreaterThan(AREA.width);
    expect(spawn('left')?.y).toBe(480);
  });

  it('P06-R07: Gnats and Splitters follow their path from the side of the entry', () => {
    for (const id of ['gnat', 'splitter']) {
      const kind = ENEMY_KINDS.find((k) => k.id === id);
      const startX = (position: number) =>
        kind?.spawn({ ...AREA, random: createRng(1), entry: { side: 'top', position } })[0]?.x ??
        NaN;
      expect(startX(0.2), id).toBeLessThan(AREA.width / 2);
      expect(startX(0.8), id).toBeGreaterThan(AREA.width / 2);
      const fromLeft = kind?.spawn({
        ...AREA,
        random: createRng(1),
        entry: { side: 'left', position: 0.5 },
      });
      expect(fromLeft?.[0]?.x ?? NaN, id).toBeLessThan(AREA.width / 2);
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

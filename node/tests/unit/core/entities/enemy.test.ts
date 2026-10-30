import { describe, expect, it } from 'vitest';
import { validateEnemyKinds } from '../../../../src/core/entities/enemy';
import { Dropper, SAMPLE_ENEMY_KINDS } from '../../../fixtures/sample-enemies';

describe('Enemy', () => {
  it('P05: takes its numbers from its stats and starts nose down, at full health', () => {
    const enemy = new Dropper(10, 20);
    expect(enemy).toMatchObject({ x: 10, y: 20, radius: 10, health: 5, maxHealth: 5 });
    expect(enemy).toMatchObject({ model: 'cube', points: 7, heading: Math.PI, charge: 0 });
    expect(enemy.gone).toBe(false);
  });

  it('GD-43: fires its laser from its nose by default', () => {
    const enemy = new Dropper(10, 20);
    expect(enemy.emitter.x).toBeCloseTo(10);
    expect(enemy.emitter.y).toBeCloseTo(10);
    enemy.heading = Math.PI / 2;
    expect(enemy.emitter.x).toBeCloseTo(20);
  });
});

describe('validateEnemyKinds', () => {
  it('accepts distinct kinds and rejects none or duplicates', () => {
    expect(() => {
      validateEnemyKinds(SAMPLE_ENEMY_KINDS);
    }).not.toThrow();
    expect(() => {
      validateEnemyKinds([]);
    }).toThrow(/at least one/);
    const [kind] = SAMPLE_ENEMY_KINDS;
    if (!kind) throw new Error('no kind');
    expect(() => {
      validateEnemyKinds([kind, kind]);
    }).toThrow(/Duplicate enemy kind id "dropper"/);
  });
});

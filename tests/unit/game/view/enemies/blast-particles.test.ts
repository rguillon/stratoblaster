import { describe, expect, it } from 'vitest';
import { createRng } from '../../../../../src/core/math/rng';
import { ENEMY_LOOK } from '../../../../../src/game/config/enemy-look';
import { BlastParticles } from '../../../../../src/game/view/enemies/blast-particles';

const LOOK = ENEMY_LOOK.blasts;

describe('BlastParticles', () => {
  it('GD-62: a destroyed enemy makes a fireball and debris, which fade away', () => {
    const blasts = new BlastParticles(createRng(1));
    blasts.emit({ kind: 'enemy', x: 100, y: 200, radius: 20 });
    const first = blasts.step(0.05);
    expect(first.fireballs).toHaveLength(1);
    expect(first.fireballs[0]).toMatchObject({ x: 100, y: 200 });
    expect(first.debris.length).toBeGreaterThanOrEqual(LOOK.debris.min);
    for (let i = 0; i < 60; i++) blasts.step(1 / 60);
    expect(blasts.count).toBe(0);
  });

  it('GD-62: bigger enemies throw more debris; missiles blow up smaller', () => {
    const count = (kind: 'enemy' | 'missile', radius: number): number => {
      const blasts = new BlastParticles(createRng(1));
      blasts.emit({ kind, x: 0, y: 0, radius });
      return blasts.step(0.01).debris.length;
    };
    expect(count('enemy', 25)).toBeGreaterThan(count('enemy', 7));
    expect(count('missile', 25)).toBeLessThan(count('enemy', 25));
  });

  it('GD-62: the debris flies out from the blast', () => {
    const blasts = new BlastParticles(createRng(2));
    blasts.emit({ kind: 'enemy', x: 0, y: 0, radius: 20 });
    const near = blasts.step(0.01).debris.map((d) => Math.hypot(d.x, d.y));
    const far = blasts.step(0.2).debris.map((d) => Math.hypot(d.x, d.y));
    const mean = (v: number[]): number => v.reduce((a, b) => a + b, 0) / v.length;
    expect(mean(far)).toBeGreaterThan(mean(near));
  });
});

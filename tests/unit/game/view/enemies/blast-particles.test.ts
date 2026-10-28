import { describe, expect, it } from 'vitest';
import { createRng } from '../../../../../src/core/math/rng';
import { ENEMY_LOOK } from '../../../../../src/game/config/enemy-look';
import {
  BlastParticles,
  ramp,
  type BlastSpots,
} from '../../../../../src/game/view/enemies/blast-particles';

const LOOK = ENEMY_LOOK.blasts;

/** Runs a blast for `seconds` in 60 Hz frames, and returns every frame. */
function run(blasts: BlastParticles, seconds: number): BlastSpots[] {
  return Array.from({ length: Math.round(seconds * 60) }, () => blasts.step(1 / 60));
}

/** The last frame of `run`. */
function lastFrame(blasts: BlastParticles, seconds: number): BlastSpots {
  const frame = run(blasts, seconds).at(-1);
  if (!frame) throw new Error('no frame');
  return frame;
}

const mean = (v: readonly number[]): number => v.reduce((a, b) => a + b, 0) / v.length;

describe('BlastParticles', () => {
  it('GD-62: a destroyed enemy makes a ring, fireballs and debris, which all fade away; no flash lights the ground', () => {
    const blasts = new BlastParticles(createRng(1));
    blasts.emit({ kind: 'enemy', x: 100, y: 200, radius: 20 });
    const first = blasts.step(0.05);
    expect(first).not.toHaveProperty('flashes');
    expect(first.rings).toHaveLength(1);
    expect(first.fireballs[0]).toMatchObject({ x: 100, y: 200 });
    expect(first.debris.length).toBeGreaterThanOrEqual(LOOK.debris.min);
    run(blasts, 5);
    expect(blasts.count).toBe(0);
  });

  it('phase 5 review: fireballs go off one after the other, around the centre', () => {
    const blasts = new BlastParticles(createRng(3));
    blasts.emit({ kind: 'enemy', x: 0, y: 0, radius: 30 });
    const counts = run(blasts, 0.5).map((f) => f.fireballs.length);
    expect(counts[0]).toBeGreaterThan(0);
    expect(Math.max(...counts)).toBeGreaterThan(counts[0] ?? 0);
    expect(Math.max(...counts)).toBeGreaterThanOrEqual(LOOK.fireball.count[0]);
  });

  it('phase 5 review: fire cools from white hot to deep red, with smoke (P14-R07: shorter)', () => {
    const blasts = new BlastParticles(createRng(4));
    blasts.emit({ kind: 'enemy', x: 0, y: 0, radius: 20 });
    const hot = lastFrame(blasts, 1 / 60).fireballs[0];
    expect(hot?.b).toBeGreaterThan(0.5);
    const cool = lastFrame(blasts, 0.25).fireballs[0];
    expect(cool?.b).toBeLessThan(hot?.b ?? 0);
    const smoky = lastFrame(blasts, 0.1);
    expect(smoky.smoke.length).toBeGreaterThan(0);
    for (const s of smoky.smoke) expect(s.a).toBeLessThanOrEqual(LOOK.smoke.alpha);
  });

  it('phase 5 review: burning debris leaves embers and smoke along its way', () => {
    const blasts = new BlastParticles(createRng(5));
    blasts.emit({ kind: 'enemy', x: 0, y: 0, radius: 20 });
    const embers = blasts.step(0.001).embers.length;
    const frames = run(blasts, 0.3);
    const last = frames.at(-1);
    expect(last?.embers.length).toBeGreaterThan(embers);
    const far = (last?.smoke ?? []).filter((s) => Math.hypot(s.x, s.y) > 30);
    expect(far.length).toBeGreaterThan(0);
  });

  it('GD-62: bigger enemies throw more debris; missiles and small enemies blow up smaller', () => {
    const count = (kind: 'enemy' | 'missile', radius: number): number => {
      const blasts = new BlastParticles(createRng(1));
      blasts.emit({ kind, x: 0, y: 0, radius });
      return blasts.step(0.01).debris.length;
    };
    expect(count('enemy', 25)).toBeGreaterThan(count('enemy', 14));
    expect(count('missile', 25)).toBeLessThan(count('enemy', 25));
  });

  it('phase 5 review: tiny ships blow up small; big ones keep their full-size pieces', () => {
    const blast = (radius: number) => {
      const blasts = new BlastParticles(createRng(7));
      blasts.emit({ kind: 'enemy', x: 0, y: 0, radius });
      return blasts.step(0.01);
    };
    const tiny = blast(6);
    const big = blast(20);
    expect(tiny.fireballs[0]?.radius ?? 0).toBeLessThan((big.fireballs[0]?.radius ?? 0) / 2);
    expect(tiny.debris.length).toBeLessThan(big.debris.length / 2);
    const largest = (spots: readonly { radius: number }[]) =>
      Math.max(...spots.map((s) => s.radius));
    expect(largest(tiny.debris)).toBeLessThanOrEqual(LOOK.debris.size[1] * (6 / LOOK.fullRadius));
    expect(largest(big.debris)).toBeGreaterThan(LOOK.debris.size[0]);
  });

  it('GD-62: the debris flies out from the blast', () => {
    const blasts = new BlastParticles(createRng(2));
    blasts.emit({ kind: 'enemy', x: 0, y: 0, radius: 20 });
    const near = blasts.step(0.01).debris.map((d) => Math.hypot(d.x, d.y));
    const far = blasts.step(0.2).debris.map((d) => Math.hypot(d.x, d.y));
    expect(mean(far)).toBeGreaterThan(mean(near));
  });

  it('phase 5 review: no layer grows past its cap, however many blasts', () => {
    const blasts = new BlastParticles(createRng(6));
    for (let i = 0; i < 200; i++) blasts.emit({ kind: 'enemy', x: i, y: 0, radius: 40 });
    const spots = blasts.step(0.5);
    expect(spots.debris.length).toBeLessThanOrEqual(LOOK.cap);
    expect(spots.embers.length).toBeLessThanOrEqual(LOOK.cap);
  });
});

describe('ramp', () => {
  it('phase 5 review: blends the colours along t, clamped to its ends', () => {
    const colors = [
      [0, 0, 0],
      [1, 0.5, 0],
    ] as const;
    expect(ramp(colors, 0.5)).toEqual([0.5, 0.25, 0]);
    expect(ramp(colors, -1)).toEqual([0, 0, 0]);
    expect(ramp(colors, 2)).toEqual([1, 0.5, 0]);
  });
});

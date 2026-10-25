import { describe, expect, it } from 'vitest';
import { at } from '../../../helpers/at';
import { createRng } from '../../../../src/core/math/rng';
import { SampleBoss, SAMPLE_BOSS_STATS } from '../../../fixtures/sample-boss';
import { RecordingContext, run, runUntil } from '../../../helpers/enemy-context';

const AREA = { width: 300, height: 400, random: createRng(1) };

/** A sample boss already in place (it takes damage). */
function inPlace(): { boss: SampleBoss; ctx: RecordingContext } {
  const boss = new SampleBoss(AREA);
  const ctx = new RecordingContext();
  runUntil(boss, ctx, () => boss.state === 'fighting');
  return { boss, ctx };
}

const part = (boss: SampleBoss, id: string) => {
  const found = boss.parts.find((p) => p.spec.id === id);
  if (!found) throw new Error(id);
  return found;
};

describe('Boss', () => {
  it('P07-R01: its parts sit at their offsets around its centre and move with it', () => {
    const boss = new SampleBoss(AREA);
    expect(part(boss, 'gun')).toMatchObject({ x: boss.x - 20, y: boss.y });
    run(boss, new RecordingContext(), 0.5);
    expect(part(boss, 'plate')).toMatchObject({ x: boss.x + 20, y: boss.y });
  });

  it('P07-R01, P07-R05: it takes no damage while it comes in; then shots damage one part only', () => {
    const boss = new SampleBoss(AREA);
    expect(boss.state).toBe('entering');
    part(boss, 'gun').health -= 5;
    boss.core.health -= 5;
    expect(part(boss, 'gun').health).toBe(20);
    expect(boss.coreHealth).toBe(30);
    const { boss: ready } = inPlace();
    part(ready, 'gun').health -= 5;
    expect(part(ready, 'gun').health).toBe(15);
    expect(part(ready, 'plate').health).toBe(10);
    expect(ready.coreHealth).toBe(30);
    expect(part(ready, 'gun').sinceHit).toBe(0);
  });

  it('P07-R01: while a part that shields the core stands, the core takes no damage', () => {
    const { boss, ctx } = inPlace();
    expect(boss.coreShielded).toBe(true);
    boss.core.health -= 10;
    expect(boss.coreHealth).toBe(30);
    part(boss, 'gun').health = 0;
    run(boss, ctx, 1 / 60);
    // The plate does not shield the core.
    expect(boss.coreShielded).toBe(false);
    boss.core.health -= 10;
    expect(boss.coreHealth).toBe(20);
  });

  it('P07-R01: a destroyed part blows up and leaves the hit targets', () => {
    const { boss, ctx } = inPlace();
    expect(boss.hitTargets).toHaveLength(3);
    part(boss, 'plate').health -= 100;
    run(boss, ctx, 1 / 60);
    expect(ctx.broken).toEqual([part(boss, 'plate')]);
    expect(boss.hitTargets).toEqual([part(boss, 'gun'), boss.core]);
    expect(part(boss, 'plate').gone).toBe(true);
  });

  it('P07-R04: each destroyed part is a stage more, with a pause without fire', () => {
    const { boss, ctx } = inPlace();
    expect(boss.stage).toBe(0);
    part(boss, 'gun').health = 0;
    run(boss, ctx, 1 / 60);
    expect(boss.stage).toBe(1);
    expect(boss.pause).toBeGreaterThan(0.9);
    const fired = ctx.shots.length;
    run(boss, ctx, 0.95);
    expect(ctx.shots).toHaveLength(fired);
    run(boss, ctx, 1.2);
    expect(ctx.shots.length).toBeGreaterThan(fired);
  });

  it('P07-R01, P07-R06: at 0 core health it blows up over its death, parts with it, then is gone', () => {
    const { boss, ctx } = inPlace();
    part(boss, 'gun').health = 0;
    run(boss, ctx, 1 / 60);
    boss.core.health = 0;
    expect(boss.state).toBe('dying');
    expect(boss.parts.every((p) => p.destroyed)).toBe(true);
    expect(boss.hitTargets).toEqual([]);
    expect(boss.remainingHealth).toBe(0);
    // No stage change for the parts lost with it.
    expect(boss.stage).toBe(1);
    run(boss, ctx, 0.5);
    expect(boss.health).toBeGreaterThan(0);
    expect(ctx.blasts.length).toBeGreaterThanOrEqual(2);
    run(boss, ctx, 0.6);
    expect(boss.health).toBe(0);
    expect(ctx.blasts).toHaveLength(5);
  });

  it('P07-R02: its full health is its core and parts; what is left goes down with each hit', () => {
    const { boss } = inPlace();
    expect(boss.fullHealth).toBe(60);
    part(boss, 'gun').health -= 5;
    expect(boss.remainingHealth).toBe(55);
  });

  it('P07-R09: breakNext destroys its next part, then its core', () => {
    const boss = new SampleBoss(AREA);
    boss.breakNext();
    expect(part(boss, 'gun').destroyed).toBe(true);
    boss.breakNext();
    expect(part(boss, 'plate').destroyed).toBe(true);
    boss.breakNext();
    expect(boss.state).toBe('dying');
    boss.breakNext();
    expect(boss.state).toBe('dying');
  });

  it('P07-R05: it never expires, is not hurt by ramming, and drops a bonus from its core', () => {
    const boss = new SampleBoss(AREA);
    expect(boss.expires).toBe(false);
    expect(boss.rammable).toBe(false);
    expect(boss.dropChance).toBe(1);
    expect(part(boss, 'gun').dropChance).toBe(1);
  });

  it('P07-R05: orbiting parts turn around its centre with its spin, clockwise on screen', () => {
    const stats = {
      ...SAMPLE_BOSS_STATS,
      parts: [{ ...at(SAMPLE_BOSS_STATS.parts, 0), x: 0, y: 30, orbits: true }],
    };
    const boss = new SampleBoss(AREA, stats);
    boss.spin = Math.PI / 2;
    run(boss, new RecordingContext(), 1 / 60);
    const [ring] = boss.parts;
    expect(ring?.x).toBeCloseTo(boss.x + 30);
    expect(ring?.y).toBeCloseTo(boss.y);
  });

  it('P07-R04: lasers fired from a part or the core leave from in front of it, straight down', () => {
    const boss = new SampleBoss(AREA);
    expect(boss.core.emitter.x).toBeCloseTo(boss.x);
    expect(boss.core.emitter.y).toBeCloseTo(boss.y - 10);
    const gun = part(boss, 'gun');
    expect(gun.emitter.y).toBeCloseTo(gun.y - 8);
    expect(gun.heading).toBe(Math.PI);
  });
});

import { describe, expect, it } from 'vitest';
import { at } from '../../../helpers/at';
import {
  BossPattern,
  patternSignature,
  type BossVolley,
  type VolleySource,
} from '../../../../src/core/systems/boss-pattern';
import { Dropper } from '../../../fixtures/sample-enemies';
import { RecordingContext } from '../../../helpers/enemy-context';

const BULLET = { speed: 50, radius: 2, style: 'dot' };
const DEG = Math.PI / 180;

/** A piece at (x, y) firing down. */
const piece = (x: number, y: number): VolleySource => ({
  x,
  y,
  emitter: { x, y: y - 5 },
  heading: Math.PI,
  gone: false,
  health: 1,
});

/** Steps `pattern` for `seconds` at 60 Hz with every piece at (240, 500) except those in `lost`. */
function fire(pattern: BossPattern, seconds: number, lost: readonly string[] = []) {
  const ctx = new RecordingContext();
  const source = piece(240, 500);
  for (let t = 0; t < seconds - 1e-9; t += 1 / 60) {
    pattern.step(ctx, 1 / 60, (from) => (lost.includes(from) ? undefined : source));
  }
  return ctx;
}

const volley = (shape: BossVolley['shape'], every = 1, from = 'core'): BossVolley => ({
  from,
  every,
  shape,
});

describe('BossPattern', () => {
  it('P07-R04: an aimed fan is centred on the player', () => {
    const ctx = fire(
      new BossPattern([volley({ kind: 'aimed', count: 3, spacingDeg: 10, bullet: BULLET })]),
      1,
    );
    expect(ctx.shots).toHaveLength(3);
    // The player (240, 90) is straight below.
    expect(ctx.shots[1]?.heading).toBeCloseTo(Math.PI);
    expect(at(ctx.shots, 2).heading - at(ctx.shots, 1).heading).toBeCloseTo(10 * DEG);
  });

  it('P07-R04: a preset fan ignores the player; 0° is straight down, + to the right', () => {
    const shape = { kind: 'fan', headingDeg: 20, count: 1, spacingDeg: 0, bullet: BULLET } as const;
    const ctx = fire(new BossPattern([volley(shape)]), 1);
    expect(Math.sin(at(ctx.shots, 0).heading)).toBeGreaterThan(0);
    expect(ctx.shots[0]?.heading).toBeCloseTo(Math.PI - 20 * DEG);
  });

  it('P07-R04: a ring goes all around and turns at each volley (a spiral)', () => {
    const ctx = fire(
      new BossPattern([volley({ kind: 'ring', count: 4, turnDeg: 15, bullet: BULLET })]),
      2,
    );
    expect(ctx.shots).toHaveLength(8);
    expect(at(ctx.shots, 4).heading - at(ctx.shots, 0).heading).toBeCloseTo(15 * DEG);
    expect(at(ctx.shots, 1).heading - at(ctx.shots, 0).heading).toBeCloseTo(90 * DEG);
  });

  it('P07-R04: a burst fires its bullets one by one, `gap` apart', () => {
    const pattern = new BossPattern([
      volley({ kind: 'burst', count: 3, gap: 0.2, bullet: BULLET }),
    ]);
    expect(fire(pattern, 1.1).shots).toHaveLength(1);
    expect(fire(new BossPattern(pattern.volleys), 1.5).shots).toHaveLength(3);
  });

  it('P07-R04: missiles, lasers and launches', () => {
    const missile = {
      speed: 1,
      turnRateDeg: 1,
      homingSeconds: 1,
      radius: 1,
      health: 1,
      style: 'm',
    };
    const laser = { warningSeconds: 1, firingSeconds: 1, width: 4, style: 'l' };
    const ctx = fire(
      new BossPattern([
        volley({ kind: 'missiles', count: 2, spacingDeg: 20, missile }),
        volley({ kind: 'laser', laser }),
        volley({ kind: 'launch', launch: (x, y) => [new Dropper(x, y)] }),
      ]),
      1,
    );
    expect(ctx.shots.filter((s) => s.kind === 'missile')).toHaveLength(2);
    expect(ctx.lasers).toHaveLength(1);
    expect(ctx.spawned).toHaveLength(1);
  });

  it('P07-R04: the volleys of a destroyed part stop; a muzzle offsets where they leave', () => {
    const shape = { kind: 'aimed', count: 1, spacingDeg: 0, bullet: BULLET } as const;
    const pattern = new BossPattern([{ ...volley(shape, 1, 'gun'), muzzle: [5, -10] }]);
    expect(fire(pattern, 1).shots[0]).toMatchObject({ x: 245, y: 490 });
    expect(fire(new BossPattern(pattern.volleys), 3, ['gun']).shots).toHaveLength(0);
  });

  it('P06-R08, P07-R04: timers run faster with the level fire rate; `first` sets the first one', () => {
    const shape = { kind: 'aimed', count: 1, spacingDeg: 0, bullet: BULLET } as const;
    const pattern = new BossPattern([{ ...volley(shape, 2), first: 0.5 }]);
    expect(fire(pattern, 0.6).shots).toHaveLength(1);
    const fast = new BossPattern([volley(shape, 2)]);
    const ctx = new RecordingContext();
    ctx.fireRate = 2;
    for (let i = 0; i < 61; i++) fast.step(ctx, 1 / 60, () => piece(0, 0));
    expect(ctx.shots).toHaveLength(1);
    expect(fast.charge).toBeLessThan(0.1);
  });

  it('P07-R04: the signature names what still fires', () => {
    const a = volley({ kind: 'aimed', count: 1, spacingDeg: 0, bullet: BULLET }, 1, 'gun');
    const b = volley({ kind: 'ring', count: 6, turnDeg: 0, bullet: BULLET });
    const all = patternSignature([a, b], () => true);
    expect(patternSignature([b, a], () => true)).toBe(all);
    expect(patternSignature([a, b], (from) => from !== 'gun')).toBe(
      patternSignature([b], () => true),
    );
    expect(patternSignature([a, b], (from) => from !== 'gun')).not.toBe(all);
  });
});

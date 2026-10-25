import { describe, expect, it } from 'vitest';
import { at } from '../../../helpers/at';
import {
  BossPattern,
  patternSignature,
  type BossVolley,
  type VolleySource,
} from '../../../../src/core/systems/boss-pattern';
import { BossTurret } from '../../../../src/core/entities/boss-turret';
import { headingTo } from '../../../../src/core/systems/projectile-motion';
import { Dropper } from '../../../fixtures/sample-enemies';
import { RecordingContext } from '../../../helpers/enemy-context';

const BULLET = { speed: 50, radius: 2, style: 'dot' };
const DEG = Math.PI / 180;

/** A piece at (x, y) firing down; its muzzles are offsets from its centre. */
const piece = (x: number, y: number): VolleySource => ({
  x,
  y,
  emitter: { x, y: y - 5 },
  heading: Math.PI,
  gone: false,
  health: 1,
  place: ([dx, dy, height]) => ({ x: x + dx, y: y + dy, height }),
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

  it('P07-R04: the volleys of a destroyed part stop', () => {
    const shape = { kind: 'aimed', count: 1, spacingDeg: 0, bullet: BULLET } as const;
    const pattern = new BossPattern([volley(shape, 1, 'gun')]);
    expect(fire(pattern, 1).shots[0]).toMatchObject({ x: 240, y: 500 });
    expect(fire(new BossPattern(pattern.volleys), 3, ['gun']).shots).toHaveLength(0);
  });

  it('phase 7 review: bullets leave from the muzzle facing their way, side by side ones in turn', () => {
    const ring = { kind: 'ring', count: 2, turnDeg: 0, bullet: BULLET } as const;
    const muzzles = [
      [0, -10, 0],
      [0, 10, 0],
    ] as const;
    const ctx = fire(new BossPattern([{ ...volley(ring), muzzles }]), 1);
    // Down from the front muzzle, up from the back one.
    expect(ctx.shots.map((s) => s.y)).toEqual([490, 510]);
    const twin = { kind: 'fan', headingDeg: 0, count: 1, spacingDeg: 0, bullet: BULLET } as const;
    const sides = [
      [-3, -10, 0],
      [3, -10, 0],
    ] as const;
    const pairs = fire(new BossPattern([{ ...volley(twin), muzzles: sides }]), 2);
    expect(pairs.shots.map((s) => s.x)).toEqual([237, 243]);
  });

  it('phase 7 review: from a raised muzzle, bullets start where the camera sees it, aimed from there', () => {
    const shape = { kind: 'aimed', count: 1, spacingDeg: 0, bullet: BULLET } as const;
    const ctx = new RecordingContext();
    ctx.eye = { x: 240, y: -150, height: 550 };
    ctx.playerX = 100;
    const pattern = new BossPattern([{ ...volley(shape), muzzles: [[0, -10, 20]] }]);
    for (let t = 0; t < 1; t += 1 / 60) pattern.step(ctx, 1 / 60, () => piece(240, 500));
    const [shot] = ctx.shots;
    const seen = ctx.seen({ x: 240, y: 490, height: 20 });
    expect(shot).toMatchObject(seen);
    expect(seen.y).toBeGreaterThan(510);
    expect(shot?.heading).toBeCloseTo(headingTo(seen.x, seen.y, 100, 90));
  });

  it('phase 7 review: a turret follows the player while it fires at the player, and its shots leave its barrels', () => {
    const turret = new BossTurret({ x: 0, y: 0, turnRateDeg: 90 });
    const source: VolleySource = {
      ...piece(240, 500),
      turret,
      place: (m, onTurret) => {
        const [dx, dy, height] = onTurret ? turret.turned(m) : m;
        return { x: 240 + dx, y: 500 + dy, height };
      },
    };
    const ctx = new RecordingContext();
    // The player is down and to the right: 45° from straight down, counter-clockwise on screen.
    [ctx.playerX, ctx.playerY] = [340, 400];
    const shape = { kind: 'aimed', count: 1, spacingDeg: 0, bullet: BULLET } as const;
    const pattern = new BossPattern([
      { ...volley(shape, 1, 'gun'), muzzles: [[0, -10, 0]], turret: true },
    ]);
    const step = (seconds: number) => {
      for (let t = 0; t < seconds - 1e-9; t += 1 / 60) {
        pattern.turnTurrets(ctx, 1 / 60, () => source);
        pattern.step(ctx, 1 / 60, () => source);
      }
    };
    // At most 90°/s.
    step(0.25);
    expect(turret.aim).toBeCloseTo(-22.5 * DEG);
    step(0.75);
    expect(turret.aim).toBeCloseTo(-45 * DEG);
    // Its shot left the turned barrel, towards the player.
    const [shot] = ctx.shots;
    expect(shot?.x).toBeCloseTo(240 + 10 * Math.SQRT1_2);
    expect(shot?.y).toBeCloseTo(500 - 10 * Math.SQRT1_2);
    expect(shot?.heading).toBeCloseTo(135 * DEG);
    // A turret only firing preset fans turns back to rest.
    const fan = { kind: 'fan', headingDeg: 0, count: 1, spacingDeg: 0, bullet: BULLET } as const;
    const resting = new BossPattern([{ ...volley(fan, 1, 'gun'), turret: true }]);
    for (let i = 0; i < 60; i++) resting.turnTurrets(ctx, 1 / 60, () => source);
    expect(turret.aim).toBeCloseTo(0);
  });

  it('phase 7 review: a laser follows its piece from its muzzle', () => {
    const laser = { warningSeconds: 1, firingSeconds: 1, width: 4, style: 'l' };
    const ctx = fire(
      new BossPattern([{ ...volley({ kind: 'laser', laser }), muzzles: [[2, -30, 6]] }]),
      1,
    );
    expect(ctx.lasers[0]?.owner.emitter).toEqual({ x: 242, y: 470, height: 6 });
    expect(ctx.lasers[0]?.owner.heading).toBe(Math.PI);
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

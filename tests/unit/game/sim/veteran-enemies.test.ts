import { describe, expect, it } from 'vitest';
import { createRng } from '../../../../src/core/math/rng';
import { EnemyShots } from '../../../../src/core/systems/enemy-shots';
import { headingTo } from '../../../../src/core/systems/projectile-motion';
import { VETERAN_CONFIG as C } from '../../../../src/game/config/enemies-veteran';
import { DEG, DOWN } from '../../../../src/game/sim/enemies/enemy-helpers';
import { Mantis } from '../../../../src/game/sim/enemies/mantis';
import { Minelayer } from '../../../../src/game/sim/enemies/minelayer';
import { Mortar } from '../../../../src/game/sim/enemies/mortar';
import { Phantom } from '../../../../src/game/sim/enemies/phantom';
import { Wasp } from '../../../../src/game/sim/enemies/wasp';
import { ENEMY_KINDS } from '../../../../src/game/sim/enemy-kinds';
import { VETERAN_KINDS } from '../../../../src/game/sim/veteran-kinds';
import { at } from '../../../helpers/at';
import { RecordingContext, run, runUntil, type FiredShot } from '../../../helpers/enemy-context';

const AREA = { width: 480, height: 640 };
const angleDiff = (a: number, b: number): number =>
  Math.abs(Math.atan2(Math.sin(a - b), Math.cos(a - b)));
const sorted = (values: number[]): number[] => [...values].sort((a, b) => a - b);

/** The bullets `shot` (a bursting one) leaves after `seconds`, stepped by the shot system. */
function afterBurst(shot: FiredShot, seconds: number) {
  const shots = new EnemyShots({ ...AREA, cullMargin: 1000 });
  shots.fireBullet(shot.x, shot.y, shot.heading, shot.spec);
  for (let t = 0; t < seconds - 1e-9; t += 1 / 60) shots.step(1 / 60, 240, 90);
  return shots.bullets.filter((b) => b.alive);
}

/** Whether `headings` are `count` directions evenly all around, one along `first`. */
function expectRing(headings: number[], count: number, first: number): void {
  expect(headings).toHaveLength(count);
  const turns = sorted(
    headings.map((h) => (((h - first) % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI)),
  );
  turns.forEach((turn, k) => {
    expect(angleDiff(turn, (2 * Math.PI * k) / count)).toBeLessThan(1e-6);
  });
}

describe('P05-R14: Wasp', () => {
  it('P05-R14: a group of 3 Wasps comes in side by side from the top', () => {
    const kind = VETERAN_KINDS.find((k) => k.id === 'wasp');
    const group = kind?.spawn({ ...AREA, random: createRng(3) }) ?? [];
    expect(group).toHaveLength(C.wasp.groupSize);
    expect(group.every((w) => w instanceof Wasp)).toBe(true);
    const ys = new Set(group.map((w) => w.y));
    expect(ys.size).toBe(1);
    expect([...ys][0]).toBeGreaterThan(AREA.height);
    const xs = sorted(group.map((w) => w.x));
    expect(at(xs, 1) - at(xs, 0)).toBeCloseTo(C.wasp.groupSpacing);
    expect(at(xs, 2) - at(xs, 1)).toBeCloseTo(C.wasp.groupSpacing);
  });

  it('P05-R14: ends its pause firing its aimed fan of 3 once, then dives at where the player was', () => {
    const ctx = new RecordingContext();
    ctx.playerX = 120;
    const wasp = new Wasp(300, 700, 450);
    runUntil(wasp, ctx, () => wasp.state === 'aim');
    expect(ctx.shots).toHaveLength(0);
    const pause = runUntil(wasp, ctx, () => wasp.state === 'dive');
    expect(pause).toBeCloseTo(C.wasp.pause, 1);
    expect(ctx.shots).toHaveLength(C.wasp.fanCount);
    const aim = headingTo(wasp.x, wasp.y, ctx.playerX, ctx.playerY);
    const headings = sorted(ctx.shots.map((s) => s.heading - aim));
    headings.forEach((h, i) => {
      expect(h).toBeCloseTo((i - 1) * C.wasp.fanSpacing * DEG, 1);
    });
    expect(wasp.diveHeading).toBeCloseTo(aim);
    // The player moves away: it keeps its dive, and fires no more.
    ctx.playerX = 400;
    run(wasp, ctx, 0.5);
    expect(ctx.shots).toHaveLength(C.wasp.fanCount);
    expect(headingTo(300, 450, wasp.x, wasp.y)).toBeCloseTo(aim, 2);
  });

  it('P05-R14, P05-R23: launched below its stop height, it starts with its pause', () => {
    const ctx = new RecordingContext();
    const wasp = new Wasp(240, 300, 450);
    run(wasp, ctx, 1 / 60);
    expect(wasp.state).toBe('aim');
    expect(wasp.y).toBe(300);
  });
});

describe('P05-R15: Mortar', () => {
  it('P05-R15: lobs a shell at the player every 2.5 s, bursting into 8 bullets all around after 1.2 s', () => {
    const ctx = new RecordingContext();
    const mortar = new Mortar(300, 600);
    run(mortar, ctx, C.mortar.firstShot + 0.01);
    expect(ctx.shots).toHaveLength(1);
    const shell = at(ctx.shots, 0);
    expect(shell.heading).toBeCloseTo(headingTo(shell.x, shell.y, ctx.playerX, ctx.playerY));
    expect(shell.spec.speed).toBeLessThan(C.mortar.shell.burst.bullet.speed);
    // Just before the burst time, the shell alone; then its ring.
    expect(afterBurst(shell, C.mortar.shell.burst.after - 0.05)).toHaveLength(1);
    const ring = afterBurst(shell, C.mortar.shell.burst.after + 0.02);
    expectRing(
      ring.map((b) => b.heading),
      8,
      shell.heading,
    );
    run(mortar, ctx, C.mortar.fireInterval);
    expect(ctx.shots).toHaveLength(2);
    expect(mortar.y).toBeLessThan(600 - C.mortar.speed * 3);
  });
});

describe('P05-R16: Mantis', () => {
  const stopped = () => {
    const ctx = new RecordingContext();
    const mantis = new Mantis(240, 700, 480);
    runUntil(mantis, ctx, () => mantis.state === 'stay');
    ctx.shots.length = 0;
    return { ctx, mantis };
  };
  const arm = (mantis: Mantis, side: string) => {
    const found = mantis.parts.find((p) => p.spec.id === `${side}-arm`);
    if (!found) throw new Error(side);
    return found;
  };

  it('P05-R16: its arms are moving parts swinging out of step', () => {
    const { ctx, mantis } = stopped();
    const [left, right] = [arm(mantis, 'left'), arm(mantis, 'right')];
    expect(left.health).toBe(C.mantis.arm.health);
    const before = [left.heading, right.heading];
    run(mantis, ctx, 0.3);
    expect(left.heading).not.toBeCloseTo(at(before, 0));
    // Out of step: they are not mirror images of each other.
    expect(angleDiff(left.heading - DOWN, DOWN - right.heading)).toBeGreaterThan(0.05);
  });

  it('P05-R16: each living arm fires a pair straight along its current direction every 1.2 s', () => {
    const { ctx, mantis } = stopped();
    run(mantis, ctx, C.mantis.arm.fireInterval * 1.6);
    const along = ctx.shots.filter((s) => s.spec === C.mantis.arm.bullet);
    expect(along.length).toBeGreaterThanOrEqual(4);
    for (const side of ['left', 'right']) {
      const part = arm(mantis, side);
      // Fired this step or the one before at most.
      const pair = along.filter((s) => Math.hypot(s.x - part.x, s.y - part.y) < 20).slice(-2);
      expect(pair).toHaveLength(2);
      for (const shot of pair) expect(angleDiff(shot.heading, part.heading)).toBeLessThan(0.2);
    }
    // The headings of later pairs follow the swing.
    run(mantis, ctx, C.mantis.arm.fireInterval);
    const headings = new Set(
      ctx.shots.filter((s) => s.spec === C.mantis.arm.bullet).map((s) => s.heading.toFixed(3)),
    );
    expect(headings.size).toBeGreaterThan(2);
  });

  it('P05-R16: a destroyed arm no longer fires; the head keeps firing', () => {
    const { ctx, mantis } = stopped();
    arm(mantis, 'left').health = 0;
    run(mantis, ctx, 4);
    expect(ctx.broken).toHaveLength(1);
    const armShots = ctx.shots.filter((s) => s.spec === C.mantis.arm.bullet);
    const right = arm(mantis, 'right');
    expect(armShots.length).toBeGreaterThan(0);
    expect(armShots.every((s) => s.x > mantis.x)).toBe(true);
    expect(right.destroyed).toBe(false);
    const head = ctx.shots.filter((s) => s.spec === C.mantis.head.bullet);
    expect(head.length).toBeGreaterThanOrEqual(2);
    const last = at(head, head.length - 1);
    expect(last.heading).toBeCloseTo(headingTo(last.x, last.y, ctx.playerX, ctx.playerY));
  });

  it('P05-R16: stays 6 s, then leaves downward', () => {
    const { ctx, mantis } = stopped();
    const stay = runUntil(mantis, ctx, () => mantis.state === 'exit');
    expect(stay).toBeCloseTo(C.mantis.stay, 1);
    const y = mantis.y;
    run(mantis, ctx, 1);
    expect(mantis.y).toBeLessThan(y);
  });
});

describe('P05-R17: Phantom', () => {
  it('P05-R17: faded out, the player cannot shoot or ram it', () => {
    const ctx = new RecordingContext();
    const phantom = new Phantom(240, 700, 500);
    runUntil(phantom, ctx, () => phantom.state === 'fadeOut');
    expect(phantom.shotTargets).toContain(phantom);
    runUntil(phantom, ctx, () => phantom.state === 'hidden');
    expect(phantom.opacity).toBe(0);
    expect(phantom.cloaked).toBe(true);
    expect(phantom.shotTargets).toHaveLength(0);
    expect(phantom.hitTargets).toHaveLength(0);
  });

  it('P05-R17: reappears elsewhere in the upper half and fires its aimed spread of 5 from there', () => {
    const ctx = new RecordingContext();
    const phantom = new Phantom(240, 700, 500);
    runUntil(phantom, ctx, () => phantom.state === 'hidden');
    const hidden = runUntil(phantom, ctx, () => phantom.state === 'fadeIn');
    expect(hidden).toBeCloseTo(C.phantom.hidden, 1);
    expect(Math.hypot(phantom.x - 240, phantom.y - 500)).toBeGreaterThanOrEqual(
      C.phantom.jumpDistance,
    );
    expect(phantom.y).toBeGreaterThan(ctx.height / 2);
    expect(ctx.shots).toHaveLength(0);
    runUntil(phantom, ctx, () => phantom.state === 'hold');
    expect(ctx.shots).toHaveLength(C.phantom.spreadCount);
    expect(phantom.cloaked).toBe(false);
    const aim = headingTo(phantom.x, phantom.y, ctx.playerX, ctx.playerY);
    const turns = sorted(ctx.shots.map((s) => s.heading - aim));
    turns.forEach((t, i) => {
      expect(t).toBeCloseTo((i - 2) * C.phantom.spreadSpacing * DEG, 1);
    });
    for (const s of ctx.shots)
      expect(Math.hypot(s.x - phantom.x, s.y - phantom.y)).toBeLessThan(20);
  });

  it('P05-R17: jumps three times, then leaves upward', () => {
    const ctx = new RecordingContext();
    const phantom = new Phantom(240, 700, 500);
    runUntil(phantom, ctx, () => phantom.state === 'exit');
    expect(phantom.jumps).toBe(C.phantom.jumps);
    expect(ctx.shots).toHaveLength(C.phantom.jumps * C.phantom.spreadCount);
    const y = phantom.y;
    run(phantom, ctx, 1);
    expect(phantom.y).toBeGreaterThan(y);
  });
});

describe('P05-R18: Minelayer', () => {
  it('P05-R18: crosses sideways, dropping a mine every 0.8 s that bursts into 6 after 1.5 s', () => {
    const ctx = new RecordingContext();
    const layer = new Minelayer(0, 480, 'left');
    run(layer, ctx, C.minelayer.firstDrop + 2 * C.minelayer.dropInterval + 0.01);
    expect(layer.x).toBeGreaterThan(0);
    expect(layer.y).toBe(480);
    expect(ctx.shots).toHaveLength(3);
    for (const mine of ctx.shots) {
      expect(mine.heading).toBe(DOWN);
      expect(mine.spec).toBe(C.minelayer.mine);
      expectRing(
        afterBurst(mine, C.minelayer.mine.burst.after + 0.02).map((b) => b.heading),
        6,
        DOWN,
      );
    }
    // Dropped along its way, from the rack's hatches in turn.
    const xs = ctx.shots.map((s) => s.x);
    expect(at(xs, 1) - at(xs, 0)).toBeGreaterThan(0);
  });

  it('P05-R18: comes in from the side of the wave entry, in the top half', () => {
    const kind = VETERAN_KINDS.find((k) => k.id === 'minelayer');
    const area = {
      ...AREA,
      random: createRng(1),
      entry: { side: 'right', position: 0.1 },
    } as const;
    const [layer] = kind?.spawn(area) ?? [];
    expect(layer?.x).toBeGreaterThan(AREA.width);
    expect(layer?.y).toBeGreaterThanOrEqual(AREA.height / 2);
  });
});

describe('P05-R14..R18: the veteran kinds', () => {
  it('P05-R14..R18: five kinds, in ENEMY_KINDS, each spawning just outside the playfield', () => {
    expect(VETERAN_KINDS.map((k) => k.id)).toEqual([
      'wasp',
      'mortar',
      'mantis',
      'phantom',
      'minelayer',
    ]);
    for (const kind of VETERAN_KINDS) {
      expect(ENEMY_KINDS).toContain(kind);
      for (const entry of [undefined, { side: 'top', position: 0.3 } as const]) {
        const group = kind.spawn({ ...AREA, random: createRng(2), ...(entry && { entry }) });
        expect(group.length, kind.id).toBeGreaterThan(0);
        for (const e of group) {
          const outside = e.y > AREA.height || e.x < 0 || e.x > AREA.width;
          expect(outside, kind.id).toBe(true);
        }
      }
    }
  });

  it('P05-R14..R18: HP and points as tuned', () => {
    const stats = Object.values(C).map((c) => [c.stats.model, c.stats.health, c.stats.points]);
    expect(stats).toEqual([
      ['wasp', 30, 150],
      ['mortar', 140, 400],
      ['mantis', 160, 500],
      ['phantom', 90, 450],
      ['minelayer', 120, 400],
    ]);
  });
});

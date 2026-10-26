import { describe, expect, it } from 'vitest';
import type { Enemy, EnemyLaserSpec, LaserOwner } from '../../../../src/core/entities/enemy';
import type { JointedEnemy } from '../../../../src/core/entities/jointed-enemy';
import { createRng } from '../../../../src/core/math/rng';
import { EnemyShots } from '../../../../src/core/systems/enemy-shots';
import { headingTo, wrapAngle } from '../../../../src/core/systems/projectile-motion';
import { ShotWorld } from '../../../../src/core/systems/shot-world';
import { ELITE_CONFIG as C } from '../../../../src/game/config/enemies-elite';
import { ELITE_KINDS } from '../../../../src/game/sim/elite-kinds';
import { ENEMY_KINDS } from '../../../../src/game/sim/enemy-kinds';
import { Hive } from '../../../../src/game/sim/enemies/hive';
import { Hydra } from '../../../../src/game/sim/enemies/hydra';
import { Juggernaut } from '../../../../src/game/sim/enemies/juggernaut';
import { Orbiter } from '../../../../src/game/sim/enemies/orbiter';
import { Scissor } from '../../../../src/game/sim/enemies/scissor';
import { Wasp } from '../../../../src/game/sim/enemies/wasp';
import { RecordingContext, run, runUntil } from '../../../helpers/enemy-context';
import { testGun } from '../../../helpers/test-weapons';

const DEG = Math.PI / 180;
const DT = 1 / 60;

/** `value`, which the test expects to be there. */
function defined<T>(value: T | undefined, what: string): T {
  if (value === undefined) throw new Error(`no ${what}`);
  return value;
}

const partOf = (enemy: JointedEnemy, id: string) => {
  const found = enemy.parts.find((p) => p.spec.id === id);
  if (!found) throw new Error(id);
  return found;
};

/** Fires a stream of test bullets straight up from (x, y) at `targets` for `seconds`. */
function shootAt(enemy: Enemy, x: number, y: number, seconds = 0.4): void {
  const world = new ShotWorld({ width: 480, height: 640, cullMargin: 20 }, testGun());
  world.select(testGun(), 1);
  world.muzzleX = x;
  world.muzzleY = y;
  for (let t = 0; t < seconds; t += DT) {
    world.targets = [...enemy.shotTargets];
    world.step(DT);
  }
}

/** A context whose lasers really run (warning line, beam), stepped with the enemy. */
class LaserContext extends RecordingContext {
  readonly laserShots = new EnemyShots({ width: 480, height: 640, cullMargin: 20 });

  override fireLaser(owner: LaserOwner, spec: EnemyLaserSpec): void {
    super.fireLaser(owner, spec);
    this.laserShots.fireLaser(owner, spec);
  }

  /** Steps `enemy` then the lasers, as the enemy world does, for `seconds`. */
  run(enemy: Enemy, seconds: number): void {
    for (let t = 0; t < seconds - 1e-9; t += DT) {
      enemy.age += DT;
      enemy.update(this, DT);
      this.laserShots.step(DT, this.playerX, this.playerY);
    }
  }
}

describe('Elite kinds (P05-R19 to P05-R23)', () => {
  it('P05-R24: the five elite kinds are listed, each spawning just above the playfield', () => {
    expect(ELITE_KINDS.map((k) => k.id)).toEqual([
      'hydra',
      'orbiter',
      'scissor',
      'juggernaut',
      'hive',
    ]);
    expect(ELITE_KINDS.map((k) => k.name)).toEqual([
      'Hydra',
      'Orbiter',
      'Scissor',
      'Juggernaut',
      'Hive',
    ]);
    for (const kind of ELITE_KINDS) expect(ENEMY_KINDS).toContain(kind);
    const area = {
      width: 480,
      height: 640,
      random: createRng(3),
      entry: { side: 'top', position: 0.3 },
      topRange: [40, 440],
    } as const;
    for (const kind of ELITE_KINDS) {
      const [enemy, ...rest] = kind.spawn(area);
      expect(rest, kind.id).toHaveLength(0);
      expect(enemy?.y, kind.id).toBeGreaterThan(area.height);
      // The wave's entry, across the top range.
      expect(enemy?.x, kind.id).toBeCloseTo(40 + 400 * 0.3);
      expect(enemy?.points, kind.id).toBe(C[kind.id as keyof typeof C].stats.points);
    }
  });

  it('P05-R19: a Hydra in place fires aimed bullets with its living heads in turn, from each head', () => {
    const hydra = new Hydra(240, 700, 470);
    const ctx = new RecordingContext();
    runUntil(hydra, ctx, () => hydra.state === 'stay');
    expect(hydra.y).toBe(470);
    ctx.shots.length = 0;
    const order: number[] = [];
    for (let t = 0; t < 3; t += DT) {
      const before = ctx.shots.length;
      run(hydra, ctx, DT);
      const shot = ctx.shots[before];
      if (!shot) continue;
      // From the eye of one of the heads, where it is now, aimed at the player.
      const eyes = C.hydra.heads.map((h) => partOf(hydra, h.id).place(h.muzzle));
      const from = eyes.findIndex((e) => Math.hypot(e.x - shot.x, e.y - shot.y) < 1e-6);
      expect(from).toBeGreaterThanOrEqual(0);
      expect(shot.heading).toBeCloseTo(headingTo(shot.x, shot.y, ctx.playerX, ctx.playerY));
      order.push(from);
    }
    // One every 0.5 s, the heads in turn.
    expect(order).toHaveLength(6);
    order.forEach((head, i) => {
      if (i > 0) expect(head).toBe(((order[i - 1] ?? 0) + 1) % 3);
    });
    // The necks sway: the heads are not where they were drawn at rest.
    const head = partOf(hydra, 'head-left');
    expect(
      Math.hypot(head.x - hydra.x - head.spec.x, head.y - hydra.y - head.spec.y),
    ).toBeGreaterThan(1);
    // A destroyed head is skipped.
    partOf(hydra, 'head-middle').health = 0;
    ctx.shots.length = 0;
    run(hydra, ctx, 2);
    expect(ctx.shots).toHaveLength(4);
  });

  it('P05-R19: with every head destroyed a Hydra no longer fires but can still be destroyed', () => {
    const hydra = new Hydra(240, 700, 470);
    const ctx = new RecordingContext();
    runUntil(hydra, ctx, () => hydra.state === 'stay');
    for (const h of C.hydra.heads) partOf(hydra, h.id).health = 0;
    ctx.shots.length = 0;
    run(hydra, ctx, 3);
    expect(ctx.shots).toHaveLength(0);
    expect(ctx.broken).toHaveLength(3);
    shootAt(hydra, hydra.x, hydra.y - 40, 0.6);
    expect(hydra.health).toBeLessThan(C.hydra.stats.health);
  });

  it('P05-R19: a Hydra stays 7 s in the upper third, then leaves downward', () => {
    const hydra = new Hydra(240, 700, 470);
    const ctx = new RecordingContext();
    runUntil(hydra, ctx, () => hydra.state === 'stay');
    const stayed = runUntil(hydra, ctx, () => hydra.state === 'exit');
    expect(stayed).toBeCloseTo(C.hydra.stay, 1);
    run(hydra, ctx, 1);
    expect(hydra.y).toBeLessThan(470);
  });

  it("P05-R20: an Orbiter's drones turn around the core, and shots hitting a drone damage it, not the core", () => {
    const orbiter = new Orbiter(240, 500, 500);
    const ctx = new RecordingContext();
    const drone = partOf(orbiter, 'drone-0');
    const angle = () => Math.atan2(drone.x - orbiter.x, drone.y - orbiter.y);
    run(orbiter, ctx, DT);
    const before = angle();
    run(orbiter, ctx, 0.5);
    expect(wrapAngle(angle() - before)).toBeCloseTo(C.orbiter.spin * DEG * 0.5, 2);
    expect(Math.hypot(drone.x - orbiter.x, drone.y - orbiter.y)).toBeCloseTo(15.5, 5);
    // Wait until the drone passes under the core, then shoot up at the core's centre line.
    runUntil(orbiter, ctx, () => Math.abs(drone.x - orbiter.x) < 1.5 && drone.y < orbiter.y);
    shootAt(orbiter, orbiter.x, orbiter.y - 45, 0.45);
    expect(drone.health).toBeLessThan(C.orbiter.design.parts[0]?.health ?? 0);
    expect(orbiter.health).toBe(C.orbiter.stats.health);
  });

  it('P05-R20: an Orbiter fires a ring of 12 every 3 s, each drone an aimed bullet every 2 s', () => {
    const orbiter = new Orbiter(240, 500, 500);
    const ctx = new RecordingContext();
    run(orbiter, ctx, 6);
    const ring = ctx.shots.filter((s) => s.spec === C.orbiter.ringBullet);
    const aimed = ctx.shots.filter((s) => s.spec === C.orbiter.droneBullet);
    expect(ring).toHaveLength(24);
    // The drones in turn: at 1, 1.67 and 2.33 s, then every 2 s.
    expect(aimed).toHaveLength(8);
    for (const s of aimed) {
      expect(s.heading).toBeCloseTo(headingTo(s.x, s.y, ctx.playerX, ctx.playerY));
    }
  });

  it('P05-R21: each living Scissor arm shows a warning line for 1 s before its laser appears on the same line', () => {
    const scissor = new Scissor(240, 700, 512);
    const ctx = new LaserContext();
    // A long way in: the arms hold still until the lasers fire.
    for (let t = 0; t < 10 && scissor.state === 'enter'; t += DT) ctx.run(scissor, DT);
    expect(scissor.state).toBe('warn');
    const lasers = () => ctx.laserShots.lasers;
    expect(lasers().map((l) => l.spec.warningSeconds)).toEqual([1, 1]);
    const lines = lasers().map((l) => [l.x, l.y, l.heading]);
    // Along the arms, 25° out from straight down.
    expect(lines.map((l) => (l[2] ?? 0) / DEG).sort((a, b) => a - b)).toEqual([
      expect.closeTo(155, 3),
      expect.closeTo(205, 3),
    ]);
    ctx.run(scissor, 0.9);
    expect(lasers().map((l) => l.phase)).toEqual(['warning', 'warning']);
    let waited = 0.9;
    while (waited < 2 && !lasers().every((l) => l.phase === 'firing')) {
      ctx.run(scissor, DT);
      waited += DT;
    }
    expect(waited).toBeCloseTo(C.scissor.laser.warningSeconds, 1);
    expect(lasers()).toHaveLength(2);
    lasers().forEach((l, i) => {
      const [x, y, heading] = lines[i] ?? [];
      expect(l.x).toBeCloseTo(x ?? NaN, 0);
      expect(l.y).toBeCloseTo(y ?? NaN, 0);
      expect(l.heading / DEG).toBeCloseTo((heading ?? NaN) / DEG, 0);
    });
  });

  it("P05-R21: the Scissor's beams turn with their arms, closing 15°; a destroyed arm's laser stops", () => {
    const scissor = new Scissor(240, 700, 512);
    const ctx = new LaserContext();
    for (let t = 0; t < 10 && scissor.state !== 'fire'; t += DT) ctx.run(scissor, DT);
    ctx.run(scissor, 1);
    const [left, right] = [partOf(scissor, 'arm-left'), partOf(scissor, 'arm-right')];
    const beams = () => [...ctx.laserShots.lasers].sort((a, b) => b.heading - a.heading);
    expect(beams()).toHaveLength(2);
    // Half way: both closed some way in, the beams along the arms.
    expect(beams()[0]?.heading).toBeCloseTo(left.heading);
    expect(beams()[1]?.heading).toBeCloseTo(right.heading);
    expect(left.heading / DEG).toBeLessThan(200);
    expect(right.heading / DEG).toBeGreaterThan(160);
    ctx.run(scissor, 0.5);
    right.health = 0;
    ctx.run(scissor, DT);
    expect(beams()).toHaveLength(1);
    expect(beams()[0]?.owner.heading).toBeCloseTo(left.heading);
    runUntil(scissor, ctx, () => scissor.state === 'exit');
    // Closed by the sweep, and the arms stay so as it moves away.
    expect(left.heading / DEG).toBeCloseTo(180 + 25 - C.scissor.sweep, 0);
    ctx.run(scissor, 0.5);
    expect(left.heading / DEG).toBeCloseTo(180 + 25 - C.scissor.sweep, 0);
    expect(ctx.laserShots.lasers).toHaveLength(0);
    expect(scissor.y).toBeGreaterThan(512);
  });

  it('P05-R22: shots on a Juggernaut core do nothing while a plate stands; once both are destroyed it can be hit', () => {
    const jug = new Juggernaut(240, 500, 500);
    const ctx = new RecordingContext();
    run(jug, ctx, DT);
    // Just under its centre, past the plates: only the core is in the way.
    shootAt(jug, jug.x, jug.y - 3);
    expect(jug.health).toBe(C.juggernaut.stats.health);
    partOf(jug, 'plate-left').health = 0;
    shootAt(jug, jug.x, jug.y - 3);
    expect(jug.health).toBe(C.juggernaut.stats.health);
    partOf(jug, 'plate-right').health = 0;
    shootAt(jug, jug.x, jug.y - 3);
    expect(jug.health).toBeLessThan(C.juggernaut.stats.health);
  });

  it('P05-R22: each shoulder cannon fires bursts of 3 along its swinging barrel; the core a spread of 7 aimed', () => {
    const jug = new Juggernaut(240, 500, 500);
    const ctx = new RecordingContext();
    const bursts: number[] = [];
    for (let t = 0; t < 3.2; t += DT) {
      const before = ctx.shots.length;
      run(jug, ctx, DT);
      for (const s of ctx.shots.slice(before)) {
        if (s.spec !== C.juggernaut.cannonBullet) continue;
        // Along the barrel of the cannon it leaves from, as it is turned now.
        const cannon = C.juggernaut.cannons.find((c) => {
          const p = partOf(jug, c.id).place(c.muzzle);
          return Math.hypot(p.x - s.x, p.y - s.y) < 1e-6;
        });
        const joint = defined(cannon, 'cannon').joint;
        expect(s.heading).toBeCloseTo(Math.PI + jug.joints.angle(joint));
        bursts.push(t);
      }
    }
    // Two bursts in 3.2 s (after 0.8 s and 2.4 s), 3 bullets from each cannon.
    expect(bursts).toHaveLength(12);
    const spread = ctx.shots.filter((s) => s.spec === C.juggernaut.bullet);
    expect(spread).toHaveLength(7);
    const middle = defined(spread[3], 'middle bullet');
    expect(middle.heading).toBeCloseTo(headingTo(middle.x, middle.y, 240, 90));
  });

  it('P05-R13: a Juggernaut destroyed with its hull takes its standing parts with it', () => {
    const jug = new Juggernaut(240, 500, 500);
    const ctx = new RecordingContext();
    partOf(jug, 'cannon-left').health = 0;
    run(jug, ctx, DT);
    expect(ctx.broken).toHaveLength(1);
    jug.health = 0;
    jug.onDestroyed(ctx);
    expect(ctx.broken).toHaveLength(4);
  });

  it("P05-R23: when its launch timer runs out, a Wasp appears at the Hive's ring and attacks", () => {
    const hive = new Hive(240, 600);
    const ctx = new RecordingContext();
    runUntil(hive, ctx, () => ctx.spawned.length > 0);
    const wasp = ctx.spawned[0];
    expect(wasp).toBeInstanceOf(Wasp);
    const hatch = hive.hatch(ctx);
    expect(wasp?.x).toBeCloseTo(hatch.x);
    expect(wasp?.y).toBeCloseTo(hatch.y);
    // Every 4 s.
    const gap = runUntil(hive, ctx, () => ctx.spawned.length > 1);
    expect(gap).toBeCloseTo(C.hive.launchInterval, 1);
    // It attacks: its aimed fan.
    const waspCtx = new RecordingContext();
    if (wasp) run(wasp, waspCtx, 2);
    expect(waspCtx.shots.length).toBeGreaterThanOrEqual(3);
  });

  it('P05-R23: a Hive fires rings of 12, and neither fires nor launches in the lower part of the screen', () => {
    const hive = new Hive(240, 600);
    const ctx = new RecordingContext();
    run(hive, ctx, 4.5);
    expect(ctx.shots).toHaveLength(24);
    const low = new Hive(240, 0.29 * 640);
    const lowCtx = new RecordingContext();
    run(low, lowCtx, 8);
    expect(lowCtx.shots).toHaveLength(0);
    expect(lowCtx.spawned).toHaveLength(0);
    // Its ring turns.
    expect(low.spin).toBeCloseTo(C.hive.ringSpin * DEG * 8, 1);
  });
});

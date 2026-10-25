import { describe, expect, it } from 'vitest';
import { headingTo } from '../../../../src/core/systems/projectile-motion';
import { ENEMY_CONFIG as C } from '../../../../src/game/config/enemies';
import { Bulwark } from '../../../../src/game/sim/enemies/bulwark';
import { Gnat } from '../../../../src/game/sim/enemies/gnat';
import { Hornet } from '../../../../src/game/sim/enemies/hornet';
import { Lancer } from '../../../../src/game/sim/enemies/lancer';
import { Rocketeer } from '../../../../src/game/sim/enemies/rocketeer';
import { Scout } from '../../../../src/game/sim/enemies/scout';
import { Spinner } from '../../../../src/game/sim/enemies/spinner';
import { Splitter } from '../../../../src/game/sim/enemies/splitter';
import { Strafer } from '../../../../src/game/sim/enemies/strafer';
import { Weaver } from '../../../../src/game/sim/enemies/weaver';
import { DEG, playfieldPath } from '../../../../src/game/sim/enemies/enemy-helpers';
import { RecordingContext, run, runUntil } from '../../../helpers/enemy-context';

const SIZE = { width: 480, height: 640 };
const angleDiff = (a: number, b: number): number =>
  Math.abs(Math.atan2(Math.sin(a - b), Math.cos(a - b)));

describe('P05-R01: Gnat', () => {
  it('P05-R01: a group follows the same path with a fixed delay between them', () => {
    const ctx = new RecordingContext();
    const path = playfieldPath(C.gnat.path, SIZE, false);
    const gnats = [0, 1, 2, 3, 4].map((i) => new Gnat(path, i * C.gnat.groupDelay));
    for (const gnat of gnats) run(gnat, ctx, 2);
    for (let i = 1; i < gnats.length; i++) {
      const leader = gnats[i - 1];
      const follower = gnats[i];
      // The follower is where the leader was `groupDelay` earlier: one delay of travel behind.
      const behind = path.at(C.gnat.speed * (2 - i * C.gnat.groupDelay));
      // Within one step of travel.
      const off = Math.hypot((follower?.x ?? 0) - behind.x, (follower?.y ?? 0) - behind.y);
      expect(off).toBeLessThan(C.gnat.speed / 60 + 0.5);
      expect(follower?.y).toBeGreaterThan(leader?.y ?? 0);
    }
  });

  it('P05-R01: goes from the top of the screen to the bottom, and never shoots', () => {
    const ctx = new RecordingContext();
    const gnat = new Gnat(playfieldPath(C.gnat.path, SIZE, true), 0);
    expect(gnat.y).toBeGreaterThan(SIZE.height);
    runUntil(gnat, ctx, () => gnat.gone);
    expect(gnat.y).toBeLessThan(0);
    expect(ctx.shots).toHaveLength(0);
  });

  it('P05-R01: dies to one level 1 bullet (10 damage)', () => {
    expect(C.gnat.stats.health).toBe(10);
  });
});

describe('P05-R02: Hornet', () => {
  const hornet = (): Hornet => new Hornet(240, 700, { ...C.hornet, stopY: 460 });

  it('P05-R02: stops for 0.5 s while turning its nose to the player', () => {
    const ctx = new RecordingContext();
    ctx.playerX = 400;
    const h = hornet();
    runUntil(h, ctx, () => h.state === 'aim');
    expect(h.y).toBe(460);
    run(h, ctx, C.hornet.pause - 0.05);
    expect(h.state).toBe('aim');
    expect(h.y).toBe(460);
    expect(angleDiff(h.heading, headingTo(240, 460, 400, 90))).toBeLessThan(0.05);
  });

  it('P05-R02: dives towards the player position recorded at the end of the pause', () => {
    const ctx = new RecordingContext();
    const h = hornet();
    runUntil(h, ctx, () => h.state === 'dive');
    const aimed = headingTo(240, 460, ctx.playerX, ctx.playerY);
    expect(h.diveHeading).toBeCloseTo(aimed);
    // The player moves away: the dive does not follow.
    ctx.playerX = 20;
    const before = { x: h.x, y: h.y };
    run(h, ctx, 0.3);
    expect(headingTo(before.x, before.y, h.x, h.y)).toBeCloseTo(aimed);
  });

  it('P05-R02: accelerates while diving, and never shoots', () => {
    const ctx = new RecordingContext();
    const h = hornet();
    runUntil(h, ctx, () => h.state === 'dive');
    const travelled = (seconds: number): number => {
      const [x, y] = [h.x, h.y];
      run(h, ctx, seconds);
      return Math.hypot(h.x - x, h.y - y);
    };
    expect(travelled(0.1)).toBeLessThan(travelled(0.1));
    expect(ctx.shots).toHaveLength(0);
  });

  it('P05-R02, phase 5 review: brakes into the stop and dives from rest, without a jolt', () => {
    const ctx = new RecordingContext();
    const h = hornet();
    const dt = 1 / 60;
    let speed: number = C.hornet.entrySpeed;
    let jolt = 0;
    for (let t = 0; t < 2.4; t += dt) {
      const [x, y] = [h.x, h.y];
      run(h, ctx, dt);
      const now = Math.hypot(h.x - x, h.y - y) / dt;
      jolt = Math.max(jolt, Math.abs(now - speed));
      speed = now;
    }
    expect(h.state).toBe('dive');
    // The speed changes by no more than the braking or the dive acceleration allows in a step.
    const limit = Math.max(C.hornet.entryBrake, C.hornet.diveAcceleration) * dt;
    expect(jolt).toBeLessThan(limit * 1.5);
  });
});

describe('P05-R03: Scout', () => {
  it('P05-R03: flies straight down and fires a bullet aimed at the player every 1.5 s', () => {
    const ctx = new RecordingContext();
    ctx.playerX = 100;
    const scout = new Scout(300, 600);
    run(scout, ctx, C.scout.firstShot + 3 * C.scout.fireInterval + 0.01);
    expect(scout.x).toBe(300);
    expect(ctx.shots).toHaveLength(4);
    for (const shot of ctx.shots) {
      expect(shot.heading).toBeCloseTo(headingTo(shot.x, shot.y, 100, 90));
    }
  });

  it('P05-R03: only shoots over the playfield', () => {
    const ctx = new RecordingContext();
    const scout = new Scout(300, 800);
    run(scout, ctx, 2);
    expect(ctx.shots).toHaveLength(0);
  });
});

describe('P05-R04: Strafer', () => {
  it('P05-R04: crosses sideways in the top third', () => {
    const ctx = new RecordingContext();
    const strafer = new Strafer(-60, 512, 'left');
    run(strafer, ctx, 2);
    expect(strafer.x).toBeCloseTo(-60 + 2 * C.strafer.speed);
    expect(strafer.y).toBe(512);
    expect(strafer.heading).toBeCloseTo(Math.PI / 2);
    const back = new Strafer(540, 512, 'right');
    run(back, ctx, 1);
    expect(back.x).toBeLessThan(540);
  });

  it('P05-R04: fires 3 bullets at -15°, 0° and +15° from straight down, whatever the player', () => {
    const ctx = new RecordingContext();
    ctx.playerX = 0;
    const strafer = new Strafer(100, 512, 'left');
    run(strafer, ctx, 1.01);
    const headings = ctx.shots.map((s) => s.heading);
    expect(headings).toHaveLength(3);
    expect(headings[0]).toBeCloseTo(Math.PI - 15 * DEG);
    expect(headings[1]).toBeCloseTo(Math.PI);
    expect(headings[2]).toBeCloseTo(Math.PI + 15 * DEG);
  });
});

describe('P05-R05: Weaver', () => {
  it('P05-R05: its X is a sine of how far it has come down', () => {
    const ctx = new RecordingContext();
    const weaver = new Weaver(240, 700);
    for (const t of [0.5, 1, 1.5, 2]) {
      run(weaver, ctx, 0.5);
      const down = C.weaver.speed * t;
      expect(weaver.y).toBeCloseTo(700 - down);
      expect(weaver.x).toBeCloseTo(
        240 + C.weaver.amplitude * Math.sin((2 * Math.PI * down) / C.weaver.wavelength),
      );
    }
  });

  it("P05-R05: every 2 s fires a pair of bullets at the player, one from each hull's gun", () => {
    const ctx = new RecordingContext();
    const weaver = new Weaver(240, 600);
    run(weaver, ctx, C.weaver.fireInterval / 2 + 0.01);
    expect(ctx.shots).toHaveLength(2);
    const [left, right] = ctx.shots;
    // From the guns on the noses of its hulls, 20 px apart (phase 7 review).
    const gap = Math.hypot((right?.x ?? 0) - (left?.x ?? 0), (right?.y ?? 0) - (left?.y ?? 0));
    expect(gap).toBeCloseTo(20);
    for (const shot of ctx.shots) {
      expect(shot.heading).toBeCloseTo(headingTo(shot.x, shot.y, ctx.playerX, ctx.playerY));
    }
    run(weaver, ctx, C.weaver.fireInterval);
    expect(ctx.shots).toHaveLength(4);
  });
});

describe('P05-R06: Spinner', () => {
  it('P05-R06: stops in the upper half, then fires from its 4 pods in directions turning with the ring', () => {
    const ctx = new RecordingContext();
    const spinner = new Spinner(240, 700, 480);
    runUntil(spinner, ctx, () => spinner.state === 'fire');
    expect(spinner.y).toBe(480);
    run(spinner, ctx, 0.5);
    expect(ctx.shots.length).toBeGreaterThan(8);
    const pods = spinner.pods();
    expect(pods).toHaveLength(4);
    const first = ctx.shots[0]?.heading ?? 0;
    const last = ctx.shots.at(-1)?.heading ?? 0;
    expect(angleDiff(first, last)).toBeGreaterThan(0.1);
    for (const shot of ctx.shots.slice(0, 4)) {
      expect(Math.hypot(shot.x - 240, shot.y - 480)).toBeCloseTo(C.spinner.podRadius);
      // Outwards: along the line from the centre through the pod.
      expect(angleDiff(shot.heading, headingTo(240, 480, shot.x, shot.y))).toBeCloseTo(0);
    }
  });

  it('P05-R06: after 3 s of firing, stops firing and leaves upward', () => {
    const ctx = new RecordingContext();
    const spinner = new Spinner(240, 700, 480);
    runUntil(spinner, ctx, () => spinner.state === 'fire');
    run(spinner, ctx, C.spinner.fireDuration + 0.05);
    expect(spinner.state).toBe('exit');
    const count = ctx.shots.length;
    run(spinner, ctx, 1);
    expect(ctx.shots).toHaveLength(count);
    expect(spinner.y).toBeGreaterThan(480);
  });
});

describe('P05-R07: Lancer', () => {
  it('P05-R07: stops at its point and fires its laser (warning first) without moving', () => {
    const ctx = new RecordingContext();
    const lancer = new Lancer(200, 700, 512);
    runUntil(lancer, ctx, () => lancer.state === 'attack');
    expect(lancer.y).toBe(512);
    expect(ctx.lasers).toHaveLength(1);
    expect(ctx.lasers[0]?.spec).toMatchObject({ warningSeconds: 1, firingSeconds: 1.5 });
    expect(lancer.emitter.x).toBeCloseTo(200);
    expect(lancer.emitter.y).toBeCloseTo(512 - C.lancer.emitterOffset);
    run(lancer, ctx, 0.5);
    expect(lancer.charge).toBeCloseTo(0.5, 1);
    run(lancer, ctx, 1.9);
    expect(lancer).toMatchObject({ state: 'attack', x: 200, y: 512 });
    run(lancer, ctx, 0.2);
    expect(lancer.state).toBe('exit');
    run(lancer, ctx, 0.5);
    expect(lancer.y).toBeGreaterThan(512);
    expect(ctx.lasers).toHaveLength(1);
  });
});

describe('P05-R08: Rocketeer', () => {
  it('P05-R08: descends slowly and launches a missile from each pod every 3 s', () => {
    const ctx = new RecordingContext();
    const rocketeer = new Rocketeer(240, 600);
    run(rocketeer, ctx, C.rocketeer.firstShot + 0.01);
    expect(ctx.shots.map((s) => s.kind)).toEqual(['missile', 'missile']);
    expect(ctx.shots[0]?.x).toBeCloseTo(240 - C.rocketeer.podOffset);
    expect(ctx.shots[1]?.x).toBeCloseTo(240 + C.rocketeer.podOffset);
    expect(rocketeer.charge).toBeLessThan(0.1);
    run(rocketeer, ctx, C.rocketeer.fireInterval);
    expect(ctx.shots).toHaveLength(4);
    expect(rocketeer.y).toBeCloseTo(
      600 - C.rocketeer.speed * (C.rocketeer.firstShot + 0.01 + 3),
      0,
    );
  });

  it('P05-R08: its missiles can be shot down', () => {
    expect(C.rocketeer.missile.health).toBeGreaterThan(0);
  });
});

describe('P05-R09: Bulwark', () => {
  it('P05-R09: comes down to the upper third, drifts for 8 s, then leaves downward', () => {
    const ctx = new RecordingContext();
    const bulwark = new Bulwark(240, 700, 474);
    runUntil(bulwark, ctx, () => bulwark.state === 'drift');
    expect(bulwark.y).toBe(474);
    run(bulwark, ctx, 1);
    expect(bulwark.x).not.toBeCloseTo(240);
    run(bulwark, ctx, C.bulwark.stay - 1 + 0.05);
    expect(bulwark.state).toBe('exit');
    run(bulwark, ctx, 1);
    expect(bulwark.y).toBeLessThan(474);
  });

  it('P05-R09: fires a spread of 5 bullets 10° apart, the middle one aimed at the player', () => {
    const ctx = new RecordingContext();
    ctx.playerX = 100;
    const bulwark = new Bulwark(240, 600, 474);
    run(bulwark, ctx, C.bulwark.fireInterval / 2 + 0.01);
    expect(ctx.shots).toHaveLength(5);
    const [middle] = ctx.shots.slice(2, 3);
    expect(middle?.heading).toBeCloseTo(headingTo(middle?.x ?? 0, middle?.y ?? 0, 100, 90));
    const headings = ctx.shots.map((s) => s.heading);
    for (let i = 1; i < 5; i++) {
      expect((headings[i] ?? 0) - (headings[i - 1] ?? 0)).toBeCloseTo(10 * DEG);
    }
  });
});

describe('P05-R10: Splitter', () => {
  it('P05-R10: follows its curved path and fires an aimed bullet every 2.5 s', () => {
    const ctx = new RecordingContext();
    const splitter = new Splitter(playfieldPath(C.splitter.path, SIZE, false));
    runUntil(splitter, ctx, () => splitter.y < SIZE.height);
    const start = ctx.shots.length;
    run(splitter, ctx, C.splitter.firstShot + C.splitter.fireInterval + 0.01);
    expect(ctx.shots.length - start).toBe(2);
    for (const shot of ctx.shots) {
      expect(shot.heading).toBeCloseTo(headingTo(shot.x, shot.y, ctx.playerX, ctx.playerY));
    }
  });

  it('P05-R10: when destroyed, 3 pods appear at its position and dive at the player', () => {
    const ctx = new RecordingContext();
    const splitter = new Splitter(playfieldPath(C.splitter.path, SIZE, false));
    run(splitter, ctx, 3);
    splitter.onDestroyed(ctx);
    expect(ctx.spawned).toHaveLength(3);
    for (const pod of ctx.spawned) {
      expect(pod).toBeInstanceOf(Hornet);
      expect(pod.model).toBe('splitter-pod');
      expect(Math.hypot(pod.x - splitter.x, pod.y - splitter.y)).toBeCloseTo(C.splitter.podOffset);
      const hornet = pod as Hornet;
      expect(hornet.state).toBe('aim');
      runUntil(hornet, ctx, () => hornet.state === 'dive');
      expect(hornet.diveHeading).toBeCloseTo(
        headingTo(hornet.x, hornet.y, ctx.playerX, ctx.playerY),
        1,
      );
    }
  });
});

import { describe, expect, it } from 'vitest';
import { at } from '../../../helpers/at';
import { createRng } from '../../../../src/core/math/rng';
import { patternSignature } from '../../../../src/core/systems/boss-pattern';
import type { BossDesign } from '../../../../src/game/config/bosses/boss-kit';
import { WORLD_1_BOSSES } from '../../../../src/game/config/world-1/bosses';
import { WORLD_2_BOSSES } from '../../../../src/game/config/world-2/bosses';
import { BOSS_DESIGNS, BOSS_KINDS } from '../../../../src/game/sim/boss-kinds';
import { WorldBoss } from '../../../../src/game/sim/bosses/world-boss';
import { WORLD_2 } from '../../../../src/game/sim/world-2';
import { bossRun, fightBoss } from '../../../helpers/boss-bot';
import { RecordingContext, run, runUntil } from '../../../helpers/enemy-context';

/** The ship's reach at the bottom of the screen (D-048). */
const REACH = [107, 373] as const;
const AREA = { width: 480, height: 640, random: createRng(1), topRange: REACH };

const design = (id: string): BossDesign => {
  const found = BOSS_DESIGNS.find((d) => d.id === id);
  if (!found) throw new Error(id);
  return found;
};
const fullHealth = (d: BossDesign): number =>
  d.stats.parts.reduce((sum, p) => sum + p.health, d.stats.health);
const increasing = (values: readonly number[]) =>
  values.every((v, i) => i === 0 || v > (values[i - 1] ?? 0));
const W2 = Object.values(WORLD_2_BOSSES);
const W2_IDS = new Set(W2.flatMap((l) => [l.mini, l.final]));
const W2_DESIGNS = BOSS_DESIGNS.filter((d) => W2_IDS.has(d.id));

/** Every order the parts can be destroyed in. */
function orders(ids: readonly string[]): string[][] {
  if (ids.length === 0) return [[]];
  return ids.flatMap((id) =>
    orders(ids.filter((other) => other !== id)).map((rest) => [id, ...rest]),
  );
}

describe('World 2 bosses', () => {
  it('P08-R10: each level has one mini boss and one final boss of the table', () => {
    expect(WORLD_2.map((l) => (l.bosses ?? []).map((b) => `${b.rank}:${b.kind}`))).toEqual([
      ['mini:floe-breaker', 'final:narwhal'],
      ['mini:fjord-lynx', 'final:harbour-kraken'],
      ['mini:snow-owl', 'final:aurora-station'],
      ['mini:avalanche', 'final:glacier-colossus'],
      ['mini:ice-queen', 'final:boreal-citadel'],
    ]);
    expect(W2_DESIGNS.map((d) => d.stats.name)).toEqual([
      'Floe Breaker',
      'Narwhal',
      'Fjord Lynx',
      'Harbour Kraken',
      'Snow Owl',
      'Aurora Station',
      'Avalanche',
      'Glacier Colossus',
      'Ice Queen',
      'Boreal Citadel',
    ]);
    expect(new Set(BOSS_KINDS.map((k) => k.id)).size).toBe(20);
  });

  it('P08-R10: mini bosses have 2 or 3 destroyable parts, final bosses 4 to 6', () => {
    for (const { mini, final } of W2) {
      const [m, f] = [design(mini).stats.parts.length, design(final).stats.parts.length];
      expect(m, mini).toBeGreaterThanOrEqual(2);
      expect(m, mini).toBeLessThanOrEqual(3);
      expect(f, final).toBeGreaterThanOrEqual(4);
      expect(f, final).toBeLessThanOrEqual(6);
    }
  });

  it('P08-R10: the sizes and fight ground speeds of the table; one stops, one chases', () => {
    const size = (id: string) => (design(id).stats.radius * 2) / 34;
    const speed = (id: string) => design(id).stats.groundSpeed;
    expect(W2.map((l) => [size(l.mini), size(l.final)])).toEqual([
      [3, 5],
      [3, 5],
      [3, 5],
      [3.5, 5.5],
      [3.5, 6],
    ]);
    expect(W2.map((l) => [speed(l.mini), speed(l.final)])).toEqual([
      [0.5, 1.5],
      [0.6, 0],
      [0.5, 0.4],
      [1.4, 0.3],
      [0.6, 0.25],
    ]);
  });

  it('P07-R01: some part shields each core, and no shielding part hides right behind it', () => {
    for (const d of W2_DESIGNS) {
      expect(
        d.stats.parts.some((p) => p.shieldsCore),
        d.id,
      ).toBe(true);
      for (const p of d.stats.parts.filter((part) => part.shieldsCore && !part.orbits)) {
        const behind = p.y > 0 && Math.abs(p.x) < d.stats.coreRadius + 4;
        expect(behind, `${d.id} ${p.id}`).toBe(false);
      }
    }
  });

  it('P07-R04: every stage fires another pattern than the one before, whatever the order', () => {
    for (const d of W2_DESIGNS) {
      const ids = d.stats.parts.map((p) => p.id);
      expect(d.stages, d.id).toHaveLength(ids.length + 1);
      for (const order of orders(ids)) {
        const signatures = d.stages.map((stage, k) => {
          const lost = new Set(order.slice(0, k));
          return patternSignature(stage, (from) => !lost.has(from));
        });
        for (let k = 1; k < signatures.length; k++)
          expect(signatures[k], `${d.id} ${order.join('>')}`).not.toBe(signatures[k - 1]);
        expect(signatures.slice(0, -1), `${d.id} last`).not.toContain(signatures.at(-1));
      }
    }
  });

  it('P08-R10: in a long fight, every boss keeps its hit circles inside the ship’s reach (D-048)', () => {
    for (const d of W2_DESIGNS) {
      const boss = new WorldBoss(d, AREA);
      const ctx = new RecordingContext();
      runUntil(boss, ctx, () => boss.state === 'fighting');
      for (let t = 0; t < 60; t += 0.25) {
        run(boss, ctx, 0.25);
        for (const target of boss.hitTargets) {
          expect(target.x - target.radius, d.id).toBeGreaterThanOrEqual(REACH[0] - 1e-6);
          expect(target.x + target.radius, d.id).toBeLessThanOrEqual(REACH[1] + 1e-6);
        }
      }
    }
  });

  /** The headings of the shots of a Fjord Lynx over `seconds`, the player at `playerX`. */
  function lynxShots(playerX: number, radarDown: boolean): number[] {
    const boss = new WorldBoss(design('fjord-lynx'), AREA);
    const ctx = new RecordingContext();
    ctx.playerX = playerX;
    runUntil(boss, ctx, () => boss.state === 'fighting');
    if (radarDown) {
      boss.parts.find((p) => p.spec.id === 'radar-mast')?.destroy();
      // Its pause and its anger (phase 7 review), then the new stage.
      run(boss, ctx, 1 + 3 + 0.5);
    }
    const before = ctx.shots.length;
    run(boss, ctx, 8);
    return ctx.shots.slice(before).map((s) => Math.round(s.heading * 1000) / 1000);
  }

  it('P08-R10: the Fjord Lynx aims at the player while its radar mast stands, then fires preset fans', () => {
    const [left, right] = [lynxShots(140, false), lynxShots(340, false)];
    expect(left.length).toBeGreaterThan(5);
    expect(left).not.toEqual(right);
    const [afterLeft, afterRight] = [lynxShots(140, true), lynxShots(340, true)];
    expect(afterLeft.length).toBeGreaterThan(5);
    expect(afterLeft).toEqual(afterRight);
  });

  it('P08-R11: full health goes up from 2-1 to 2-5; each final outlasts its mini boss', () => {
    const minis = W2.map((l) => fullHealth(design(l.mini)));
    const finals = W2.map((l) => fullHealth(design(l.final)));
    expect(increasing(minis)).toBe(true);
    expect(increasing(finals)).toBe(true);
    finals.forEach((f, i) => {
      expect(f).toBeGreaterThan(minis[i] ?? Infinity);
    });
  });

  it('P08-R11: each World 2 boss has more full health than the World 1 boss of its level and kind', () => {
    const w1 = Object.values(WORLD_1_BOSSES);
    W2.forEach((l, i) => {
      const w = at(w1, i);
      expect(fullHealth(design(l.mini)), l.mini).toBeGreaterThan(fullHealth(design(w.mini)));
      expect(fullHealth(design(l.final)), l.final).toBeGreaterThan(fullHealth(design(w.final)));
    });
  });

  /** The speeds of the bullets `d` fires (stages and anger, bursts included). */
  const bulletSpeeds = (d: BossDesign): Set<number> => {
    const speeds = new Set<number>();
    for (const { shape } of [...d.stages.flat(), ...(d.rage ?? [])]) {
      if (!('bullet' in shape)) continue;
      speeds.add(shape.bullet.speed);
      if (shape.bullet.burst) speeds.add(shape.bullet.burst.bullet.speed);
    }
    return speeds;
  };

  /** The speeds of the boss bullets in flight over 20 s of `level`'s mini boss, unscaled. */
  const firedSpeeds = (level: (typeof WORLD_2)[number], at: number): Set<number> => {
    const r = bossRun(level);
    r.seek(at / r.track.speed);
    const seen = new Set<number>();
    for (let t = 0; t < 20; t += 1 / 60) {
      r.step(1 / 60, { move: { x: 0, y: 0 }, fire: false });
      for (const b of r.enemies.shots.bullets.filter((bullet) => bullet.alive)) {
        seen.add(Math.round((b.speed / level.difficulty.bulletSpeed) * 1000) / 1000);
      }
    }
    return seen;
  };

  it('P08-R11: the boss bullets use the level’s bullet speed factor', () => {
    for (const level of WORLD_2) {
      const boss = level.bosses?.find((b) => b.rank === 'mini');
      if (!boss) throw new Error(level.id);
      const speeds = bulletSpeeds(design(boss.kind));
      const seen = firedSpeeds(level, boss.at);
      expect(seen.size, level.id).toBeGreaterThan(0);
      for (const speed of seen)
        expect(speeds.has(speed), `${level.id} ${String(speed)}`).toBe(true);
    }
  });

  it.each(WORLD_2.map((l, i) => [l.id, i] as const))(
    'P08-R11: in %s, a player with guns at level 3 always on target needs the planned fight times',
    (_id, i) => {
      // Tunable values: mini 30–40 s in 2-1 up to 45–55 s in 2-5, final 60–80 s up to 100–130 s.
      const lerp = (a: number, b: number) => a + ((b - a) * i) / 4;
      const level = at(WORLD_2, i);
      const mini = fightBoss(bossRun(level), 'mini');
      const final = fightBoss(bossRun(level), 'final');
      expect(mini).toBeGreaterThanOrEqual(lerp(30, 45));
      expect(mini).toBeLessThanOrEqual(lerp(40, 55));
      expect(final).toBeGreaterThanOrEqual(lerp(60, 100));
      expect(final).toBeLessThanOrEqual(lerp(80, 130));
    },
  );
});

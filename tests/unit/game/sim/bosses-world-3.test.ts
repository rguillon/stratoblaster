import { describe, expect, it } from 'vitest';
import { at } from '../../../helpers/at';
import { createRng } from '../../../../src/core/math/rng';
import { patternSignature } from '../../../../src/core/systems/boss-pattern';
import type { BossDesign } from '../../../../src/game/config/bosses/boss-kit';
import { WORLD_2_BOSSES } from '../../../../src/game/config/world-2/bosses';
import { WORLD_3_BOSSES } from '../../../../src/game/config/world-3/bosses';
import { BOSS_DESIGNS, BOSS_KINDS } from '../../../../src/game/sim/boss-kinds';
import { WorldBoss } from '../../../../src/game/sim/bosses/world-boss';
import { WORLD_3 } from '../../../../src/game/sim/world-3';
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
const W3 = Object.values(WORLD_3_BOSSES);
const W3_IDS = new Set(W3.flatMap((l) => [l.mini, l.final]));
const W3_DESIGNS = BOSS_DESIGNS.filter((d) => W3_IDS.has(d.id));

/** Every order the parts can be destroyed in. */
function orders(ids: readonly string[]): string[][] {
  if (ids.length === 0) return [[]];
  return ids.flatMap((id) =>
    orders(ids.filter((other) => other !== id)).map((rest) => [id, ...rest]),
  );
}

describe('World 3 bosses', () => {
  it('P09-R09: each level has one mini boss and one final boss of the table', () => {
    expect(WORLD_3.map((l) => (l.bosses ?? []).map((b) => `${b.rank}:${b.kind}`))).toEqual([
      ['mini:mangrove-croc', 'final:river-leviathan'],
      ['mini:toucan', 'final:canopy-spider'],
      ['mini:stone-idol', 'final:sky-temple'],
      ['mini:mosquito', 'final:dam-breaker'],
      ['mini:jaguar', 'final:verdant-crown'],
    ]);
    expect(W3_DESIGNS.map((d) => d.stats.name)).toEqual([
      'Mangrove Croc',
      'River Leviathan',
      'Toucan',
      'Canopy Spider',
      'Stone Idol',
      'Sky Temple',
      'Mosquito',
      'Dam Breaker',
      'Jaguar',
      'Verdant Crown',
    ]);
    expect(new Set(BOSS_KINDS.map((k) => k.id)).size).toBe(40);
  });

  it('P09-R09: mini bosses have 2 or 3 destroyable parts, final bosses 4 to 6', () => {
    for (const { mini, final } of W3) {
      const [m, f] = [design(mini).stats.parts.length, design(final).stats.parts.length];
      expect(m, mini).toBeGreaterThanOrEqual(2);
      expect(m, mini).toBeLessThanOrEqual(3);
      expect(f, final).toBeGreaterThanOrEqual(4);
      expect(f, final).toBeLessThanOrEqual(6);
    }
  });

  it('P09-R09: the sizes and fight ground speeds of the table; one stops, one chases', () => {
    expect(
      W3.some(
        (l) => design(l.mini).stats.groundSpeed === 0 || design(l.final).stats.groundSpeed === 0,
      ),
    ).toBe(true);
    expect(
      W3.some((l) => design(l.mini).stats.groundSpeed > 1 || design(l.final).stats.groundSpeed > 1),
    ).toBe(true);
    const size = (id: string) => (design(id).stats.radius * 2) / 34;
    const speed = (id: string) => design(id).stats.groundSpeed;
    expect(W3.map((l) => [size(l.mini), size(l.final)])).toEqual([
      [3, 6],
      [3, 5],
      [3, 5.5],
      [3, 5.5],
      [3.5, 6],
    ]);
    expect(W3.map((l) => [speed(l.mini), speed(l.final)])).toEqual([
      [1.4, 0.5],
      [0.6, 0.4],
      [0, 0.3],
      [0.6, 0.3],
      [0.6, 0.25],
    ]);
  });

  it('P07-R01: some part shields each core, and no shielding part hides right behind it', () => {
    for (const d of W3_DESIGNS) {
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
    for (const d of W3_DESIGNS) {
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

  it('P09-R09: in a long fight, every boss keeps its hit circles inside the ship’s reach (D-048), the River Leviathan’s swaying segments included', () => {
    for (const d of W3_DESIGNS) {
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

  it('P09-R09: the River Leviathan’s segments and the Canopy Spider’s legs move with their joints', () => {
    for (const [id, minimum] of [
      ['river-leviathan', 4],
      ['canopy-spider', 2],
    ] as const) {
      const boss = new WorldBoss(design(id), AREA);
      const ctx = new RecordingContext();
      runUntil(boss, ctx, () => boss.state === 'fighting');
      const offsets = () => boss.parts.map((p) => [p.x - boss.x, p.y - boss.y] as const);
      const before = offsets();
      let moved = 0;
      for (let t = 0; t < 6; t += 0.25) {
        run(boss, ctx, 0.25);
        offsets().forEach(([x, y], i) => {
          const [x0, y0] = before[i] ?? [x, y];
          moved = Math.max(moved, Math.hypot(x - x0, y - y0));
        });
      }
      expect(moved, id).toBeGreaterThan(minimum);
    }
  });

  it('P09-R10: full health goes up from 2-1 to 2-5; each final outlasts its mini boss', () => {
    const minis = W3.map((l) => fullHealth(design(l.mini)));
    const finals = W3.map((l) => fullHealth(design(l.final)));
    expect(increasing(minis)).toBe(true);
    expect(increasing(finals)).toBe(true);
    finals.forEach((f, i) => {
      expect(f).toBeGreaterThan(minis[i] ?? Infinity);
    });
  });

  it('P09-R10: each World 3 boss has more full health than the World 2 boss of its level and kind', () => {
    const w2 = Object.values(WORLD_2_BOSSES);
    W3.forEach((l, i) => {
      const w = at(w2, i);
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
  const firedSpeeds = (level: (typeof WORLD_3)[number], at: number): Set<number> => {
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

  it('P09-R10: the boss bullets use the level’s bullet speed factor', () => {
    for (const level of WORLD_3) {
      const boss = level.bosses?.find((b) => b.rank === 'mini');
      if (!boss) throw new Error(level.id);
      const speeds = bulletSpeeds(design(boss.kind));
      const seen = firedSpeeds(level, boss.at);
      expect(seen.size, level.id).toBeGreaterThan(0);
      for (const speed of seen)
        expect(speeds.has(speed), `${level.id} ${String(speed)}`).toBe(true);
    }
  });

  it.each(WORLD_3.map((l, i) => [l.id, i] as const))(
    'P09-R10: in %s, a player with guns at level 3 always on target needs the planned fight times',
    (_id, i) => {
      // Tunable values: mini 35–45 s in 3-1 up to 50–60 s in 3-5, final 70–90 s up to 110–140 s.
      const lerp = (a: number, b: number) => a + ((b - a) * i) / 4;
      const level = at(WORLD_3, i);
      const mini = fightBoss(bossRun(level), 'mini');
      const final = fightBoss(bossRun(level), 'final');
      expect(mini).toBeGreaterThanOrEqual(lerp(35, 50));
      expect(mini).toBeLessThanOrEqual(lerp(45, 60));
      expect(final).toBeGreaterThanOrEqual(lerp(70, 110));
      expect(final).toBeLessThanOrEqual(lerp(90, 140));
    },
  );
});

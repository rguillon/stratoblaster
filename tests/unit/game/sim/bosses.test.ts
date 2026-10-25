import { describe, expect, it } from 'vitest';
import { at } from '../../../helpers/at';
import { createRng } from '../../../../src/core/math/rng';
import { patternSignature } from '../../../../src/core/systems/boss-pattern';
import type { BossDesign } from '../../../../src/game/config/bosses/boss-kit';
import { WORLD_1_BOSSES } from '../../../../src/game/config/world-1/bosses';
import { BOSS_DESIGNS, BOSS_KINDS } from '../../../../src/game/sim/boss-kinds';
import { WorldBoss } from '../../../../src/game/sim/bosses/world-boss';
import { WORLD_1 } from '../../../../src/game/sim/world-1';
import { bossRun, fightBoss } from '../../../helpers/boss-bot';
import { RecordingContext, run, runUntil } from '../../../helpers/enemy-context';

/** The ship's reach at the bottom of the screen (phase 6 review, D-048). */
const REACH = [107, 373] as const;
const AREA = { width: 480, height: 640, random: createRng(1), topRange: REACH };

const design = (id: string): BossDesign => {
  const found = BOSS_DESIGNS.find((d) => d.id === id);
  if (!found) throw new Error(id);
  return found;
};

const fullHealth = (d: BossDesign): number =>
  d.stats.parts.reduce((sum, p) => sum + p.health, d.stats.health);

/** Every order the parts of `d` can be destroyed in, as lists of part ids. */
function orders(ids: readonly string[]): string[][] {
  if (ids.length === 0) return [[]];
  return ids.flatMap((id) =>
    orders(ids.filter((other) => other !== id)).map((rest) => [id, ...rest]),
  );
}

const increasing = (values: readonly number[]) =>
  values.every((v, i) => i === 0 || v > (values[i - 1] ?? 0));

describe('World 1 bosses', () => {
  it('P07-R05: each level has one mini boss and one final boss of the table', () => {
    expect(WORLD_1.map((l) => (l.bosses ?? []).map((b) => `${b.rank}:${b.kind}`))).toEqual([
      ['mini:reef-warden', 'final:storm-petrel'],
      ['mini:breakwater', 'final:gull-mothership'],
      ['mini:dust-devil', 'final:mesa-fortress'],
      ['mini:scorpion', 'final:refinery-titan'],
      ['mini:sentinel', 'final:overlord'],
    ]);
    expect(BOSS_KINDS.map((k) => k.name)).toEqual(BOSS_DESIGNS.map((d) => d.stats.name));
    expect(new Set(BOSS_KINDS.map((k) => k.id)).size).toBe(10);
  });

  it('P07-R01: mini bosses have 2 or 3 destroyable parts, final bosses 4 to 6', () => {
    for (const [id, { mini, final }] of Object.entries(WORLD_1_BOSSES)) {
      const [m, f] = [design(mini).stats.parts.length, design(final).stats.parts.length];
      expect(m, id).toBeGreaterThanOrEqual(2);
      expect(m, id).toBeLessThanOrEqual(3);
      expect(f, id).toBeGreaterThanOrEqual(4);
      expect(f, id).toBeLessThanOrEqual(6);
    }
  });

  it('P07-R01: some part of each boss shields its core, and every part can be reached', () => {
    for (const d of BOSS_DESIGNS) {
      expect(
        d.stats.parts.some((p) => p.shieldsCore),
        d.id,
      ).toBe(true);
      // A shielding part must not sit right behind the core, where the core blocks the shots.
      for (const p of d.stats.parts.filter((part) => part.shieldsCore && !part.orbits)) {
        const behind = p.y > 0 && Math.abs(p.x) < d.stats.coreRadius + 4;
        expect(behind, `${d.id} ${p.id}`).toBe(false);
      }
    }
  });

  it('P07-R04: every stage fires another pattern than the stage before, whatever the order', () => {
    for (const d of BOSS_DESIGNS) {
      const ids = d.stats.parts.map((p) => p.id);
      expect(d.stages, d.id).toHaveLength(ids.length + 1);
      for (const order of orders(ids)) {
        const signatures = d.stages.map((stage, k) => {
          const lost = new Set(order.slice(0, k));
          return patternSignature(stage, (from) => !lost.has(from));
        });
        for (let k = 1; k < signatures.length; k++) {
          expect(signatures[k], `${d.id} ${order.join('>')} stage ${String(k)}`).not.toBe(
            signatures[k - 1],
          );
        }
        // The last stage (only the core left) fires a pattern used in no earlier stage.
        const last = signatures.at(-1);
        expect(signatures.slice(0, -1), `${d.id} last stage`).not.toContain(last);
      }
    }
  });

  it('P07-R04: volleys only fire from the boss’s own parts or its core', () => {
    for (const d of BOSS_DESIGNS) {
      const ids = new Set(['core', ...d.stats.parts.map((p) => p.id)]);
      for (const volley of d.stages.flat())
        expect(ids.has(volley.from), `${d.id} ${volley.from}`).toBe(true);
      for (const launch of d.launches ?? []) expect(ids.has(launch.from), d.id).toBe(true);
    }
  });

  it('P07-R05: once in place, every boss keeps its hit circles inside the ship’s reach', () => {
    for (const kind of BOSS_KINDS) {
      const boss = kind.spawn(AREA);
      const ctx = new RecordingContext();
      runUntil(boss, ctx, () => boss.state === 'fighting');
      for (let t = 0; t < 60; t += 0.25) {
        run(boss, ctx, 0.25);
        for (const target of boss.hitTargets) {
          expect(target.x - target.radius, kind.id).toBeGreaterThanOrEqual(REACH[0] - 1e-6);
          expect(target.x + target.radius, kind.id).toBeLessThanOrEqual(REACH[1] + 1e-6);
        }
      }
    }
  });

  it('P07-R05: a boss comes in from above the top edge and is in place in about 3 to 6 s', () => {
    for (const kind of BOSS_KINDS) {
      const boss = kind.spawn(AREA);
      expect(boss.y, kind.id).toBeGreaterThan(640);
      const seconds = runUntil(boss, new RecordingContext(), () => boss.state === 'fighting');
      expect(seconds, kind.id).toBeGreaterThan(2.5);
      expect(seconds, kind.id).toBeLessThan(6.5);
      expect(boss.y, kind.id).toBeGreaterThan(0.6 * 640);
    }
  });

  it('P07-R03: each boss has its fight ground speed; one stops the ground, one speeds it up', () => {
    const factors = BOSS_DESIGNS.map((d) => d.stats.groundSpeed);
    expect(factors).toContain(0);
    expect(factors.some((f) => f > 1)).toBe(true);
    expect(factors.some((f) => f > 0 && f < 1)).toBe(true);
    expect(design('storm-petrel').stats.groundSpeed).toBe(1.5);
    expect(design('mesa-fortress').stats.groundSpeed).toBe(0);
  });

  it('P07-R07: parts drop a bonus half the time (60 % on final bosses); final cores always', () => {
    for (const { mini, final } of Object.values(WORLD_1_BOSSES)) {
      expect(
        design(mini).stats.parts.every((p) => p.dropChance === 0.5),
        mini,
      ).toBe(true);
      expect(
        design(final).stats.parts.every((p) => p.dropChance === 0.6),
        final,
      ).toBe(true);
      expect(design(final).stats.coreDropChance, final).toBe(1);
    }
  });

  it('P07-R10: full health goes up from 1-1 to 1-5, and each final boss outlasts its mini boss', () => {
    const levels = Object.values(WORLD_1_BOSSES);
    const minis = levels.map((l) => fullHealth(design(l.mini)));
    const finals = levels.map((l) => fullHealth(design(l.final)));
    expect(increasing(minis)).toBe(true);
    expect(increasing(finals)).toBe(true);
    finals.forEach((f, i) => {
      expect(f).toBeGreaterThan(minis[i] ?? Infinity);
    });
  });

  it('P07-R05: the Refinery Titan’s fuel tanks burst into a ring of bullets', () => {
    const boss = new WorldBoss(design('refinery-titan'), AREA);
    const ctx = new RecordingContext();
    runUntil(boss, ctx, () => boss.state === 'fighting');
    const before = ctx.shots.length;
    boss.parts.find((p) => p.spec.id === 'tank-left')?.destroy();
    run(boss, ctx, 1 / 60);
    expect(ctx.shots.length - before).toBe(12);
  });

  it('P07-R05: hangars launch Gnats and a drone bay launches Hornets', () => {
    for (const [id, model] of [
      ['gull-mothership', 'gnat'],
      ['sentinel', 'hornet'],
    ] as const) {
      const boss = new WorldBoss(design(id), AREA);
      const ctx = new RecordingContext();
      runUntil(boss, ctx, () => boss.state === 'fighting');
      run(boss, ctx, 8);
      expect(
        ctx.spawned.some((e) => e.model === model),
        id,
      ).toBe(true);
    }
  });

  it('P07-R05: the Dust Devil’s blades turn around it', () => {
    const boss = new WorldBoss(design('dust-devil'), AREA);
    const ctx = new RecordingContext();
    runUntil(boss, ctx, () => boss.state === 'fighting');
    const blade = at(boss.parts, 0);
    const start = Math.atan2(blade.x - boss.x, blade.y - boss.y);
    run(boss, ctx, 1);
    expect(Math.atan2(blade.x - boss.x, blade.y - boss.y)).not.toBeCloseTo(start, 1);
  });

  it.each(WORLD_1.map((l, i) => [l.id, i] as const))(
    'P07-R10: in %s, a player with guns at level 3 always on target needs the planned fight times',
    (_id, i) => {
      // Tunable values: mini 25–35 s in 1-1 up to 40–50 s in 1-5, final 50–70 s up to 90–120 s,
      // in between for the levels in between.
      const lerp = (a: number, b: number) => a + ((b - a) * i) / 4;
      const level = at(WORLD_1, i);
      const mini = fightBoss(bossRun(level), 'mini');
      const final = fightBoss(bossRun(level), 'final');
      expect(mini).toBeGreaterThanOrEqual(lerp(25, 40));
      expect(mini).toBeLessThanOrEqual(lerp(35, 50));
      expect(final).toBeGreaterThanOrEqual(lerp(50, 90));
      expect(final).toBeLessThanOrEqual(lerp(70, 120));
    },
  );

  it('P07-R07: destroying parts drops bonuses, the same ones every time', () => {
    const drops = () => {
      const r = bossRun(at(WORLD_1, 1), 3, true);
      fightBoss(r, 'final');
      return r.bonuses?.dropped ?? 0;
    };
    const first = drops();
    expect(first).toBeGreaterThanOrEqual(1);
    expect(drops()).toBe(first);
  });
});

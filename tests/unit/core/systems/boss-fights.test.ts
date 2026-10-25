import { describe, expect, it } from 'vitest';
import { at } from '../../../helpers/at';
import type { Boss } from '../../../../src/core/entities/boss';
import { createRng } from '../../../../src/core/math/rng';
import { ScrollTrack } from '../../../../src/core/scenery/scroll-track';
import {
  BossFights,
  validateLevelBosses,
  type LevelBoss,
} from '../../../../src/core/systems/boss-fights';
import { SAMPLE_BOSS_KINDS } from '../../../fixtures/sample-boss';
import { RecordingContext, runUntil } from '../../../helpers/enemy-context';

const RULES = { speedEaseSeconds: 2, barFillSeconds: 1 };
const BOSSES: readonly LevelBoss[] = [
  { kind: 'big-cube', rank: 'final', at: 1000 },
  { kind: 'big-cube', rank: 'mini', at: 300 },
];

/** Fights over a 60 px/s, 1000 long track; `added` collects the bosses brought in. */
function setup() {
  const added: Boss[] = [];
  const area = () => ({ width: 300, height: 400, random: createRng(1) });
  const fights = new BossFights(BOSSES, SAMPLE_BOSS_KINDS, RULES, {
    area,
    add: (boss) => added.push(boss),
  });
  const track = new ScrollTrack(60, 1000);
  const step = (seconds: number) => {
    for (let t = 0; t < seconds - 1e-9; t += 1 / 60) {
      track.step(1 / 60);
      fights.step(1 / 60, track);
    }
  };
  return { fights, track, added, step };
}

describe('BossFights', () => {
  it('P07-R06: a boss arrives when the level gets to it, in order', () => {
    const { fights, track, added, step } = setup();
    expect(fights.bosses.map((b) => b.rank)).toEqual(['mini', 'final']);
    step(4.9);
    expect(added).toHaveLength(0);
    step(0.2);
    expect(added).toHaveLength(1);
    expect(fights.active).toBe(true);
    expect(fights.rank).toBe('mini');
    expect(track.held).toBe(true);
    expect(fights.hasFinal).toBe(true);
  });

  it('P07-R03: the ground eases to the fight speed over 2 s and stays there; the level waits', () => {
    const { fights, track, step } = setup();
    step(5.1);
    const progress = track.progress;
    step(2);
    expect(track.speedFactor).toBeCloseTo(0.5);
    const distance = track.distance;
    step(10);
    expect(track.speedFactor).toBe(0.5);
    expect(track.distance - distance).toBeCloseTo(300, 0);
    expect(track.progress).toBe(progress);
    expect(fights.boss?.groundSpeed).toBe(0.5);
  });

  it('P07-R03, P07-R06: once the boss is gone the ground eases back and the level goes on', () => {
    const { fights, track, step } = setup();
    step(5.1);
    const boss = fights.boss;
    if (!boss) throw new Error('no boss');
    boss.gone = true;
    step(1 / 60);
    expect(fights.active).toBe(false);
    expect(fights.justDefeated?.rank).toBe('mini');
    expect(fights.defeated).toHaveLength(1);
    expect(track.held).toBe(false);
    step(2);
    expect(track.speedFactor).toBeCloseTo(1);
    expect(fights.justDefeated).toBeUndefined();
    expect(fights.finalDefeated).toBe(false);
  });

  it('P07-R02: the bar fills up over 1 s and shows the health left with a notch per part', () => {
    const { fights, step } = setup();
    expect(fights.bar).toBeUndefined();
    step(5.1);
    expect(fights.bar?.share).toBeLessThan(0.2);
    step(1);
    expect(fights.bar).toMatchObject({ name: 'Big Cube', rank: 'mini', share: 1, fullHealth: 60 });
    expect(fights.bar?.notches[0]).toBeCloseTo(20 / 60);
    expect(fights.bar?.notches[1]).toBeCloseTo(30 / 60);
    const boss = fights.boss;
    if (!boss) throw new Error('no boss');
    // The enemy world moves the boss: here it is brought into place, where it takes damage.
    runUntil(boss, new RecordingContext(), () => boss.state === 'fighting');
    at(boss.parts, 0).health -= 6;
    expect(fights.bar?.share).toBeCloseTo(1 - 6 / 60);
  });

  it('P06-R09, P07-R08: skipTo drops the fight and starts again from the next boss', () => {
    const { fights, track, added, step } = setup();
    step(5.1);
    track.seek(6);
    fights.skipTo(track);
    expect(fights.active).toBe(false);
    expect(track.held).toBe(false);
    expect(track.speedFactor).toBe(1);
    expect(fights.passed).toBe(1);
    track.seek(0);
    fights.skipTo(track, 1);
    step(6);
    expect(added).toHaveLength(1);
  });

  it('rejects a boss of an unknown kind', () => {
    expect(() => {
      validateLevelBosses([{ kind: 'nope', rank: 'mini', at: 0 }], ['big-cube']);
    }).toThrow(/nope/);
    expect(() => {
      validateLevelBosses([{ kind: 'big-cube', rank: 'mini', at: -1 }], ['big-cube']);
    }).toThrow(/distance/);
  });
});

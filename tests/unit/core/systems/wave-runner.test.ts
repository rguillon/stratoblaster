import { describe, expect, it } from 'vitest';
import type { EnemyEntry } from '../../../../src/core/entities/enemy';
import {
  validateWaveScript,
  WaveRunner,
  type Wave,
  type WaveScript,
} from '../../../../src/core/systems/wave-runner';

const top = (position: number): EnemyEntry => ({ side: 'top', position });

const wave = (at: number, kind: string, count = 1, interval = 0, spread?: number): Wave => ({
  at,
  kind,
  count,
  interval,
  entry: top(0.5),
  ...(spread === undefined ? {} : { spread }),
});

/** A runner over `script` that records each group as `[time, kind, entry]`. */
function record(script: WaveScript) {
  const spawned: { time: number; kind: string; entry: EnemyEntry }[] = [];
  let time = 0;
  const runner = new WaveRunner(script, (kind, entry) => spawned.push({ time, kind, entry }));
  /** Steps of `dt` while the level scrolls at `speed`, from `time` to `until`. */
  const run = (until: number, speed = 10, dt = 0.5) => {
    while (time < until - 1e-9) {
      time += dt;
      runner.step(dt, time * speed);
    }
  };
  return { runner, spawned, run };
}

describe('WaveRunner', () => {
  it('P06-R07: a wave spawns when the level scrolls past its distance, and not before', () => {
    const { spawned, run } = record([wave(100, 'a')]);
    run(9.5);
    expect(spawned).toEqual([]);
    run(10);
    expect(spawned).toEqual([{ time: 10, kind: 'a', entry: top(0.5) }]);
    run(30);
    expect(spawned).toHaveLength(1);
  });

  it('P06-R07: the groups of a wave come one every interval, waves in distance order', () => {
    const { spawned, run } = record([wave(50, 'late'), wave(0, 'b', 3, 1)]);
    run(10);
    expect(spawned.map((s) => [s.time, s.kind])).toEqual([
      [0.5, 'b'],
      [1.5, 'b'],
      [2.5, 'b'],
      [5, 'late'],
    ]);
  });

  it('P06-R07: several waves can be on at the same time', () => {
    const { spawned, run } = record([wave(0, 'a', 3, 2), wave(10, 'b', 2, 2)]);
    run(6);
    expect(spawned.map((s) => s.kind)).toEqual(['a', 'b', 'a', 'b', 'a']);
  });

  it('P06-R07: the entry moves by `spread` for each group, wrapped into 0..1', () => {
    const { spawned, run } = record([wave(0, 'a', 3, 0, 0.3)]);
    run(1);
    expect(spawned.map((s) => s.entry.position)).toEqual([
      0.5,
      expect.closeTo(0.8),
      expect.closeTo(0.1),
    ]);
  });

  it('P06-R07: the same script played twice spawns at the same distances', () => {
    const script = [wave(30, 'a', 2, 1.5), wave(80, 'b'), wave(5, 'c', 4, 0.25)];
    const first = record(script);
    const second = record(script);
    first.run(20);
    second.run(20);
    expect(first.spawned).toEqual(second.spawned);
    expect(first.runner.finished).toBe(true);
  });

  it('P06-R03: once stopped, nothing more spawns, not even the rest of a wave', () => {
    const { runner, spawned, run } = record([wave(0, 'a', 5, 1), wave(50, 'b')]);
    run(2);
    expect(spawned).toHaveLength(2);
    runner.stop();
    expect(runner.finished).toBe(true);
    run(20);
    expect(spawned).toHaveLength(2);
  });

  it('P06-R09: skipping to a distance skips the waves before it and keeps the later ones', () => {
    const { runner, spawned, run } = record([wave(10, 'a'), wave(50, 'b'), wave(120, 'c')]);
    run(0.5);
    runner.skipTo(60);
    expect(runner.triggered).toBe(2);
    run(20);
    expect(spawned.map((s) => s.kind)).toEqual(['c']);
    runner.skipTo(1000);
    expect(runner.triggered).toBe(3);
    expect(runner.finished).toBe(true);
  });

  it('validates the kinds, counts, timings and entries of a script', () => {
    expect(() => {
      validateWaveScript([wave(0, 'a', 2, 1)], ['a']);
    }).not.toThrow();
    expect(() => {
      validateWaveScript([wave(0, 'x')], ['a']);
    }).toThrow(/unknown enemy kind/);
    expect(() => {
      validateWaveScript([wave(0, 'a', 0)], ['a']);
    }).toThrow(/bad count/);
    expect(() => {
      validateWaveScript([wave(-1, 'a')], ['a']);
    }).toThrow(/bad timing/);
    expect(() => {
      validateWaveScript([{ ...wave(0, 'a'), entry: top(1.5) }], ['a']);
    }).toThrow(/bad entry/);
  });
});

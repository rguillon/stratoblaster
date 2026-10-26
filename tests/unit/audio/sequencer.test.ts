import { describe, expect, it } from 'vitest';
import type { Track } from '../../../src/audio/audio-types';
import { beatSeconds, midiToHz, trackSeconds } from '../../../src/audio/audio-types';
import { Sequencer } from '../../../src/audio/sequencer';

/** 4 beats at 60 BPM (4 s), a note on every beat. */
const TRACK: Track = {
  id: 't',
  bpm: 60,
  beats: 4,
  loop: true,
  notes: [0, 1, 2, 3].map((beat) => ({
    beat,
    beats: 0.5,
    pitch: 60 + beat,
    velocity: 1,
    instrument: 'i',
  })),
};

describe('Sequencer', () => {
  it('converts beats, track lengths and pitches', () => {
    expect(beatSeconds(120)).toBe(0.5);
    expect(trackSeconds(TRACK)).toBe(4);
    expect(midiToHz(69)).toBe(440);
    expect(midiToHz(81)).toBeCloseTo(880);
  });

  it('P12-R05: hands out each note once, ahead of time, with its time and length in seconds', () => {
    const seq = new Sequencer(TRACK);
    expect(seq.advance(1.5).map((n) => [n.at, n.seconds, n.note.pitch])).toEqual([
      [0, 0.5, 60],
      [1, 0.5, 61],
    ]);
    expect(seq.advance(1.5)).toEqual([]);
    expect(seq.advance(2.1).map((n) => n.at)).toEqual([2]);
    expect(seq.position).toBe(2.1);
  });

  it('P12-R06: loops without a gap: the first note comes again right after the last', () => {
    const seq = new Sequencer(TRACK);
    expect(seq.advance(9).map((n) => n.at)).toEqual([0, 1, 2, 3, 4, 5, 6, 7, 8]);
  });

  it('P12-R11: seeking back hands the notes from there out again', () => {
    const seq = new Sequencer(TRACK);
    seq.advance(6);
    seq.seek(5.5);
    expect(seq.position).toBe(5.5);
    expect(seq.advance(7.5).map((n) => n.at)).toEqual([6, 7]);
    seq.seek(-1);
    expect(seq.advance(0.5).map((n) => n.at)).toEqual([0]);
  });

  it('a track that does not loop is done after its last note; an empty one hands out nothing', () => {
    const once = new Sequencer({ ...TRACK, loop: false });
    expect(once.advance(100)).toHaveLength(4);
    expect(once.done).toBe(true);
    expect(once.advance(200)).toEqual([]);
    once.seek(3);
    expect(once.done).toBe(false);
    const empty = new Sequencer({ ...TRACK, notes: [] });
    expect(empty.advance(100)).toEqual([]);
    const silent = new Sequencer({ ...TRACK, beats: 0 });
    expect(silent.advance(5)).toEqual([]);
  });
});

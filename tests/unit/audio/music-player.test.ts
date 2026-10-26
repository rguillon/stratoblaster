import { describe, expect, it } from 'vitest';
import type { Instrument, Track } from '../../../src/audio/audio-types';
import { MusicPlayer } from '../../../src/audio/music-player';
import { FakeAudioContext, FakeGain, FakeOscillator } from '../../helpers/fake-audio';

const INSTRUMENTS: Record<string, Instrument> = {
  beep: {
    gain: 0.5,
    layers: [
      {
        wave: 'square',
        gain: 1,
        pitch: 1,
        envelope: { attack: 0, decay: 0.1, sustain: 0, release: 0.01 },
      },
    ],
  },
};

/** 60 BPM: one note a second, looping every 60 s. */
function track(id: string, loop = true): Track {
  return {
    id,
    bpm: 60,
    beats: 60,
    loop,
    notes: Array.from({ length: 60 }, (_, beat) => ({
      beat,
      beats: 0.5,
      pitch: 69,
      velocity: 1,
      instrument: 'beep',
    })),
  };
}

function setup(): { context: FakeAudioContext; player: MusicPlayer; music: FakeGain } {
  const context = new FakeAudioContext();
  const music = context.createGain();
  const player = new MusicPlayer(
    () => ({ context: context.asContext(), music: music as unknown as AudioNode }),
    INSTRUMENTS,
    { lookaheadSeconds: 0.1, pauseFadeSeconds: 0.05 },
  );
  return { context, player, music };
}

/** Runs the scheduler every 25 ms up to `seconds` of audio time. */
function runTo(context: FakeAudioContext, player: MusicPlayer, seconds: number): void {
  while (context.currentTime < seconds - 1e-9) {
    context.currentTime = Math.min(seconds, context.currentTime + 0.025);
    player.update();
  }
}

const oscillators = (context: FakeAudioContext): FakeOscillator[] =>
  context.nodes.filter((n) => n instanceof FakeOscillator);

describe('MusicPlayer', () => {
  it('P12-R05: schedules the notes ahead on the audio clock, at their time', () => {
    const { context, player } = setup();
    player.play(track('a'), 0);
    player.update();
    expect(oscillators(context).map((o) => o.started)).toEqual([0]);
    runTo(context, player, 2.95);
    expect(oscillators(context).map((o) => o.started)).toEqual([0, 1, 2, 3]);
    expect(oscillators(context)[1]?.frequency.value).toBe(440);
    expect(player.track?.id).toBe('a');
    expect(player.position).toBeCloseTo(2.95);
  });

  it('P12-R11: paused 30 s in for 10 s, the track goes on from about 30 s, not 40 s', () => {
    const { context, player } = setup();
    player.play(track('level'), 0);
    runTo(context, player, 30);
    player.pause();
    expect(player.position).toBeCloseTo(30);
    const before = oscillators(context).length;
    runTo(context, player, 40);
    expect(oscillators(context)).toHaveLength(before);
    expect(player.position).toBeCloseTo(30);
    player.resume();
    runTo(context, player, 40.5);
    expect(player.position).toBeCloseTo(30.5);
    // The note of second 31 of the track plays at 41 s of audio time.
    runTo(context, player, 41.05);
    expect(oscillators(context).at(-1)?.started).toBeCloseTo(41);
  });

  it('P12-R07: cross-fades: the old track fades out over the fade and stops, the new one fades in', () => {
    const { context, player, music } = setup();
    player.play(track('level'), 0);
    runTo(context, player, 5);
    player.play(track('boss'), 1);
    runTo(context, player, 5.5);
    expect(player.track?.id).toBe('boss');
    const gains = context.nodes.filter(
      (n): n is FakeGain => n instanceof FakeGain && n.outputs[0] === music,
    );
    expect(gains).toHaveLength(2);
    expect(gains[0]?.gain.events.at(-1)).toMatchObject({ kind: 'exponential', time: 6 });
    // The boss track started at the next update, 25 ms later.
    expect(gains[1]?.gain.events.at(-1)).toMatchObject({ kind: 'exponential', value: 1 });
    expect(gains[1]?.gain.events.at(-1)?.time).toBeCloseTo(6.025);
    runTo(context, player, 6.1);
    expect(gains[0]?.disconnected).toBe(true);
    expect(player.position).toBeCloseTo(1.075);
  });

  it('P12-R06: fades out to silence; a jingle plays once over the music', () => {
    const { context, player } = setup();
    player.play(track('level'), 0);
    runTo(context, player, 1);
    player.play(null, 1);
    expect(player.track).toBeUndefined();
    const notes = track('j')
      .notes.slice(0, 2)
      .map((n) => ({ ...n, pitch: 81 }));
    player.jingle({ ...track('jingle', false), beats: 2, notes });
    runTo(context, player, 10);
    // The level goes on while it fades, then stops; the jingle plays its two notes once.
    const level = oscillators(context).filter((o) => o.frequency.value === 440);
    expect(Math.max(...level.map((o) => o.started ?? 0))).toBeLessThanOrEqual(2);
    expect(oscillators(context).filter((o) => o.frequency.value === 880)).toHaveLength(2);
    player.stop();
    expect(player.position).toBe(0);
  });

  it('P12-R05: waits for the audio context; once it exists, the track starts from its beginning', () => {
    const context = new FakeAudioContext();
    let ready = false;
    const music = context.createGain() as unknown as AudioNode;
    const player = new MusicPlayer(
      () => (ready ? { context: context.asContext(), music } : undefined),
      INSTRUMENTS,
      { lookaheadSeconds: 0.1, pauseFadeSeconds: 0.05 },
    );
    player.play(track('menu'), 1);
    player.pause();
    player.resume();
    player.update();
    expect(player.position).toBe(0);
    expect(oscillators(context)).toEqual([]);
    context.currentTime = 12;
    ready = true;
    player.update();
    expect(oscillators(context).map((o) => o.started)).toEqual([12]);
  });
});

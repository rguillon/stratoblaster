import { describe, expect, it } from 'vitest';
import type { SoundDesign } from '../../../src/audio/audio-types';
import { panAt, SfxPlayer } from '../../../src/audio/sfx-player';
import { FakeAudioContext, FakeOscillator, FakePanner } from '../../helpers/fake-audio';

const SETTINGS = {
  maxVoices: 2,
  retriggerSeconds: 0.03,
  retriggerBoost: 1.25,
  panMax: 0.6,
  stopFadeSeconds: 0.05,
};

const sound = (name: string, rest: Partial<SoundDesign> = {}): SoundDesign => ({
  name,
  priority: 1,
  gain: 0.5,
  hold: 0,
  layers: [
    {
      wave: 'square',
      gain: 1,
      pitch: 440,
      envelope: { attack: 0, decay: 0.1, sustain: 0, release: 0.02 },
    },
  ],
  ...rest,
});

function setup(withContext = true) {
  const context = new FakeAudioContext();
  const sfx = context.createGain();
  let now = 0;
  const player = new SfxPlayer(
    () =>
      withContext ? { context: context.asContext(), sfx: sfx as unknown as AudioNode } : undefined,
    () => now,
    SETTINGS,
  );
  return {
    context,
    player,
    at: (t: number) => {
      now = t;
      context.currentTime = t;
    },
  };
}

describe('panAt', () => {
  it('P12-R09: an explosion at the left edge pans to −sfx_pan_max, at the centre to 0', () => {
    expect(panAt(0, 480, 0.6)).toBeCloseTo(-0.6);
    expect(panAt(240, 480, 0.6)).toBe(0);
    expect(panAt(480, 480, 0.6)).toBeCloseTo(0.6);
    expect(panAt(-50, 480, 0.6)).toBeCloseTo(-0.6);
    expect(panAt(10, 0, 0.6)).toBe(0);
  });
});

describe('SfxPlayer', () => {
  it('P12-R09: plays a sound on the sound effect bus, panned when positional', () => {
    const { context, player } = setup();
    expect(player.play(sound('boom', { positional: true }), -0.6)).toBe(true);
    const panner = context.nodes.find((n) => n instanceof FakePanner);
    expect(panner?.pan.value).toBeCloseTo(-0.6);
    expect(player.play(sound('menu'), 0.5)).toBe(true);
    expect(context.nodes.filter((n) => n instanceof FakePanner)).toHaveLength(1);
  });

  it('P12-R10: the same sound again within 30 ms is not played twice, but louder', () => {
    const { player, at } = setup();
    at(1);
    expect(player.play(sound('hit'))).toBe(true);
    at(1.01);
    expect(player.play(sound('hit'))).toBe(false);
    expect(player.voices).toBe(1);
  });

  it('P12-R10: a sound of higher priority replaces the oldest; a lower one is dropped', () => {
    const { player, at } = setup();
    player.play(sound('a', { priority: 0 }));
    player.play(sound('b', { priority: 0 }));
    at(0.05);
    expect(player.play(sound('player', { priority: 6 }))).toBe(true);
    player.play(sound('player-2', { priority: 6 }));
    at(0.06);
    expect(player.play(sound('enemy', { priority: 0 }))).toBe(false);
  });

  it('P12-R09, P12-R11: a looping sound plays until stopped; stopAll stops everything', () => {
    const { context, player } = setup();
    const hum = sound('hum', { loop: true });
    expect(player.play(hum)).toBe(true);
    expect(player.play(hum)).toBe(false);
    expect(player.looping('hum')).toBe(true);
    player.stopLoop('hum');
    expect(player.looping('hum')).toBe(false);
    player.stopLoop('hum');
    player.play(hum);
    player.play(sound('x'));
    player.stopAll();
    expect(player.voices).toBe(0);
    expect(player.looping('hum')).toBe(false);
    const stopped = context.nodes.filter((n) => n instanceof FakeOscillator).map((o) => o.stopped);
    expect(stopped.every((t) => t !== undefined)).toBe(true);
  });

  it('P12-R05: without a context the limits still decide, and nothing throws', () => {
    const { player, at } = setup(false);
    expect(player.play(sound('a'))).toBe(true);
    at(0.01);
    expect(player.play(sound('a'))).toBe(false);
    player.stopAll();
    expect(player.voices).toBe(0);
  });
});

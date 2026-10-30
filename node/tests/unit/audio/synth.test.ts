import { describe, expect, it } from 'vitest';
import type { ToneLayer } from '../../../src/audio/audio-types';
import { layerSeconds, soundSeconds } from '../../../src/audio/audio-types';
import { playVoice } from '../../../src/audio/synth';
import {
  FakeAudioContext,
  FakeBufferSource,
  FakeFilter,
  FakeGain,
  FakeOscillator,
} from '../../helpers/fake-audio';

const PLUCK: ToneLayer = {
  wave: 'sawtooth',
  gain: 0.5,
  pitch: 2,
  envelope: { attack: 0.01, decay: 0.1, sustain: 0.5, release: 0.2 },
  filter: { type: 'lowpass', frequency: 800, from: 3000, sweepSeconds: 0.1 },
};

const NOISE: ToneLayer = {
  wave: 'noise',
  gain: 1,
  pitch: 100,
  glideTo: 50,
  glideSeconds: 0.2,
  delay: 0.05,
  envelope: { attack: 0, decay: 0.1, sustain: 0, release: 0.05 },
};

describe('playVoice', () => {
  it('P12-R05: an oscillator at the note times the layer pitch, through its filter and envelope', () => {
    const context = new FakeAudioContext();
    const out = context.createGain();
    const voice = playVoice(context.asContext(), out as unknown as AudioNode, [PLUCK], {
      when: 1,
      noteHz: 220,
      hold: 0.5,
      gain: 0.8,
    });
    const osc = context.nodes.find((n) => n instanceof FakeOscillator);
    expect(osc?.type).toBe('sawtooth');
    expect(osc?.frequency.events[0]).toEqual({ kind: 'set', value: 440, time: 1 });
    expect(osc?.started).toBe(1);
    const filter = context.nodes.find((n) => n instanceof FakeFilter);
    expect(filter?.frequency.events.map((e) => e.value)).toEqual([3000, 800]);
    const gain = context.nodes.filter((n) => n instanceof FakeGain).at(-1);
    const peak = gain?.gain.events.find((e) => e.kind === 'linear');
    expect(peak).toEqual({ kind: 'linear', value: 0.4, time: 1.01 });
    expect(gain?.outputs).toEqual([out]);
    // Held 0.5 s, then a 0.2 s release.
    expect(voice.end).toBeCloseTo(1.7);
    expect(osc?.stopped).toBeGreaterThan(1.7);
  });

  it('P12-R05: noise comes from one shared buffer per context, gliding its rate, after its delay', () => {
    const context = new FakeAudioContext();
    const out = context.createGain() as unknown as AudioNode;
    playVoice(context.asContext(), out, [NOISE], { when: 0, hold: 0, gain: 1 });
    playVoice(context.asContext(), out, [NOISE], { when: 0, hold: 0, gain: 1 });
    expect(context.buffers).toBe(1);
    const noise = context.nodes.find((n) => n instanceof FakeBufferSource);
    expect(noise?.loop).toBe(true);
    expect(noise?.started).toBe(0.05);
    expect(noise?.playbackRate.events.at(-1)?.value).toBeCloseTo(0.5);
  });

  it('P12-R10, P12-R11: a held voice goes on until stopped; stopping fades it and stops its sources', () => {
    const context = new FakeAudioContext();
    const out = context.createGain() as unknown as AudioNode;
    const voice = playVoice(context.asContext(), out, [PLUCK], {
      when: 0,
      hold: Infinity,
      gain: 1,
    });
    expect(voice.end).toBe(Infinity);
    const osc = context.nodes.find((n) => n instanceof FakeOscillator);
    expect(osc?.stopped).toBeUndefined();
    voice.stop(2, 0.05);
    expect(osc?.stopped).toBeCloseTo(2.07);
    const gain = context.nodes.filter((n) => n instanceof FakeGain).at(-1);
    expect(gain?.gain.events.at(-1)?.kind).toBe('target');
  });

  it('measures layers and sounds', () => {
    expect(layerSeconds(PLUCK, 0.5)).toBeCloseTo(0.7);
    expect(layerSeconds(NOISE, 0)).toBeCloseTo(0.2);
    const sound = { name: 's', layers: [PLUCK, NOISE], gain: 1, priority: 0, hold: 0 };
    expect(soundSeconds(sound)).toBeCloseTo(0.31);
    expect(soundSeconds({ ...sound, loop: true })).toBe(Infinity);
  });
});

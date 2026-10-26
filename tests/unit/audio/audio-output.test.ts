import { describe, expect, it } from 'vitest';
import { AudioOutput, volumeGain, type AudioOutputOptions } from '../../../src/audio/audio-output';
import { AUDIO_CONFIG } from '../../../src/config/audio';
import { FakeAudioContext, FakeCompressor, FakeGain } from '../../helpers/fake-audio';

function output(context?: FakeAudioContext, rest: Partial<AudioOutputOptions> = {}): AudioOutput {
  return new AudioOutput({
    ...(context ? { createContext: () => context.asContext() } : {}),
    mix: { music: 0.5, sfx: 0.8 },
    peakDb: AUDIO_CONFIG.masterPeakDb,
    limiter: AUDIO_CONFIG.limiter,
    ...rest,
  });
}

describe('volumeGain', () => {
  it('P12-R04: a step gives (step / 10)², 0 silent, 10 full', () => {
    expect(volumeGain(0, 10)).toBe(0);
    expect(volumeGain(3, 10)).toBeCloseTo(0.09);
    expect(volumeGain(6, 10)).toBeCloseTo(0.36);
    expect(volumeGain(10, 10)).toBe(1);
    expect(volumeGain(12, 10)).toBe(1);
    expect(volumeGain(5, 0)).toBe(0);
  });
});

describe('AudioOutput', () => {
  it('P12-R05: nothing exists before the unlock; it then builds the buses into a limiter', () => {
    const context = new FakeAudioContext();
    const audio = output(context);
    expect(audio.state).toBe('none');
    expect(audio.buses).toBeUndefined();
    const buses = audio.unlock();
    expect(audio.state).toBe('running');
    expect(audio.unlock()).toBe(buses);
    const compressor = context.nodes.find((n) => n instanceof FakeCompressor);
    expect(compressor?.threshold.value).toBe(-1);
    expect(compressor?.outputs).toEqual([context.destination]);
    const gains = context.nodes.filter((n) => n instanceof FakeGain);
    expect(gains.map((g) => g.outputs[0])).toEqual([compressor, compressor]);
  });

  it('P12-R05: without Web Audio, or when it fails, it stays silent and throws nothing', () => {
    const none = output();
    expect(none.unlock()).toBeUndefined();
    none.setHidden(true);
    none.setVolumes(1, 1);
    expect(none.state).toBe('none');
    const failing = output(undefined, {
      createContext: () => {
        throw new Error('no audio device');
      },
    });
    expect(failing.unlock()).toBeUndefined();
    expect(failing.unlock()).toBeUndefined();
    expect(failing.state).toBe('none');
  });

  it('P12-R04: the bus gains follow the volumes (times the mix); 0 is silent', () => {
    const context = new FakeAudioContext();
    const audio = output(context);
    audio.setVolumes(volumeGain(6, 10), volumeGain(8, 10));
    const buses = audio.unlock();
    expect((buses?.music as unknown as FakeGain).gain.value).toBeCloseTo(0.36 * 0.5);
    expect((buses?.sfx as unknown as FakeGain).gain.value).toBeCloseTo(0.64 * 0.8);
    audio.setVolumes(volumeGain(3, 10), volumeGain(0, 10));
    expect((buses?.music as unknown as FakeGain).gain.value).toBeCloseTo(0.09 * 0.5);
    expect((buses?.sfx as unknown as FakeGain).gain.value).toBe(0);
  });

  it('P12-R11: a hidden page suspends the context; shown again, it resumes', () => {
    const context = new FakeAudioContext();
    const audio = output(context);
    audio.unlock();
    audio.setHidden(true);
    expect(context.state).toBe('suspended');
    audio.setHidden(false);
    expect(context.state).toBe('running');
    context.state = 'suspended';
    audio.unlock();
    expect(context.state).toBe('running');
  });
});

import { describe, expect, it } from 'vitest';
import type { Instrument } from '../../../src/audio/audio-types';
import { TrackMixer } from '../../../src/audio/track-mixer';
import { FakeAudioContext, FakeDelay, FakeGain } from '../../helpers/fake-audio';

const DRY: Instrument = { gain: 1, layers: [] };
const WET: Instrument = { gain: 1, layers: [], echo: 0.4, reverb: 0.5 };
const EFFECTS = { echoBeats: 0.75, echoFeedback: 0.35, reverbSeconds: 2 };

function setup(withReverb = true) {
  const context = new FakeAudioContext();
  const music = context.createGain();
  const reverb = context.createGain();
  const bus = {
    context: context.asContext(),
    music: music as unknown as AudioNode,
    ...(withReverb ? { reverb: reverb as unknown as AudioNode } : {}),
  };
  return { context, music, reverb, mixer: new TrackMixer(bus, EFFECTS, 120) };
}

describe('TrackMixer', () => {
  it('P12-R06: each instrument gets one input into the track fader, made once', () => {
    const { mixer, music } = setup();
    const input = mixer.input('kick', DRY) as unknown as FakeGain;
    expect(mixer.input('kick', DRY)).toBe(input);
    expect(input.outputs).toEqual([mixer.output]);
    expect((mixer.output as unknown as FakeGain).outputs).toEqual([music]);
  });

  it('P12-R06 (synthwave): echoes are a dotted eighth at the track tempo, fed back, into the fader', () => {
    const { context, mixer } = setup();
    mixer.input('arp', WET);
    mixer.input('lead', WET);
    const delays = context.nodes.filter((n) => n instanceof FakeDelay);
    expect(delays).toHaveLength(1);
    // 0.75 beat at 120 BPM.
    expect(delays[0]?.delayTime.value).toBeCloseTo(0.375);
    expect(delays[0]?.outputs).toContain(mixer.output);
    const feedback = delays[0]?.outputs.find((n) => n !== (mixer.output as unknown));
    expect((feedback as FakeGain | undefined)?.gain.value).toBe(0.35);
  });

  it('P12-R06 (synthwave): the reverb send goes to the bus reverb through a fader that fades with the track', () => {
    const { context, mixer, reverb } = setup();
    mixer.input('pad', WET);
    const sends = context.nodes.filter((n) => n instanceof FakeGain && n.outputs.includes(reverb));
    expect(sends).toHaveLength(1);
    mixer.fadeIn(0, 1);
    mixer.fadeTo(0, 5, 2);
    const fader = sends[0] as FakeGain;
    expect(fader.gain.events.at(-1)).toMatchObject({ kind: 'exponential', time: 7 });
    expect((mixer.output as unknown as FakeGain).gain.events.at(-1)).toMatchObject({ time: 7 });
    mixer.fadeIn(8, 0);
    expect(fader.gain.value).toBe(1);
    mixer.disconnect();
    expect(fader.disconnected).toBe(true);
  });

  it('without a bus reverb, or without effects, the instruments stay dry', () => {
    const { context, mixer } = setup(false);
    mixer.input('pad', WET);
    expect(context.nodes.filter((n) => n instanceof FakeDelay)).toHaveLength(1);
    const dry = new FakeAudioContext();
    const plain = new TrackMixer(
      { context: dry.asContext(), music: dry.createGain() as unknown as AudioNode },
      undefined,
      100,
    );
    plain.input('pad', WET);
    expect(dry.nodes.filter((n) => n instanceof FakeDelay)).toEqual([]);
  });
});

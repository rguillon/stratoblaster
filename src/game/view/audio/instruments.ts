import type { Envelope, Instrument, ToneLayer } from '../../../audio/audio-types';

/**
 * The instruments of the generated music (P12-R06..R08, GD-70): synthwave (reviewer,
 * 2026-10-26), all synthesised from oscillators and noise through filters and envelopes. An 80s
 * drum machine (punchy kicks, big gated snares, synth toms), pumping and rolling saw basses,
 * detuned saw pads, plucked arpeggios and leads sent to the track's echo, and the music reverb.
 * Drums play at {@link DRUM_PITCH} (toms higher or lower for fills); their layers' pitches are
 * ratios of it.
 */

const env = (attack: number, decay: number, sustain: number, release: number): Envelope => ({
  attack,
  decay,
  sustain,
  release,
});

const layer = (
  wave: ToneLayer['wave'],
  gain: number,
  rest: Partial<ToneLayer> = {},
): ToneLayer => ({ wave, gain, pitch: 1, envelope: env(0.002, 0.12, 0, 0.05), ...rest });

/** Saws detuned by `cents`: the classic analog "supersaw". */
const saws = (cents: readonly number[], gain: number, rest: Partial<ToneLayer>): ToneLayer[] =>
  cents.map((detuneCents) => layer('sawtooth', gain, { detuneCents, ...rest }));

/** The MIDI pitch drum notes are played at (their layers' pitches are ratios of it). */
export const DRUM_PITCH = 36;

const DRUMS: Readonly<Record<string, Instrument>> = {
  kick: {
    gain: 0.95,
    layers: [
      layer('sine', 1, {
        pitch: 2.6,
        glideTo: 0.75,
        glideSeconds: 0.09,
        envelope: env(0.001, 0.3, 0, 0.05),
      }),
      layer('noise', 0.2, {
        envelope: env(0.001, 0.01, 0, 0.01),
        filter: { type: 'highpass', frequency: 3000 },
      }),
    ],
  },
  'kick-heavy': {
    gain: 1,
    layers: [
      layer('sine', 1, {
        pitch: 2,
        glideTo: 0.6,
        glideSeconds: 0.16,
        envelope: env(0.002, 0.42, 0, 0.08),
      }),
      layer('square', 0.14, {
        pitch: 1.2,
        glideTo: 0.6,
        glideSeconds: 0.08,
        envelope: env(0.001, 0.06, 0, 0.02),
        filter: { type: 'lowpass', frequency: 600 },
      }),
    ],
  },
  /** The big 80s snare: noise held at half its peak for the note, then cut (the "gate"). */
  'snare-gated': {
    gain: 0.6,
    reverb: 0.45,
    layers: [
      layer('noise', 0.9, {
        envelope: env(0.001, 0.05, 0.45, 0.025),
        filter: { type: 'bandpass', frequency: 1900, q: 0.6 },
      }),
      layer('triangle', 0.6, {
        pitch: 5.2,
        glideTo: 4,
        glideSeconds: 0.06,
        envelope: env(0.001, 0.1, 0, 0.03),
      }),
    ],
  },
  hat: {
    gain: 0.2,
    layers: [
      layer('noise', 1, {
        envelope: env(0.001, 0.03, 0, 0.02),
        filter: { type: 'highpass', frequency: 8500 },
      }),
    ],
  },
  'open-hat': {
    gain: 0.15,
    layers: [
      layer('noise', 1, {
        envelope: env(0.001, 0.2, 0.1, 0.08),
        filter: { type: 'highpass', frequency: 7500 },
      }),
    ],
  },
  shaker: {
    gain: 0.15,
    layers: [
      layer('noise', 1, {
        envelope: env(0.012, 0.05, 0, 0.03),
        filter: { type: 'bandpass', frequency: 6500, q: 1.2 },
      }),
    ],
  },
  /** Simmons-style synth toms: a falling sine with a touch of noise, played at several pitches. */
  tom: {
    gain: 0.55,
    reverb: 0.35,
    layers: [
      layer('sine', 1, {
        pitch: 3,
        glideTo: 2,
        glideSeconds: 0.2,
        envelope: env(0.002, 0.32, 0, 0.08),
      }),
      layer('noise', 0.12, {
        envelope: env(0.001, 0.04, 0, 0.02),
        filter: { type: 'lowpass', frequency: 2500 },
      }),
    ],
  },
};

const BASSES: Readonly<Record<string, Instrument>> = {
  /** Outrun: the pumping octave saw bass. */
  'bass-saw': {
    gain: 0.42,
    layers: [
      layer('sawtooth', 0.7, {
        envelope: env(0.004, 0.16, 0.45, 0.04),
        filter: { type: 'lowpass', frequency: 650, from: 2600, sweepSeconds: 0.12, q: 5 },
      }),
      layer('square', 0.45, { pitch: 0.5, envelope: env(0.004, 0.2, 0.6, 0.04) }),
    ],
  },
  /** Dreamwave: a round filtered saw over a sine sub. */
  'bass-dream': {
    gain: 0.45,
    layers: [
      layer('sawtooth', 0.55, {
        envelope: env(0.02, 0.3, 0.7, 0.2),
        filter: { type: 'lowpass', frequency: 520, q: 1 },
      }),
      layer('sine', 0.6, { pitch: 0.5, envelope: env(0.02, 0.3, 0.8, 0.2) }),
    ],
  },
  /** A plucked square bass for syncopated lines. */
  'bass-pluck': {
    gain: 0.45,
    layers: [
      layer('square', 0.6, {
        envelope: env(0.003, 0.16, 0.2, 0.06),
        filter: { type: 'lowpass', frequency: 450, from: 2000, sweepSeconds: 0.09, q: 6 },
      }),
      layer('sine', 0.6, { pitch: 0.5, envelope: env(0.003, 0.2, 0.3, 0.06) }),
    ],
  },
  /** Darksynth: two detuned saws, growling, over a sub. */
  'bass-heavy': {
    gain: 0.42,
    layers: [
      ...saws([-14, 14], 0.6, {
        envelope: env(0.004, 0.18, 0.6, 0.05),
        filter: { type: 'lowpass', frequency: 560, from: 1600, sweepSeconds: 0.08, q: 3 },
      }),
      layer('sine', 0.7, { pitch: 0.5, envelope: env(0.004, 0.2, 0.8, 0.05) }),
    ],
  },
};

const PADS: Readonly<Record<string, Instrument>> = {
  'pad-warm': {
    gain: 0.1,
    reverb: 0.5,
    layers: saws([-12, 0, 12], 0.5, {
      envelope: env(0.35, 0.6, 0.75, 0.8),
      filter: { type: 'lowpass', frequency: 1700, q: 0.8 },
    }),
  },
  'pad-dream': {
    gain: 0.1,
    reverb: 0.6,
    layers: [
      ...saws([-9, 9], 0.5, {
        envelope: env(0.7, 0.8, 0.8, 1.2),
        filter: { type: 'lowpass', frequency: 1200, q: 0.7 },
      }),
      layer('triangle', 0.5, { pitch: 2, envelope: env(0.9, 0.8, 0.7, 1.4) }),
    ],
  },
  'pad-dark': {
    gain: 0.11,
    reverb: 0.5,
    layers: saws([-14, 0, 14], 0.5, {
      envelope: env(0.45, 0.8, 0.7, 0.9),
      filter: { type: 'lowpass', frequency: 800, q: 1.4 },
    }),
  },
};

const ARPS: Readonly<Record<string, Instrument>> = {
  'arp-pluck': {
    gain: 0.13,
    echo: 0.4,
    reverb: 0.2,
    layers: [
      layer('sawtooth', 0.7, {
        envelope: env(0.002, 0.13, 0.1, 0.07),
        filter: { type: 'lowpass', frequency: 1300, from: 5000, sweepSeconds: 0.09, q: 4 },
      }),
    ],
  },
  'arp-square': {
    gain: 0.13,
    echo: 0.4,
    reverb: 0.2,
    layers: [
      layer('square', 0.6, {
        envelope: env(0.002, 0.12, 0.1, 0.06),
        filter: { type: 'lowpass', frequency: 1500, from: 4200, sweepSeconds: 0.08, q: 3 },
      }),
    ],
  },
  /** A glassy FM-style bell arpeggio (dreamwave). */
  'arp-glass': {
    gain: 0.12,
    echo: 0.45,
    reverb: 0.4,
    layers: [
      layer('sine', 0.8, { envelope: env(0.002, 0.3, 0.1, 0.4) }),
      layer('sine', 0.25, { pitch: 3, envelope: env(0.002, 0.12, 0, 0.2) }),
    ],
  },
};

const LEADS: Readonly<Record<string, Instrument>> = {
  'lead-square': {
    gain: 0.14,
    echo: 0.3,
    reverb: 0.3,
    layers: [
      layer('square', 0.55, {
        envelope: env(0.01, 0.2, 0.65, 0.15),
        filter: { type: 'lowpass', frequency: 2800, q: 1 },
      }),
      layer('sawtooth', 0.35, {
        detuneCents: 8,
        envelope: env(0.01, 0.2, 0.65, 0.15),
        filter: { type: 'lowpass', frequency: 2800, q: 1 },
      }),
    ],
  },
  /** The supersaw lead. */
  'lead-saw': {
    gain: 0.13,
    echo: 0.3,
    reverb: 0.35,
    layers: saws([-14, 0, 14], 0.45, {
      envelope: env(0.02, 0.25, 0.7, 0.2),
      filter: { type: 'lowpass', frequency: 3200, q: 1 },
    }),
  },
  /** An FM-style electric bell (DX7 style, dreamwave). */
  bell: {
    gain: 0.13,
    echo: 0.35,
    reverb: 0.45,
    layers: [
      layer('sine', 0.8, { envelope: env(0.002, 0.8, 0.1, 1.2) }),
      layer('sine', 0.3, { pitch: 2.76, envelope: env(0.002, 0.4, 0, 0.6) }),
      layer('sine', 0.15, { pitch: 5.4, envelope: env(0.002, 0.2, 0, 0.3) }),
    ],
  },
  /** Analog brass (darksynth). */
  'lead-brass': {
    gain: 0.14,
    echo: 0.2,
    reverb: 0.3,
    layers: saws([-6, 6], 0.6, {
      envelope: env(0.04, 0.25, 0.6, 0.2),
      filter: { type: 'lowpass', frequency: 1400, from: 400, sweepSeconds: 0.12, q: 2 },
    }),
  },
};

/** Every instrument the game's tracks name. */
export const INSTRUMENTS: Readonly<Record<string, Instrument>> = {
  ...DRUMS,
  ...BASSES,
  ...PADS,
  ...ARPS,
  ...LEADS,
};

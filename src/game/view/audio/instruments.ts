import type { Envelope, Instrument, ToneLayer } from '../../../audio/audio-types';

/**
 * The instruments of the generated music (P12-R06..R08, GD-70), all synthesised: oscillators and
 * noise through filters and envelopes, in the cyberpunk / synthwave direction (GD-60). Drums play
 * at a fixed note (their layers' pitches are ratios of it); the others follow the notes.
 */

const env = (attack: number, decay: number, sustain: number, release: number): Envelope => ({
  attack,
  decay,
  sustain,
  release,
});

const PERC = env(0.002, 0.12, 0, 0.05);

const layer = (
  wave: ToneLayer['wave'],
  gain: number,
  rest: Partial<ToneLayer> = {},
): ToneLayer => ({
  wave,
  gain,
  pitch: 1,
  envelope: PERC,
  ...rest,
});

/** The MIDI pitch drum notes are played at (their layers' pitches are ratios of it). */
export const DRUM_PITCH = 36;

/** Drums, shared by every style (their patterns differ). */
const DRUMS: Readonly<Record<string, Instrument>> = {
  kick: {
    gain: 0.9,
    layers: [
      layer('sine', 1, {
        pitch: 2.4,
        glideTo: 0.72,
        glideSeconds: 0.11,
        envelope: env(0.002, 0.28, 0, 0.06),
      }),
      layer('noise', 0.18, {
        envelope: env(0.001, 0.012, 0, 0.01),
        filter: { type: 'highpass', frequency: 2500 },
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
      layer('square', 0.12, {
        pitch: 1.2,
        glideTo: 0.6,
        glideSeconds: 0.08,
        envelope: env(0.001, 0.06, 0, 0.02),
        filter: { type: 'lowpass', frequency: 600 },
      }),
    ],
  },
  snare: {
    gain: 0.55,
    layers: [
      layer('noise', 0.8, {
        envelope: env(0.001, 0.16, 0, 0.06),
        filter: { type: 'bandpass', frequency: 2200, q: 0.8 },
      }),
      layer('triangle', 0.5, {
        pitch: 2.8,
        glideTo: 2.2,
        glideSeconds: 0.05,
        envelope: env(0.001, 0.08, 0, 0.03),
      }),
    ],
  },
  clap: {
    gain: 0.45,
    layers: [0, 0.012, 0.024].map((delay) =>
      layer('noise', 0.6, {
        delay,
        envelope: env(0.001, 0.05, 0, 0.08),
        filter: { type: 'bandpass', frequency: 1500, q: 1.5 },
      }),
    ),
  },
  hat: {
    gain: 0.22,
    layers: [
      layer('noise', 1, {
        envelope: env(0.001, 0.035, 0, 0.02),
        filter: { type: 'highpass', frequency: 8000 },
      }),
    ],
  },
  'open-hat': {
    gain: 0.18,
    layers: [
      layer('noise', 1, {
        envelope: env(0.001, 0.22, 0.1, 0.1),
        filter: { type: 'highpass', frequency: 7000 },
      }),
    ],
  },
  shaker: {
    gain: 0.16,
    layers: [
      layer('noise', 1, {
        envelope: env(0.015, 0.05, 0, 0.03),
        filter: { type: 'bandpass', frequency: 6000, q: 1.2 },
      }),
    ],
  },
  tom: {
    gain: 0.6,
    layers: [
      layer('sine', 1, {
        pitch: 3,
        glideTo: 2,
        glideSeconds: 0.18,
        envelope: env(0.002, 0.3, 0, 0.08),
      }),
    ],
  },
  'tom-low': {
    gain: 0.65,
    layers: [
      layer('sine', 1, {
        pitch: 2,
        glideTo: 1.3,
        glideSeconds: 0.22,
        envelope: env(0.002, 0.4, 0, 0.1),
      }),
    ],
  },
};

/** Basses: World 1 driving saw, World 2 soft triangle, World 3 plucked, World 4 heavy. */
const BASSES: Readonly<Record<string, Instrument>> = {
  'bass-saw': {
    gain: 0.4,
    layers: [
      layer('sawtooth', 0.7, {
        envelope: env(0.004, 0.18, 0.5, 0.05),
        filter: { type: 'lowpass', frequency: 700, from: 2400, sweepSeconds: 0.12, q: 4 },
      }),
      layer('square', 0.4, { pitch: 0.5, envelope: env(0.004, 0.2, 0.6, 0.05) }),
    ],
  },
  'bass-soft': {
    gain: 0.45,
    layers: [
      layer('triangle', 1, { envelope: env(0.02, 0.3, 0.7, 0.2) }),
      layer('sine', 0.5, { pitch: 0.5, envelope: env(0.02, 0.3, 0.7, 0.2) }),
    ],
  },
  'bass-pluck': {
    gain: 0.45,
    layers: [
      layer('square', 0.6, {
        envelope: env(0.003, 0.16, 0.2, 0.06),
        filter: { type: 'lowpass', frequency: 450, from: 1800, sweepSeconds: 0.09, q: 6 },
      }),
      layer('sine', 0.6, { pitch: 0.5, envelope: env(0.003, 0.2, 0.3, 0.06) }),
    ],
  },
  'bass-heavy': {
    gain: 0.42,
    layers: [
      layer('sawtooth', 0.7, {
        envelope: env(0.005, 0.25, 0.7, 0.08),
        filter: { type: 'lowpass', frequency: 520, q: 2 },
      }),
      layer('sawtooth', 0.55, {
        detuneCents: 14,
        envelope: env(0.005, 0.25, 0.7, 0.08),
        filter: { type: 'lowpass', frequency: 520, q: 2 },
      }),
      layer('sine', 0.7, { pitch: 0.5, envelope: env(0.005, 0.25, 0.8, 0.08) }),
    ],
  },
};

/** Pads, arpeggios, leads and bells. */
const TONES: Readonly<Record<string, Instrument>> = {
  'pad-warm': {
    gain: 0.12,
    layers: [-8, 8].map((detuneCents) =>
      layer('sawtooth', 0.6, {
        detuneCents,
        envelope: env(0.4, 0.6, 0.7, 0.8),
        filter: { type: 'lowpass', frequency: 1400, q: 0.7 },
      }),
    ),
  },
  'pad-cold': {
    gain: 0.12,
    layers: [
      layer('triangle', 0.7, { envelope: env(0.8, 1, 0.8, 1.4) }),
      layer('sine', 0.5, { pitch: 2, detuneCents: 6, envelope: env(1, 1, 0.7, 1.6) }),
    ],
  },
  'pad-dark': {
    gain: 0.12,
    layers: [-10, 10].map((detuneCents) =>
      layer('sawtooth', 0.6, {
        detuneCents,
        envelope: env(0.5, 0.8, 0.7, 0.9),
        filter: { type: 'lowpass', frequency: 750, q: 1.2 },
      }),
    ),
  },
  'arp-pluck': {
    gain: 0.13,
    layers: [
      layer('sawtooth', 0.7, {
        envelope: env(0.002, 0.14, 0.1, 0.08),
        filter: { type: 'lowpass', frequency: 1200, from: 4500, sweepSeconds: 0.1, q: 3 },
      }),
    ],
  },
  'arp-glass': {
    gain: 0.12,
    layers: [
      layer('sine', 0.8, { envelope: env(0.002, 0.3, 0.1, 0.4) }),
      layer('sine', 0.25, { pitch: 3, envelope: env(0.002, 0.12, 0, 0.2) }),
    ],
  },
  marimba: {
    gain: 0.2,
    layers: [
      layer('sine', 1, { envelope: env(0.002, 0.22, 0, 0.08) }),
      layer('sine', 0.35, { pitch: 4, envelope: env(0.001, 0.05, 0, 0.03) }),
    ],
  },
  'lead-square': {
    gain: 0.14,
    layers: [
      layer('square', 0.6, {
        envelope: env(0.01, 0.2, 0.6, 0.15),
        filter: { type: 'lowpass', frequency: 2600, q: 1 },
      }),
      layer('sawtooth', 0.35, {
        detuneCents: 7,
        envelope: env(0.01, 0.2, 0.6, 0.15),
        filter: { type: 'lowpass', frequency: 2600, q: 1 },
      }),
    ],
  },
  'lead-flute': {
    gain: 0.16,
    layers: [
      layer('triangle', 0.8, { envelope: env(0.04, 0.2, 0.7, 0.18) }),
      layer('noise', 0.05, {
        envelope: env(0.02, 0.08, 0.2, 0.1),
        filter: { type: 'bandpass', frequency: 3000, q: 2 },
      }),
    ],
  },
  'lead-brass': {
    gain: 0.14,
    layers: [-6, 6].map((detuneCents) =>
      layer('sawtooth', 0.6, {
        detuneCents,
        envelope: env(0.04, 0.25, 0.6, 0.2),
        filter: { type: 'lowpass', frequency: 1300, from: 400, sweepSeconds: 0.12, q: 2 },
      }),
    ),
  },
  bell: {
    gain: 0.12,
    layers: [
      layer('sine', 0.8, { envelope: env(0.002, 0.8, 0.1, 1.2) }),
      layer('sine', 0.3, { pitch: 2.76, envelope: env(0.002, 0.4, 0, 0.6) }),
      layer('sine', 0.15, { pitch: 5.4, envelope: env(0.002, 0.2, 0, 0.3) }),
    ],
  },
};

/** Every instrument the game's tracks name. */
export const INSTRUMENTS: Readonly<Record<string, Instrument>> = {
  ...DRUMS,
  ...BASSES,
  ...TONES,
};

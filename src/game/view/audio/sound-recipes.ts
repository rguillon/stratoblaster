import type { Envelope, ToneLayer } from '../../../audio/audio-types';

/** The building blocks of the game's sound effects (P12-R09): envelopes, tones and recipes. */

export const env = (attack: number, decay: number, sustain = 0, release = 0.03): Envelope => ({
  attack,
  decay,
  sustain,
  release,
});

export const tone = (
  wave: ToneLayer['wave'],
  pitch: number,
  gain: number,
  envelope: Envelope,
  rest: Partial<ToneLayer> = {},
): ToneLayer => ({ wave, pitch, gain, envelope, ...rest });

/** Rounds in a minigun burst, and the seconds between them (about 48 rounds a second). */
export const MINIGUN = { rounds: 6, gap: 0.021 };

/**
 * A minigun burst (reviewer, 2026-10-26): rounds `gap` apart, each a gritty crack over a short
 * thump. A volley's burst lasts until the next volley (the gun fires 8 a second), so holding fire
 * rattles on without a break: BRRRT.
 */
export function minigun({ rounds, gap }: typeof MINIGUN): ToneLayer[] {
  return Array.from({ length: rounds }, (_, i) => {
    const delay = i * gap;
    const accent = i % 2 ? 0.75 : 1;
    return [
      tone('noise', 1, accent, env(0.001, 0.014, 0, 0.004), {
        delay,
        filter: { type: 'bandpass', frequency: 1700, q: 0.9 },
      }),
      tone('square', 150, 0.5 * accent, env(0.001, 0.016, 0, 0.004), {
        delay,
        glideTo: 65,
        glideSeconds: 0.018,
        filter: { type: 'lowpass', frequency: 1200 },
      }),
    ];
  }).flat();
}

/** How big an explosion is (reviewer, 2026-10-26: more realistic). */
export interface ExplosionSize {
  /** How long its body lasts, in seconds. */
  readonly seconds: number;
  /** Cut-off its body starts from, closing down to a rumble (Hz). */
  readonly body: number;
  /** Pitch of its sub-bass thump, falling by half (Hz). */
  readonly thump: number;
  /** A low rumble rolling on after it, in seconds (0: none). */
  readonly tail: number;
  /** Bits of debris crackling after it. */
  readonly debris: number;
}

/** Spacing and pitches of the debris crackles: fixed, so a sound is the same each time. */
const DEBRIS_GAPS = [0.11, 0.07, 0.16, 0.09, 0.13, 0.06, 0.18, 0.1];
const DEBRIS_PITCHES = [2400, 1700, 3100, 2000, 2700, 1500, 3500, 2200];

/**
 * A realistic explosion (reviewer, 2026-10-26), layer by layer: a few milliseconds of broadband
 * crack (the shock front), a body of noise whose brightness closes fast (the fireball), a
 * sub-bass thump, a low rumble rolling on for the big ones, and debris crackling after it.
 * Most of its energy is low, so a busy wave does not turn into a hiss. Starts `delay` seconds in.
 */
export function explosion(size: ExplosionSize, delay = 0): ToneLayer[] {
  const { seconds, body, thump, tail, debris } = size;
  const layers: ToneLayer[] = [
    tone('noise', 1, 0.35, env(0.001, 0.012, 0, 0.006), {
      delay,
      filter: { type: 'highpass', frequency: 1200 },
    }),
    tone('noise', 1, 0.8, env(0.003, seconds * 0.6, 0, seconds * 0.35), {
      delay,
      filter: { type: 'lowpass', frequency: 180, from: body, sweepSeconds: seconds * 0.8, q: 0.5 },
    }),
    tone('sine', thump, 0.9, env(0.002, seconds * 0.7, 0, 0.05), {
      delay,
      glideTo: thump * 0.45,
      glideSeconds: seconds * 0.6,
    }),
  ];
  if (tail > 0) {
    layers.push(
      tone('noise', 1, 0.35, env(0.04, tail, 0, 0.1), {
        delay,
        filter: { type: 'lowpass', frequency: 260, q: 0.7 },
      }),
    );
  }
  let at = delay + seconds * 0.2;
  for (let i = 0; i < debris; i++) {
    at += (DEBRIS_GAPS[i % DEBRIS_GAPS.length] ?? 0.1) * (1 + seconds * 0.5);
    layers.push(
      tone('noise', 1, 0.14 * (1 - (0.5 * i) / Math.max(1, debris)), env(0.001, 0.016, 0, 0.01), {
        delay: at,
        filter: {
          type: 'bandpass',
          frequency: DEBRIS_PITCHES[i % DEBRIS_PITCHES.length] ?? 2000,
          q: 2,
        },
      }),
    );
  }
  return layers;
}

/** Notes of a little arpeggio, one after the other. */
export function chime(
  wave: ToneLayer['wave'],
  pitches: readonly number[],
  gap: number,
  gain: number,
): ToneLayer[] {
  return pitches.map((pitch, i) =>
    tone(wave, pitch, gain, env(0.003, 0.12, 0.2, 0.12), { delay: i * gap }),
  );
}

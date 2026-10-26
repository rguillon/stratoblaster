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

/** A noisy blast: filtered noise closing down, and a falling thump. */
export function blast(seconds: number, from: number, thump: number): ToneLayer[] {
  return [
    tone('noise', 1, 0.9, env(0.002, seconds * 0.7, 0.15, seconds * 0.3), {
      filter: { type: 'lowpass', frequency: 160, from, sweepSeconds: seconds },
    }),
    tone('sine', thump, 0.8, env(0.002, seconds * 0.6, 0, 0.05), {
      glideTo: thump / 3,
      glideSeconds: seconds * 0.6,
    }),
  ];
}

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

/**
 * An enemy going down (reviewer, 2026-10-26: the hissing blasts were annoying): a short, muffled
 * boom, a deep falling thump, a low noise body closing down fast, and a tiny crackle on top. No
 * bright hiss and no tail, so a busy wave does not turn into a wash of noise.
 */
export function boom(seconds: number, body: number, thump: number): ToneLayer[] {
  return [
    tone('sine', thump, 0.9, env(0.002, seconds * 0.8, 0, 0.03), {
      glideTo: thump / 3,
      glideSeconds: seconds * 0.7,
    }),
    tone('noise', 1, 0.5, env(0.002, seconds * 0.7, 0, 0.04), {
      filter: { type: 'lowpass', frequency: 110, from: body, sweepSeconds: seconds * 0.8, q: 0.7 },
    }),
    tone('noise', 1, 0.15, env(0.001, 0.03, 0, 0.01), {
      filter: { type: 'bandpass', frequency: 2200, q: 1.5 },
    }),
  ];
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

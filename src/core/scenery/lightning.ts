import { LIGHTNING } from '../../config/weather';
import { createRng, randomIn, type Random } from '../math/rng';
import type { Atmosphere } from './atmosphere';

// Lightning (phase 9, P09-R05): when the flashes of a storm come, drawn from the level's seed,
// and how a flash lights the scene. Pure: the renderer asks for the flash at its own clock, so
// the same level always flashes at the same times, and nothing in the simulation reads it.

type Rgb = readonly [number, number, number];

/** How lightning comes and how bright it gets (see `LIGHTNING`). */
export interface LightningRules {
  /** Seconds between two strikes. */
  readonly gap: readonly [number, number];
  /** Seconds a flash lasts, and how long it takes to rise to full brightness. */
  readonly flash: number;
  readonly rise: number;
  /** Chance that a strike flashes twice, and the seconds between its two flashes. */
  readonly double: { readonly chance: number; readonly after: number };
  /** Ambient light and sky at most this many times as bright as the storm's. */
  readonly brightness: number;
  /** A flash brightens no channel of the haze past this (0..1), so it never turns white. */
  readonly maxHaze: number;
  /** Chance that a strike draws a bolt in the clouds. */
  readonly boltChance: number;
}

/** One strike: when its flashes start, and where its bolt is drawn (0..1 across and along). */
export interface Strike {
  readonly flashes: readonly number[];
  readonly bolt: { readonly x: number; readonly z: number; readonly seed: number } | undefined;
}

/**
 * The strikes of a storm along a level's clock (P09-R05): every `gap` seconds, drawn from `seed`,
 * so the same level always flashes at the same times. Strikes are drawn as far as they are asked
 * for.
 */
export class LightningSchedule {
  readonly #random: Random;
  readonly #strikes: Strike[] = [];
  #next: number;

  constructor(
    seed: number,
    private readonly rules: LightningRules = LIGHTNING,
  ) {
    this.#random = createRng(seed * 7 + 17);
    this.#next = randomIn(this.#random, rules.gap);
  }

  /** The strikes whose first flash comes before `time`. */
  strikesBefore(time: number): readonly Strike[] {
    while (this.#next < time) this.#strike();
    return this.#strikes;
  }

  /** Every flash start in [`from`, `to`). */
  flashesBetween(from: number, to: number): number[] {
    return this.strikesBefore(to)
      .flatMap((s) => s.flashes)
      .filter((t) => t >= from && t < to);
  }

  /** The strike lit at `time`, if any. */
  strikeAt(time: number): Strike | undefined {
    const strikes = this.strikesBefore(time);
    for (let i = strikes.length - 1; i >= 0; i--) {
      const strike = strikes[i];
      const last = strike?.flashes.at(-1);
      if (last === undefined || !strike) continue;
      if (time >= (strike.flashes[0] ?? 0) && time < last + this.rules.flash) return strike;
      if (last + this.rules.flash < time) break;
    }
    return undefined;
  }

  /** How bright the lightning is at `time`: 0 between flashes, 1 at a flash's height. */
  flashAt(time: number): number {
    const strike = this.strikeAt(time);
    if (!strike) return 0;
    const { flash, rise } = this.rules;
    return Math.max(...strike.flashes.map((start) => envelope(time - start, rise, flash)));
  }

  #strike(): void {
    const r = this.#random;
    const start = this.#next;
    const flashes =
      r() < this.rules.double.chance ? [start, start + this.rules.double.after] : [start];
    const bolt =
      r() < this.rules.boltChance ? { x: r(), z: r(), seed: Math.floor(r() * 1e6) } : undefined;
    this.#strikes.push({ flashes, bolt });
    this.#next = start + randomIn(r, this.rules.gap);
  }
}

/** A flash `age` seconds after it starts: a quick rise, then a fade out over `length`. */
function envelope(age: number, rise: number, length: number): number {
  if (age < 0 || age >= length) return 0;
  if (age < rise) return age / rise;
  const t = (age - rise) / (length - rise);
  return (1 - t) * (1 - t);
}

/** `c` brightened `k` times, no channel past `cap` (or past itself, if it already is). */
const brighter = (c: Rgb, k: number, cap: number): Rgb => [
  Math.min(c[0] * k, Math.max(c[0], cap)),
  Math.min(c[1] * k, Math.max(c[1], cap)),
  Math.min(c[2] * k, Math.max(c[2], cap)),
];

/**
 * `atmosphere` lit by a flash of `flash` (0..1) of a storm's lightning of strength
 * `atmosphere.lightning` (P09-R05): the ambient light, the sky and the haze up to `brightness`
 * times as bright, never more, the haze never past `maxHaze`, so the playfield never turns white.
 */
export function flashed(
  atmosphere: Atmosphere,
  flash: number,
  { brightness, maxHaze }: Pick<LightningRules, 'brightness' | 'maxHaze'> = LIGHTNING,
): Atmosphere {
  const f = Math.min(1, Math.max(0, flash)) * Math.min(1, Math.max(0, atmosphere.lightning));
  if (f <= 0) return atmosphere;
  const k = 1 + (brightness - 1) * f;
  const { ambient, sky } = atmosphere;
  return {
    ...atmosphere,
    ambient: { ...ambient, intensity: ambient.intensity * k },
    sky: {
      ...sky,
      haze: brighter(sky.haze, k, maxHaze),
      environmentIntensity: sky.environmentIntensity * k,
    },
  };
}

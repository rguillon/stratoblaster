import type { EnemySide } from '../../../core/entities/enemy';
import type { WaveScript } from '../../../core/systems/wave-runner';

/*
 * The wave scripts of World 1 (P06-R07, R08). Each beat is written in seconds from the start of
 * the level for readability, and turned into a scrolled distance at the level's ground speed:
 * waves are triggered by distance (GD-40). A beat is
 * `[seconds, kind, groups, seconds between groups, side, position (0..1), spread]`.
 * Gnats come in groups of five; every other kind one by one.
 */

type Kind =
  | 'gnat'
  | 'hornet'
  | 'scout'
  | 'strafer'
  | 'weaver'
  | 'splitter'
  | 'carrier'
  | 'spinner'
  | 'lancer'
  | 'rocketeer'
  | 'bulwark';

type Beat = readonly [
  seconds: number,
  kind: Kind,
  count: number,
  interval: number,
  side: EnemySide,
  position: number,
  spread?: number,
];

/**
 * Enemy density (phase 6 review: +50 %): each beat brings this many times its groups, rounded.
 * A beat of one group gets its extra groups `DENSITY_GAP` seconds apart and, from the top,
 * `DENSITY_SPREAD` across the screen, so they do not come in on top of each other.
 */
export const WAVE_DENSITY = 1.5;
const DENSITY_GAP = 1.5;
const DENSITY_SPREAD = 0.3;

/** A beat with `density` times its groups (see {@link WAVE_DENSITY}). */
function denser(beat: Beat, density: number): Beat {
  const [seconds, kind, count, interval, side, position, spread] = beat;
  const more = Math.max(1, Math.round(count * density));
  if (more === count || count > 1) {
    const head = [seconds, kind, more, interval, side, position] as const;
    return spread === undefined ? head : [...head, spread];
  }
  const across = side === 'top' ? DENSITY_SPREAD : -DENSITY_SPREAD / 2;
  return [seconds, kind, more, DENSITY_GAP, side, position, spread ?? across];
}

/** The beats as a wave script, at `speed` world units per second and `density` (×1: as written). */
export function waveScript(
  speed: number,
  beats: readonly Beat[],
  density = WAVE_DENSITY,
): WaveScript {
  return beats.map((beat) => {
    const [seconds, kind, count, interval, side, position, spread] = denser(beat, density);
    return {
      at: seconds * speed,
      kind,
      count,
      interval,
      entry: { side, position },
      ...(spread === undefined ? {} : { spread }),
    };
  });
}

/**
 * `script` without the waves that would start in the `quiet` world units before each of the
 * distances `bosses` (P07-R06: the stretch before a boss is left free).
 */
export function quietBefore(
  script: WaveScript,
  bosses: readonly number[],
  quiet: number,
): WaveScript {
  return script.filter((wave) => !bosses.some((at) => wave.at > at - quiet && wave.at <= at));
}

/** Light groups that fill a level's lulls (phase 6 review: the levels felt empty). */
export interface Filler {
  /** Kinds taken in turn, each group from the top. */
  readonly kinds: readonly Kind[];
  /**
   * Longest stretch, in seconds, without a group coming in: `start` at the first beat, going
   * down to `end` at the last one, so the level fills up as it goes.
   */
  readonly maxGap: readonly [start: number, end: number];
}

/** Where the filler groups come in from the top, in turn. */
const FILL_POSITIONS = [0.3, 0.7, 0.5, 0.2, 0.8];

/**
 * `beats` with filler groups in their lulls (phase 6 review): after each beat, a group of the
 * filler's kinds in turn every `maxGap` seconds, as long as the next beat is more than one and
 * a half gaps away.
 */
export function fill(beats: readonly Beat[], filler: Filler): Beat[] {
  const sorted = [...beats].sort((a, b) => a[0] - b[0]);
  const [first, last] = [sorted[0]?.[0] ?? 0, sorted.at(-1)?.[0] ?? 0];
  const [start, end] = filler.maxGap;
  const gapAt = (t: number): number => start + ((end - start) * (t - first)) / (last - first || 1);
  const out: Beat[] = [];
  let n = 0;
  sorted.forEach((beat, i) => {
    out.push(beat);
    const next = sorted[i + 1]?.[0] ?? beat[0];
    for (let t = beat[0] + gapAt(beat[0]); next - t > gapAt(t) / 2; t += gapAt(t), n++) {
      const kind = filler.kinds[n % filler.kinds.length];
      const position = FILL_POSITIONS[n % FILL_POSITIONS.length] ?? 0.5;
      if (kind) out.push([t, kind, 1, 0, 'top', position]);
    }
  });
  return out;
}

/** 1-1: Gnats, Hornets, Scouts and Strafers, a few at a time (easy, even for a kid). */
export const WAVES_1_1: readonly Beat[] = [
  [4, 'scout', 1, 0, 'top', 0.5],
  [12, 'scout', 2, 2.5, 'top', 0.3, 0.4],
  [22, 'gnat', 1, 0, 'top', 0.3],
  [33, 'hornet', 2, 2, 'top', 0.3, 0.4],
  [42, 'strafer', 1, 0, 'left', 0.8],
  [50, 'scout', 3, 1.5, 'top', 0.2, 0.3],
  [62, 'gnat', 1, 0, 'top', 0.7],
  [73, 'hornet', 3, 1.5, 'top', 0.25, 0.25],
  [82, 'strafer', 1, 0, 'right', 0.75],
  [90, 'scout', 2, 2, 'top', 0.4, 0.2],
  [100, 'gnat', 1, 0, 'top', 0.3],
  [133, 'strafer', 2, 3, 'left', 0.82],
  [142, 'hornet', 3, 1.2, 'top', 0.2, 0.3],
  [152, 'scout', 3, 1.2, 'top', 0.25, 0.25],
  [163, 'gnat', 1, 0, 'top', 0.7],
  [173, 'strafer', 2, 2.5, 'right', 0.78],
  [182, 'hornet', 3, 1, 'top', 0.2, 0.3],
  [191, 'scout', 3, 1.2, 'top', 0.3, 0.2],
  [201, 'gnat', 1, 0, 'top', 0.3],
  [211, 'strafer', 2, 2, 'left', 0.8],
  [219, 'hornet', 3, 1, 'top', 0.15, 0.35],
  [226, 'gnat', 1, 0, 'top', 0.6],
];

/** 1-2: the 1-1 kinds, plus Weavers and Splitters. */
export const WAVES_1_2: readonly Beat[] = [
  [4, 'scout', 2, 2, 'top', 0.35, 0.3],
  [12, 'gnat', 1, 0, 'top', 0.3],
  [20, 'weaver', 1, 0, 'top', 0.5],
  [28, 'hornet', 3, 1.5, 'top', 0.2, 0.3],
  [36, 'strafer', 1, 0, 'left', 0.8],
  [42, 'weaver', 2, 3, 'top', 0.35, 0.3],
  [50, 'gnat', 1, 0, 'top', 0.7],
  [56, 'scout', 3, 1.2, 'top', 0.2, 0.3],
  [64, 'splitter', 1, 0, 'top', 0.3],
  [72, 'strafer', 2, 2, 'right', 0.75],
  [80, 'hornet', 3, 1, 'top', 0.25, 0.25],
  [88, 'weaver', 2, 2.5, 'top', 0.4, 0.2],
  [96, 'gnat', 1, 0, 'top', 0.3],
  [104, 'splitter', 1, 0, 'top', 0.7],
  [130, 'weaver', 2, 2, 'top', 0.3, 0.4],
  [136, 'gnat', 1, 0, 'top', 0.3],
  [146, 'splitter', 2, 3, 'top', 0.3, 0.4],
  [154, 'strafer', 2, 2, 'left', 0.8],
  [160, 'scout', 3, 1, 'top', 0.2, 0.3],
  [168, 'hornet', 4, 1, 'top', 0.15, 0.23],
  [176, 'weaver', 3, 2, 'top', 0.3, 0.2],
  [184, 'gnat', 1, 0, 'top', 0.7],
  [190, 'splitter', 2, 2.5, 'top', 0.7, -0.4],
  [198, 'strafer', 2, 2, 'right', 0.78],
  [204, 'scout', 4, 1, 'top', 0.15, 0.23],
  [212, 'gnat', 1, 0, 'top', 0.7],
  [220, 'weaver', 3, 1.5, 'top', 0.25, 0.25],
  [226, 'hornet', 4, 0.8, 'top', 0.15, 0.23],
];

/** 1-3: the 1-2 kinds, plus Carriers and Spinners. */
export const WAVES_1_3: readonly Beat[] = [
  [4, 'scout', 3, 1.5, 'top', 0.25, 0.25],
  [12, 'gnat', 1, 0, 'top', 0.3],
  [18, 'weaver', 2, 2, 'top', 0.3, 0.4],
  [26, 'spinner', 1, 0, 'top', 0.5],
  [34, 'hornet', 4, 1, 'top', 0.15, 0.23],
  [42, 'strafer', 2, 2, 'left', 0.8],
  [50, 'splitter', 2, 2.5, 'top', 0.3, 0.4],
  [58, 'carrier', 1, 0, 'top', 0.5],
  [70, 'scout', 3, 1, 'top', 0.2, 0.3],
  [78, 'spinner', 2, 4, 'top', 0.3, 0.4],
  [88, 'weaver', 3, 1.5, 'top', 0.25, 0.25],
  [96, 'gnat', 2, 2.5, 'top', 0.3, 0.4],
  [104, 'strafer', 2, 2, 'right', 0.78],
  [130, 'spinner', 2, 3, 'top', 0.3, 0.4],
  [136, 'hornet', 4, 0.8, 'top', 0.15, 0.23],
  [144, 'carrier', 1, 0, 'top', 0.35],
  [150, 'weaver', 3, 1.5, 'top', 0.6, 0.15],
  [160, 'splitter', 3, 2, 'top', 0.2, 0.3],
  [168, 'strafer', 2, 2, 'left', 0.8],
  [176, 'spinner', 2, 3, 'top', 0.7, -0.4],
  [182, 'gnat', 2, 2, 'top', 0.3, 0.4],
  [190, 'weaver', 2, 2, 'top', 0.3, 0.4],
  [198, 'scout', 4, 1, 'top', 0.15, 0.23],
  [206, 'hornet', 4, 0.8, 'top', 0.2, 0.2],
  [212, 'weaver', 3, 1.2, 'top', 0.3, 0.2],
  [218, 'spinner', 2, 2, 'top', 0.3, 0.4],
  [224, 'splitter', 2, 2, 'top', 0.3, 0.4],
];

/** 1-4: the 1-3 kinds, plus Lancers and Rocketeers. */
export const WAVES_1_4: readonly Beat[] = [
  [4, 'scout', 3, 1.2, 'top', 0.25, 0.25],
  [10, 'gnat', 2, 2.5, 'top', 0.3, 0.4],
  [18, 'lancer', 1, 0, 'top', 0.5],
  [26, 'hornet', 4, 0.8, 'top', 0.15, 0.23],
  [32, 'weaver', 3, 1.5, 'top', 0.3, 0.2],
  [40, 'rocketeer', 1, 0, 'top', 0.5],
  [48, 'strafer', 2, 2, 'left', 0.8],
  [54, 'splitter', 2, 2, 'top', 0.3, 0.4],
  [62, 'spinner', 2, 3, 'top', 0.3, 0.4],
  [70, 'lancer', 2, 3, 'top', 0.25, 0.5],
  [78, 'carrier', 1, 0, 'top', 0.5],
  [86, 'scout', 4, 1, 'top', 0.15, 0.23],
  [94, 'rocketeer', 2, 3, 'top', 0.3, 0.4],
  [102, 'gnat', 2, 2, 'top', 0.3, 0.4],
  [130, 'lancer', 2, 2, 'top', 0.3, 0.4],
  [134, 'hornet', 5, 0.7, 'top', 0.1, 0.2],
  [142, 'rocketeer', 2, 3, 'top', 0.25, 0.5],
  [148, 'weaver', 4, 1.2, 'top', 0.2, 0.2],
  [156, 'carrier', 1, 0, 'top', 0.4],
  [164, 'spinner', 2, 3, 'top', 0.7, -0.4],
  [170, 'strafer', 3, 1.5, 'right', 0.8],
  [178, 'splitter', 3, 2, 'top', 0.2, 0.3],
  [186, 'lancer', 3, 2, 'top', 0.2, 0.3],
  [194, 'gnat', 2, 2, 'top', 0.3, 0.4],
  [200, 'rocketeer', 2, 2, 'top', 0.3, 0.4],
  [206, 'scout', 4, 0.8, 'top', 0.15, 0.23],
  [212, 'carrier', 1, 0, 'top', 0.6],
  [218, 'hornet', 5, 0.6, 'top', 0.1, 0.2],
  [224, 'spinner', 2, 2, 'top', 0.3, 0.4],
];

/** 1-5: every kind, Bulwarks included. */
export const WAVES_1_5: readonly Beat[] = [
  [4, 'scout', 4, 1, 'top', 0.15, 0.23],
  [10, 'gnat', 2, 2, 'top', 0.3, 0.4],
  [16, 'bulwark', 1, 0, 'top', 0.5],
  [24, 'hornet', 5, 0.7, 'top', 0.1, 0.2],
  [30, 'weaver', 3, 1.2, 'top', 0.3, 0.2],
  [36, 'lancer', 2, 2, 'top', 0.25, 0.5],
  [44, 'rocketeer', 2, 2.5, 'top', 0.3, 0.4],
  [50, 'strafer', 3, 1.5, 'left', 0.8],
  [56, 'splitter', 3, 2, 'top', 0.2, 0.3],
  [64, 'spinner', 2, 2.5, 'top', 0.3, 0.4],
  [70, 'carrier', 1, 0, 'top', 0.5],
  [78, 'bulwark', 1, 0, 'top', 0.35],
  [84, 'scout', 4, 0.8, 'top', 0.15, 0.23],
  [92, 'lancer', 3, 1.5, 'top', 0.2, 0.3],
  [98, 'gnat', 3, 1.5, 'top', 0.2, 0.3],
  [104, 'rocketeer', 2, 2, 'top', 0.3, 0.4],
  [130, 'bulwark', 2, 4, 'top', 0.3, 0.4],
  [134, 'hornet', 5, 0.6, 'top', 0.1, 0.2],
  [140, 'spinner', 2, 2.5, 'top', 0.7, -0.4],
  [146, 'carrier', 1, 0, 'top', 0.4],
  [152, 'weaver', 4, 1, 'top', 0.2, 0.2],
  [158, 'strafer', 3, 1.5, 'right', 0.8],
  [164, 'lancer', 3, 1.5, 'top', 0.2, 0.3],
  [170, 'rocketeer', 3, 2, 'top', 0.2, 0.3],
  [176, 'splitter', 3, 1.5, 'top', 0.2, 0.3],
  [182, 'bulwark', 2, 3, 'top', 0.3, 0.4],
  [188, 'gnat', 3, 1.5, 'top', 0.2, 0.3],
  [194, 'carrier', 1, 0, 'top', 0.6],
  [200, 'scout', 5, 0.6, 'top', 0.1, 0.2],
  [206, 'spinner', 3, 2, 'top', 0.2, 0.3],
  [212, 'hornet', 5, 0.5, 'top', 0.1, 0.2],
  [218, 'lancer', 3, 1.2, 'top', 0.2, 0.3],
  [222, 'rocketeer', 2, 1.5, 'top', 0.3, 0.4],
  [226, 'bulwark', 1, 0, 'top', 0.5],
];

/**
 * The filler of each level (phase 6 review: the levels felt empty), in level order. 1-1 gets
 * only Hornets and Gnats, which do not shoot, so it stays easy; later levels fill up sooner and
 * tighter (D-051).
 */
export const WORLD_1_FILLERS: Readonly<Record<string, Filler>> = {
  '1-1': { kinds: ['hornet', 'hornet', 'gnat', 'hornet'], maxGap: [4.5, 3] },
  '1-2': { kinds: ['hornet', 'gnat', 'weaver', 'scout'], maxGap: [3.5, 2.4] },
  '1-3': { kinds: ['hornet', 'gnat', 'weaver', 'scout'], maxGap: [3.3, 2.2] },
  '1-4': { kinds: ['gnat', 'weaver', 'hornet', 'scout', 'splitter'], maxGap: [3.2, 2] },
  '1-5': { kinds: ['gnat', 'weaver', 'hornet', 'scout', 'splitter', 'spinner'], maxGap: [3, 1.6] },
};

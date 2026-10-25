import type { EnemySide } from '../../../core/entities/enemy';
import type { Filler } from '../world-1/waves';

/*
 * The wave scripts of World 2 (P08-R08, R09). Each level cycles through its own phrases: a beat
 * every `gap` seconds (from `gap[0]` at the start to `gap[1]` at the end, so the level fills up
 * as it goes), each beat the next phrase of the cycle, its groups growing by `growth` over the
 * level (so the second half carries more enemy HP). Beats are written in seconds, as World 1's,
 * and turned into distances at the level's ground speed; the World 1 filler (D-051) fills the
 * lulls. A phrase is `[kind, groups, seconds between groups, side, position (0..1), spread]`.
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

type Phrase = readonly [
  kind: Kind,
  count: number,
  interval: number,
  side: EnemySide,
  position: number,
  spread?: number,
];

/** A beat as World 1 writes them: `[seconds, ...phrase]`. */
export type Beat = readonly [seconds: number, ...phrase: Phrase];

/** How a level's beats are composed (see above). */
export interface WavePlan {
  readonly from: number;
  readonly to: number;
  readonly gap: readonly [start: number, end: number];
  readonly growth: number;
  readonly phrases: readonly Phrase[];
}

/** The beats of `plan`, deterministic. */
export function composeBeats(plan: WavePlan): Beat[] {
  const beats: Beat[] = [];
  const span = plan.to - plan.from;
  for (let t = plan.from, i = 0; t <= plan.to; i++) {
    const phrase = plan.phrases[i % plan.phrases.length];
    if (!phrase) break;
    const [kind, count, interval, side, position, spread] = phrase;
    const grown = Math.max(1, Math.round(count * (1 + (plan.growth * (t - plan.from)) / span)));
    const head = [Math.round(t * 10) / 10, kind, grown, interval, side, position] as const;
    beats.push(spread === undefined ? head : [...head, spread]);
    t += plan.gap[0] + ((plan.gap[1] - plan.gap[0]) * (t - plan.from)) / span;
  }
  return beats;
}

/** 2-1: Gnats, Hornets, Scouts, Strafers and Weavers low over the sea (P08-R08). */
export const PLAN_2_1: WavePlan = {
  from: 4,
  to: 292,
  gap: [6.5, 4.8],
  growth: 0.6,
  phrases: [
    ['scout', 3, 1.2, 'top', 0.25, 0.25],
    ['weaver', 3, 1.4, 'top', 0.3, 0.2],
    ['strafer', 2, 1.6, 'left', 0.8],
    ['hornet', 4, 0.8, 'top', 0.15, 0.23],
    ['gnat', 2, 2, 'top', 0.3, 0.4],
    ['scout', 4, 1, 'top', 0.2, 0.2],
    ['strafer', 2, 1.6, 'right', 0.78],
    ['weaver', 3, 1.2, 'top', 0.6, -0.2],
  ],
};

/** 2-2: the 2-1 kinds plus Splitters and Lancers, along the fjords. */
export const PLAN_2_2: WavePlan = {
  from: 4,
  to: 292,
  gap: [5.4, 3.9],
  growth: 0.6,
  phrases: [
    ['scout', 3, 1.2, 'top', 0.25, 0.25],
    ['splitter', 2, 2, 'top', 0.3, 0.4],
    ['weaver', 3, 1.2, 'top', 0.3, 0.2],
    ['lancer', 2, 2.5, 'top', 0.25, 0.5],
    ['strafer', 2, 1.5, 'left', 0.8],
    ['hornet', 4, 0.8, 'top', 0.15, 0.23],
    ['splitter', 2, 2, 'top', 0.7, -0.4],
    ['gnat', 2, 2, 'top', 0.3, 0.4],
    ['lancer', 2, 2, 'top', 0.3, 0.4],
    ['strafer', 2, 1.5, 'right', 0.78],
  ],
};

/** 2-3: every kind, with Carrier and Spinner groups over the tundra. */
export const PLAN_2_3: WavePlan = {
  from: 4,
  to: 292,
  gap: [6.6, 5],
  growth: 0.6,
  phrases: [
    ['spinner', 2, 2.5, 'top', 0.3, 0.4],
    ['scout', 4, 1, 'top', 0.15, 0.23],
    ['carrier', 1, 0, 'top', 0.5],
    ['weaver', 3, 1.2, 'top', 0.3, 0.2],
    ['spinner', 2, 2.5, 'top', 0.7, -0.4],
    ['splitter', 2, 2, 'top', 0.3, 0.4],
    ['lancer', 2, 2, 'top', 0.25, 0.5],
    ['spinner', 1, 0, 'top', 0.5],
    ['rocketeer', 1, 0, 'top', 0.5],
    ['strafer', 2, 1.5, 'left', 0.8],
    ['hornet', 4, 0.7, 'top', 0.1, 0.2],
    ['bulwark', 1, 0, 'top', 0.5],
    ['gnat', 2, 2, 'top', 0.3, 0.4],
  ],
};

/** 2-4: every kind, with Rocketeers and Bulwarks in the blizzard. */
export const PLAN_2_4: WavePlan = {
  from: 4,
  to: 292,
  gap: [4.8, 3.4],
  growth: 0.6,
  phrases: [
    ['rocketeer', 2, 2.5, 'top', 0.3, 0.4],
    ['scout', 4, 1, 'top', 0.15, 0.23],
    ['bulwark', 1, 0, 'top', 0.5],
    ['weaver', 3, 1.2, 'top', 0.3, 0.2],
    ['rocketeer', 2, 2, 'top', 0.7, -0.4],
    ['spinner', 2, 2.5, 'top', 0.3, 0.4],
    ['bulwark', 1, 0, 'top', 0.35],
    ['lancer', 2, 2, 'top', 0.25, 0.5],
    ['splitter', 2, 2, 'top', 0.3, 0.4],
    ['carrier', 1, 0, 'top', 0.5],
    ['strafer', 3, 1.5, 'right', 0.8],
    ['hornet', 5, 0.7, 'top', 0.1, 0.2],
    ['gnat', 2, 2, 'top', 0.3, 0.4],
  ],
};

/** 2-5: every kind, the heaviest mixes: Bulwarks and Carriers together. */
export const PLAN_2_5: WavePlan = {
  from: 4,
  to: 292,
  gap: [5, 3.6],
  growth: 0.6,
  phrases: [
    ['bulwark', 1, 0, 'top', 0.35],
    ['carrier', 1, 0, 'top', 0.65],
    ['scout', 4, 1, 'top', 0.15, 0.23],
    ['rocketeer', 2, 2, 'top', 0.3, 0.4],
    ['lancer', 3, 1.5, 'top', 0.2, 0.3],
    ['spinner', 2, 2.5, 'top', 0.7, -0.4],
    ['bulwark', 2, 3, 'top', 0.3, 0.4],
    ['weaver', 4, 1, 'top', 0.2, 0.2],
    ['splitter', 3, 1.5, 'top', 0.2, 0.3],
    ['carrier', 1, 0, 'top', 0.4],
    ['strafer', 3, 1.5, 'left', 0.8],
    ['hornet', 5, 0.6, 'top', 0.1, 0.2],
    ['gnat', 3, 1.5, 'top', 0.2, 0.3],
  ],
};

/** The filler of each level (D-051), from the kinds the level may use (P08-R08). */
export const WORLD_2_FILLERS: Readonly<Record<string, Filler>> = {
  '2-1': { kinds: ['hornet', 'scout', 'gnat', 'weaver'], maxGap: [3.4, 2.3] },
  '2-2': { kinds: ['hornet', 'gnat', 'weaver', 'scout', 'splitter'], maxGap: [3.2, 2.1] },
  '2-3': { kinds: ['gnat', 'weaver', 'hornet', 'scout', 'splitter', 'spinner'], maxGap: [3, 2] },
  '2-4': {
    kinds: ['gnat', 'weaver', 'hornet', 'scout', 'splitter', 'spinner'],
    maxGap: [2.9, 1.8],
  },
  '2-5': {
    kinds: ['gnat', 'weaver', 'hornet', 'scout', 'splitter', 'spinner'],
    maxGap: [2.8, 1.6],
  },
};

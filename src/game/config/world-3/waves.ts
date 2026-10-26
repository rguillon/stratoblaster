import type { Filler } from '../world-1/waves';
import type { WavePlan } from '../world-2/waves';

/*
 * The wave scripts of World 3 (P09-R07, R08), composed as World 2's (`composeBeats`, D-067): a
 * beat every `gap` seconds shrinking over the level, each the next phrase of the level's cycle,
 * its groups growing over the level; the World 1 filler (D-051) fills the lulls. A phrase is
 * `[kind, groups, seconds between groups, side, position (0..1), spread]`. A veteran kind comes in
 * at each level, from the Wasp in 3-1 to the Phantom in 3-5 (P05-R24, D-090).
 */

/** 3-1: Gnats, Hornets, Scouts, Strafers, Weavers and Splitters skimming the delta. */
export const PLAN_3_1: WavePlan = {
  from: 4,
  to: 292,
  gap: [4.9, 3.5],
  growth: 0.7,
  phrases: [
    ['scout', 4, 1, 'top', 0.2, 0.25],
    ['splitter', 2, 2, 'top', 0.3, 0.4],
    ['weaver', 4, 1.1, 'top', 0.3, 0.2],
    ['strafer', 3, 1.4, 'left', 0.8],
    ['hornet', 5, 0.7, 'top', 0.15, 0.23],
    ['gnat', 3, 1.6, 'top', 0.3, 0.4],
    ['splitter', 2, 2, 'top', 0.7, -0.4],
    ['scout', 4, 1, 'top', 0.6, -0.2],
    ['strafer', 3, 1.4, 'right', 0.78],
    ['weaver', 4, 1.1, 'top', 0.6, -0.2],
    // P05-R24: a new kind.
    ['wasp', 2, 1.6, 'top', 0.4, 0.3],
  ],
};

/** 3-2: every kind, Hornet swarms diving out of the canopy and Lancers along the river. */
export const PLAN_3_2: WavePlan = {
  from: 4,
  to: 292,
  gap: [5, 3.6],
  growth: 0.7,
  phrases: [
    ['hornet', 6, 0.6, 'top', 0.1, 0.25],
    ['lancer', 2, 2, 'top', 0.4, 0.2],
    ['scout', 4, 1, 'top', 0.15, 0.23],
    ['hornet', 6, 0.6, 'top', 0.9, -0.25],
    ['spinner', 2, 2.5, 'top', 0.3, 0.4],
    ['lancer', 3, 1.6, 'top', 0.5, -0.2],
    ['carrier', 1, 0, 'top', 0.5],
    ['weaver', 4, 1.1, 'top', 0.3, 0.2],
    ['rocketeer', 1, 0, 'top', 0.4],
    ['hornet', 6, 0.6, 'top', 0.2, 0.3],
    ['splitter', 2, 2, 'top', 0.7, -0.4],
    ['bulwark', 1, 0, 'top', 0.5],
    ['strafer', 3, 1.4, 'left', 0.8],
    ['gnat', 3, 1.6, 'top', 0.3, 0.4],
    // P05-R24: a new kind.
    ['wasp', 2, 1.6, 'top', 0.6, -0.3],
    ['mortar', 1, 0, 'top', 0.35],
  ],
};

/** 3-3: every kind, Spinner and Rocketeer groups around the temples. */
export const PLAN_3_3: WavePlan = {
  from: 4,
  to: 292,
  gap: [4.6, 3.1],
  growth: 0.6,
  phrases: [
    ['spinner', 3, 2, 'top', 0.25, 0.5],
    ['rocketeer', 2, 2.2, 'top', 0.3, 0.4],
    ['scout', 4, 1, 'top', 0.15, 0.23],
    ['spinner', 2, 2.2, 'top', 0.7, -0.4],
    ['lancer', 2, 2, 'top', 0.25, 0.5],
    ['rocketeer', 2, 2, 'top', 0.7, -0.4],
    ['weaver', 4, 1.1, 'top', 0.3, 0.2],
    ['bulwark', 1, 0, 'top', 0.4],
    ['splitter', 2, 2, 'top', 0.3, 0.4],
    ['carrier', 1, 0, 'top', 0.6],
    ['strafer', 3, 1.4, 'right', 0.8],
    ['hornet', 5, 0.6, 'top', 0.1, 0.2],
    ['gnat', 3, 1.6, 'top', 0.3, 0.4],
    // P05-R24: a new kind.
    ['wasp', 2, 1.6, 'top', 0.3, 0.3],
    ['mortar', 1, 0, 'top', 0.65],
    ['minelayer', 1, 0, 'right', 0.72],
  ],
};

/** 3-4: every kind, Carriers over the swamp. */
export const PLAN_3_4: WavePlan = {
  from: 4,
  to: 292,
  gap: [3.6, 2.6],
  growth: 0.6,
  phrases: [
    ['carrier', 1, 0, 'top', 0.35],
    ['scout', 4, 1, 'top', 0.15, 0.23],
    ['rocketeer', 2, 2, 'top', 0.3, 0.4],
    ['rocketeer', 2, 2, 'top', 0.65, -0.3],
    ['lancer', 3, 1.6, 'top', 0.2, 0.3],
    ['spinner', 2, 2.2, 'top', 0.7, -0.4],
    ['bulwark', 1, 0, 'top', 0.5],
    ['weaver', 4, 1, 'top', 0.2, 0.2],
    ['carrier', 1, 0, 'top', 0.5],
    ['splitter', 3, 1.5, 'top', 0.2, 0.3],
    ['strafer', 3, 1.4, 'left', 0.8],
    ['hornet', 6, 0.6, 'top', 0.1, 0.2],
    ['gnat', 3, 1.5, 'top', 0.2, 0.3],
    // P05-R24: a new kind.
    ['wasp', 2, 1.6, 'top', 0.7, -0.3],
    ['mortar', 1, 0, 'top', 0.4],
    ['minelayer', 1, 0, 'left', 0.74],
    ['mantis', 1, 0, 'top', 0.5],
  ],
};

/** 3-5: every kind, the heaviest mixes: Bulwarks escorting Carriers. */
export const PLAN_3_5: WavePlan = {
  from: 4,
  to: 292,
  gap: [3.6, 2.8],
  growth: 0.6,
  phrases: [
    ['bulwark', 1, 0, 'top', 0.3],
    ['carrier', 1, 0, 'top', 0.5],
    ['bulwark', 1, 0, 'top', 0.7],
    ['scout', 5, 0.9, 'top', 0.15, 0.23],
    ['rocketeer', 3, 1.8, 'top', 0.3, 0.4],
    ['lancer', 3, 1.5, 'top', 0.2, 0.3],
    ['spinner', 3, 2, 'top', 0.7, -0.4],
    ['bulwark', 2, 2.5, 'top', 0.3, 0.4],
    ['carrier', 1, 0, 'top', 0.4],
    ['weaver', 5, 0.9, 'top', 0.2, 0.2],
    ['splitter', 3, 1.4, 'top', 0.2, 0.3],
    ['strafer', 3, 1.4, 'right', 0.8],
    ['hornet', 6, 0.55, 'top', 0.1, 0.2],
    ['gnat', 3, 1.4, 'top', 0.2, 0.3],
    // P05-R24: a new kind.
    ['wasp', 2, 1.6, 'top', 0.3, 0.3],
    ['mortar', 1, 0, 'top', 0.6],
    ['minelayer', 1, 0, 'right', 0.74],
    ['mantis', 1, 0, 'top', 0.4],
    ['phantom', 1, 0, 'top', 0.6],
  ],
};

/** The filler of each level (D-051), from the kinds the level may use (P09-R07). */
export const WORLD_3_FILLERS: Readonly<Record<string, Filler>> = {
  '3-1': { kinds: ['hornet', 'scout', 'gnat', 'weaver', 'splitter'], maxGap: [3, 2] },
  '3-2': {
    kinds: ['hornet', 'gnat', 'weaver', 'hornet', 'scout', 'splitter', 'spinner'],
    maxGap: [2.9, 1.9],
  },
  '3-3': {
    kinds: ['gnat', 'weaver', 'hornet', 'scout', 'splitter', 'spinner'],
    maxGap: [2.8, 1.8],
  },
  '3-4': {
    kinds: ['gnat', 'weaver', 'hornet', 'scout', 'splitter', 'spinner'],
    maxGap: [2.7, 1.7],
  },
  '3-5': {
    kinds: ['gnat', 'weaver', 'hornet', 'scout', 'splitter', 'spinner'],
    maxGap: [2.6, 1.5],
  },
};

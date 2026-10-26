import type { Filler } from '../world-1/waves';
import type { WavePlan } from '../world-2/waves';

/*
 * The wave scripts of World 4 (P10-R09, R10), composed as Worlds 2 and 3's (`composeBeats`,
 * D-067): a beat every `gap` seconds shrinking over the level, each the next phrase of the
 * level's cycle, its groups growing over the level; the World 1 filler (D-051) fills the lulls.
 * A phrase is `[kind, groups, seconds between groups, side, position (0..1), spread]`. Every
 * level uses all eleven kinds.
 */

/** 4-1: every kind, Weavers and Strafers low over the steaming sea. */
export const PLAN_4_1: WavePlan = {
  from: 4,
  to: 292,
  gap: [3.8, 2.7],
  growth: 1.1,
  phrases: [
    ['weaver', 4, 1.1, 'top', 0.25, 0.2],
    ['strafer', 3, 1.4, 'left', 0.8],
    ['scout', 4, 1, 'top', 0.15, 0.23],
    ['weaver', 4, 1.1, 'top', 0.6, -0.2],
    ['lancer', 2, 2, 'top', 0.3, 0.4],
    ['strafer', 3, 1.4, 'right', 0.78],
    ['spinner', 2, 2.2, 'top', 0.7, -0.4],
    ['hornet', 5, 0.6, 'top', 0.1, 0.2],
    ['weaver', 5, 1, 'top', 0.2, 0.25],
    ['rocketeer', 2, 2, 'top', 0.4, 0.2],
    ['splitter', 2, 2, 'top', 0.3, 0.4],
    ['strafer', 3, 1.3, 'left', 0.75],
    ['bulwark', 1, 0, 'top', 0.5],
    ['carrier', 1, 0, 'top', 0.4],
    ['gnat', 3, 1.6, 'top', 0.3, 0.4],
  ],
};

/** 4-2: every kind, Splitters and Spinners over the ash plains. */
export const PLAN_4_2: WavePlan = {
  from: 4,
  to: 292,
  gap: [4, 2.8],
  growth: 1,
  phrases: [
    ['splitter', 3, 1.6, 'top', 0.2, 0.3],
    ['spinner', 3, 2, 'top', 0.25, 0.5],
    ['scout', 4, 1, 'top', 0.15, 0.23],
    ['splitter', 3, 1.6, 'top', 0.8, -0.3],
    ['lancer', 2, 2, 'top', 0.3, 0.4],
    ['spinner', 2, 2.2, 'top', 0.7, -0.4],
    ['weaver', 4, 1.1, 'top', 0.3, 0.2],
    ['rocketeer', 2, 2, 'top', 0.6, -0.3],
    ['splitter', 3, 1.5, 'top', 0.4, 0.2],
    ['bulwark', 1, 0, 'top', 0.4],
    ['strafer', 3, 1.4, 'right', 0.8],
    ['spinner', 3, 1.8, 'top', 0.4, 0.3],
    ['carrier', 1, 0, 'top', 0.6],
    ['hornet', 5, 0.6, 'top', 0.1, 0.2],
    ['gnat', 3, 1.5, 'top', 0.3, 0.4],
  ],
};

/** 4-3: every kind, Lancers and Rocketeers along the lava rivers. */
export const PLAN_4_3: WavePlan = {
  from: 4,
  to: 292,
  gap: [3.6, 2.5],
  growth: 1.1,
  phrases: [
    ['lancer', 3, 1.6, 'top', 0.25, 0.4],
    ['rocketeer', 2, 2, 'top', 0.3, 0.4],
    ['scout', 4, 1, 'top', 0.15, 0.23],
    ['lancer', 3, 1.6, 'top', 0.75, -0.4],
    ['rocketeer', 3, 1.8, 'top', 0.7, -0.4],
    ['spinner', 2, 2.2, 'top', 0.25, 0.5],
    ['weaver', 4, 1.1, 'top', 0.3, 0.2],
    ['bulwark', 1, 0, 'top', 0.4],
    ['lancer', 2, 2, 'top', 0.5, 0.2],
    ['splitter', 2, 2, 'top', 0.3, 0.4],
    ['carrier', 1, 0, 'top', 0.6],
    ['rocketeer', 2, 2, 'top', 0.2, 0.3],
    ['strafer', 3, 1.4, 'left', 0.8],
    ['hornet', 5, 0.6, 'top', 0.1, 0.2],
    ['gnat', 3, 1.5, 'top', 0.3, 0.4],
  ],
};

/** 4-4: every kind, Carriers and Bulwarks out of the foundries. */
export const PLAN_4_4: WavePlan = {
  from: 4,
  to: 292,
  gap: [4, 2.8],
  growth: 0.6,
  phrases: [
    ['carrier', 1, 0, 'top', 0.35],
    ['bulwark', 2, 2.5, 'top', 0.3, 0.4],
    ['scout', 5, 0.9, 'top', 0.15, 0.23],
    ['carrier', 1, 0, 'top', 0.65],
    ['lancer', 3, 1.5, 'top', 0.2, 0.3],
    ['bulwark', 1, 0, 'top', 0.5],
    ['rocketeer', 2, 2, 'top', 0.3, 0.4],
    ['spinner', 3, 2, 'top', 0.7, -0.4],
    ['weaver', 5, 0.9, 'top', 0.2, 0.2],
    ['splitter', 3, 1.4, 'top', 0.2, 0.3],
    ['bulwark', 1, 0, 'top', 0.7],
    ['strafer', 3, 1.4, 'right', 0.8],
    ['hornet', 6, 0.55, 'top', 0.1, 0.2],
    ['gnat', 3, 1.4, 'top', 0.2, 0.3],
  ],
};

/** 4-5: every kind, the heaviest mixes of the game so far. */
export const PLAN_4_5: WavePlan = {
  from: 4,
  to: 292,
  gap: [3.8, 2.7],
  growth: 1,
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
    ['strafer', 3, 1.3, 'left', 0.8],
    ['lancer', 3, 1.5, 'top', 0.7, -0.3],
    ['carrier', 1, 0, 'top', 0.6],
    ['hornet', 7, 0.45, 'top', 0.1, 0.2],
    ['gnat', 5, 1.1, 'top', 0.2, 0.3],
  ],
};

/** The filler of each level (D-051). */
export const WORLD_4_FILLERS: Readonly<Record<string, Filler>> = {
  '4-1': {
    kinds: ['weaver', 'gnat', 'hornet', 'scout', 'weaver', 'splitter', 'spinner'],
    maxGap: [2.7, 1.8],
  },
  '4-2': {
    kinds: ['splitter', 'gnat', 'weaver', 'hornet', 'scout', 'spinner'],
    maxGap: [2.6, 1.7],
  },
  '4-3': {
    kinds: ['gnat', 'weaver', 'hornet', 'scout', 'splitter', 'spinner'],
    maxGap: [2.5, 1.6],
  },
  '4-4': {
    kinds: ['gnat', 'weaver', 'hornet', 'scout', 'splitter', 'spinner'],
    maxGap: [2.4, 1.5],
  },
  '4-5': {
    kinds: ['gnat', 'weaver', 'hornet', 'scout', 'splitter', 'spinner'],
    maxGap: [2.3, 1.4],
  },
};

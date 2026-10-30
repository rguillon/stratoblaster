/** A level's mini and final boss kinds, and its runout (see {@link WORLD_1_BOSSES}). */
export interface LevelBosses {
  readonly mini: string;
  readonly final: string;
  readonly runout: number;
}

/**
 * The bosses of each World 1 level (GD-41, P07-R05, R06): a mini boss at the middle of the
 * level and a final boss at its end, by boss kind id. No new wave starts in the `quietSeconds`
 * before each of them (`quiet_before_boss`). `runout` is how many seconds of extra ground (at
 * the level's speed) are drawn past the level's end: the scenery gets ahead of the level during
 * the fights by about each fight's time × its ground speed factor, and the final fight keeps
 * scrolling (P07-R03).
 */
export const WORLD_1_BOSSES: Readonly<Record<string, LevelBosses>> = {
  '1-1': { mini: 'reef-warden', final: 'storm-petrel', runout: 150 },
  '1-2': { mini: 'breakwater', final: 'gull-mothership', runout: 80 },
  '1-3': { mini: 'dust-devil', final: 'mesa-fortress', runout: 30 },
  '1-4': { mini: 'scorpion', final: 'refinery-titan', runout: 70 },
  '1-5': { mini: 'sentinel', final: 'overlord', runout: 75 },
};

/** Where the mini boss comes, as a share of the level's length (`mini_boss_at`). */
export const MINI_BOSS_AT = 0.5;

/** Seconds before each boss without a new wave (`quiet_before_boss`). */
export const QUIET_BEFORE_BOSS = 10;

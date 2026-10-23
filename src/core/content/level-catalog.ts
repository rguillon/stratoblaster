/** One level as shown on the level select screen (data only). */
export interface LevelEntry {
  /** Stable identifier, e.g. `1-1`. */
  readonly id: string;
  /** Text shown on the level select screen. */
  readonly label: string;
  /** 1-based world number. */
  readonly world: number;
  /** 1-based level number inside its world. */
  readonly level: number;
  /** Locked levels are shown but cannot be started. */
  readonly unlocked: boolean;
}

/** The levels of a game, laid out as one row per world. */
export interface LevelCatalog {
  /** Levels per world, i.e. entries per row of the level select grid. */
  readonly columns: number;
  /** World 1 level 1 first, row by row. */
  readonly levels: readonly LevelEntry[];
}

/** Builds a catalog of `worlds × levelsPerWorld` levels labelled `world-level`. */
export function buildLevelGrid(
  worlds: number,
  levelsPerWorld: number,
  unlockedIds: readonly string[],
): LevelCatalog {
  if (!Number.isInteger(worlds) || !Number.isInteger(levelsPerWorld)) {
    throw new RangeError('worlds and levelsPerWorld must be integers');
  }
  if (worlds < 1 || levelsPerWorld < 1) throw new RangeError('A level grid needs one level');
  const levels: LevelEntry[] = [];
  for (let world = 1; world <= worlds; world++) {
    for (let level = 1; level <= levelsPerWorld; level++) {
      const id = `${String(world)}-${String(level)}`;
      levels.push({ id, label: id, world, level, unlocked: unlockedIds.includes(id) });
    }
  }
  return { columns: levelsPerWorld, levels };
}

/** Index of the first unlocked level, or 0 when every level is locked. */
export function firstUnlockedLevel(catalog: LevelCatalog): number {
  return Math.max(
    0,
    catalog.levels.findIndex((l) => l.unlocked),
  );
}

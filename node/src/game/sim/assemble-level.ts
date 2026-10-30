import type { GameLevel } from '../../core/content/game-level';
import { levelLength, type SceneryLevel } from '../../core/scenery/scenery-level';
import type { LevelBoss } from '../../core/systems/boss-fights';
import type { EnemyDifficulty } from '../../core/systems/enemy-world';
import { MINI_BOSS_AT, QUIET_BEFORE_BOSS, type LevelBosses } from '../config/world-1/bosses';
import { fill, quietBefore, waveScript, type Filler } from '../config/world-1/waves';

/** What a world gives each of its levels, by level id. */
export interface WorldTables {
  readonly difficulty: Readonly<Record<string, EnemyDifficulty>>;
  readonly fillers: Readonly<Record<string, Filler>>;
  readonly bosses: Readonly<Record<string, LevelBosses>>;
}

/**
 * A playable level (P06, P07, P08): its scenery, its written beats with light groups filling
 * their lulls (phase 6 review) and nothing new in the stretch before each boss (P07-R06), its
 * difficulty, and its mini boss at the middle and final boss at the end.
 */
export function assembleLevel(
  id: string,
  scenery: SceneryLevel,
  beats: Parameters<typeof waveScript>[1],
  tables: WorldTables,
): GameLevel {
  const difficulty = tables.difficulty[id];
  const filler = tables.fillers[id];
  const bosses = tables.bosses[id];
  if (!difficulty || !filler || !bosses)
    throw new Error(`No difficulty, filler or boss for "${id}"`);
  const length = levelLength(scenery);
  const fights: LevelBoss[] = [
    { kind: bosses.mini, rank: 'mini', at: length * MINI_BOSS_AT },
    { kind: bosses.final, rank: 'final', at: length },
  ];
  const script = waveScript(scenery.scrollSpeed, fill(beats, filler));
  const quiet = QUIET_BEFORE_BOSS * scenery.scrollSpeed;
  const waves = quietBefore(
    script,
    fights.map((f) => f.at),
    quiet,
  );
  return { id, scenery, waves, difficulty, bosses: fights, runout: bosses.runout };
}

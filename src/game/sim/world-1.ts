import type { GameLevel } from '../../core/content/game-level';
import { levelLength, type SceneryLevel } from '../../core/scenery/scenery-level';
import type { LevelBoss } from '../../core/systems/boss-fights';
import { MINI_BOSS_AT, QUIET_BEFORE_BOSS, WORLD_1_BOSSES } from '../config/world-1/bosses';
import { WORLD_1_DIFFICULTY } from '../config/world-1/difficulty';
import { LEVEL_1_1, LEVEL_1_2 } from '../config/world-1/scenery-coast';
import { LEVEL_1_3, LEVEL_1_4, LEVEL_1_5 } from '../config/world-1/scenery-desert';
import {
  WAVES_1_1,
  WAVES_1_2,
  WAVES_1_3,
  WAVES_1_4,
  WAVES_1_5,
  WORLD_1_FILLERS,
  fill,
  quietBefore,
  waveScript,
} from '../config/world-1/waves';

function level(
  id: string,
  scenery: SceneryLevel,
  beats: Parameters<typeof waveScript>[1],
): GameLevel {
  const difficulty = WORLD_1_DIFFICULTY[id];
  const filler = WORLD_1_FILLERS[id];
  const bosses = WORLD_1_BOSSES[id];
  if (!difficulty || !filler || !bosses)
    throw new Error(`No difficulty, filler or boss for "${id}"`);
  const length = levelLength(scenery);
  // P07-R06: the mini boss at the middle, the final boss at the end.
  const fights: LevelBoss[] = [
    { kind: bosses.mini, rank: 'mini', at: length * MINI_BOSS_AT },
    { kind: bosses.final, rank: 'final', at: length },
  ];
  // The written beats, with light groups filling their lulls (phase 6 review), and nothing
  // new in the stretch before each boss (P07-R06).
  const script = waveScript(scenery.scrollSpeed, fill(beats, filler));
  const quiet = QUIET_BEFORE_BOSS * scenery.scrollSpeed;
  const waves = quietBefore(
    script,
    fights.map((f) => f.at),
    quiet,
  );
  return { id, scenery, waves, difficulty, bosses: fights, runout: bosses.runout };
}

/**
 * World 1 (P06): five levels of about 4 minutes, from the open sea to a desert city, each with
 * a mini boss and a final boss (P07).
 */
export const WORLD_1: readonly GameLevel[] = [
  level('1-1', LEVEL_1_1, WAVES_1_1),
  level('1-2', LEVEL_1_2, WAVES_1_2),
  level('1-3', LEVEL_1_3, WAVES_1_3),
  level('1-4', LEVEL_1_4, WAVES_1_4),
  level('1-5', LEVEL_1_5, WAVES_1_5),
];

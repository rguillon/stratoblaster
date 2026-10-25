import type { GameLevel } from '../../core/content/game-level';
import type { SceneryLevel } from '../../core/scenery/scenery-level';
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
  waveScript,
} from '../config/world-1/waves';

function level(
  id: string,
  scenery: SceneryLevel,
  beats: Parameters<typeof waveScript>[1],
): GameLevel {
  const difficulty = WORLD_1_DIFFICULTY[id];
  const filler = WORLD_1_FILLERS[id];
  if (!difficulty || !filler) throw new Error(`No difficulty or filler for level "${id}"`);
  // The written beats, with light groups filling their lulls (phase 6 review).
  return { id, scenery, waves: waveScript(scenery.scrollSpeed, fill(beats, filler)), difficulty };
}

/** World 1 (P06): five levels of about 4 minutes, from the open sea to a desert city. */
export const WORLD_1: readonly GameLevel[] = [
  level('1-1', LEVEL_1_1, WAVES_1_1),
  level('1-2', LEVEL_1_2, WAVES_1_2),
  level('1-3', LEVEL_1_3, WAVES_1_3),
  level('1-4', LEVEL_1_4, WAVES_1_4),
  level('1-5', LEVEL_1_5, WAVES_1_5),
];

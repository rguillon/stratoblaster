import type { GameLevel } from '../../core/content/game-level';
import type { SceneryLevel } from '../../core/scenery/scenery-level';
import { WORLD_1_BOSSES } from '../config/world-1/bosses';
import { WORLD_1_DIFFICULTY } from '../config/world-1/difficulty';
import { LEVEL_1_1, LEVEL_1_2 } from '../config/world-1/scenery-coast';
import { LEVEL_1_3 } from '../config/world-1/scenery-country';
import { LEVEL_1_4, LEVEL_1_5 } from '../config/world-1/scenery-desert';
import {
  WAVES_1_1,
  WAVES_1_2,
  WAVES_1_3,
  WAVES_1_4,
  WAVES_1_5,
  WORLD_1_FILLERS,
} from '../config/world-1/waves';
import { assembleLevel } from './assemble-level';

const TABLES = {
  difficulty: WORLD_1_DIFFICULTY,
  fillers: WORLD_1_FILLERS,
  bosses: WORLD_1_BOSSES,
};

const level = (id: string, scenery: SceneryLevel, beats: Parameters<typeof assembleLevel>[2]) =>
  assembleLevel(id, scenery, beats, TABLES);

/**
 * World 1 (P06): five levels of about 4 minutes, from the open sea over green grassland to a desert city, each with
 * a mini boss and a final boss (P07).
 */
export const WORLD_1: readonly GameLevel[] = [
  level('1-1', LEVEL_1_1, WAVES_1_1),
  level('1-2', LEVEL_1_2, WAVES_1_2),
  level('1-3', LEVEL_1_3, WAVES_1_3),
  level('1-4', LEVEL_1_4, WAVES_1_4),
  level('1-5', LEVEL_1_5, WAVES_1_5),
];

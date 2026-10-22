import type { GameDefinition } from '../core/content/game-definition';
import { GAME_CONFIG } from './config/game';

/** The single entry point of this game's content (ENG-144). */
export const GAME: GameDefinition = {
  id: GAME_CONFIG.id,
  title: GAME_CONFIG.title,
};

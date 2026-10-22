import type { GameDefinition } from '../core/content/game-definition';
import type { GameView } from '../render/game-view';
import { GAME_CONFIG } from './config/game';
import { PLAYER_SHIPS } from './config/player-ships';
import { PLAYER_SHIP_MODELS } from './view/player-ship-models';

/** The single entry point of this game's content (ENG-144). */
export const GAME: GameDefinition<GameView> = {
  id: GAME_CONFIG.id,
  title: GAME_CONFIG.title,
  playerShips: PLAYER_SHIPS,
  view: { playerShipModels: PLAYER_SHIP_MODELS },
};

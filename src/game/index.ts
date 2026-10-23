import type { GameDefinition } from '../core/content/game-definition';
import type { GameView } from '../render/game-view';
import { GAME_CONFIG } from './config/game';
import { MENU_TEXTS } from './config/menu-texts';
import { PLAYER_SHIPS } from './config/player-ships';
import { PLAYER_WEAPONS } from './config/player-weapons';
import { PLAYER_SHIP_SCALE } from './config/ship-look';
import { LEVELS } from './sim/levels';
import { SCENERY_LEVELS } from './sim/scenery-levels';
import { PLAYER_SHIP_MODELS } from './view/player-ship-models';
import { PLAYER_SHOT_RENDERERS } from './view/shots/player-shot-renderers';
import { SCENERY_BINDINGS } from './view/scenery-bindings';
import { buildTitleBackdrop } from './view/title-backdrop';

/** The single entry point of this game's content (ENG-144). */
export const GAME: GameDefinition<GameView> = {
  id: GAME_CONFIG.id,
  title: GAME_CONFIG.title,
  screen: GAME_CONFIG.screen,
  playerShips: PLAYER_SHIPS,
  playerWeapons: PLAYER_WEAPONS,
  levels: LEVELS,
  sceneryLevels: SCENERY_LEVELS,
  texts: MENU_TEXTS,
  view: {
    playerShipModels: PLAYER_SHIP_MODELS,
    playerShipScale: PLAYER_SHIP_SCALE,
    playerShotRenderers: PLAYER_SHOT_RENDERERS,
    menuBackdrop: buildTitleBackdrop,
    scenery: SCENERY_BINDINGS,
  },
};

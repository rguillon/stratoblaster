import type { GameDefinition } from '../core/content/game-definition';
import type { GameView } from '../render/game-view';
import { BOMB_RULES } from './config/bombs';
import { BONUS_RULES } from './config/bonuses';
import { BOSS_FIGHT_RULES } from './config/boss-fights';
import { GAME_CONFIG } from './config/game';
import { HULL_RULES } from './config/hull';
import { MENU_TEXTS } from './config/menu-texts';
import { PLAYER_SHIPS } from './config/player-ships';
import { PLAYER_WEAPONS } from './config/player-weapons';
import { PLAYER_SHIP_SCALE } from './config/ship-look';
import { BOSS_KINDS } from './sim/boss-kinds';
import { ENEMY_KINDS } from './sim/enemy-kinds';
import { GAME_LEVELS, LEVELS } from './sim/levels';
import { GAME_AUDIO } from './view/audio/game-audio';
import { createBombRenderer } from './view/bombs/bomb-renderer';
import { createBonusRenderer } from './view/bonuses/bonus-renderer';
import { ENEMY_BINDINGS } from './view/enemies/enemy-bindings';
import { PLAYER_SHIP_MODELS } from './view/player-ship-models';
import { PLAYER_SHOT_RENDERERS } from './view/shots/player-shot-renderers';
import { SCENERY_BINDINGS } from './view/scenery-bindings';
import { buildTitleBackdrop } from './view/title-backdrop';
import { READABILITY } from './config/readability';
import { buildHitboxMarker, outlinedShips, tonedShots } from './view/readability-view';

/** The single entry point of this game's content (ENG-144). */
export const GAME: GameDefinition<GameView> = {
  id: GAME_CONFIG.id,
  title: GAME_CONFIG.title,
  screen: GAME_CONFIG.screen,
  playerShips: PLAYER_SHIPS,
  playerWeapons: PLAYER_WEAPONS,
  levels: LEVELS,
  gameLevels: GAME_LEVELS,
  enemyKinds: ENEMY_KINDS,
  bossKinds: BOSS_KINDS,
  bossFights: BOSS_FIGHT_RULES,
  bonuses: BONUS_RULES,
  bombs: BOMB_RULES,
  hull: HULL_RULES,
  texts: MENU_TEXTS,
  view: {
    // Phase 14: the ships with a rim glow (P14-R03), the shots toned down (P14-R06).
    playerShipModels: outlinedShips(PLAYER_SHIP_MODELS),
    playerShipScale: PLAYER_SHIP_SCALE,
    playerShotRenderers: tonedShots(PLAYER_SHOT_RENDERERS),
    menuBackdrop: buildTitleBackdrop,
    scenery: SCENERY_BINDINGS,
    enemies: ENEMY_BINDINGS,
    bonuses: createBonusRenderer,
    bombs: createBombRenderer,
    audio: GAME_AUDIO,
    outline: READABILITY.outline,
    hitboxMarker: buildHitboxMarker,
  },
};

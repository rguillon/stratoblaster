/** Pages the app can start on. */
export type AppRoute =
  | 'game'
  | 'player-ship-viewer'
  | 'player-shots-viewer'
  | 'scenery-viewer'
  | 'enemy-viewer'
  | 'boss-viewer';

const PLAYER_SHIP_VIEWER = /\/player_ship(\/(index\.html)?)?$/;
const PLAYER_SHOTS_VIEWER = /\/player_shots(\/(index\.html)?)?$/;
const SCENERY_VIEWER = /\/level_zero(\/(index\.html)?)?$/;
const ENEMY_VIEWER = /\/enemies(\/(index\.html)?)?$/;
const BOSS_VIEWER = /\/bosses(\/(index\.html)?)?$/;

/** Picks the page to start from the URL path (works under any deployment sub-path). */
export function resolveRoute(pathname: string): AppRoute {
  if (PLAYER_SHIP_VIEWER.test(pathname)) return 'player-ship-viewer';
  if (PLAYER_SHOTS_VIEWER.test(pathname)) return 'player-shots-viewer';
  if (SCENERY_VIEWER.test(pathname)) return 'scenery-viewer';
  if (ENEMY_VIEWER.test(pathname)) return 'enemy-viewer';
  if (BOSS_VIEWER.test(pathname)) return 'boss-viewer';
  return 'game';
}

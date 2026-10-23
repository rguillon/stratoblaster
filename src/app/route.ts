/** Pages the app can start on. */
export type AppRoute = 'game' | 'player-ship-viewer' | 'player-shots-viewer';

const PLAYER_SHIP_VIEWER = /\/player_ship(\/(index\.html)?)?$/;
const PLAYER_SHOTS_VIEWER = /\/player_shots(\/(index\.html)?)?$/;

/** Picks the page to start from the URL path (works under any deployment sub-path). */
export function resolveRoute(pathname: string): AppRoute {
  if (PLAYER_SHIP_VIEWER.test(pathname)) return 'player-ship-viewer';
  if (PLAYER_SHOTS_VIEWER.test(pathname)) return 'player-shots-viewer';
  return 'game';
}

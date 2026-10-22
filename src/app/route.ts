/** Pages the app can start on. */
export type AppRoute = 'game' | 'player-ship-viewer';

const PLAYER_SHIP_VIEWER = /\/player_ship(\/(index\.html)?)?$/;

/** Picks the page to start from the URL path (works under any deployment sub-path). */
export function resolveRoute(pathname: string): AppRoute {
  return PLAYER_SHIP_VIEWER.test(pathname) ? 'player-ship-viewer' : 'game';
}

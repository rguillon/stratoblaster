/** Pages the app can start on. */
export type AppRoute =
  | 'game'
  | 'player-ship-viewer'
  | 'player-shots-viewer'
  | 'enemy-viewer'
  | 'boss-viewer'
  | 'prop-viewer';

const PLAYER_SHIP_VIEWER = /\/player_ship(\/(index\.html)?)?$/;
const PLAYER_SHOTS_VIEWER = /\/player_shots(\/(index\.html)?)?$/;
const ENEMY_VIEWER = /\/enemies(\/(index\.html)?)?$/;
/** `bosses/`, or `boss/` (phase 7 review). */
const BOSS_VIEWER = /\/boss(es)?(\/(index\.html)?)?$/;
/** `props/` (reviewer, 2026-10-28). */
const PROP_VIEWER = /\/props(\/(index\.html)?)?$/;

/** Picks the page to start from the URL path (works under any deployment sub-path). */
export function resolveRoute(pathname: string): AppRoute {
  if (PLAYER_SHIP_VIEWER.test(pathname)) return 'player-ship-viewer';
  if (PLAYER_SHOTS_VIEWER.test(pathname)) return 'player-shots-viewer';
  if (ENEMY_VIEWER.test(pathname)) return 'enemy-viewer';
  if (BOSS_VIEWER.test(pathname)) return 'boss-viewer';
  if (PROP_VIEWER.test(pathname)) return 'prop-viewer';
  return 'game';
}

/**
 * Where to send the browser instead of `pathname`, if anywhere: a viewer's path without its
 * trailing slash (`/props`) gets the game's page from the dev server, so it goes to `/props/`.
 */
export function redirectOf(pathname: string): string | undefined {
  if (resolveRoute(pathname) === 'game' || /(\/|\.html)$/.test(pathname)) return undefined;
  return `${pathname}/`;
}

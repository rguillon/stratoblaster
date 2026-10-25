import type { GameDebugOptions } from './game-session';

/**
 * Reads the debug options of the game screen from a URL query (P06-R09):
 * `?level=1-3&t=120&ship=heavy` starts level 1-3 at 2:00 with the heavy ship. `level` turns
 * debug on; `t` (seconds, default 0) and `ship` (default: the first ship) are optional.
 * Without `level`, or with a value that does not parse, there are no debug options.
 */
export function parseDebugOptions(search: string): GameDebugOptions | undefined {
  const query = new URLSearchParams(search);
  const levelId = query.get('level');
  if (!levelId) return undefined;
  const time = Number(query.get('t') ?? '0');
  return {
    levelId,
    time: Number.isFinite(time) && time > 0 ? time : 0,
    shipId: query.get('ship'),
  };
}

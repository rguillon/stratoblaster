import { describe, expect, it } from 'vitest';
import { resolveRoute } from '../../../src/app/route';

describe('resolveRoute', () => {
  it.each([
    ['/', 'game'],
    ['/pewet/', 'game'],
    ['/pewet/index.html', 'game'],
    ['/player_ship/', 'player-ship-viewer'],
    ['/player_ship', 'player-ship-viewer'],
    ['/pewet/player_ship/', 'player-ship-viewer'],
    ['/pewet/player_ship/index.html', 'player-ship-viewer'],
    ['/player_ship/other', 'game'],
    ['/player_shots/', 'player-shots-viewer'],
    ['/player_shots', 'player-shots-viewer'],
    ['/pewet/player_shots/index.html', 'player-shots-viewer'],
    ['/player_shots/other', 'game'],
  ] as const)('maps %s to %s', (pathname, route) => {
    expect(resolveRoute(pathname)).toBe(route);
  });
});

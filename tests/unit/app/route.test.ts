import { describe, expect, it } from 'vitest';
import { resolveRoute } from '../../../src/app/route';

describe('resolveRoute', () => {
  it.each([
    ['/', 'game'],
    ['/stratoblaster/', 'game'],
    ['/stratoblaster/index.html', 'game'],
    ['/player_ship/', 'player-ship-viewer'],
    ['/player_ship', 'player-ship-viewer'],
    ['/stratoblaster/player_ship/', 'player-ship-viewer'],
    ['/stratoblaster/player_ship/index.html', 'player-ship-viewer'],
    ['/player_ship/other', 'game'],
    ['/player_shots/', 'player-shots-viewer'],
    ['/player_shots', 'player-shots-viewer'],
    ['/stratoblaster/player_shots/index.html', 'player-shots-viewer'],
    ['/player_shots/other', 'game'],
    ['/level_zero/', 'scenery-viewer'],
    ['/level_zero', 'scenery-viewer'],
    ['/stratoblaster/level_zero/index.html', 'scenery-viewer'],
    ['/level_zero/other', 'game'],
  ] as const)('maps %s to %s', (pathname, route) => {
    expect(resolveRoute(pathname)).toBe(route);
  });
});

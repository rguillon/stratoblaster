import { describe, expect, it } from 'vitest';
import { redirectOf, resolveRoute } from '../../../src/app/route';

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
    ['/level_zero/other', 'game'],
    ['/enemies/', 'enemy-viewer'],
    ['/enemies', 'enemy-viewer'],
    ['/stratoblaster/enemies/index.html', 'enemy-viewer'],
    ['/enemies/other', 'game'],
    ['/bosses/', 'boss-viewer'],
    ['/bosses', 'boss-viewer'],
    ['/stratoblaster/bosses/index.html', 'boss-viewer'],
    ['/bosses/other', 'game'],
    ['/props/', 'prop-viewer'],
    ['/props', 'prop-viewer'],
    ['/stratoblaster/props/index.html', 'prop-viewer'],
    ['/props/other', 'game'],
    ['/boss/', 'boss-viewer'],
    ['/boss', 'boss-viewer'],
    ['/stratoblaster/boss/index.html', 'boss-viewer'],
    ['/bossy/', 'game'],
  ] as const)('maps %s to %s', (pathname, route) => {
    expect(resolveRoute(pathname)).toBe(route);
  });
});

describe('redirectOf', () => {
  it.each([
    ['/props', '/props/'],
    ['/stratoblaster/enemies', '/stratoblaster/enemies/'],
    ['/props/', undefined],
    ['/props/index.html', undefined],
    ['/', undefined],
    ['/stratoblaster', undefined],
  ])('%s → %s', (path, to) => {
    expect(redirectOf(path)).toBe(to);
  });
});

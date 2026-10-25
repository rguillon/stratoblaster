import type { Page } from '@playwright/test';
import { expect } from './fixtures';

/** What `window.__GAME_TEST__.getState()` returns (src/debug/test-api.ts). */
export interface TestState {
  screen: string;
  selection: number;
  selectedId: string | null;
  highlightedShipId: string;
  chosenShipId: string | null;
  chosenLevelId: string | null;
  transitioning: boolean;
  levelResult: { levelId: string; destroyed: number; spawned: number } | null;
  loadingProgress: number[];
  /** The level being played (src/debug/test-api.ts, `GameTestLevelState`). */
  game: {
    levelId: string;
    phase: string;
    time: number;
    duration: number;
    timeScale: number;
    enemies: number;
    destroyed: number;
    spawned: number;
    wavesTriggered: number;
    player: { x: number; y: number };
    firing: boolean;
    shots: number;
    /** The boss being fought (P07). */
    boss: { name: string; rank: string; state: string; stage: number; partsLeft: number } | null;
    bossesDefeated: number;
    groundSpeed: number;
  } | null;
}

interface TestWindow {
  __GAME_TEST__?: { getState(): TestState; sendAction(action: string): void };
}

/** Loading (with shader compilation under SwiftShader) can take a while on CI. */
export const LOAD_TIMEOUT = 60_000;

export function gameState(page: Page): Promise<TestState> {
  return page.evaluate(() => {
    const api = (window as TestWindow).__GAME_TEST__;
    if (!api) throw new Error('__GAME_TEST__ is missing');
    return api.getState();
  });
}

/** Waits until no screen transition is running (input is ignored during one, P01-R15). */
export async function waitIdle(page: Page): Promise<void> {
  await page.waitForFunction(() => {
    const api = (window as TestWindow).__GAME_TEST__;
    return api !== undefined && !api.getState().transitioning;
  });
}

/**
 * Waits for `count` rendered frames, so the game has polled its input in between. Frames
 * can be slow under software WebGL, so tests wait for frames rather than fixed delays.
 */
export async function waitFrames(page: Page, count = 3): Promise<void> {
  await page.evaluate(async (n) => {
    for (let i = 0; i < n; i++) {
      await new Promise((resolve) => requestAnimationFrame(resolve));
    }
  }, count);
}

/** Opens the game and waits for the title screen. */
export async function openGame(page: Page): Promise<void> {
  await page.goto('./');
  await page.waitForFunction(
    () => (window as TestWindow).__GAME_TEST__?.getState().screen === 'title',
    undefined,
    { timeout: LOAD_TIMEOUT },
  );
  await waitIdle(page);
}

/** Sends a menu action through the test API, once the screen accepts input. */
export async function sendAction(page: Page, action: string): Promise<void> {
  await waitIdle(page);
  await page.evaluate((a) => {
    (window as TestWindow).__GAME_TEST__?.sendAction(a);
  }, action);
}

/** Expects the state to reach `expected` (screen, selection...), then waits for input. */
export async function expectState(page: Page, expected: Partial<TestState>): Promise<void> {
  await expect.poll(() => gameState(page)).toMatchObject(expected);
  await waitIdle(page);
}

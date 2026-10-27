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
  /** Phase 13 (P13-R01): long frames, longest frame and level loading times, in ms. */
  perf: {
    longFrames: number;
    longestFrame: number;
    frames: number;
    lastLoad: number | null;
    longestLoadStep: number | null;
  };
  /** Phase 12 (P12-R12): pause, volumes, music and sounds. */
  paused: boolean;
  leaving: boolean;
  /** The choice selected on a panel: Continue / level select, or No / Yes before leaving. */
  choice: number;
  volumes: { music: number; sfx: number };
  music: string | null;
  sounds: string[];
  audio: string;
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
    /** Points scored in this attempt (P11-R01). */
    score: number;
    /** The boss being fought (P07). */
    boss: {
      name: string;
      rank: string;
      state: string;
      stage: number;
      partsLeft: number;
      parts: number;
    } | null;
    bossesDefeated: number;
    groundSpeed: number;
    sky?: {
      weatherParticles: number;
      aurora: number;
      groundLights: number;
      sunIntensity: number;
      fogEnd: number;
      /** Phase 10 (P10-R05, R07). */
      lava: boolean;
      liquidDepth: number;
      shotStyle: string;
    };
  } | null;
}

interface TestWindow {
  __GAME_TEST__?: {
    getState(): TestState;
    sendAction(action: string): void;
    step(frames: number, render?: boolean): void;
    advance(seconds: number): void;
  };
}

/**
 * Loading the menus (and a level's scenery, with debug options) is real work, not game time:
 * under software WebGL on CI it can take a while.
 */
export const LOAD_TIMEOUT = 60_000;

/** Frames stepped between two checks of {@link stepUntil}. */
const POLL_FRAMES = 10;

export function gameState(page: Page): Promise<TestState> {
  return page.evaluate(() => {
    const api = (window as TestWindow).__GAME_TEST__;
    if (!api) throw new Error('__GAME_TEST__ is missing');
    return api.getState();
  });
}

/**
 * Runs the app by `frames` frames of 1/60 s, then renders once (ENG-52). e2e builds have no
 * render loop: the game only moves when a test steps it, so no test waits on real time.
 */
export async function step(page: Page, frames = 1): Promise<void> {
  await page.evaluate((n) => {
    (window as TestWindow).__GAME_TEST__?.step(n);
  }, frames);
}

/** Runs the app by `seconds` of game time (whole frames), then renders once. */
export async function advance(page: Page, seconds: number): Promise<void> {
  await page.evaluate((s) => {
    (window as TestWindow).__GAME_TEST__?.advance(s);
  }, seconds);
}

/**
 * Steps the app {@link POLL_FRAMES} frames at a time until `read` returns what the chained
 * matcher expects: `await stepUntil(page, () => level(page).then((g) => g.shots)).toBe(3)`.
 * Fails after `timeout` ms of real time (each step renders a frame).
 */
export function stepUntil<T>(
  page: Page,
  read: () => Promise<T>,
  { frames = POLL_FRAMES, timeout = LOAD_TIMEOUT }: { frames?: number; timeout?: number } = {},
) {
  return expect.poll(
    async () => {
      await step(page, frames);
      return read();
    },
    { timeout, intervals: [0] },
  );
}

/**
 * Steps the app until no screen transition runs (input is ignored during one, P01-R15), then
 * renders the frame it stopped at.
 */
export async function waitIdle(page: Page): Promise<void> {
  await page.evaluate(() => {
    const api = (window as TestWindow).__GAME_TEST__;
    if (!api) throw new Error('__GAME_TEST__ is missing');
    // At least one frame, so input sent before is read. A fade lasts 15 frames; the result
    // overlay ignores input for a second (P06-R03).
    api.step(1, false);
    for (let i = 0; i < 600 && api.getState().transitioning; i++) api.step(1, false);
    api.step(0);
  });
}

/** Opens the game and waits for the title screen, faded in. */
export async function openGame(page: Page): Promise<void> {
  await page.goto('./');
  await page.waitForFunction(
    () => (window as TestWindow).__GAME_TEST__?.getState().screen === 'title',
    undefined,
    { timeout: LOAD_TIMEOUT },
  );
  await waitIdle(page);
}

/** Opens the game with debug options (P06-R09) and waits for their level to be playing. */
export async function openDebug(page: Page, query: string): Promise<void> {
  await page.goto(`./${query}`);
  await page.waitForFunction(
    () => (window as TestWindow).__GAME_TEST__?.getState().screen === 'game',
    undefined,
    { timeout: LOAD_TIMEOUT },
  );
  await waitForLoad(page);
  await step(page);
}

/** Sends a menu action through the test API, once the screen accepts input. */
export async function sendAction(page: Page, action: string): Promise<void> {
  await page.evaluate((a) => {
    const api = (window as TestWindow).__GAME_TEST__;
    if (!api) throw new Error('__GAME_TEST__ is missing');
    // Through any transition first, without drawing: the next check renders.
    for (let i = 0; i < 600 && api.getState().transitioning; i++) api.step(1, false);
    api.sendAction(a);
  }, action);
}

/**
 * Leaves the level being played through the pause menu (P12-R02): pause, Main menu, Yes. The
 * title screen shows.
 */
export async function leaveLevel(page: Page): Promise<void> {
  await sendAction(page, 'pause');
  await expectState(page, { screen: 'pause', paused: true });
  for (const action of ['down', 'down', 'confirm', 'right', 'confirm']) {
    await sendAction(page, action);
  }
  await expectState(page, { screen: 'title', paused: false });
}

/**
 * Steps the app a frame at a time, without rendering, until the state matches `expected`
 * (screen, selection...), then until it takes input again. Entering a level generates its
 * scenery in the frame that starts it.
 */
export async function expectState(page: Page, expected: Partial<TestState>): Promise<void> {
  await expect
    .poll(
      () =>
        page.evaluate(() => {
          const api = (window as TestWindow).__GAME_TEST__;
          if (!api) throw new Error('__GAME_TEST__ is missing');
          api.step(1, false);
          return api.getState();
        }),
      { timeout: LOAD_TIMEOUT, intervals: [0] },
    )
    .toMatchObject(expected);
  await waitIdle(page);
}

/** The level being played; fails the test when there is none. */
/**
 * Steps through the loading of the level chosen, if one is loading (P13-R03: a level loads in
 * steps, one per frame, behind its loading screen).
 */
export async function waitForLoad(page: Page): Promise<void> {
  await page.evaluate(() => {
    const api = (window as TestWindow).__GAME_TEST__;
    if (!api) throw new Error('__GAME_TEST__ is missing');
    const loading = () => {
      const state = api.getState();
      return state.screen === 'game' && state.game === null && state.levelResult === null;
    };
    for (let i = 0; i < 600 && loading(); i++) api.step(1);
  });
}

export async function level(page: Page): Promise<NonNullable<TestState['game']>> {
  await waitForLoad(page);
  const { game } = await gameState(page);
  if (!game) throw new Error('No level is being played');
  return game;
}

/** Runs the level being played on to `seconds` of level time. */
export async function waitForLevelTime(page: Page, seconds: number): Promise<void> {
  const now = (await level(page)).time;
  if (now <= seconds) await advance(page, seconds - now + 0.05);
  expect((await level(page)).time).toBeGreaterThan(seconds);
}

/**
 * Destroys the parts left then the core of the boss `name` with K (P07-R09), one at a time (the
 * stage goes up), and steps on to the "Level complete" overlay.
 */
export async function destroyBoss(page: Page, name: string): Promise<void> {
  await stepUntil(page, async () => (await gameState(page)).game?.boss?.name ?? null).toBe(name);
  const { parts = 0, stage: done = 0 } = (await level(page)).boss ?? {};
  for (let stage = done + 1; stage <= parts; stage++) {
    await page.keyboard.press('KeyK');
    await stepUntil(page, async () => (await gameState(page)).game?.boss?.stage ?? -1).toBe(stage);
  }
  await page.keyboard.press('KeyK');
  await stepUntil(page, async () => (await gameState(page)).levelResult !== null, {
    frames: 30,
  }).toBe(true);
  await step(page);
  await expect(page.locator('.level-complete')).toBeVisible();
}

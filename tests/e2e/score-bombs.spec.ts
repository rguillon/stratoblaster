import type { Locator, Page } from '@playwright/test';
import { test, expect } from './fixtures';
import { expectState, gameState, openGame, sendAction, LOAD_TIMEOUT } from './menu-helpers';

/** A level's scene is generated when it starts; under software WebGL that takes a while. */
const LEVEL_TIMEOUT = 60_000;

/** What P11 adds to the test API's state (src/debug/test-api.ts). */
interface ScoreState {
  highScore: number;
  levelResult: {
    outcome: string;
    score: number;
    newHighScore?: boolean;
    checkpoint?: { score: number };
  } | null;
  game: {
    score: number;
    bombs: number;
    enemyShots: number;
    bonusKinds: string[];
    bossesDefeated: number;
    boss: { name: string; stage: number; health: number } | null;
  } | null;
}

interface ScoreWindow {
  __GAME_TEST__?: {
    getState(): ScoreState;
    sendAction(action: string): void;
    advance(seconds: number): void;
  };
}

function scoreState(page: Page): Promise<ScoreState> {
  return page.evaluate(() => {
    const api = (window as ScoreWindow).__GAME_TEST__;
    if (!api) throw new Error('__GAME_TEST__ is missing');
    return api.getState();
  });
}

/** Runs the level on by `seconds` of level time through the test API. */
async function advance(page: Page, seconds: number): Promise<void> {
  await page.evaluate((s) => {
    (window as ScoreWindow).__GAME_TEST__?.advance(s);
  }, seconds);
}

/** Opens the game with debug options (P06-R09) and waits for the level to run. */
async function openDebug(page: Page, query: string): Promise<void> {
  await page.goto(`./${query}`);
  await expect
    .poll(async () => (await gameState(page)).game?.levelId ?? null, { timeout: LOAD_TIMEOUT })
    .not.toBeNull();
}

/** Waits for the boss `name` to be fought. */
async function waitForBoss(page: Page, name: string): Promise<void> {
  await expect
    .poll(async () => (await scoreState(page)).game?.boss?.name ?? null, {
      timeout: LEVEL_TIMEOUT,
    })
    .toBe(name);
}

/** Whether two elements' boxes overlap. */
async function overlap(a: Locator, b: Locator): Promise<boolean> {
  const [x, y] = await Promise.all([a.boundingBox(), b.boundingBox()]);
  if (!x || !y) return false;
  return x.x < y.x + y.width && y.x < x.x + x.width && x.y < y.y + y.height && y.y < x.y + x.height;
}

test.describe('P11: score, lives and bombs', () => {
  // Each test software-renders a generated level: one at a time, so they do not starve each other.
  test.describe.configure({ mode: 'default' });
  test.setTimeout(180_000);

  test('P11-R01, P11-R02, P11-R03, P11-R08: boss parts score; a new high score is saved and shown after a reload', async ({
    page,
  }) => {
    await openDebug(page, '?level=1-1&boss=final&ship=light');
    await waitForBoss(page, 'Storm Petrel');
    await expect(page.locator('.hud-score-value')).toHaveText('0000000');
    await expect(page.locator('.hud-high-score')).toHaveText('HI 0000000');
    expect((await scoreState(page)).highScore).toBe(0);
    // K destroys its four parts (800 points each, 10 % of its 8 000), then its core.
    for (let stage = 1; stage <= 4; stage++) {
      await page.keyboard.press('KeyK');
      await expect
        .poll(async () => (await scoreState(page)).game?.boss?.stage ?? -1, {
          timeout: LEVEL_TIMEOUT,
        })
        .toBe(stage);
    }
    await expect
      .poll(async () => (await scoreState(page)).game?.score ?? 0)
      .toBeGreaterThanOrEqual(3200);
    await expect(page.locator('.hud-score-value')).toHaveText(/^00\d{5}$/);
    await page.keyboard.press('KeyK');
    await expect(page.locator('.level-complete')).toBeVisible({ timeout: LEVEL_TIMEOUT });
    const { levelResult, highScore } = await scoreState(page);
    const score = levelResult?.score ?? 0;
    expect(score).toBeGreaterThanOrEqual(3200 + 8000);
    expect(levelResult?.newHighScore).toBe(true);
    expect(highScore).toBe(score);
    await expect(page.locator('.level-complete-score')).toHaveText(`Score: ${String(score)}`);
    await expect(page.locator('.level-complete-high-score')).toHaveText('New high score!');
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'level-select' });
    await sendAction(page, 'back');
    await sendAction(page, 'back');
    await expectState(page, { screen: 'title' });
    await expect(page.locator('.title-high-score')).toHaveText(String(score));
    await page.reload();
    await openGame(page);
    await expect(page.locator('.title-high-score')).toHaveText(String(score));
  });

  test('P11-R03: leaving a level with Esc saves its score as the high score', async ({ page }) => {
    await openDebug(page, '?level=1-1&boss=final');
    await waitForBoss(page, 'Storm Petrel');
    await page.keyboard.press('KeyK');
    await expect
      .poll(async () => (await scoreState(page)).game?.score ?? 0, { timeout: LEVEL_TIMEOUT })
      .toBe(800);
    await sendAction(page, 'back');
    await expectState(page, { screen: 'title' });
    await expect(page.locator('.title-high-score')).toHaveText('800');
    await page.reload();
    await openGame(page);
    await expect(page.locator('.title-high-score')).toHaveText('800');
  });

  test('P11-R05, P11-R06, P11-R08: R sets a bomb off: the enemy shots go, the boss is hurt; then `bomb` from the test API', async ({
    page,
  }) => {
    await openDebug(page, '?level=1-2&boss=mini');
    await expect
      .poll(async () => (await scoreState(page)).game?.boss?.name ?? null, {
        timeout: LEVEL_TIMEOUT,
      })
      .not.toBeNull();
    await expect(page.locator('.hud-bombs')).toHaveText('●●●');
    // Let the mini boss come in and fire.
    await expect
      .poll(
        async () => {
          await advance(page, 0.5);
          return (await scoreState(page)).game?.enemyShots ?? 0;
        },
        { timeout: LEVEL_TIMEOUT },
      )
      .toBeGreaterThan(0);
    const before = (await scoreState(page)).game?.boss?.health ?? 0;
    await page.keyboard.press('KeyR');
    await expect
      .poll(async () => (await scoreState(page)).game?.bombs ?? -1, { timeout: LEVEL_TIMEOUT })
      .toBe(2);
    expect((await scoreState(page)).game?.enemyShots).toBe(0);
    expect((await scoreState(page)).game?.boss?.health ?? before).toBeLessThan(before);
    await expect(page.locator('.hud-bombs')).toHaveText('●●');
    // E switches the weapon and sets no bomb off.
    await advance(page, 1.1);
    await page.keyboard.press('KeyE');
    await expect(page.locator('.hud-weapon')).toHaveText('Laser · Lv 1/5');
    expect((await scoreState(page)).game?.bombs).toBe(2);
    await sendAction(page, 'bomb');
    await expect
      .poll(async () => (await scoreState(page)).game?.bombs ?? -1, { timeout: LEVEL_TIMEOUT })
      .toBe(1);
  });

  test('P11-R04: a Continue after the mini boss keeps the score earned up to the checkpoint', async ({
    page,
  }) => {
    await openDebug(page, '?level=1-1&boss=mini&ship=light');
    await waitForBoss(page, 'Reef Warden');
    await expect
      .poll(
        async () => {
          await page.keyboard.press('KeyK');
          return (await scoreState(page)).game?.bossesDefeated ?? 0;
        },
        { timeout: LEVEL_TIMEOUT },
      )
      .toBe(1);
    // The ship sits still until the enemies have taken all its lives.
    await expect
      .poll(
        async () => {
          await advance(page, 20);
          return (await scoreState(page)).levelResult?.outcome ?? null;
        },
        { timeout: 150_000, intervals: [100] },
      )
      .toBe('over');
    const { levelResult } = await scoreState(page);
    const saved = levelResult?.checkpoint?.score ?? -1;
    expect(saved).toBeGreaterThanOrEqual(3000);
    await expect(page.locator('.level-complete-choice').first()).toHaveText('Continue');
    await sendAction(page, 'confirm');
    await expect
      .poll(async () => (await scoreState(page)).levelResult, { timeout: LEVEL_TIMEOUT })
      .toBeNull();
    await expect
      .poll(async () => (await scoreState(page)).game?.score ?? -1, { timeout: LEVEL_TIMEOUT })
      .toBe(saved);
    expect((await scoreState(page)).game?.bombs).toBe(3);
  });

  for (const viewport of [
    { width: 800, height: 600 },
    { width: 390, height: 844 },
  ]) {
    test(`P11-R02: at ${String(viewport.width)}×${String(viewport.height)} the score lines show and cover no other HUD part`, async ({
      page,
    }) => {
      await page.setViewportSize(viewport);
      await openDebug(page, '?level=1-1&boss=final');
      await waitForBoss(page, 'Storm Petrel');
      const score = page.locator('.hud-score');
      await expect(score).toBeVisible();
      await expect(page.locator('.boss-bar')).toBeVisible({ timeout: LEVEL_TIMEOUT });
      for (const other of ['.hud-health', '.hud-weapon', '.hud-progress', '.boss-bar']) {
        expect(await overlap(score, page.locator(other)), other).toBe(false);
      }
      const box = await score.boundingBox();
      expect(box?.y ?? -1).toBeGreaterThanOrEqual(0);
      expect((box?.x ?? -1) + (box?.width ?? 0)).toBeLessThanOrEqual(viewport.width);
    });
  }
});

test.describe('P11: touch bomb button', () => {
  test.use({ hasTouch: true, viewport: { width: 390, height: 844 } });
  test.setTimeout(120_000);

  test('P11-R06: the BOMB button sets a bomb off; the fire button still shows', async ({
    page,
  }) => {
    await openDebug(page, '?level=1-1&t=10');
    const button = page.locator('.hud-bomb-button');
    await expect(button).toBeVisible({ timeout: LEVEL_TIMEOUT });
    await expect(button).toHaveText('Bomb 3');
    await button.tap();
    await expect
      .poll(async () => (await scoreState(page)).game?.bombs ?? -1, { timeout: LEVEL_TIMEOUT })
      .toBe(2);
    await expect(button).toHaveText('Bomb 2');
    await expect(page.locator('.game-fire')).toBeVisible();
  });
});

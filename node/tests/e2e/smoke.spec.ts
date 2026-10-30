import { readFileSync } from 'node:fs';
import { test, expect } from './fixtures';
import {
  advance,
  expectState,
  gameState,
  leaveLevel,
  openGame,
  sendAction,
  LOAD_TIMEOUT,
  waitForLoad,
} from './menu-helpers';

const PACKAGE_VERSION = (
  JSON.parse(readFileSync(new URL('../../package.json', import.meta.url), 'utf8')) as {
    version: string;
  }
).version;

test('ENG-54, P12-R12: loading → title → ship select → level select → game → pause / resume → back to title', async ({
  page,
}) => {
  await page.goto('./');
  await expect(page).toHaveTitle('Stratoblaster');
  await expect(page.locator('#game-canvas')).toBeVisible();
  await expect(page.locator('#fatal')).toBeHidden();
  await expect(page.locator('.title-screen')).toBeVisible({ timeout: LOAD_TIMEOUT });
  await expectState(page, { screen: 'title', selectedId: 'start' });
  await sendAction(page, 'confirm');
  await expectState(page, { screen: 'ship-select', selectedId: 'balanced' });
  await sendAction(page, 'confirm');
  await expectState(page, { screen: 'level-select', selectedId: '1-1', chosenShipId: 'balanced' });
  await sendAction(page, 'confirm');
  await expectState(page, { screen: 'game', chosenLevelId: '1-1' });
  await expect(page.locator('.game-level')).toHaveText('Level 1-1');
  // P13-R03: the level loads in steps (its ground from a worker) before it plays.
  await waitForLoad(page);
  await expect.poll(async () => (await gameState(page)).game?.levelId).toBe('1-1');
  await advance(page, 1);
  // P12-R12: `pause` pauses the level; nothing moves until `resume`.
  await sendAction(page, 'pause');
  await expectState(page, { screen: 'pause', paused: true });
  const paused = (await gameState(page)).game?.time ?? -1;
  await advance(page, 2);
  expect((await gameState(page)).game?.time).toBe(paused);
  await sendAction(page, 'resume');
  await expectState(page, { screen: 'game', paused: false });
  await advance(page, 1);
  expect((await gameState(page)).game?.time).toBeGreaterThan(paused);
  // P12-R03: a hidden page pauses the level by itself.
  await page.evaluate(() => {
    Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => 'hidden' });
    document.dispatchEvent(new Event('visibilitychange'));
  });
  await expectState(page, { screen: 'pause', paused: true });
  await sendAction(page, 'resume');
  await expectState(page, { screen: 'game', paused: false });
  await leaveLevel(page);
  expect((await gameState(page)).game).toBeNull();
});

test('P01-R02: a progress bar goes from 0 % to 100 %, then the title appears by itself', async ({
  page,
}) => {
  await page.goto('./');
  await expect(page.locator('.loading-bar')).toBeVisible();
  await expect(page.locator('.title-screen')).toBeVisible({ timeout: LOAD_TIMEOUT });
  const { loadingProgress } = await gameState(page);
  expect(loadingProgress[0]).toBe(0);
  expect(loadingProgress.at(-1)).toBe(1);
  expect(loadingProgress.length).toBeGreaterThan(2);
  expect([...loadingProgress].sort((a, b) => a - b)).toEqual(loadingProgress);
});

test('P01-R03: without WebGL2, a friendly message replaces the menu, without errors', async ({
  page,
}) => {
  await page.addInitScript(() => {
    type GetContext = (this: HTMLCanvasElement, id: string, ...rest: unknown[]) => unknown;
    const proto = HTMLCanvasElement.prototype as unknown as { getContext: GetContext };
    const original = proto.getContext;
    proto.getContext = function (id, ...rest) {
      return id === 'webgl2' ? null : original.call(this, id, ...rest);
    };
  });
  await page.goto('./');
  await expect(page.locator('#fatal')).toBeVisible();
  await expect(page.locator('#fatal')).toContainText(
    'cannot run in this browser or on this device',
  );
  await expect(page.locator('.menu-screen')).toHaveCount(0);
});

test.describe('P01-R04: title screen', () => {
  test('shows the title, Start (selected), a high score of 0, the hint and the version', async ({
    page,
  }) => {
    await openGame(page);
    await expect(page.locator('.title-name')).toHaveText('Stratoblaster');
    // The title logo fits the screen width (no clipped letters).
    const { logo, screen } = await page.locator('.title-name').evaluate((el) => ({
      logo: el.scrollWidth,
      screen: el.parentElement?.clientWidth ?? 0,
    }));
    expect(logo).toBeLessThanOrEqual(screen);
    await expect(page.locator('.title-start.selected')).toHaveText('Start');
    await expect(page.locator('.title-high-score')).toHaveText('0');
    await expect(page.locator('.title-hint')).toContainText('Space / Enter');
    await expect(page.locator('.version-number')).toHaveText(`v${PACKAGE_VERSION}`);
    await expect(page.locator('.version-commit')).toHaveText(/^([0-9a-f]{7,}|unknown)$/);
  });

  for (const [value, shown] of [
    ['12345', '12345'],
    ['not-a-score', '0'],
  ] as const) {
    test(`a high-score cookie of "${value}" shows ${shown}`, async ({ page, context, baseURL }) => {
      await context.addCookies([{ name: 'stratoblaster_high_score', value, url: baseURL ?? '' }]);
      await openGame(page);
      await expect(page.locator('.title-high-score')).toHaveText(shown);
    });
  }
});

test('P01-R05, P01-R13: everything comes from the same origin (no downloaded fonts)', async ({
  page,
  baseURL,
}) => {
  const foreign: string[] = [];
  page.on('request', (request) => {
    if (!request.url().startsWith(baseURL ?? '')) foreign.push(request.url());
  });
  await openGame(page);
  expect(foreign).toEqual([]);
});

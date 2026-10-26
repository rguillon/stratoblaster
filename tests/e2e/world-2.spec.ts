import type { Page } from '@playwright/test';
import { test, expect } from './fixtures';
import {
  expectState,
  gameState,
  openGame,
  sendAction,
  waitForLevelTime,
  LOAD_TIMEOUT,
} from './menu-helpers';

const WORLD_2 = ['2-1', '2-2', '2-3', '2-4', '2-5'];

/** A level's scene is generated when it starts; under software WebGL that takes a while. */
const LEVEL_TIMEOUT = 60_000;

/** Opens the game with debug options (P06-R09, P08-R12) and waits for the level to run. */
async function openDebug(page: Page, query: string): Promise<void> {
  await page.goto(`./${query}`);
  await expect
    .poll(async () => (await gameState(page)).game?.levelId ?? null, { timeout: LOAD_TIMEOUT })
    .not.toBeNull();
}

test.describe('P08: World 2', () => {
  // Each test software-renders a generated level: one at a time.
  test.describe.configure({ mode: 'default' });
  test.setTimeout(150_000);

  test('P08-R01: the World 2 row shows 2-1 to 2-5, all unlocked', async ({ page }) => {
    await openGame(page);
    await sendAction(page, 'confirm');
    await sendAction(page, 'confirm');
    const cells = page.locator('.level-cell');
    for (const [i, id] of WORLD_2.entries()) {
      await expect(cells.nth(5 + i)).toHaveText(id);
      await expect(cells.nth(5 + i)).not.toHaveClass(/locked/);
    }
  });

  for (const [index, id] of WORLD_2.entries()) {
    test(`P08-R01: ${id} can be confirmed from a fresh start and plays without errors`, async ({
      page,
    }) => {
      await openGame(page);
      await sendAction(page, 'confirm');
      await sendAction(page, 'confirm');
      await expectState(page, { screen: 'level-select', selectedId: '1-1' });
      // Down a row to World 2, then along it.
      await sendAction(page, 'down');
      for (let i = 0; i < index; i++) await sendAction(page, 'right');
      await expectState(page, { selectedId: id });
      await sendAction(page, 'confirm');
      await expectState(page, { screen: 'game', chosenLevelId: id });
      await waitForLevelTime(page, 0.2);
      const { game } = await gameState(page);
      expect(game).toMatchObject({ levelId: id, phase: 'playing', timeScale: 1 });
      expect(game?.duration).toBeGreaterThanOrEqual(290);
      expect(game?.duration).toBeLessThanOrEqual(310);
      await expect(page.locator('.game-level')).toHaveText(`Level ${id}`);
    });
  }

  test('P08-R12: ?level=2-4&t=150 starts 2-4 at 2:30 in its blizzard', async ({ page }) => {
    await openDebug(page, '?level=2-4&t=150');
    // At 2:30, the middle of the level, its mini boss comes (and holds the level's progress).
    await expect
      .poll(async () => (await gameState(page)).game?.sky?.weatherParticles ?? -1, {
        timeout: LEVEL_TIMEOUT,
      })
      .toBe(1500);
    const { game } = await gameState(page);
    expect(game?.levelId).toBe('2-4');
    expect(game?.time).toBeGreaterThanOrEqual(150);
    expect(game?.time).toBeLessThan(156);
  });

  test('P08-R12: ?level=2-3&weather=0 shows no snow; without it, 2-3 snows', async ({ page }) => {
    await openDebug(page, '?level=2-3&weather=0');
    await waitForLevelTime(page, 0.2);
    expect((await gameState(page)).game?.sky?.weatherParticles).toBe(0);
    await openDebug(page, '?level=2-3');
    await waitForLevelTime(page, 0.2);
    expect((await gameState(page)).game?.sky?.weatherParticles).toBe(600);
  });

  test('P08-R04, P08-R12: 2-5 turns to night, its aurora on; look= forces a time of day', async ({
    page,
  }) => {
    await openDebug(page, '?level=2-5&t=120');
    await waitForLevelTime(page, 120.1);
    const night = (await gameState(page)).game?.sky;
    expect(night?.aurora).toBe(1);
    expect(night?.groundLights).toBeGreaterThan(1);
    await openDebug(page, '?level=2-5&t=120&look=midday');
    await waitForLevelTime(page, 120.1);
    const midday = (await gameState(page)).game?.sky;
    expect(midday?.groundLights).toBeLessThan(0.5);
    expect(midday?.sunIntensity).toBeGreaterThan(night?.sunIntensity ?? Infinity);
  });

  test('P08-R10: ?level=2-1&boss=final: K destroys the Narwhal and the level is complete', async ({
    page,
  }) => {
    await openDebug(page, '?level=2-1&boss=final');
    await expect
      .poll(async () => (await gameState(page)).game?.boss?.name ?? null, {
        timeout: LEVEL_TIMEOUT,
      })
      .toBe('Narwhal');
    const parts = (await gameState(page)).game?.boss?.parts ?? 0;
    expect(parts).toBeGreaterThanOrEqual(4);
    for (let stage = 1; stage <= parts; stage++) {
      await page.keyboard.press('KeyK');
      await expect
        .poll(async () => (await gameState(page)).game?.boss?.stage ?? -1, {
          timeout: LEVEL_TIMEOUT,
        })
        .toBe(stage);
    }
    await page.keyboard.press('KeyK');
    await expect(page.locator('.level-complete')).toBeVisible({ timeout: LEVEL_TIMEOUT });
    await expect(page.locator('.level-complete-level')).toHaveText('2-1');
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'level-select', selectedId: '2-2', game: null });
  });

  test('P08-R01: after 1-5, the level select highlights 2-1', async ({ page }) => {
    await openDebug(page, '?level=1-5&boss=final');
    await expect
      .poll(async () => (await gameState(page)).game?.boss?.name ?? null, {
        timeout: LEVEL_TIMEOUT,
      })
      .toBe('Overlord');
    const parts = (await gameState(page)).game?.boss?.parts ?? 0;
    for (let stage = 1; stage <= parts; stage++) {
      await page.keyboard.press('KeyK');
      await expect
        .poll(async () => (await gameState(page)).game?.boss?.stage ?? -1, {
          timeout: LEVEL_TIMEOUT,
        })
        .toBe(stage);
    }
    await page.keyboard.press('KeyK');
    await expect(page.locator('.level-complete')).toBeVisible({ timeout: LEVEL_TIMEOUT });
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'level-select', selectedId: '2-1', game: null });
  });
});

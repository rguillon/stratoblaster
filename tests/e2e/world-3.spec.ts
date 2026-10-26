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

const WORLD_3 = ['3-1', '3-2', '3-3', '3-4', '3-5'];

/** A level's scene is generated when it starts; under software WebGL that takes a while. */
const LEVEL_TIMEOUT = 60_000;

/** Opens the game with debug options (P06-R09, P09-R11) and waits for the level to run. */
async function openDebug(page: Page, query: string): Promise<void> {
  await page.goto(`./${query}`);
  await expect
    .poll(async () => (await gameState(page)).game?.levelId ?? null, { timeout: LOAD_TIMEOUT })
    .not.toBeNull();
}

/** Destroys every part then the core of the boss being fought, with K (P07-R09). */
async function destroyBoss(page: Page, name: string): Promise<void> {
  await expect
    .poll(async () => (await gameState(page)).game?.boss?.name ?? null, {
      timeout: LEVEL_TIMEOUT,
    })
    .toBe(name);
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
}

test.describe('P09: World 3', () => {
  // Each test software-renders a generated level: one at a time.
  test.describe.configure({ mode: 'default' });
  test.setTimeout(150_000);

  test('P09-R01: the World 3 row shows 3-1 to 3-5, all unlocked; World 5 stays locked (P10-R01)', async ({
    page,
  }) => {
    await openGame(page);
    await sendAction(page, 'confirm');
    await sendAction(page, 'confirm');
    const cells = page.locator('.level-cell');
    for (const [i, id] of WORLD_3.entries()) {
      await expect(cells.nth(10 + i)).toHaveText(id);
      await expect(cells.nth(10 + i)).not.toHaveClass(/locked/);
    }
    for (let i = 20; i < 25; i++) await expect(cells.nth(i)).toHaveClass(/locked/);
  });

  for (const [index, id] of WORLD_3.entries()) {
    test(`P09-R01: ${id} can be confirmed from the menu and plays without errors`, async ({
      page,
    }) => {
      await openGame(page);
      await sendAction(page, 'confirm');
      await sendAction(page, 'confirm');
      await expectState(page, { screen: 'level-select', selectedId: '1-1' });
      // Down two rows to World 3, then along it.
      await sendAction(page, 'down');
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

  test('P09-R11: ?level=3-3&t=120 starts 3-3 at 2:00 in its thunderstorm', async ({ page }) => {
    await openDebug(page, '?level=3-3&t=120');
    await waitForLevelTime(page, 120.1);
    const { game } = await gameState(page);
    expect(game?.levelId).toBe('3-3');
    expect(game?.time).toBeGreaterThanOrEqual(120);
    expect(game?.time).toBeLessThan(126);
    // P09-R04: rain 0.8 (1 600 of the 2 000 streaks) with lightning.
    expect(game?.sky).toMatchObject({ weather: 'rain', weatherParticles: 1600, lightning: 1 });
  });

  test('P09-R11: ?level=3-3&weather=0 shows no rain and no lightning', async ({ page }) => {
    await openDebug(page, '?level=3-3&t=120&weather=0');
    await waitForLevelTime(page, 120.1);
    expect((await gameState(page)).game?.sky).toMatchObject({
      weather: 'none',
      weatherParticles: 0,
      rainRings: 0,
      lightning: 0,
      flash: 0,
    });
  });

  test('P09-R04: 3-5 rains at night over the lit city', async ({ page }) => {
    await openDebug(page, '?level=3-5&t=60');
    await waitForLevelTime(page, 60.1);
    const sky = (await gameState(page)).game?.sky;
    expect(sky).toMatchObject({ weather: 'rain', weatherParticles: 1000 });
    expect(sky?.groundLights).toBeGreaterThan(1);
  });

  test('P09-R09: ?level=3-1&boss=final: K destroys the River Leviathan and the level is complete', async ({
    page,
  }) => {
    await openDebug(page, '?level=3-1&boss=final');
    await destroyBoss(page, 'River Leviathan');
    await expect(page.locator('.level-complete-level')).toHaveText('3-1');
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'level-select', selectedId: '3-2', game: null });
  });

  test('P09-R01: after 2-5, the level select highlights 3-1', async ({ page }) => {
    await openDebug(page, '?level=2-5&boss=final');
    await destroyBoss(page, 'Boreal Citadel');
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'level-select', selectedId: '3-1', game: null });
  });

  test('P10-R01: after 3-5, the level select highlights 4-1', async ({ page }) => {
    await openDebug(page, '?level=3-5&boss=final');
    await destroyBoss(page, 'Verdant Crown');
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'level-select', selectedId: '4-1', game: null });
  });
});

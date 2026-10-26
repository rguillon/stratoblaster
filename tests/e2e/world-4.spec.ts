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

const WORLD_4 = ['4-1', '4-2', '4-3', '4-4', '4-5'];

/** A level's scene is generated when it starts; under software WebGL that takes a while. */
const LEVEL_TIMEOUT = 60_000;

/** Opens the game with debug options (P06-R09, P10-R13) and waits for the level to run. */
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

test.describe('P10: World 4', () => {
  // Each test software-renders a generated level: one at a time.
  test.describe.configure({ mode: 'default' });
  test.setTimeout(150_000);

  test('P10-R01: the World 4 row shows 4-1 to 4-5, all unlocked, the last row of the grid', async ({
    page,
  }) => {
    await openGame(page);
    await sendAction(page, 'confirm');
    await sendAction(page, 'confirm');
    const cells = page.locator('.level-cell');
    for (const [i, id] of WORLD_4.entries()) {
      await expect(cells.nth(15 + i)).toHaveText(id);
      await expect(cells.nth(15 + i)).not.toHaveClass(/locked/);
    }
    await expect(cells).toHaveCount(20);
    await expect(page.locator('.level-cell.locked')).toHaveCount(0);
  });

  for (const [index, id] of WORLD_4.entries()) {
    test(`P10-R01: ${id} can be confirmed from the menu and plays without errors`, async ({
      page,
    }) => {
      await openGame(page);
      await sendAction(page, 'confirm');
      await sendAction(page, 'confirm');
      await expectState(page, { screen: 'level-select', selectedId: '1-1' });
      // Down three rows to World 4, then along it.
      for (let i = 0; i < 3; i++) await sendAction(page, 'down');
      for (let i = 0; i < index; i++) await sendAction(page, 'right');
      await expectState(page, { selectedId: id });
      await sendAction(page, 'confirm');
      await expectState(page, { screen: 'game', chosenLevelId: id });
      await waitForLevelTime(page, 0.2);
      const { game } = await gameState(page);
      expect(game).toMatchObject({ levelId: id, phase: 'playing', timeScale: 1 });
      expect(game?.duration).toBeGreaterThanOrEqual(290);
      expect(game?.duration).toBeLessThanOrEqual(310);
      // P10-R07: the shots are drawn in the contrast style in every World 4 level.
      expect(game?.sky?.shotStyle).toBe('contrast');
      await expect(page.locator('.game-level')).toHaveText(`Level ${id}`);
    });
  }

  test('P10-R04: 4-2 falls ash at midday; ?level=4-2&weather=0 shows none', async ({ page }) => {
    await openDebug(page, '?level=4-2&t=60');
    await waitForLevelTime(page, 60.1);
    // Falling ash 0.5: 750 of the 1 500 flakes.
    expect((await gameState(page)).game?.sky).toMatchObject({
      weather: 'ash',
      weatherParticles: 750,
      lava: false,
    });
    await openDebug(page, '?level=4-2&t=60&weather=0');
    await waitForLevelTime(page, 60.1);
    expect((await gameState(page)).game?.sky).toMatchObject({
      weather: 'none',
      secondWeather: 'none',
      weatherParticles: 0,
    });
  });

  test('P10-R04: 4-4 a furnace-lit night with ash and embers together', async ({ page }) => {
    await openDebug(page, '?level=4-4&t=60');
    await waitForLevelTime(page, 60.1);
    const sky = (await gameState(page)).game?.sky;
    // Ash 0.3 (450) and embers 0.3 (240).
    expect(sky).toMatchObject({
      weather: 'ash',
      secondWeather: 'embers',
      weatherParticles: 690,
      lava: true,
    });
    expect(sky?.groundLights).toBeGreaterThan(1);
  });

  test('P10-R13: ?level=4-5&boss=final starts at the Caldera Throne, over the magma lake, in the eruption', async ({
    page,
  }) => {
    await openDebug(page, '?level=4-5&boss=final');
    await expect
      .poll(async () => (await gameState(page)).game?.boss?.name ?? null, {
        timeout: LEVEL_TIMEOUT,
      })
      .toBe('Caldera Throne');
    const sky = (await gameState(page)).game?.sky;
    // Over the lake: lava under the middle of the playfield; the embers at their strongest.
    expect(sky).toMatchObject({ lava: true, weather: 'embers', weatherParticles: 800 });
    expect(sky?.liquidDepth).toBeGreaterThan(0);
  });

  test('P10-R11: ?level=4-1&boss=final: K destroys the Steam Dreadnought and the level is complete', async ({
    page,
  }) => {
    await openDebug(page, '?level=4-1&boss=final');
    await destroyBoss(page, 'Steam Dreadnought');
    await expect(page.locator('.level-complete-level')).toHaveText('4-1');
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'level-select', selectedId: '4-2', game: null });
  });

  test('P10-R01: after 4-5, the level select highlights 4-5', async ({ page }) => {
    await openDebug(page, '?level=4-5&boss=final');
    await destroyBoss(page, 'Caldera Throne');
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'level-select', selectedId: '4-5', game: null });
  });
});

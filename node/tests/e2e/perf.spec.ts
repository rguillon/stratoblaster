import { test, expect } from './fixtures';
import {
  expectState,
  gameState,
  openGame,
  sendAction,
  waitForLevelTime,
  waitForLoad,
} from './menu-helpers';

// Tunable values of phase 13: level_load_max_s, scaled by e2e_slowdown (software WebGL).
const LEVEL_LOAD_MAX_S = 2;
const E2E_SLOWDOWN = 10;

test.describe('P13: perf', () => {
  for (const world of [1, 2, 3, 4]) {
    test(`P13-R03: ${String(world)}-1 loads in steps, its loading time recorded and in budget`, async ({
      page,
    }) => {
      const id = `${String(world)}-1`;
      await openGame(page);
      await sendAction(page, 'confirm');
      await sendAction(page, 'confirm');
      await expectState(page, { screen: 'level-select' });
      for (let i = 1; i < world; i++) await sendAction(page, 'down');
      await expectState(page, { selectedId: id });
      await sendAction(page, 'confirm');
      // P13-R02: the press shows the game screen at once; the level loads behind its loading
      // screen, then plays.
      await expectState(page, { screen: 'game', chosenLevelId: id });
      await waitForLoad(page);
      await waitForLevelTime(page, 0.2);
      const { perf, game } = await gameState(page);
      expect(game?.levelId).toBe(id);
      expect(perf.lastLoad).not.toBeNull();
      expect(perf.lastLoad ?? Infinity).toBeLessThan(LEVEL_LOAD_MAX_S * 1000 * E2E_SLOWDOWN);
      expect(perf.longestLoadStep).not.toBeNull();
    });
  }

  test('P13-R01: F3 shows the perf overlay with long frames, longest frame and loading time', async ({
    page,
  }) => {
    await openGame(page);
    const overlay = page.locator('.perf-overlay');
    await expect(overlay).toBeHidden();
    await page.keyboard.press('F3');
    await page.evaluate(() => {
      (window as { __GAME_TEST__?: { step(n: number): void } }).__GAME_TEST__?.step(30);
    });
    await expect(overlay).toBeVisible();
    await expect(overlay).toContainText('Long frames:');
    await expect(overlay).toContainText('Longest frame:');
    await expect(overlay).toContainText('Level load:');
    await page.keyboard.press('F3');
    await expect(overlay).toBeHidden();
  });
});

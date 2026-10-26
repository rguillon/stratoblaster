import type { Locator, Page } from '@playwright/test';
import { test, expect } from './fixtures';
import { expectState, openGame, sendAction } from './menu-helpers';

type Press = (target: Locator) => Promise<void>;

/** Title → ship select → level select → game → back to title with one kind of press. */
async function runFlow(page: Page, press: Press): Promise<void> {
  await openGame(page);
  await press(page.locator('.title-start'));
  await expectState(page, { screen: 'ship-select', selectedId: 'balanced' });
  await press(page.locator('.ship-card').nth(2));
  await expectState(page, { selectedId: 'light' });
  await press(page.locator('.ship-card').nth(2));
  await expectState(page, { screen: 'level-select', chosenShipId: 'light' });
  await press(page.locator('.menu-back'));
  await expectState(page, { screen: 'ship-select', selectedId: 'light' });
  await press(page.locator('.ship-card.selected'));
  await expectState(page, { screen: 'level-select', selectedId: '1-1' });
  await press(page.locator('.level-cell').first());
  await expectState(page, { screen: 'game', chosenShipId: 'light', chosenLevelId: '1-1' });
  await expect(page.locator('.game-level')).toHaveText('Level 1-1');
  // Phase 6 review: no Back button over the playfield; Esc (or the gamepad's B) leaves.
  await expect(page.locator('.menu-back')).toHaveCount(0);
  await sendAction(page, 'back');
  await expectState(page, { screen: 'title' });
}

test('P01-R11: the whole flow with the mouse only', async ({ page }) => {
  await runFlow(page, (target) => target.click());
});

test.describe('touch', () => {
  test.use({ hasTouch: true, viewport: { width: 390, height: 844 } });

  test('P01-R11: the whole flow with taps only', async ({ page }) => {
    await runFlow(page, (target) => target.tap());
  });
});

test('P01-R07, P06-R01, P08-R01, P09-R01, P10-R01: 20 levels 1-1 … 4-5, all unlocked', async ({
  page,
}) => {
  await openGame(page);
  await page.locator('.title-start').click();
  await expectState(page, { screen: 'ship-select' });
  await page.locator('.ship-card.selected').click();
  await expectState(page, { screen: 'level-select' });
  const cells = page.locator('.level-cell');
  await expect(cells).toHaveCount(20);
  await expect(cells.first()).toHaveText('1-1');
  await expect(cells.last()).toHaveText('4-5');
  // Every level of Worlds 1 to 4 is built; the "locked" feedback is unit tested (menu-overlay,
  // menu-controller), as no level of this game is locked any more.
  await expect(page.locator('.level-cell.locked')).toHaveCount(0);
  await cells.nth(16).click();
  await expectState(page, { selectedId: '4-2' });
});

test('P01-R14: the last chosen ship is highlighted after a reload', async ({ page }) => {
  await openGame(page);
  await page.locator('.title-start').click();
  await expectState(page, { screen: 'ship-select' });
  await page.locator('.ship-card').nth(2).click();
  await page.locator('.ship-card').nth(2).click();
  await expectState(page, { screen: 'level-select', chosenShipId: 'light' });
  await page.reload();
  await openGame(page);
  await page.locator('.title-start').click();
  await expectState(page, { screen: 'ship-select', selectedId: 'light' });
});

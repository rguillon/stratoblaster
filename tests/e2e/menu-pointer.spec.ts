import type { Locator, Page } from '@playwright/test';
import { test, expect } from './fixtures';
import { expectState, openGame } from './menu-helpers';

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
  await expect(page.locator('.game-message')).toContainText('Light ship — Level 1-1');
  await press(page.locator('.menu-back'));
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

test('P01-R07: 25 levels 1-1 … 5-5; a locked level only gives a "locked" feedback', async ({
  page,
}) => {
  await openGame(page);
  await page.locator('.title-start').click();
  await expectState(page, { screen: 'ship-select' });
  await page.locator('.ship-card.selected').click();
  await expectState(page, { screen: 'level-select' });
  const cells = page.locator('.level-cell');
  await expect(cells).toHaveCount(25);
  await expect(cells.first()).toHaveText('1-1');
  await expect(cells.last()).toHaveText('5-5');
  await expect(page.locator('.level-cell.locked')).toHaveCount(24);
  await expect(page.locator('.level-cell.locked .padlock')).toHaveCount(24);
  await cells.nth(6).click();
  await expectState(page, { selectedId: '2-2' });
  await cells.nth(6).click();
  await expect(page.locator('.level-cell.selected')).toHaveClass(/shake/);
  await expect(page.locator('.menu-status')).toHaveText('Locked!');
  await expectState(page, { screen: 'level-select', selectedId: '2-2' });
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

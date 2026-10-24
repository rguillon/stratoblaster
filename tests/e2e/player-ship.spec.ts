import { test, expect, waitForFrames } from './fixtures';

test('P02-R01..R03: player_ship/ shows the 3 player ships with their stats', async ({ page }) => {
  await page.goto('./player_ship/');
  await expect(page.locator('#game-canvas')).toBeVisible();
  await expect(page.locator('#fatal')).toBeHidden();
  const titles = page.locator('.caption-title');
  await expect(titles).toHaveText(['Balanced', 'Heavy', 'Light']);
  const captions = page.locator('.caption');
  await expect(captions.nth(0)).toContainText('Speed ×1 (225 px/s)');
  await expect(captions.nth(0)).toContainText('HP 100');
  await expect(captions.nth(1)).toContainText('Speed ×0.8 (180 px/s)');
  await expect(captions.nth(1)).toContainText('HP 140');
  await expect(captions.nth(2)).toContainText('Speed ×1.4 (315 px/s)');
  await expect(captions.nth(2)).toContainText('HP 80');
  for (let i = 0; i < 3; i++) await expect(captions.nth(i)).toContainText(/\d polygons/);
  // Let a few frames render so WebGL errors (shaders, textures) surface in the console.
  await waitForFrames(page);
  // The viewer page has no menu.
  await expect(page.locator('.menu-screen')).toHaveCount(0);
});

test('the game page does not start the ship viewer', async ({ page }) => {
  await page.goto('./');
  await expect(page.locator('#game-canvas')).toBeVisible();
  await expect(page.locator('.caption')).toHaveCount(0);
});

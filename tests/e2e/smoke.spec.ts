import { test, expect } from './fixtures';

test('ENG-54: page loads and the game canvas is shown without errors', async ({ page }) => {
  await page.goto('./');
  await expect(page).toHaveTitle('Pewet');
  await expect(page.locator('#game-canvas')).toBeVisible();
  await expect(page.locator('#fatal')).toBeHidden();
});

import { test, expect } from './fixtures';

test.describe('props/ page (reviewer, 2026-10-28)', () => {
  test('shows the props of a group, and picks one with the buttons and the arrow keys', async ({
    page,
  }) => {
    await page.goto('./props/');
    await expect(page.locator('#game-canvas')).toBeVisible();
    await expect(page.locator('#fatal')).toBeHidden();
    await expect(page.locator('.enemy-title')).toHaveText('Props');
    await expect(page.locator('.prop-groups button.selected')).toHaveText(/^Shared \(\d+\)$/);
    await page.locator('.prop-groups button', { hasText: 'Cars' }).click();
    await expect(page.locator('.prop-kinds button.selected')).toHaveText('car-red');
    await expect(page.locator('.prop-readout')).toHaveText(/^car-red — .* — \d+ triangles$/);
    await page.keyboard.press('ArrowRight');
    await expect(page.locator('.prop-kinds button.selected')).toHaveText('car-blue');
    await page.evaluate(() => {
      (window as unknown as { __PROPS_TEST__: { step(n: number): void } }).__PROPS_TEST__.step(1);
    });
    await expect(page.locator('#fatal')).toBeHidden();
  });
});

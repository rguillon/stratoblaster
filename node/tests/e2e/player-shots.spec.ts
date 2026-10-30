import type { Page } from '@playwright/test';
import { test, expect } from './fixtures';

/**
 * Advances the page by `frames` frames of 1/60 s through its e2e test API, then renders once.
 * The page has no render loop in e2e builds: nothing moves between two steps.
 */
async function step(page: Page, frames = 1): Promise<void> {
  await page.evaluate((n) => {
    (window as unknown as { __SHOTS_TEST__: { step(n: number): void } }).__SHOTS_TEST__.step(n);
  }, frames);
}

/** Steps the page half a second at a time until the targets take damage. */
async function expectDamage(page: Page): Promise<void> {
  await expect
    .poll(
      async () => {
        await step(page, 30);
        return page.locator('.shot-damage').textContent();
      },
      { intervals: [0] },
    )
    .not.toBe('Damage/s: 0.0');
}

test.describe('P03-R10: player_shots/ debug page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./player_shots/');
    await expect(page.locator('#game-canvas')).toBeVisible();
    await expect(page.locator('#fatal')).toBeHidden();
    // The panel shows the selection as of the last frame.
    await step(page);
  });

  test('lists every ship, weapon and level, with the bullet at level 1 selected', async ({
    page,
  }) => {
    await expect(page.locator('.shot-ship button')).toHaveText(['Balanced', 'Heavy', 'Light']);
    await expect(page.locator('.shot-weapon button')).toHaveText(['Bullet', 'Laser', 'Missile']);
    await expect(page.locator('.shot-level button')).toHaveText(['L1', 'L2', 'L3', 'L4', 'L5']);
    await expect(page.locator('.shot-weapon button.selected')).toHaveText('Bullet');
    await expect(page.locator('.shot-summary')).toContainText('Bullet L1 · 1 stream (0°)');
    // The page has no menu.
    await expect(page.locator('.menu-screen')).toHaveCount(0);
    // Phase 3 review: a debug tile with the frame rate and the polygons drawn.
    // A first frame drawn, then a second of frames: the debug tile shows them both.
    await step(page, 1);
    await step(page, 60);
    await expect(page.locator('.stats-fps')).toHaveText(/^FPS: [1-9]\d*$/);
    await expect(page.locator('.stats-polygons')).toHaveText(/^Polygons: [1-9][\d,]*$/);
  });

  test('P03-R01: bullets fly and hit the targets', async ({ page }) => {
    await page.locator('.shot-level button', { hasText: 'L5' }).click();
    await step(page);
    await expect(page.locator('.shot-summary')).toContainText(
      '5 streams (0°, −10°, +10°, −20°, +20°)',
    );
    await step(page, 30);
    await expect(page.locator('.shot-shots')).not.toHaveText('Shots in flight: 0');
    await expectDamage(page);
  });

  test('P03-R02: the laser damages the targets, and goes through ships above level 1', async ({
    page,
  }) => {
    await page.locator('.shot-weapon button', { hasText: 'Laser' }).click();
    await page.locator('.shot-level button', { hasText: 'L3' }).click();
    await step(page);
    await expect(page.locator('.shot-summary')).toContainText('goes through 2 ships');
    await expectDamage(page);
    await expect(page.locator('.shot-shots')).toHaveText('Shots in flight: 0');
  });

  test('P03-R03: missiles fly, and keyboard shortcuts switch weapon, level and ship', async ({
    page,
  }) => {
    await page.keyboard.press('w');
    await page.keyboard.press('w');
    await page.keyboard.press('4');
    await page.keyboard.press('s');
    await step(page);
    await expect(page.locator('.shot-weapon button.selected')).toHaveText('Missile');
    await expect(page.locator('.shot-level button.selected')).toHaveText('L4');
    await expect(page.locator('.shot-ship button.selected')).toHaveText('Heavy');
    await expect(page.locator('.shot-summary')).toContainText('14 damage within 10 px');
    // Frames drawn, so WebGL errors surface in the console.
    await step(page, 30);
    await expect(page.locator('.shot-shots')).not.toHaveText('Shots in flight: 0');
  });
});

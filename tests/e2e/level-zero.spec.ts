import { test, expect, waitForFrames } from './fixtures';

test.describe('P04: level_zero/ page', () => {
  // Each test software-renders a heavy scene: run them one after another in one worker, so they
  // do not starve the other specs running in parallel (menu tests timed out under that load).
  test.describe.configure({ mode: 'default' });

  test.beforeEach(async ({ page }) => {
    await page.goto('./level_zero/');
    await expect(page.locator('#game-canvas')).toBeVisible();
    await expect(page.locator('#fatal')).toBeHidden();
    await expect(page.locator('.scenery-title')).toHaveText('Level Zero');
  });

  test('P04-R01, P04-R04, P04-R06: renders the generated ground with props, and lasts 3 minutes', async ({
    page,
  }) => {
    await expect(page.locator('.scenery-time')).toHaveText(/^Time: 0:\d\d \/ 3:00$/);
    await expect(page.locator('.scenery-section')).toHaveText('Section: plains');
    await expect(page.locator('.scenery-props')).toHaveText(/^Props: [1-9]\d*$/);
    await expect(page.locator('.stats-fps')).toHaveText(/^FPS: [1-9]\d*$/, { timeout: 20_000 });
    await expect(page.locator('.stats-polygons')).toHaveText(/^Polygons: [1-9][\d,]*$/);
    // The page has no menu.
    await expect(page.locator('.menu-screen')).toHaveCount(0);
  });

  test('P04-R06: the level scrolls, and ends after 3 minutes', async ({ page }) => {
    await page.keyboard.press('f');
    await expect(page.locator('.scenery-fast')).toHaveAttribute('aria-pressed', 'true');
    await expect(page.locator('.scenery-time')).not.toHaveText(/^Time: 0:00 /, { timeout: 20_000 });
    await page.locator('.scenery-time-slider').fill('180');
    await expect(page.locator('.scenery-end')).toBeVisible();
    await expect(page.locator('.scenery-time')).toHaveText('Time: 3:00 / 3:00');
    await page.keyboard.press('r');
    await expect(page.locator('.scenery-end')).toBeHidden();
  });

  test('P04-R01, P04-R02: every section renders, with and without the sea', async ({ page }) => {
    await page.keyboard.press('p');
    const sections = [
      ['70', 'mountains'],
      ['96', 'canyon'],
      ['140', 'open sea'],
    ] as const;
    for (const [time, name] of sections) {
      await page.locator('.scenery-time-slider').fill(time);
      await expect(page.locator('.scenery-section')).toHaveText(`Section: ${name}`);
      await waitForFrames(page, 3);
    }
    await page.keyboard.press('s');
    await expect(page.locator('.scenery-sea')).toHaveAttribute('aria-pressed', 'false');
    await waitForFrames(page, 3);
  });

  test('P04-R03: cloud layers switch off and change intensity and opacity', async ({ page }) => {
    const layer = page.locator('.scenery-cloud-1');
    await expect(layer.locator('.scenery-cloud-toggle')).toHaveAttribute('aria-pressed', 'true');
    await layer.locator('.scenery-coverage').fill('90');
    await layer.locator('.scenery-opacity').fill('40');
    await waitForFrames(page, 3);
    await page.keyboard.press('1');
    await expect(layer.locator('.scenery-cloud-toggle')).toHaveAttribute('aria-pressed', 'false');
    await expect(page.locator('.scenery-cloud-2 .scenery-cloud-toggle')).toHaveAttribute(
      'aria-pressed',
      'true',
    );
  });

  test('P04-R05: the playfield outline can be shown, and a new seed rebuilds the ground', async ({
    page,
  }) => {
    await page.keyboard.press('o');
    await expect(page.locator('.scenery-frame')).toHaveAttribute('aria-pressed', 'true');
    await expect(page.locator('.scenery-seed')).toHaveText('Seed: 4242');
    await page.keyboard.press('n');
    await expect(page.locator('.scenery-seed')).toHaveText('Seed: 4243');
    await waitForFrames(page, 3);
  });
});

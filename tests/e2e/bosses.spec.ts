import type { Page } from '@playwright/test';
import type { BossViewerState } from '../../src/debug/boss-viewer-test-api';
import { test, expect } from './fixtures';

/** Advances the page by `frames` frames through its e2e test API, and returns its state. */
async function step(page: Page, frames: number): Promise<BossViewerState> {
  return page.evaluate((n) => {
    const api = (
      window as unknown as { __BOSSES_TEST__: { step(n: number): void; getState(): unknown } }
    ).__BOSSES_TEST__;
    api.step(n);
    return api.getState() as BossViewerState;
  }, frames);
}

const BOSSES = [
  'Reef Warden',
  'Storm Petrel',
  'Breakwater',
  'Gull Mothership',
  'Dust Devil',
  'Mesa Fortress',
  'Scorpion',
  'Refinery Titan',
  'Sentinel',
  'Overlord',
];

test.describe('P07: bosses/ page', () => {
  // Heavy software-rendered scenes (a World 1 level per boss): one test after another.
  test.describe.configure({ mode: 'default' });
  test.setTimeout(150_000);

  test.beforeEach(async ({ page }) => {
    await page.goto('./bosses/');
    await expect(page.locator('#game-canvas')).toBeVisible();
    await expect(page.locator('#fatal')).toBeHidden();
    await expect(page.locator('.enemy-title')).toHaveText('Bosses');
    await expect(page.locator('.stats-fps')).toHaveText(/^FPS: [1-9]\d*$/, { timeout: 60_000 });
  });

  test('P07-R09: loads without errors, every boss can be picked and comes in', async ({ page }) => {
    // Ten bosses over five generated levels under software WebGL.
    test.setTimeout(300_000);
    await expect(page.locator('.enemy-kind button')).toHaveText(BOSSES);
    await expect(page.locator('.stats-polygons')).toHaveText(/^Polygons: [1-9][\d,]*$/);
    for (const [i, name] of BOSSES.entries()) {
      await page.locator('.enemy-kind button').nth(i).click();
      const state = await step(page, 30);
      expect(state.boss?.name, name).toBe(name);
      expect(state.boss?.state, name).toBe('entering');
    }
  });

  test('P07-R09: K destroys the next part, and the stage shown goes up', async ({ page }) => {
    let state = await step(page, 6 * 60);
    expect(state.boss).toMatchObject({ name: 'Reef Warden', state: 'fighting', stage: 0 });
    await page.keyboard.press('KeyK');
    state = await step(page, 2);
    expect(state.boss).toMatchObject({ stage: 1, partsLeft: 1 });
    await expect(page.locator('.enemy-stage')).toHaveText(/^Reef Warden: stage 1 \/ 2/);
    await page.keyboard.press('KeyK');
    await page.keyboard.press('KeyK');
    state = await step(page, 3 * 60);
    expect(state.kills).toBe(1);
  });

  test('P07-R09: the model and wireframe views show the boss close up; ← / → switch it', async ({
    page,
  }) => {
    await page.keyboard.press('m');
    await expect(page.locator('.enemy-view button').nth(1)).toHaveAttribute('aria-pressed', 'true');
    await page.keyboard.press('ArrowRight');
    await expect(page.locator('.enemy-kind button').nth(1)).toHaveAttribute('aria-pressed', 'true');
    await page.keyboard.press('v');
    await expect(page.locator('.enemy-view button').nth(2)).toHaveAttribute('aria-pressed', 'true');
    await step(page, 10);
  });
});

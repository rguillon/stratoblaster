import type { Page } from '@playwright/test';
import type { EnemyViewerTestState } from '../../src/debug/enemy-viewer-test-api';
import { test, expect, waitForFrames } from './fixtures';

/** Advances the page by `frames` frames through its e2e test API, and returns its state. */
async function step(page: Page, frames: number): Promise<EnemyViewerTestState> {
  return page.evaluate((n) => {
    const api = (
      window as unknown as { __ENEMIES_TEST__: { step(n: number): void; getState(): unknown } }
    ).__ENEMIES_TEST__;
    api.step(n);
    return api.getState() as EnemyViewerTestState;
  }, frames);
}

const KINDS = [
  'Gnat',
  'Hornet',
  'Scout',
  'Strafer',
  'Weaver',
  'Spinner',
  'Lancer',
  'Rocketeer',
  'Bulwark',
  'Splitter',
  'Carrier',
];

test.describe('P05: enemies/ page', () => {
  // Heavy software-rendered scene (Level Zero): one test after another, as for level_zero/.
  test.describe.configure({ mode: 'default' });

  test.beforeEach(async ({ page }) => {
    await page.goto('./enemies/');
    await expect(page.locator('#game-canvas')).toBeVisible();
    await expect(page.locator('#fatal')).toBeHidden();
    await expect(page.locator('.enemy-title')).toHaveText('Enemies');
    // Frames are being drawn: the first ones (shader compilation) are slow under SwiftShader,
    // and keys pressed before them would be checked against a page that has not moved yet.
    await expect(page.locator('.stats-fps')).toHaveText(/^FPS: [1-9]\d*$/, { timeout: 20_000 });
  });

  test('P05-R11: loads without errors, with the 11 enemy kinds and the debug tile', async ({
    page,
  }) => {
    await expect(page.locator('.enemy-kind button')).toHaveText(KINDS);
    await expect(page.locator('.stats-fps')).toHaveText(/^FPS: [1-9]\d*$/, { timeout: 20_000 });
    await expect(page.locator('.stats-polygons')).toHaveText(/^Polygons: [1-9][\d,]*$/);
  });

  test('P05-R01..R12: every enemy kind can be picked, spawns and attacks', async ({ page }) => {
    test.setTimeout(90_000);
    await page.keyboard.press('f');
    for (const [i, name] of KINDS.entries()) {
      await page.locator('.enemy-kind button').nth(i).click();
      await expect(page.locator('.enemy-kind button').nth(i)).toHaveAttribute(
        'aria-pressed',
        'true',
      );
      await expect(page.locator('.enemy-enemies'), name).not.toHaveText('Enemies: 0');
      // Every kind but the Gnat, the Hornet and the Carrier shoots within 6 s; the Carrier
      // launches Gnats instead.
      let [shots, enemies] = [0, 0];
      for (let s = 0; s < 6; s++) {
        const state = await step(page, 60);
        shots = Math.max(shots, state.bullets + state.missiles + state.lasers.length);
        enemies = Math.max(enemies, state.enemies.length);
      }
      if (name === 'Carrier') expect(enemies, name).toBeGreaterThan(1);
      else if (i > 1) expect(shots, name).toBeGreaterThan(0);
      await waitForFrames(page, 3);
    }
  });

  test('P05-R07, P05-R08: the Lancer warns before its laser; Rocketeer missiles fly', async ({
    page,
  }) => {
    await page.keyboard.press('f');
    await page.locator('.enemy-kind button').nth(6).click();
    const phases = new Set<string>();
    for (let i = 0; i < 20; i++) for (const p of (await step(page, 30)).lasers) phases.add(p);
    expect([...phases]).toEqual(['warning', 'firing']);
    await page.locator('.enemy-kind button').nth(7).click();
    expect((await step(page, 4 * 60)).missiles).toBeGreaterThan(0);
    await waitForFrames(page, 3);
  });

  test('P05-R11: the model view shows the picked enemy close up; ← / → switch it', async ({
    page,
  }) => {
    await page.keyboard.press('n');
    await expect(page.locator('.enemy-kind button').nth(1)).toHaveAttribute('aria-pressed', 'true');
    await page.keyboard.press('m');
    await expect(page.locator('.enemy-view button').nth(1)).toHaveAttribute('aria-pressed', 'true');
    await expect(page.locator('.enemy-enemies')).toHaveText('Enemies: 0');
    await page.keyboard.press('ArrowRight');
    await expect(page.locator('.enemy-kind button').nth(2)).toHaveAttribute('aria-pressed', 'true');
    await page.keyboard.press('ArrowLeft');
    await page.keyboard.press('ArrowLeft');
    await expect(page.locator('.enemy-kind button').nth(0)).toHaveAttribute('aria-pressed', 'true');
    await page.keyboard.press('ArrowLeft');
    await expect(page.locator('.enemy-kind button').nth(KINDS.length - 1)).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    await waitForFrames(page, 5);
    await page.keyboard.press('v');
    await expect(page.locator('.enemy-view button').nth(2)).toHaveAttribute('aria-pressed', 'true');
    await expect(page.locator('.enemy-enemies')).toHaveText('Enemies: 0');
    await waitForFrames(page, 5);
    await page.keyboard.press('m');
    await page.keyboard.press('m');
    await expect(page.locator('.enemy-enemies')).not.toHaveText('Enemies: 0');
  });

  test('P05-R11: the player ship shoots the enemies down, with any weapon', async ({ page }) => {
    // Gnats cross the middle of the screen, where the ship fires straight up.
    const state = await step(page, 10 * 60);
    expect(state.kills).toBeGreaterThan(0);
    await expect(page.locator('.enemy-kills')).not.toHaveText('Destroyed: 0');
    await expect(page.locator('.enemy-score')).not.toHaveText('Score: 0');
    await page.keyboard.press('x');
    await expect(page.locator('.enemy-weapon button').nth(1)).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    await page.keyboard.press('3');
    await expect(page.locator('.enemy-level button').nth(2)).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    const before = (await step(page, 1)).player.x;
    await page.keyboard.down('ArrowLeft');
    const after = (await step(page, 30)).player.x;
    await page.keyboard.up('ArrowLeft');
    expect(after).toBeLessThan(before);
    await page.keyboard.press('f');
    await expect(page.locator('.enemy-toggles button').first()).toHaveAttribute(
      'aria-pressed',
      'false',
    );
  });
});

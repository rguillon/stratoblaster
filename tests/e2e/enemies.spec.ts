import type { Page } from '@playwright/test';
import type { EnemyViewerTestState } from '../../src/debug/enemy-viewer-test-api';
import { test, expect } from './fixtures';

/**
 * Advances the page by `frames` frames through its e2e test API, renders once, and returns its
 * state. The page has no render loop in e2e builds: nothing moves between two steps.
 */
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
  // P05-R24: the veteran and elite kinds.
  'Wasp',
  'Mortar',
  'Mantis',
  'Phantom',
  'Minelayer',
  'Hydra',
  'Orbiter',
  'Scissor',
  'Juggernaut',
  'Hive',
];

test.describe('P05: enemies/ page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./enemies/');
    await expect(page.locator('#game-canvas')).toBeVisible();
    await expect(page.locator('#fatal')).toBeHidden();
    await expect(page.locator('.enemy-title')).toHaveText('Enemies');
  });

  test('P05-R11, P05-R24: loads without errors, with the 21 enemy kinds and the debug tile', async ({
    page,
  }) => {
    await expect(page.locator('.enemy-kind button')).toHaveText(KINDS);
    // A first frame drawn, then a second of frames: the debug tile shows them both.
    await step(page, 1);
    await step(page, 60);
    await expect(page.locator('.stats-fps')).toHaveText(/^FPS: [1-9]\d*$/);
    await expect(page.locator('.stats-polygons')).toHaveText(/^Polygons: [1-9][\d,]*$/);
  });

  // The 21 kinds in three groups of seven, in parallel.
  for (const first of [0, 7, 14]) {
    test(`P05-R01..R24: enemy kinds ${String(first + 1)} to ${String(first + 7)} can be picked, spawn and attack`, async ({
      page,
    }) => {
      await page.keyboard.press('f');
      for (let i = first; i < first + 7; i++) {
        const name = KINDS[i] ?? '';
        await page.locator('.enemy-kind button').nth(i).click();
        await expect(page.locator('.enemy-kind button').nth(i)).toHaveAttribute(
          'aria-pressed',
          'true',
        );
        await step(page, 1);
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
      }
    });
  }

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
  });

  test('P05-R11: the model view shows the picked enemy close up; ← / → switch it', async ({
    page,
  }) => {
    await page.keyboard.press('n');
    await expect(page.locator('.enemy-kind button').nth(1)).toHaveAttribute('aria-pressed', 'true');
    await page.keyboard.press('m');
    await expect(page.locator('.enemy-view button').nth(1)).toHaveAttribute('aria-pressed', 'true');
    await step(page, 1);
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
    await step(page, 5);
    await page.keyboard.press('v');
    await expect(page.locator('.enemy-view button').nth(2)).toHaveAttribute('aria-pressed', 'true');
    await step(page, 5);
    await expect(page.locator('.enemy-enemies')).toHaveText('Enemies: 0');
    await page.keyboard.press('m');
    await page.keyboard.press('m');
    await step(page, 1);
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

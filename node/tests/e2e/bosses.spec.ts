import type { Page } from '@playwright/test';
import type { BossViewerState } from '../../src/debug/boss-viewer-test-api';
import { test, expect } from './fixtures';

/**
 * Advances the page by `frames` frames through its e2e test API, renders once, and returns its
 * state. The page has no render loop in e2e builds: nothing moves between two steps.
 */
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
  // World 2 (P08-R12), after World 1.
  'Floe Breaker',
  'Narwhal',
  'Fjord Lynx',
  'Harbour Kraken',
  'Snow Owl',
  'Aurora Station',
  'Avalanche',
  'Glacier Colossus',
  'Ice Queen',
  'Boreal Citadel',
  // World 3 (P09-R11), after World 2.
  'Mangrove Croc',
  'River Leviathan',
  'Toucan',
  'Canopy Spider',
  'Stone Idol',
  'Sky Temple',
  'Mosquito',
  'Dam Breaker',
  'Jaguar',
  'Verdant Crown',
  // World 4 (P10-R13), after World 3.
  'Cinder Crab',
  'Steam Dreadnought',
  'Ash Wraith',
  'Geyser Rig',
  'Magma Salamander',
  'Obsidian Golem',
  'Furnace Drake',
  'Foundry Ark',
  'Ember Herald',
  'Caldera Throne',
];

/** Steps a first frame (drawn), then a second of frames: the debug tile shows them both. */
async function expectStats(page: Page): Promise<void> {
  await step(page, 1);
  await step(page, 60);
  await expect(page.locator('.stats-fps')).toHaveText(/^FPS: [1-9]\d*$/);
  await expect(page.locator('.stats-polygons')).toHaveText(/^Polygons: [1-9][\d,]*$/);
}

test('P07-R09 (review): boss/ opens the same page, with every boss', async ({ page }) => {
  await page.goto('./boss/');
  await expect(page.locator('.enemy-title')).toHaveText('Bosses');
  await expect(page.locator('.enemy-kind button')).toHaveText(BOSSES);
  await expectStats(page);
});

test.describe('P07: bosses/ page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./bosses/');
    await expect(page.locator('#game-canvas')).toBeVisible();
    await expect(page.locator('#fatal')).toBeHidden();
    await expect(page.locator('.enemy-title')).toHaveText('Bosses');
  });

  test('P07-R09: loads without errors, with every boss and the debug tile', async ({ page }) => {
    await expect(page.locator('.enemy-kind button')).toHaveText(BOSSES);
    await expectStats(page);
  });

  // Each world's ten bosses (P07-R09, P08-R12, P09-R11, P10-R13), over its five generated levels.
  for (const [world, id] of ['P07-R09', 'P08-R12', 'P09-R11', 'P10-R13'].entries()) {
    test(`${id}: every boss of World ${String(world + 1)} can be picked and comes in`, async ({
      page,
    }) => {
      // Five generated levels: more than the default 30 s on a CI runner.
      test.setTimeout(120_000);
      for (let i = world * 10; i < world * 10 + 10; i++) {
        const name = BOSSES[i];
        await page.locator('.enemy-kind button').nth(i).click();
        const state = await step(page, 30);
        expect(state.boss?.name, name).toBe(name);
        expect(state.boss?.state, name).toBe('entering');
      }
    });
  }

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
  test('P16-R10: every boss model shows close up with its hit circles, moving or still', async ({
    page,
  }) => {
    await page.keyboard.press('m');
    await page.keyboard.press('h');
    const toggles = page.locator('.enemy-toggles button');
    await expect(toggles.nth(3)).toHaveAttribute('aria-pressed', 'true');
    for (let i = 0; i < BOSSES.length; i++) {
      await expect(page.locator('.enemy-kind button').nth(i)).toHaveAttribute(
        'aria-pressed',
        'true',
      );
      await step(page, 2);
      await page.keyboard.press('ArrowRight');
    }
    await page.keyboard.press('l');
    await expect(toggles.nth(2)).toHaveAttribute('aria-pressed', 'false');
    await step(page, 2);
  });
});

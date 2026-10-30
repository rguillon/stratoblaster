import { test, expect } from './fixtures';
import { gameState, openDebug, waitForLevelTime } from './menu-helpers';

// Phase 15: the road kit and the models made for the grid on the `props/` page, and the grid of
// tiles over the districts with `tiles=1` (P15-R10).

test.describe('P15: districts on a grid of tiles', () => {
  test('P15-R10: the props/ page shows the road kit, its sample layout and footprints in tiles', async ({
    page,
  }) => {
    await page.goto('./props/');
    await expect(page.locator('#game-canvas')).toBeVisible();
    await expect(page.locator('#fatal')).toBeHidden();
    const kit = page.locator('.prop-groups button', { hasText: 'Road kit' });
    await expect(kit).toHaveText(/^Road kit \((\d+)\)$/);
    const count = Number((await kit.textContent())?.match(/\((\d+)\)/)?.[1] ?? 0);
    expect(count).toBe(19);
    await kit.click();
    await expect(page.locator('.prop-kinds button.selected')).toHaveText('road-straight-1 · 1×1');
    await expect(page.locator('.prop-kinds button', { hasText: 'road-sample' })).toHaveCount(1);
    await expect(page.locator('.prop-kinds button', { hasText: 'road-cross-3-1' })).toHaveText(
      'road-cross-3-1 · 3×3 adapter',
    );
    await page.locator('.prop-groups button', { hasText: 'Tiles: industrial' }).click();
    const buttons = page.locator('.prop-kinds button');
    const n = await buttons.count();
    expect(n).toBeGreaterThanOrEqual(5);
    for (let i = 0; i < n; i++) await expect(buttons.nth(i)).toHaveText(/ · \d×\d tiles$/);
    await page.evaluate(() => {
      (window as unknown as { __PROPS_TEST__: { step(n: number): void } }).__PROPS_TEST__.step(1);
    });
    await expect(page.locator('#fatal')).toBeHidden();
  });

  for (const id of ['1-5', '2-5', '3-3', '4-5']) {
    test(`P15-R10: ?level=${id}&tiles=1 plays over its districts with the grid drawn`, async ({
      page,
    }) => {
      await openDebug(page, `?level=${id}&t=200&tiles=1`);
      await waitForLevelTime(page, 200.1);
      const { game } = await gameState(page);
      expect(game).toMatchObject({ levelId: id, phase: 'playing' });
      await expect(page.locator('#fatal')).toBeHidden();
    });
  }
});

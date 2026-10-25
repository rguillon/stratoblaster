import type { Page } from '@playwright/test';
import { test, expect } from './fixtures';
import { expectState, gameState, openGame, sendAction, LOAD_TIMEOUT } from './menu-helpers';

const WORLD_1 = ['1-1', '1-2', '1-3', '1-4', '1-5'];

/** A level's scene is generated when it starts; under software WebGL that takes a while. */
const LEVEL_TIMEOUT = 60_000;

/** Through the menus to level `index` of World 1, with the ship at `ship` (0 = balanced). */
async function playLevel(page: Page, index: number, ship = 0): Promise<void> {
  const id = WORLD_1[index] ?? '';
  await openGame(page);
  await sendAction(page, 'confirm');
  for (let i = 0; i < ship; i++) await sendAction(page, 'right');
  await sendAction(page, 'confirm');
  await expectState(page, { screen: 'level-select', selectedId: '1-1' });
  for (let i = 0; i < index; i++) await sendAction(page, 'right');
  await expectState(page, { selectedId: id });
  await sendAction(page, 'confirm');
  await expectState(page, { screen: 'game', chosenLevelId: id });
  await waitForLevelTime(page, 0.2);
}

/** Waits until the level being played has run for `seconds`. */
async function waitForLevelTime(page: Page, seconds: number): Promise<void> {
  await expect
    .poll(async () => (await gameState(page)).game?.time ?? -1, { timeout: LEVEL_TIMEOUT })
    .toBeGreaterThan(seconds);
}

/** The level being played; fails the test when there is none. */
async function level(page: Page) {
  const { game } = await gameState(page);
  if (!game) throw new Error('No level is being played');
  return game;
}

/** Opens the game with debug options (P06-R09) and waits for the level to run. */
async function openDebug(page: Page, query: string): Promise<void> {
  await page.goto(`./${query}`);
  await expect
    .poll(async () => (await gameState(page)).game?.levelId ?? null, { timeout: LOAD_TIMEOUT })
    .not.toBeNull();
}

test.describe('P06: World 1', () => {
  // Each test software-renders a generated level: one at a time, so they do not starve each other.
  test.describe.configure({ mode: 'default' });
  test.setTimeout(150_000);

  test('P06-R01: the World 1 row shows 1-1 to 1-5, all unlocked; worlds 2 to 5 stay locked', async ({
    page,
  }) => {
    await openGame(page);
    await sendAction(page, 'confirm');
    await sendAction(page, 'confirm');
    const cells = page.locator('.level-cell');
    for (const [i, id] of WORLD_1.entries()) {
      await expect(cells.nth(i)).toHaveText(id);
      await expect(cells.nth(i)).not.toHaveClass(/locked/);
    }
    for (let i = 5; i < 25; i++) await expect(cells.nth(i)).toHaveClass(/locked/);
  });

  for (const [index, id] of WORLD_1.entries()) {
    test(`P06-R01, P06-R02: ${id} can be confirmed from a fresh start and plays without errors`, async ({
      page,
    }) => {
      await playLevel(page, index);
      const { game } = await gameState(page);
      expect(game).toMatchObject({ levelId: id, phase: 'playing', timeScale: 1 });
      expect(game?.duration).toBeGreaterThanOrEqual(230);
      expect(game?.duration).toBeLessThanOrEqual(250);
      await expect(page.locator('.game-level')).toHaveText(`Level ${id}`);
      // Phase 6 review: a HUD with the ship's health, the weapon level and the kills.
      await expect(page.locator('.hud-health-text')).toHaveText('HP 100 / 100');
      await expect(page.locator('.hud-weapon')).toHaveText('Bullet · Lv 1/5');
      await expect(page.locator('.hud-destroyed')).toHaveText(/^Destroyed: \d+$/);
      await expect(page.locator('.menu-back')).toHaveCount(0);
      await sendAction(page, 'back');
      await expectState(page, { screen: 'title', game: null });
    });
  }

  test('P06-R02: the heavy ship flies over 1-1, shoots, and stays on screen', async ({ page }) => {
    await playLevel(page, 0, 1);
    expect((await gameState(page)).chosenShipId).toBe('heavy');
    const start = (await level(page)).player;
    await page.keyboard.down('ArrowUp');
    await page.keyboard.down('Space');
    await expect.poll(async () => (await level(page)).player.y).toBeGreaterThan(start.y + 20);
    await expect.poll(async () => (await level(page)).shots).toBeGreaterThan(0);
    expect((await level(page)).firing).toBe(true);
    // Phase 6 review: E (by position) switches to the next weapon.
    await page.keyboard.press('KeyE');
    await expect(page.locator('.hud-weapon')).toHaveText('Laser · Lv 1/5');
    await page.keyboard.press('KeyE');
    await expect(page.locator('.hud-weapon')).toHaveText('Missile · Lv 1/5');
    await page.keyboard.up('Space');
    await page.keyboard.up('ArrowUp');
    // Pushed against the left edge for a while, it stops there, inside the playfield.
    await page.keyboard.down('ArrowLeft');
    await waitForLevelTime(page, (await level(page)).time + 4);
    const first = await level(page);
    await waitForLevelTime(page, first.time + 0.5);
    const second = await level(page);
    await page.keyboard.up('ArrowLeft');
    expect(second.player.x).toBe(first.player.x);
    expect(second.player.x).toBeGreaterThan(0);
    expect(second.player.x).toBeLessThan(240 - 100);
  });

  test('P06-R09: without debug options, F, ← and → do not change the time', async ({ page }) => {
    await playLevel(page, 0);
    await page.keyboard.press('KeyF');
    await page.keyboard.press('ArrowRight');
    await page.keyboard.press('ArrowRight');
    const { game } = await gameState(page);
    expect(game?.timeScale).toBe(1);
    expect(game?.time).toBeLessThan(15);
    await expect(page.locator('.stats-tile')).toHaveCount(0);
  });

  test('P06-R09: ?level=1-3&t=120 starts 1-3 at 2:00, the waves before it skipped', async ({
    page,
  }) => {
    await openDebug(page, '?level=1-3&t=120');
    const { game, chosenShipId, screen } = await gameState(page);
    expect(screen).toBe('game');
    expect(chosenShipId).toBe('balanced');
    expect(game?.levelId).toBe('1-3');
    expect(game?.time).toBeGreaterThanOrEqual(120);
    expect(game?.time).toBeLessThan(125);
    // The first wave after 2:00 comes at 2:10: nothing before it came in.
    expect(game?.spawned).toBe(0);
    await expect(page.locator('.stats-fps')).toHaveText(/^FPS: \d+$/, { timeout: 20_000 });
    await expect(page.locator('.stats-polygons')).toHaveText(/^Polygons: [\d,]+$/);
    await page.keyboard.press('KeyF');
    await expect.poll(async () => (await gameState(page)).game?.timeScale).toBe(4);
    const before = (await gameState(page)).game?.time ?? 0;
    await page.keyboard.press('ArrowRight');
    expect((await gameState(page)).game?.time).toBeGreaterThanOrEqual(before + 10);
  });

  test('P06-R03: the end of 1-1 shows "Level complete"; Confirm goes to level-select on 1-2', async ({
    page,
  }) => {
    await openDebug(page, '?level=1-1&t=237&ship=light');
    expect((await gameState(page)).chosenShipId).toBe('light');
    await expect(page.locator('.level-complete')).toBeVisible({ timeout: LEVEL_TIMEOUT });
    await expect(page.locator('.level-complete-heading')).toHaveText('Level complete!');
    await expect(page.locator('.level-complete-level')).toHaveText('1-1');
    await expect(page.locator('.level-complete-enemies')).toHaveText(
      /^Enemies destroyed: \d+ \/ \d+$/,
    );
    const { levelResult, game } = await gameState(page);
    expect(levelResult?.levelId).toBe('1-1');
    expect(game?.phase).toBe('complete');
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'level-select', selectedId: '1-2', game: null });
  });
});

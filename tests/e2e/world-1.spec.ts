import type { Page } from '@playwright/test';
import { test, expect } from './fixtures';
import {
  advance,
  destroyBoss,
  expectState,
  gameState,
  leaveLevel,
  level,
  openDebug,
  openGame,
  sendAction,
  step,
  stepUntil,
  waitForLevelTime,
} from './menu-helpers';

const WORLD_1 = ['1-1', '1-2', '1-3', '1-4', '1-5'];

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

test.describe('P06: World 1', () => {
  test('P06-R01: the World 1 row shows 1-1 to 1-5, all unlocked', async ({ page }) => {
    await openGame(page);
    await sendAction(page, 'confirm');
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'level-select' });
    const cells = page.locator('.level-cell');
    for (const [i, id] of WORLD_1.entries()) {
      await expect(cells.nth(i)).toHaveText(id);
      await expect(cells.nth(i)).not.toHaveClass(/locked/);
    }
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
      // Phase 6 review: a HUD with the ship's health and the weapon level; no kills since the
      // reviewer's rework (2026-10-28).
      await expect(page.locator('.hud-health-text')).toHaveText('HP 100 / 100');
      await expect(page.locator('.hud-weapon')).toHaveText('Bullet · Lv 1/5');
      await expect(page.locator('.hud-destroyed')).toHaveCount(0);
      await expect(page.locator('.menu-back')).toHaveCount(0);
      await leaveLevel(page);
      await expectState(page, { screen: 'title', game: null });
    });
  }

  test('P06-R02: the heavy ship flies over 1-1, shoots, and stays on screen', async ({ page }) => {
    await playLevel(page, 0, 1);
    expect((await gameState(page)).chosenShipId).toBe('heavy');
    const start = (await level(page)).player;
    await page.keyboard.down('ArrowUp');
    await page.keyboard.down('Space');
    await advance(page, 0.5);
    const flying = await level(page);
    expect(flying.player.y).toBeGreaterThan(start.y + 20);
    expect(flying.shots).toBeGreaterThan(0);
    expect(flying.firing).toBe(true);
    // Phase 6 review: E (by position) switches to the next weapon.
    await page.keyboard.press('KeyE');
    await step(page);
    await expect(page.locator('.hud-weapon')).toHaveText('Laser · Lv 1/5');
    await page.keyboard.press('KeyE');
    await step(page);
    await expect(page.locator('.hud-weapon')).toHaveText('Missile · Lv 1/5');
    await page.keyboard.up('Space');
    await page.keyboard.up('ArrowUp');
    // Pushed against the left edge for a while, it stops there, inside the playfield.
    await page.keyboard.down('ArrowLeft');
    await advance(page, 4);
    const first = await level(page);
    await advance(page, 0.5);
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
    await step(page);
    const { game } = await gameState(page);
    expect(game?.timeScale).toBe(1);
    expect(game?.time).toBeLessThan(1);
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
    expect(game?.time).toBeLessThan(121);
    // The first wave after 2:00 comes at 2:10: nothing before it came in. At 2:00, the middle
    // of the level, its mini boss arrives (P07-R06), and only it.
    expect(game?.boss?.name).toBe('Dust Devil');
    expect(game?.spawned).toBe(1);
    // The debug tile: one simulated second of frames, then the polygons of the frame drawn.
    await step(page, 60);
    await expect(page.locator('.stats-fps')).toHaveText(/^FPS: [1-9]\d*$/);
    await expect(page.locator('.stats-polygons')).toHaveText(/^Polygons: [1-9][\d,]*$/);
    await page.keyboard.press('KeyF');
    expect((await level(page)).timeScale).toBe(4);
    const before = (await level(page)).time;
    await page.keyboard.press('ArrowRight');
    expect((await level(page)).time).toBeGreaterThanOrEqual(before + 10);
  });

  test('P06-R03, P07-R06, P07-R09: 1-1 ends once its final boss is destroyed; Confirm goes to 1-2', async ({
    page,
  }) => {
    await openDebug(page, '?level=1-1&boss=final&ship=light');
    expect((await gameState(page)).chosenShipId).toBe('light');
    await stepUntil(page, async () => (await gameState(page)).game?.boss?.name ?? null).toBe(
      'Storm Petrel',
    );
    // P07-R02: its health bar shows.
    await expect(page.locator('.boss-bar')).toBeVisible();
    await expect(page.locator('.boss-name')).toHaveText('Storm Petrel');
    expect((await level(page)).phase).toBe('playing');
    // K destroys its four parts one by one (the stage goes up), then its core.
    await destroyBoss(page, 'Storm Petrel');
    await expect(page.locator('.level-complete-heading')).toHaveText('Level complete!');
    await expect(page.locator('.level-complete-level')).toHaveText('1-1');
    await expect(page.locator('.level-complete-enemies')).toHaveText(
      /^Enemies destroyed: \d+ \/ \d+$/,
    );
    const { levelResult, game } = await gameState(page);
    expect(levelResult?.levelId).toBe('1-1');
    expect(game?.phase).toBe('complete');
    expect(game?.bossesDefeated).toBe(1);
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'level-select', selectedId: '1-2', game: null });
  });
});

import type { Page } from '@playwright/test';
import { test, expect } from './fixtures';
import {
  destroyBoss,
  expectState,
  gameState,
  openDebug,
  openGame,
  sendAction,
  stepUntil,
  waitForLevelTime,
} from './menu-helpers';

const WORLD_2 = ['2-1', '2-2', '2-3', '2-4', '2-5'];

test.describe('P08: World 2', () => {
  test('P08-R01: the World 2 row shows 2-1 to 2-5, all unlocked', async ({ page }) => {
    await openGame(page);
    await sendAction(page, 'confirm');
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'level-select' });
    const cells = page.locator('.level-cell');
    for (const [i, id] of WORLD_2.entries()) {
      await expect(cells.nth(5 + i)).toHaveText(id);
      await expect(cells.nth(5 + i)).not.toHaveClass(/locked/);
    }
  });

  for (const [index, id] of WORLD_2.entries()) {
    test(`P08-R01: ${id} can be confirmed from a fresh start and plays without errors`, async ({
      page,
    }) => {
      await openGame(page);
      await sendAction(page, 'confirm');
      await sendAction(page, 'confirm');
      await expectState(page, { screen: 'level-select', selectedId: '1-1' });
      // Down a row to World 2, then along it.
      await sendAction(page, 'down');
      for (let i = 0; i < index; i++) await sendAction(page, 'right');
      await expectState(page, { selectedId: id });
      await sendAction(page, 'confirm');
      await expectState(page, { screen: 'game', chosenLevelId: id });
      await waitForLevelTime(page, 0.2);
      const { game } = await gameState(page);
      expect(game).toMatchObject({ levelId: id, phase: 'playing', timeScale: 1 });
      expect(game?.duration).toBeGreaterThanOrEqual(290);
      expect(game?.duration).toBeLessThanOrEqual(310);
      await expect(page.locator('.game-level')).toHaveText(`Level ${id}`);
    });
  }

  test('P08-R12: ?level=2-4&t=150 starts 2-4 at 2:30', async ({ page }) => {
    await openDebug(page, '?level=2-4&t=150');
    // At 2:30, the middle of the level, its mini boss comes (and holds the level's progress).
    await stepUntil(page, async () => ((await gameState(page)).game?.time ?? 0) >= 150).toBe(true);
    const { game } = await gameState(page);
    expect(game?.levelId).toBe('2-4');
    expect(game?.time).toBeGreaterThanOrEqual(150);
    expect(game?.time).toBeLessThan(156);
  });

  /** The sky of the level opened with `query`, once its clock is past `time`. */
  const skyAt = async (page: Page, query: string, time: number) => {
    await openDebug(page, query);
    await waitForLevelTime(page, time);
    return (await gameState(page)).game?.sky;
  };

  test('P08-R06 (rework, 2026-10-27): no weather or aurora in World 2', async ({ page }) => {
    for (const [query, time] of [
      ['?level=2-1', 0.2],
      ['?level=2-5&t=120', 120.1],
    ] as const) {
      expect(await skyAt(page, query, time), query).toMatchObject({
        weatherParticles: 0,
        aurora: 0,
      });
    }
  });

  test('P08-R06 (rework, 2026-10-27): the lights come on at dusk and night', async ({ page }) => {
    const morning = await skyAt(page, '?level=2-1', 0.2);
    const dusk = await skyAt(page, '?level=2-4&t=60', 60.1);
    const night = await skyAt(page, '?level=2-5&t=120', 120.1);
    expect(morning?.groundLights).toBeLessThan(0.5);
    expect(dusk?.groundLights).toBeGreaterThan(morning?.groundLights ?? Infinity);
    expect(night?.groundLights).toBeGreaterThan(1);
    expect(night?.sunIntensity).toBeLessThan(morning?.sunIntensity ?? 0);
  });

  test('P08-R12: look= forces a time of day', async ({ page }) => {
    await openDebug(page, '?level=2-5&t=120');
    await waitForLevelTime(page, 120.1);
    const night = (await gameState(page)).game?.sky;
    await openDebug(page, '?level=2-5&t=120&look=midday');
    await waitForLevelTime(page, 120.1);
    const midday = (await gameState(page)).game?.sky;
    expect(midday?.groundLights).toBeLessThan(0.5);
    expect(midday?.sunIntensity).toBeGreaterThan(night?.sunIntensity ?? Infinity);
  });

  test('P08-R10: ?level=2-1&boss=final: K destroys the Narwhal and the level is complete', async ({
    page,
  }) => {
    await openDebug(page, '?level=2-1&boss=final');
    await stepUntil(
      page,
      async () => (await gameState(page)).game?.boss?.parts ?? 0,
    ).toBeGreaterThanOrEqual(4);
    await destroyBoss(page, 'Narwhal');
    await expect(page.locator('.level-complete-level')).toHaveText('2-1');
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'level-select', selectedId: '2-2', game: null });
  });

  test('P08-R01: after 1-5, the level select highlights 2-1', async ({ page }) => {
    await openDebug(page, '?level=1-5&boss=final');
    await destroyBoss(page, 'Overlord');
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'level-select', selectedId: '2-1', game: null });
  });
});

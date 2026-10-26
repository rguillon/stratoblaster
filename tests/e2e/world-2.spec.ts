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

  test('P08-R12: ?level=2-4&t=150 starts 2-4 at 2:30 in its blizzard', async ({ page }) => {
    await openDebug(page, '?level=2-4&t=150');
    // At 2:30, the middle of the level, its mini boss comes (and holds the level's progress).
    await stepUntil(
      page,
      async () => (await gameState(page)).game?.sky?.weatherParticles ?? -1,
    ).toBe(1500);
    const { game } = await gameState(page);
    expect(game?.levelId).toBe('2-4');
    expect(game?.time).toBeGreaterThanOrEqual(150);
    expect(game?.time).toBeLessThan(156);
  });

  test('P08-R12: ?level=2-3&weather=0 shows no snow; without it, 2-3 snows', async ({ page }) => {
    await openDebug(page, '?level=2-3&weather=0');
    await waitForLevelTime(page, 0.2);
    expect((await gameState(page)).game?.sky?.weatherParticles).toBe(0);
    await openDebug(page, '?level=2-3');
    await waitForLevelTime(page, 0.2);
    expect((await gameState(page)).game?.sky?.weatherParticles).toBe(600);
  });

  test('P08-R04, P08-R12: 2-5 turns to night, its aurora on; look= forces a time of day', async ({
    page,
  }) => {
    await openDebug(page, '?level=2-5&t=120');
    await waitForLevelTime(page, 120.1);
    const night = (await gameState(page)).game?.sky;
    expect(night?.aurora).toBe(1);
    expect(night?.groundLights).toBeGreaterThan(1);
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

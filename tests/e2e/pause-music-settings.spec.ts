import type { Locator, Page } from '@playwright/test';
import { test, expect } from './fixtures';
import {
  advance,
  expectState,
  gameState,
  leaveLevel,
  openDebug,
  openGame,
  sendAction,
  step,
  stepUntil,
} from './menu-helpers';

/** Whether two elements' boxes overlap. */
async function overlap(a: Locator, b: Locator): Promise<boolean> {
  const [x, y] = await Promise.all([a.boundingBox(), b.boundingBox()]);
  if (!x || !y) return false;
  return x.x < y.x + y.width && y.x < x.x + x.width && x.y < y.y + y.height && y.y < x.y + x.height;
}

/** The box of an element shown on screen. */
async function boxOf(
  locator: Locator,
): Promise<{ x: number; y: number; width: number; height: number }> {
  const box = await locator.boundingBox();
  if (!box) throw new Error('not shown');
  return box;
}

/** Fakes the page going hidden or visible again (tab switched, window minimised). */
async function setHidden(page: Page, hidden: boolean): Promise<void> {
  await page.evaluate((h) => {
    Object.defineProperty(document, 'visibilityState', {
      configurable: true,
      get: () => (h ? 'hidden' : 'visible'),
    });
    document.dispatchEvent(new Event('visibilitychange'));
  }, hidden);
}

/** Goes from the title to level 1-1 with the keyboard. */
async function playFirstLevel(page: Page): Promise<void> {
  await openGame(page);
  for (const screen of ['ship-select', 'level-select', 'game']) {
    await page.keyboard.press('Enter');
    await expectState(page, { screen });
  }
}

test.describe('P12: pause', () => {
  for (const viewport of [
    { width: 390, height: 844 },
    { width: 800, height: 600 },
  ]) {
    test(`P12-R01: at ${String(viewport.width)}×${String(viewport.height)} the pause button shows, is at least 44 px and covers no HUD part`, async ({
      page,
    }) => {
      await page.setViewportSize(viewport);
      await openDebug(page, '?level=1-1&boss=final');
      await stepUntil(page, async () => (await gameState(page)).game?.boss?.name ?? null).toBe(
        'Storm Petrel',
      );
      const button = page.locator('.game-pause');
      await expect(button).toBeVisible();
      await expect(page.locator('.boss-bar')).toBeVisible();
      const box = await boxOf(button);
      expect(Math.min(box.width, box.height)).toBeGreaterThanOrEqual(44);
      expect(box.y).toBeGreaterThanOrEqual(0);
      expect(box.x + box.width).toBeLessThanOrEqual(viewport.width);
      const hud = ['.hud-health', '.hud-weapon', '.hud-score', '.hud-progress', '.boss-bar'];
      for (const other of hud)
        expect(await overlap(button, page.locator(other)), other).toBe(false);
    });
  }

  test('P12-R01, P12-R02: P pauses: nothing moves; Resume goes on from the same point', async ({
    page,
  }) => {
    await openDebug(page, '?level=1-2&t=20');
    await advance(page, 1);
    await page.keyboard.press('KeyP');
    await expectState(page, { screen: 'pause', paused: true, selectedId: 'resume' });
    await expect(page.locator('.pause-panel')).toBeVisible();
    await expect(page.locator('.pause-entry')).toHaveText(['Resume', 'Settings', 'Main menu']);
    const before = await gameState(page);
    await advance(page, 10);
    const after = await gameState(page);
    expect(after.game?.time).toBe(before.game?.time);
    expect(after.game?.player).toEqual(before.game?.player);
    expect(after.game?.enemies).toBe(before.game?.enemies);
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'game', paused: false });
    await expect(page.locator('.pause-panel')).toHaveCount(0);
    await advance(page, 0.5);
    expect((await gameState(page)).game?.time).toBeGreaterThan(before.game?.time ?? 0);
  });

  test('P12-R02: Back resumes; No and Back on the question go back to the paused menu', async ({
    page,
  }) => {
    await openDebug(page, '?level=1-1&t=10');
    await sendAction(page, 'pause');
    await expectState(page, { screen: 'pause' });
    await sendAction(page, 'back');
    await expectState(page, { screen: 'game', paused: false });
    await sendAction(page, 'pause');
    await expectState(page, { screen: 'pause' });
    for (const answer of ['confirm', 'back']) {
      await sendAction(page, 'down');
      await sendAction(page, 'down');
      await sendAction(page, 'confirm');
      await expectState(page, { leaving: true, choice: 0 });
      await expect(page.locator('.pause-question-text')).toHaveText('Leave the level?');
      await sendAction(page, answer);
      await expectState(page, { screen: 'pause', paused: true, leaving: false });
      await sendAction(page, 'up');
      await sendAction(page, 'up');
    }
    expect((await gameState(page)).game).not.toBeNull();
  });

  test('P12-R02, P11-R03: Main menu then Yes saves a score above the saved high score', async ({
    page,
    context,
    baseURL,
  }) => {
    await context.addCookies([
      { name: 'stratoblaster_high_score', value: '1000', url: baseURL ?? '' },
    ]);
    await openDebug(page, '?level=1-1&boss=final');
    await stepUntil(page, async () => (await gameState(page)).game?.boss?.name ?? null).toBe(
      'Storm Petrel',
    );
    // K destroys its four parts: 4 × 800 points.
    for (let stage = 1; stage <= 4; stage++) {
      await page.keyboard.press('KeyK');
      await stepUntil(page, async () => (await gameState(page)).game?.boss?.stage ?? -1).toBe(
        stage,
      );
    }
    const score = (await gameState(page)).game?.score ?? 0;
    expect(score).toBeGreaterThanOrEqual(3000);
    await leaveLevel(page);
    await expect(page.locator('.title-high-score')).toHaveText(String(score));
  });

  test('P12-R02: Settings from the pause menu, then Back, shows the pause menu with the level still paused', async ({
    page,
  }) => {
    await openDebug(page, '?level=1-1&t=10');
    await sendAction(page, 'pause');
    await expectState(page, { screen: 'pause' });
    const time = (await gameState(page)).game?.time;
    await sendAction(page, 'down');
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'settings', paused: true });
    await expect(page.locator('.settings-screen.over-level')).toBeVisible();
    await advance(page, 2);
    await sendAction(page, 'back');
    await expectState(page, { screen: 'pause', paused: true });
    expect((await gameState(page)).game?.time).toBe(time);
  });

  test('P12-R03, P12-R11: a hidden page pauses the level and suspends the audio; it stays paused once shown', async ({
    page,
  }) => {
    await playFirstLevel(page);
    await expect.poll(async () => (await gameState(page)).audio).toBe('running');
    await setHidden(page, true);
    await expectState(page, { screen: 'pause', paused: true });
    await expect.poll(async () => (await gameState(page)).audio).toBe('suspended');
    await setHidden(page, false);
    await expect.poll(async () => (await gameState(page)).audio).toBe('running');
    await step(page, 5);
    await expectState(page, { screen: 'pause', paused: true });
    await expect(page.locator('.pause-panel')).toBeVisible();
    // Hidden and shown again while paused: still paused.
    await setHidden(page, true);
    await setHidden(page, false);
    await step(page, 5);
    expect((await gameState(page)).paused).toBe(true);
  });
});

test.describe('P12: settings', () => {
  test('P12-R04: from the title, with no cookie, Music shows 6 and Sound effects 8; Back returns to the title', async ({
    page,
  }) => {
    await openGame(page);
    await expect(page.locator('.title-settings')).toHaveText('Settings');
    await page.keyboard.press('ArrowDown');
    await expectState(page, { selectedId: 'settings' });
    await page.keyboard.press('Enter');
    await expectState(page, { screen: 'settings', volumes: { music: 6, sfx: 8 } });
    await expect(page.locator('.slider-value')).toHaveText(['6', '8']);
    await page.keyboard.press('Escape');
    await expectState(page, { screen: 'title', selectedId: 'settings' });
  });

  test('P12-R04: Music set to 3 is kept after a reload', async ({ page }) => {
    await openGame(page);
    await sendAction(page, 'down');
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'settings' });
    for (let i = 0; i < 3; i++) await sendAction(page, 'left');
    await expectState(page, { volumes: { music: 3, sfx: 8 } });
    await sendAction(page, 'down');
    await sendAction(page, 'left');
    await expectState(page, { volumes: { music: 3, sfx: 7 } });
    await page.reload();
    await openGame(page);
    expect((await gameState(page)).volumes).toEqual({ music: 3, sfx: 7 });
  });

  for (const value of ['banana', '42']) {
    test(`P12-R04: a volume cookie of "${value}" reads as the default`, async ({
      page,
      context,
      baseURL,
    }) => {
      await context.addCookies([
        { name: 'stratoblaster_music_volume', value, url: baseURL ?? '' },
        { name: 'stratoblaster_sfx_volume', value, url: baseURL ?? '' },
      ]);
      await openGame(page);
      expect((await gameState(page)).volumes).toEqual({ music: 6, sfx: 8 });
    });
  }

  test.describe('touch', () => {
    test.use({ hasTouch: true, viewport: { width: 390, height: 844 } });

    test('P12-R04: taps set the sliders; every target is at least 44 px', async ({ page }) => {
      await openGame(page);
      await page.locator('.title-settings').tap();
      await page.locator('.title-settings').tap();
      await expectState(page, { screen: 'settings' });
      const bars = page.locator('.slider-bar');
      for (const target of [bars.nth(0), bars.nth(1), page.locator('.menu-back')]) {
        expect((await boxOf(target)).height).toBeGreaterThanOrEqual(44);
      }
      const box = await boxOf(bars.nth(1));
      // The left edge of the bar: 0, silent.
      await page.touchscreen.tap(box.x + 1, box.y + box.height / 2);
      await expectState(page, { volumes: { music: 6, sfx: 0 }, selectedId: 'sfx' });
      await page.touchscreen.tap(box.x + box.width - 1, box.y + box.height / 2);
      await expectState(page, { volumes: { music: 6, sfx: 10 } });
      await page.locator('.menu-back').tap();
      await expectState(page, { screen: 'title' });
    });
  });
});

test.describe('P12: audio', () => {
  test('P12-R05: no audio before the first input, and no autoplay warning; a key press starts it', async ({
    page,
    baseURL,
  }) => {
    const warnings: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'warning') warnings.push(msg.text());
    });
    const media: string[] = [];
    page.on('request', (request) => {
      const url = request.url();
      if (request.resourceType() === 'media' || /\.(ogg|mp3|wav|m4a|aac|flac|opus)$/i.test(url)) {
        media.push(url);
      }
    });
    await openGame(page);
    expect((await gameState(page)).audio).toBe('none');
    expect((await gameState(page)).music).toBe('menu');
    await page.keyboard.press('ArrowDown');
    await step(page);
    await expect.poll(async () => (await gameState(page)).audio).toBe('running');
    expect(warnings.filter((w) => /audio/i.test(w))).toEqual([]);
    expect(media, `audio files fetched from ${baseURL ?? ''}`).toEqual([]);
  });

  test('P12-R08, P12-R12: the menu theme plays in the menus, the level track in the level, the boss track in its fight', async ({
    page,
  }) => {
    await openGame(page);
    expect((await gameState(page)).music).toBe('menu');
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'ship-select', music: 'menu' });
    await openDebug(page, '?level=2-3');
    await step(page, 2);
    expect((await gameState(page)).music).toBe('level-2-3');
    await openDebug(page, '?level=2-3&boss=mini');
    await stepUntil(page, async () => (await gameState(page)).music).toBe('boss-2');
  });

  test('P12-R09, P12-R12: a gun shot and a menu move are listed among the last sounds', async ({
    page,
  }) => {
    await openDebug(page, '?level=1-1&t=5');
    await page.keyboard.down('Space');
    await stepUntil(page, async () => (await gameState(page)).sounds.includes('gun-shot')).toBe(
      true,
    );
    await page.keyboard.up('Space');
    await sendAction(page, 'pause');
    await expectState(page, { screen: 'pause' });
    expect((await gameState(page)).sounds.at(-1)).toBe('pause');
    await sendAction(page, 'down');
    await step(page);
    expect((await gameState(page)).sounds.at(-1)).toBe('menu-move');
  });
});

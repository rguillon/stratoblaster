import type { Page } from '@playwright/test';
import { test, expect } from './fixtures';
import { READABILITY } from '../../src/game/config/readability';
import { openDebug, step } from './menu-helpers';

/** What `__GAME_TEST__.readability()` returns (src/core/math/pixel-contrast.ts). */
interface Report {
  player: number | null;
  enemy: number | null;
  enemyBullet: number | null;
  playerShot: number | null;
  backgroundLuminance: number;
}

interface TestWindow {
  __GAME_TEST__?: { readability(share: number): Promise<Report | null> };
}

function readability(page: Page): Promise<Report | null> {
  return page.evaluate(
    (share) => (window as TestWindow).__GAME_TEST__?.readability(share) ?? null,
    READABILITY.backgroundBrightPixelBudget,
  );
}

/** Steps the level until the ship, an enemy, an enemy bullet and a player shot are all on screen. */
async function fullFrame(page: Page): Promise<Report> {
  let last: Report | null = null;
  for (let i = 0; i < 120; i++) {
    await step(page, 5);
    last = await readability(page);
    if (!last) continue;
    if (last.enemy !== null && last.enemyBullet !== null && last.playerShot !== null) return last;
  }
  throw new Error(`No full frame: ${JSON.stringify(last)}`);
}

/** One level of each world, at a time it is busy with enemies shooting. */
const LEVELS = [
  { id: '1-2', time: 40 },
  { id: '2-1', time: 40 },
  { id: '3-1', time: 40 },
  { id: '4-1', time: 90 },
];

test.describe('P14: readability', () => {
  for (const { id, time } of LEVELS) {
    test(`P14-R08: in ${id}, the ship, enemies and shots stand out from the background`, async ({
      page,
    }) => {
      test.setTimeout(180_000);
      await openDebug(page, `?level=${id}&t=${String(time)}`);
      await page.keyboard.down('Space');
      const report = await fullFrame(page);
      await page.keyboard.up('Space');
      test.info().annotations.push({ type: 'readability', description: JSON.stringify(report) });
      // P14-R01: the background is dimmed, but for a few small lights.
      expect(report.backgroundLuminance).toBeLessThanOrEqual(READABILITY.backgroundMaxLuminance);
      // P14-R03, R04: the ship and the enemies stand out.
      expect(report.player).toBeGreaterThanOrEqual(READABILITY.minObjectContrast);
      expect(report.enemy).toBeGreaterThanOrEqual(READABILITY.minObjectContrast);
      // P14-R05: the enemy bullets most of all; P14-R06: the player shots, toned down, still show.
      expect(report.enemyBullet).toBeGreaterThanOrEqual(READABILITY.minBulletContrast);
      expect(report.playerShot).toBeGreaterThanOrEqual(READABILITY.minPlayerShotContrast);
    });
  }
});

import type { Page } from '@playwright/test';
import { test, expect } from './fixtures';
import { expectState, gameState, openGame, step } from './menu-helpers';

/** Dispatches a key press as a layout would: `code` is the position, `key` the label. */
async function pressPosition(page: Page, code: string, key: string): Promise<void> {
  await page.evaluate(
    ([c, k]) => {
      window.dispatchEvent(new KeyboardEvent('keydown', { code: c, key: k }));
      window.dispatchEvent(new KeyboardEvent('keyup', { code: c, key: k }));
    },
    [code, key] as const,
  );
}

test('P01-R09: the whole flow with arrows, Enter/Space and Esc', async ({ page }) => {
  await openGame(page);
  await page.keyboard.press('Enter');
  await expectState(page, { screen: 'ship-select', selectedId: 'balanced' });
  await page.keyboard.press('ArrowRight');
  await expectState(page, { selectedId: 'heavy' });
  await page.keyboard.press('Space');
  await expectState(page, { screen: 'level-select', selectedId: '1-1', chosenShipId: 'heavy' });
  await page.keyboard.press('Escape');
  await expectState(page, { screen: 'ship-select', selectedId: 'heavy' });
  await page.keyboard.press('Enter');
  await expectState(page, { screen: 'level-select' });
  await page.keyboard.press('Enter');
  await expectState(page, { screen: 'game', chosenShipId: 'heavy', chosenLevelId: '1-1' });
  // P12-R01: Backspace no longer leaves the level; Esc pauses and resumes, P too.
  await page.keyboard.press('Backspace');
  await step(page, 3);
  expect((await gameState(page)).screen).toBe('game');
  await page.keyboard.press('Escape');
  await expectState(page, { screen: 'pause', paused: true, selectedId: 'resume' });
  await page.keyboard.press('Escape');
  await expectState(page, { screen: 'game', paused: false });
  await page.keyboard.press('KeyP');
  await expectState(page, { screen: 'pause', paused: true });
  // P12-R02: Main menu asks first; Yes leaves to the title.
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('ArrowDown');
  await expectState(page, { selectedId: 'main-menu' });
  await page.keyboard.press('Enter');
  await expectState(page, { leaving: true, choice: 0 });
  await page.keyboard.press('ArrowRight');
  await page.keyboard.press('Enter');
  await expectState(page, { screen: 'title' });
});

test('P01-R09: on an AZERTY layout, Z/Q/S/D (the WASD positions) move the selection', async ({
  page,
}) => {
  await openGame(page);
  await page.keyboard.press('Enter');
  await expectState(page, { screen: 'ship-select' });
  await page.keyboard.press('Enter');
  await expectState(page, { screen: 'level-select', selectedId: '1-1' });
  await pressPosition(page, 'KeyD', 'd');
  await expectState(page, { selectedId: '1-2' });
  await pressPosition(page, 'KeyS', 's');
  await expectState(page, { selectedId: '2-2' });
  await pressPosition(page, 'KeyA', 'q');
  await expectState(page, { selectedId: '2-1' });
  await pressPosition(page, 'KeyW', 'z');
  await expectState(page, { selectedId: '1-1' });
  // The keys labelled W and A on AZERTY are elsewhere: they do nothing.
  await pressPosition(page, 'KeyZ', 'w');
  await pressPosition(page, 'KeyQ', 'a');
  await step(page, 3);
  expect((await gameState(page)).selectedId).toBe('1-1');
});

test('P01-R09: holding Right moves once, then repeats after the repeat delay', async ({ page }) => {
  await openGame(page);
  await page.keyboard.press('Enter');
  await expectState(page, { screen: 'ship-select' });
  await page.keyboard.press('Enter');
  await expectState(page, { screen: 'level-select', selectedId: '1-1' });
  // Exact timings are unit-tested (keyboard-menu-input.test.ts).
  await page.keyboard.down('ArrowRight');
  await step(page);
  expect((await gameState(page)).selection).toBe(1);
  // Held for a second of game time, it repeats.
  await step(page, 60);
  expect((await gameState(page)).selection).toBeGreaterThanOrEqual(3);
  await page.keyboard.up('ArrowRight');
});

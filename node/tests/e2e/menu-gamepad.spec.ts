import type { Page } from '@playwright/test';
import { test, expect } from './fixtures';
import { expectState, gameState, openGame, step, type TestState } from './menu-helpers';

interface FakePadWindow {
  __pad: { buttons: { pressed: boolean }[]; axes: number[] };
}

/** Replaces the Gamepad API with one fake standard gamepad the test controls. */
test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    // Babylon's gamepad manager reads the same API, so the fake has the standard fields.
    const pad = {
      id: 'Fake gamepad (STANDARD GAMEPAD)',
      index: 0,
      connected: true,
      mapping: 'standard',
      timestamp: 0,
      buttons: Array.from({ length: 17 }, () => ({ pressed: false, touched: false, value: 0 })),
      axes: [0, 0, 0, 0],
    };
    (window as unknown as FakePadWindow).__pad = pad;
    navigator.getGamepads = () => [pad as unknown as Gamepad];
  });
});

function setPad(page: Page, change: { button?: [number, boolean]; axes?: number[] }) {
  return page.evaluate((c) => {
    const pad = (window as unknown as FakePadWindow).__pad;
    if (c.button) {
      const button = pad.buttons[c.button[0]];
      if (button) button.pressed = c.button[1];
    }
    if (c.axes) pad.axes = c.axes;
  }, change);
}

/** Holds a button until the game reaches `expected`, then releases it. */
async function pressButton(page: Page, index: number, expected: Partial<TestState>) {
  await setPad(page, { button: [index, true] });
  await expectState(page, expected);
  await setPad(page, { button: [index, false] });
  await step(page);
}

/** Tilts the left stick until the game reaches `expected` (or for 5 frames), then centres it. */
async function tiltStick(page: Page, x: number, y: number, expected?: Partial<TestState>) {
  await setPad(page, { axes: [x, y, 0, 0] });
  if (expected) await expectState(page, expected);
  else await step(page, 5);
  await setPad(page, { axes: [0, 0, 0, 0] });
  await step(page);
}

const A = 0;
const B = 1;
const SELECT = 8;
const START = 9;
const DPAD_DOWN = 13;
const DPAD_RIGHT = 15;

test('P01-R10: the whole flow with the gamepad only (stick, D-pad, A and B)', async ({ page }) => {
  await openGame(page);
  await pressButton(page, A, { screen: 'ship-select', selectedId: 'balanced' });
  await tiltStick(page, 0.2, 0); // inside the dead zone
  expect((await gameState(page)).selectedId).toBe('balanced');
  await tiltStick(page, 0.9, 0, { selectedId: 'heavy' });
  await pressButton(page, DPAD_RIGHT, { selectedId: 'light' });
  await pressButton(page, A, { screen: 'level-select', chosenShipId: 'light' });
  await pressButton(page, B, { screen: 'ship-select', selectedId: 'light' });
  await pressButton(page, A, { screen: 'level-select' });
  await pressButton(page, A, { screen: 'game', chosenLevelId: '1-1' });
  // P12-R01, P12-R02: B does nothing in a level; Start and Select pause; B resumes; the level is
  // left from the pause menu.
  await setPad(page, { button: [B, true] });
  await step(page, 3);
  await setPad(page, { button: [B, false] });
  await step(page);
  expect((await gameState(page)).screen).toBe('game');
  await pressButton(page, START, { screen: 'pause', paused: true });
  await pressButton(page, B, { screen: 'game', paused: false });
  await pressButton(page, SELECT, { screen: 'pause', selectedId: 'resume' });
  await pressButton(page, DPAD_DOWN, { selectedId: 'settings' });
  await pressButton(page, DPAD_DOWN, { selectedId: 'main-menu' });
  await pressButton(page, A, { leaving: true, choice: 0 });
  await pressButton(page, DPAD_RIGHT, { choice: 1 });
  await pressButton(page, A, { screen: 'title' });
});

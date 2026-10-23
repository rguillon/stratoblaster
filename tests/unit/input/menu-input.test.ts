import { describe, expect, it, vi } from 'vitest';
import { MenuInput } from '../../../src/input/menu-input';
import { KeyboardMenuInput } from '../../../src/input/keyboard-menu-input';
import { GamepadMenuInput } from '../../../src/input/gamepad-menu-input';
import { pointerCommand } from '../../../src/input/pointer-menu-input';
import { isMenuAction, isMenuDirection, MENU_ACTIONS } from '../../../src/input/menu-action';
import { MENU_INPUT_CONFIG } from '../../../src/config/menu-input';

const press = (code: string) => ({ code, repeat: false, preventDefault: vi.fn() });

describe('unified menu input', () => {
  it('P01-R12: Enter, Space, gamepad A and a tap on the selected entry all produce confirm', () => {
    const keyboard = new KeyboardMenuInput(MENU_INPUT_CONFIG.keyboard, MENU_INPUT_CONFIG);
    let aPressed = false;
    const gamepad = new GamepadMenuInput(
      () => [{ buttons: [{ pressed: aPressed }], axes: [] }],
      MENU_INPUT_CONFIG,
    );
    const input = new MenuInput([keyboard, gamepad]);
    keyboard.keyDown(press('Enter'));
    expect(input.update(0)).toEqual(['confirm']);
    keyboard.keyDown(press('Space'));
    expect(input.update(0)).toEqual(['confirm']);
    aPressed = true;
    expect(input.update(0)).toEqual(['confirm']);
    expect(pointerCommand(2, 2)).toBe('confirm');
  });

  it('P01-R11: a tap on another entry selects it', () => {
    expect(pointerCommand(1, 0)).toEqual({ select: 1 });
  });

  it('P01-R12: the six abstract actions', () => {
    expect(MENU_ACTIONS).toEqual(['up', 'down', 'left', 'right', 'confirm', 'back']);
    expect(MENU_ACTIONS.filter(isMenuDirection)).toEqual(['up', 'down', 'left', 'right']);
    expect(isMenuAction('confirm')).toBe(true);
    expect(isMenuAction('jump')).toBe(false);
    expect(isMenuAction(3)).toBe(false);
  });

  it('P01-R12: the key and button mapping lives in config', () => {
    expect(MENU_INPUT_CONFIG.keyboard.Enter).toBe('confirm');
    expect(MENU_INPUT_CONFIG.gamepadButtons[0]).toBe('confirm');
    expect(MENU_INPUT_CONFIG.gamepadButtons[1]).toBe('back');
    expect(MENU_INPUT_CONFIG.gamepadDeadZone).toBe(0.35);
    expect(MENU_INPUT_CONFIG.repeatDelaySeconds).toBe(0.35);
    expect(MENU_INPUT_CONFIG.repeatIntervalSeconds).toBe(0.12);
  });
});

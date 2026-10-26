import { describe, expect, it, vi } from 'vitest';
import { KeyboardMenuInput, type MenuKeyEvent } from '../../../src/input/keyboard-menu-input';
import { MENU_INPUT_CONFIG } from '../../../src/config/menu-input';

const key = (code: string, repeat = false): MenuKeyEvent => ({
  code,
  repeat,
  preventDefault: vi.fn(),
});

function keyboard(): KeyboardMenuInput {
  return new KeyboardMenuInput(MENU_INPUT_CONFIG.keyboard, MENU_INPUT_CONFIG);
}

describe('KeyboardMenuInput', () => {
  it('P01-R09, P12-R01: maps arrows, Enter/Space, Esc (cancel), Backspace (back) and P (pause)', () => {
    const input = keyboard();
    for (const code of ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight']) {
      input.keyDown(key(code));
      input.keyUp({ code });
    }
    for (const code of ['Enter', 'Space', 'Escape', 'Backspace', 'KeyP']) input.keyDown(key(code));
    expect(input.update(0)).toEqual([
      'up',
      'down',
      'left',
      'right',
      'confirm',
      'confirm',
      'cancel',
      'back',
      'pause',
    ]);
  });

  it('P01-R09: AZERTY Z/Q/S/D (the WASD positions) move the selection', () => {
    const input = keyboard();
    // On AZERTY, the keys labelled Z, Q, S, D sit at the KeyW, KeyA, KeyS, KeyD positions.
    for (const code of ['KeyW', 'KeyA', 'KeyS', 'KeyD']) {
      input.keyDown(key(code));
      input.keyUp({ code });
    }
    expect(input.update(0)).toEqual(['up', 'left', 'down', 'right']);
    input.keyDown(key('KeyZ')); // the AZERTY "W" key
    input.keyDown(key('KeyQ')); // the AZERTY "A" key
    expect(input.update(0)).toEqual([]);
  });

  it('P01-R09: holding Right moves once, then repeats after the repeat delay', () => {
    const input = keyboard();
    input.keyDown(key('ArrowRight'));
    expect(input.update(0.016)).toEqual(['right']);
    input.keyDown(key('ArrowRight', true)); // browser auto-repeat is ignored
    expect(input.update(0.3)).toEqual([]);
    expect(input.update(0.06)).toEqual(['right']);
    expect(input.update(0.12)).toEqual(['right']);
    input.keyUp({ code: 'ArrowRight' });
    expect(input.update(1)).toEqual([]);
  });

  it('keeps a quick tap that is released before the next frame', () => {
    const input = keyboard();
    input.keyDown(key('ArrowLeft'));
    input.keyUp({ code: 'ArrowLeft' });
    expect(input.update(0.016)).toEqual(['left']);
  });

  it('prevents the browser default for mapped keys only', () => {
    const input = keyboard();
    const spaceDefault = vi.fn();
    const tabDefault = vi.fn();
    input.keyDown({ code: 'Space', repeat: false, preventDefault: spaceDefault });
    input.keyDown({ code: 'Tab', repeat: false, preventDefault: tabDefault });
    expect(spaceDefault).toHaveBeenCalled();
    expect(tabDefault).not.toHaveBeenCalled();
  });

  it('listens to a target and forgets held keys when it loses focus', () => {
    const target = new EventTarget();
    const input = keyboard();
    const stop = input.listen(target);
    target.dispatchEvent(Object.assign(new Event('keydown'), { code: 'ArrowDown', repeat: false }));
    expect(input.update(0)).toEqual(['down']);
    target.dispatchEvent(new Event('blur'));
    expect(input.update(1)).toEqual([]);
    target.dispatchEvent(Object.assign(new Event('keydown'), { code: 'Enter', repeat: false }));
    target.dispatchEvent(Object.assign(new Event('keyup'), { code: 'Enter' }));
    expect(input.update(0)).toEqual(['confirm']);
    stop();
    target.dispatchEvent(Object.assign(new Event('keydown'), { code: 'Enter', repeat: false }));
    expect(input.update(0)).toEqual([]);
  });
});

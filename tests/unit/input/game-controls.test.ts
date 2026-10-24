import { describe, expect, it } from 'vitest';
import { GameControls } from '../../../src/input/game-controls';
import type { GamepadLike } from '../../../src/input/gamepad-menu-input';
import { GAME_CONTROLS_CONFIG } from '../../../src/config/game-controls';

function pad(buttons: number[] = [], axes: number[] = [0, 0]): GamepadLike {
  return {
    buttons: Array.from({ length: 16 }, (_, i) => ({ pressed: buttons.includes(i) })),
    axes,
  };
}

describe('GameControls', () => {
  it('P06-R02: arrows / WASD (by key position) move, Space shoots while held', () => {
    const controls = new GameControls(GAME_CONTROLS_CONFIG);
    expect(controls.key('KeyD', true)).toBe(true);
    expect(controls.key('ArrowUp', true)).toBe(true);
    expect(controls.key('Space', true)).toBe(true);
    expect(controls.key('KeyQ', true)).toBe(false);
    const state = controls.read(1 / 60, 100);
    expect(state.fire).toBe(true);
    expect(state.move.x).toBeCloseTo(Math.SQRT1_2);
    expect(state.move.y).toBeCloseTo(Math.SQRT1_2);
    controls.key('Space', false);
    expect(controls.read(1 / 60, 100).fire).toBe(false);
    controls.clear();
    expect(controls.read(1 / 60, 100).move).toEqual({ x: 0, y: 0 });
  });

  it('P06-R02: the left stick (Y up), the D-pad and the gamepad buttons fly and shoot', () => {
    let pads: (GamepadLike | null)[] = [null, pad([0], [0.5, -0.5])];
    const controls = new GameControls(GAME_CONTROLS_CONFIG, () => pads);
    let state = controls.read(1 / 60, 100);
    expect(state.fire).toBe(true);
    expect(state.move.x).toBeCloseTo(0.5);
    expect(state.move.y).toBeCloseTo(0.5);
    pads = [pad([7, 14], [0.1, 0.1])];
    state = controls.read(1 / 60, 100);
    expect(state).toEqual({ move: { x: -1, y: 0 }, fire: true });
    pads = [pad([], [1, -1])];
    state = controls.read(1 / 60, 100);
    expect(Math.hypot(state.move.x, state.move.y)).toBeCloseTo(1);
    expect(state.fire).toBe(false);
  });

  it('P06-R02: the stronger of the keys and the gamepad wins', () => {
    const controls = new GameControls(GAME_CONTROLS_CONFIG, () => [pad([], [0.3, 0])]);
    expect(controls.read(1 / 60, 100).move.x).toBeCloseTo(0.3);
    controls.key('ArrowLeft', true);
    expect(controls.read(1 / 60, 100).move.x).toBe(-1);
  });

  it('P06-R02: a touch drag flies the ship by the distance dragged, the button shoots', () => {
    const controls = new GameControls(GAME_CONTROLS_CONFIG);
    controls.drag(3, -4);
    controls.setTouchFire(true);
    // At 100 px/s, a 1/10 s step covers 10 px: the whole 5 px drag, at half speed.
    let state = controls.read(0.1, 100);
    expect(state.fire).toBe(true);
    expect(state.move.x).toBeCloseTo(0.3);
    expect(state.move.y).toBeCloseTo(-0.4);
    expect(controls.read(0.1, 100).move).toEqual({ x: 0, y: 0 });
    // A longer drag goes at full speed, over several steps.
    controls.drag(0, 25);
    state = controls.read(0.1, 100);
    expect(state.move).toEqual({ x: 0, y: 1 });
    expect(controls.read(0.1, 100).move).toEqual({ x: 0, y: 1 });
    expect(controls.read(0.1, 100).move.y).toBeCloseTo(0.5);
    controls.setTouchFire(false);
    expect(controls.read(0.1, 100).fire).toBe(false);
  });
});

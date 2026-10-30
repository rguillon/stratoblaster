import { describe, expect, it } from 'vitest';
import {
  browserGamepads,
  GamepadMenuInput,
  stickDirection,
  type GamepadLike,
} from '../../../src/input/gamepad-menu-input';
import { MENU_INPUT_CONFIG } from '../../../src/config/menu-input';

/** A fake standard-mapping gamepad, as `navigator.getGamepads()` would return it. */
function pad(pressed: number[] = [], axes: number[] = [0, 0]): GamepadLike {
  return {
    buttons: Array.from({ length: 17 }, (_, i) => ({ pressed: pressed.includes(i) })),
    axes,
  };
}

function setup(): { input: GamepadMenuInput; connect: (...pads: (GamepadLike | null)[]) => void } {
  let pads: (GamepadLike | null)[] = [];
  const input = new GamepadMenuInput(() => pads, MENU_INPUT_CONFIG);
  return {
    input,
    connect: (...next) => {
      pads = next;
    },
  };
}

describe('GamepadMenuInput', () => {
  it('P01-R10: A confirms, B goes back, the D-pad moves', () => {
    const { input, connect } = setup();
    connect(pad([0]));
    expect(input.update(0.016)).toEqual(['confirm']);
    connect(pad([1]));
    expect(input.update(0.016)).toEqual(['back']);
    for (const [button, action] of [
      [12, 'up'],
      [13, 'down'],
      [14, 'left'],
      [15, 'right'],
    ] as const) {
      connect(pad([button]));
      expect(input.update(0.016)).toEqual([action]);
      connect(pad());
      input.update(0.016);
    }
  });

  it('P01-R12: gamepad A produces confirm only once per press', () => {
    const { input, connect } = setup();
    connect(pad([0]));
    expect(input.update(0.016)).toEqual(['confirm']);
    expect(input.update(1)).toEqual([]);
    connect(pad());
    input.update(0.016);
    connect(pad([0]));
    expect(input.update(0.016)).toEqual(['confirm']);
  });

  it('P01-R10: the left stick moves the selection and repeats while held', () => {
    const { input, connect } = setup();
    connect(pad([], [0.9, 0.1]));
    expect(input.update(0.016)).toEqual(['right']);
    expect(input.update(0.3)).toEqual([]);
    expect(input.update(0.06)).toEqual(['right']);
    connect(pad([], [0, -0.8]));
    expect(input.update(0.016)).toEqual(['up']);
  });

  it('P01-R10: a stick tilt inside the dead zone does not move the selection', () => {
    const { input, connect } = setup();
    connect(pad([], [0.3, 0.1]));
    expect(input.update(0.016)).toEqual([]);
    expect(input.update(1)).toEqual([]);
  });

  it('merges several gamepads and skips empty slots', () => {
    const { input, connect } = setup();
    connect(null, pad([13]), pad([0]));
    expect(input.update(0.016).sort()).toEqual(['confirm', 'down']);
  });

  it('works with no gamepad API', () => {
    expect(browserGamepads({})()).toEqual([]);
    const gamepads = [pad()];
    expect(browserGamepads({ getGamepads: () => gamepads as unknown as Gamepad[] })()).toBe(
      gamepads,
    );
  });
});

describe('stickDirection', () => {
  it('picks the dominant axis outside the dead zone', () => {
    expect(stickDirection(0.5, 0.2, 0.35)).toBe('right');
    expect(stickDirection(-0.5, 0.2, 0.35)).toBe('left');
    expect(stickDirection(0.2, 0.5, 0.35)).toBe('down');
    expect(stickDirection(0.2, -0.5, 0.35)).toBe('up');
    expect(stickDirection(0.2, 0.2, 0.35)).toBeUndefined();
  });
});

import type { MenuAction } from '../input/menu-action';

/**
 * Menu input mapping and feel (P01-R09, P01-R10, P01-R12). Kept in config so it can be
 * remapped later (ENG-112).
 */
export const MENU_INPUT_CONFIG = {
  /** `KeyboardEvent.code` → action: physical key positions, so AZERTY works too. */
  keyboard: {
    ArrowUp: 'up',
    ArrowDown: 'down',
    ArrowLeft: 'left',
    ArrowRight: 'right',
    KeyW: 'up',
    KeyS: 'down',
    KeyA: 'left',
    KeyD: 'right',
    Enter: 'confirm',
    NumpadEnter: 'confirm',
    Space: 'confirm',
    Escape: 'back',
    Backspace: 'back',
  } satisfies Readonly<Record<string, MenuAction>>,
  /** Standard-mapping gamepad button index → action (A = 0, B = 1, D-pad = 12..15). */
  gamepadButtons: {
    0: 'confirm',
    1: 'back',
    12: 'up',
    13: 'down',
    14: 'left',
    15: 'right',
  } satisfies Readonly<Record<number, MenuAction>>,
  /** Left stick axes of the standard mapping (+X right, +Y down). */
  gamepadStick: { xAxis: 0, yAxis: 1 },
  /** `gamepad_dead_zone`: stick magnitude below which input is ignored. */
  gamepadDeadZone: 0.35,
  /** `menu_repeat_delay`: hold time before a held direction starts repeating. */
  repeatDelaySeconds: 0.35,
  /** `menu_repeat_interval`: time between repeats while held. */
  repeatIntervalSeconds: 0.12,
} as const;

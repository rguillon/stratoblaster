/**
 * In-game controls (GD §2, GD-10, P06-R02, P11-R06): which keys and gamepad buttons shoot and set
 * bombs off, and how the
 * left stick and the touch drag move the ship. Kept in config so they can be remapped later
 * (ENG-112). Moving uses the arrows / WASD by key position (`HeldDirections`).
 */
export const GAME_CONTROLS_CONFIG = {
  /** `KeyboardEvent.code` of the keys that shoot while held. */
  fireKeys: ['Space'],
  /** Keys that switch to the next weapon, once per press (phase 6 review: E, by position). */
  switchKeys: ['KeyE'],
  /**
   * Keys that set a bomb off, once per press (P11-R06): R and the left Shift, by position. E
   * switches the weapon (D-043).
   */
  bombKeys: ['KeyR', 'ShiftLeft'],
  /** Standard-mapping gamepad buttons that shoot while held: A, and the right trigger. */
  fireButtons: [0, 7],
  /** Gamepad buttons that set a bomb off, once per press (P11-R06): X / Square and LB. */
  bombButtons: [2, 4],
  /** D-pad buttons of the standard mapping: up, down, left, right. */
  dpad: { up: 12, down: 13, left: 14, right: 15 },
  /** Left stick axes (+X right, +Y down) and the tilt below which it is ignored. */
  stick: { xAxis: 0, yAxis: 1, deadZone: 0.2 },
  /**
   * Seconds from rest to full speed (GD-10: little acceleration, but felt: phase 6 review,
   * from 0.08 s).
   */
  accelerationSeconds: 0.18,
} as const;

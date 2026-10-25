import type { Muzzle } from './muzzle';

/**
 * A turret on a boss's piece (phase 7 review): its guns' muzzles turn with it around its pivot,
 * so that the barrels the player sees point the way it aims.
 */
export interface BossTurretSpec {
  /** Its pivot, from the boss's centre (X right, Y up), as the boss is drawn. */
  readonly x: number;
  readonly y: number;
  /** Degrees a second it turns at, at most. */
  readonly turnRateDeg: number;
}

/** A turret of a boss's piece, and how far it has turned (see {@link BossTurretSpec}). */
export class BossTurret {
  /** How far it has turned from its rest (barrels straight down): radians, clockwise on screen. */
  aim = 0;

  constructor(readonly spec: BossTurretSpec) {}

  /** `muzzle` (from the boss's centre, as drawn at rest) turned with it around its pivot. */
  turned([mx, my, mh]: Muzzle): Muzzle {
    const [c, s] = [Math.cos(this.aim), Math.sin(this.aim)];
    const [dx, dy] = [mx - this.spec.x, my - this.spec.y];
    return [this.spec.x + dx * c + dy * s, this.spec.y - dx * s + dy * c, mh];
  }
}

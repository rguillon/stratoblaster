/** Where the player ship may fly, in playfield logical pixels (X right, Y up). */
export interface FlightBounds {
  readonly minY: number;
  readonly maxY: number;
  /** X of the middle of the area the ship may fly in. */
  readonly centerX: number;
  /**
   * Half the width the ship may use at height `y` (with a tilted camera the screen shows less
   * of the playfield at the bottom than at the top).
   */
  halfWidthAt(y: number): number;
}

/** A direction to fly in, X right, Y up, of length 0..1 (0 = let go, 1 = full speed). */
export interface FlightInput {
  readonly x: number;
  readonly y: number;
}

/**
 * The player ship's movement (P06-R02, GD-10): its velocity eases towards the stick or keys at
 * a high acceleration, so it reaches its top speed after `accelerationSeconds`, and it stays
 * inside its {@link FlightBounds}. Pure and deterministic.
 */
export class PlayerFlight {
  x: number;
  y: number;
  vx = 0;
  vy = 0;

  constructor(
    start: { readonly x: number; readonly y: number },
    readonly maxSpeed: number,
    /** Seconds from rest to full speed (and from full speed to rest). */
    readonly accelerationSeconds: number,
  ) {
    if (!(maxSpeed > 0) || !(accelerationSeconds >= 0)) {
      throw new RangeError('A ship needs a positive speed and a non-negative acceleration time');
    }
    this.x = start.x;
    this.y = start.y;
  }

  /** Moves for `dt` seconds towards `input`, then keeps the ship inside `bounds`. */
  step(dt: number, input: FlightInput, bounds: FlightBounds): void {
    const length = Math.hypot(input.x, input.y);
    const scale = length > 1 ? 1 / length : 1;
    const [tx, ty] = [input.x * scale * this.maxSpeed, input.y * scale * this.maxSpeed];
    const change =
      this.accelerationSeconds > 0 ? (this.maxSpeed / this.accelerationSeconds) * dt : Infinity;
    const [dx, dy] = [tx - this.vx, ty - this.vy];
    const gap = Math.hypot(dx, dy);
    const k = gap > change ? change / gap : 1;
    this.vx += dx * k;
    this.vy += dy * k;
    this.x += this.vx * dt;
    this.y += this.vy * dt;
    this.#keepInside(bounds);
  }

  /** Puts the ship back inside `bounds`, stopping it against the edge it hit. */
  #keepInside(bounds: FlightBounds): void {
    const y = Math.min(bounds.maxY, Math.max(bounds.minY, this.y));
    if (y !== this.y) this.vy = 0;
    this.y = y;
    const half = Math.max(0, bounds.halfWidthAt(y));
    const x = Math.min(bounds.centerX + half, Math.max(bounds.centerX - half, this.x));
    if (x !== this.x) this.vx = 0;
    this.x = x;
  }
}

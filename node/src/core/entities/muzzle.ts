/**
 * Where enemy shots leave from (phase 7 review: from the barrels the player sees). A gun's
 * muzzle is a point of the enemy as it is drawn, above the playfield; the tilted camera sees it
 * in front of another point of the playfield, where its shots (flying on the playfield) start.
 */

/**
 * A muzzle: its offset from the enemy's centre as seen when the enemy faces down the screen
 * (X right, Y up, logical pixels), and its height above the playfield (towards the camera).
 */
export type Muzzle = readonly [x: number, y: number, height: number];

/** A point of the playfield (X right, Y up), and its height above it. */
export interface RaisedPoint {
  readonly x: number;
  readonly y: number;
  readonly height: number;
}

/** Where the camera's eye is: the playfield point under it, and its height above the playfield. */
export interface PlayfieldEye {
  readonly x: number;
  readonly y: number;
  readonly height: number;
}

/**
 * The point of the playfield the eye sees behind `point`: along the line from the eye through
 * it, down to the playfield. Straight below it without an eye (or when it is on the playfield).
 */
export function seenOnPlayfield(
  eye: PlayfieldEye | undefined,
  point: RaisedPoint,
): { x: number; y: number } {
  if (!eye || point.height === 0) return { x: point.x, y: point.y };
  const k = eye.height / Math.max(1, eye.height - point.height);
  return { x: eye.x + (point.x - eye.x) * k, y: eye.y + (point.y - eye.y) * k };
}

/** How a body is placed: its centre, the way its nose points, how far it is rolled. */
export interface MuzzleBody {
  readonly x: number;
  readonly y: number;
  readonly heading: number;
  /** Radians about its nose; positive dips its right side as seen when it faces down. */
  readonly roll?: number;
}

/**
 * Where `muzzle` is on the playfield, and how high, on `body`. `spin` (radians, clockwise on
 * screen) first turns it around the body's centre, as for a boss's orbiting parts.
 */
export function muzzlePoint(body: MuzzleBody, [mx, my, mh]: Muzzle, spin = 0): RaisedPoint {
  const [sc, ss] = [Math.cos(spin), Math.sin(spin)];
  const [x0, y0] = [mx * sc + my * ss, -mx * ss + my * sc];
  const roll = body.roll ?? 0;
  const [rc, rs] = [Math.cos(roll), Math.sin(roll)];
  const [x1, height] = [x0 * rc + mh * rs, mh * rc - x0 * rs];
  // Facing down (heading π) the offset is as given; otherwise it turns with the nose.
  const [hc, hs] = [Math.cos(body.heading), Math.sin(body.heading)];
  return { x: body.x - x1 * hc - y0 * hs, y: body.y + x1 * hs - y0 * hc, height };
}

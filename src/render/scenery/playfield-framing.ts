import type { LogicalScreen } from '../../core/content/game-definition';
import type { PlayfieldCameraLook } from './scenery-look';

const DEG = Math.PI / 180;

/**
 * Where the tilted camera stands relative to the playfield (P04-R05). The playfield is a
 * `screen`-sized rectangle on the flight plane: X across (centred on 0), Z along the level from
 * its bottom edge. The camera is tilted from straight down towards +Z, and placed so the bottom
 * and top edges of the screen pass through the bottom and top edges of the playfield.
 */
export interface PlayfieldFraming {
  readonly tilt: number;
  /** Half of the vertical field of view, in radians. */
  readonly halfFov: number;
  /** Camera height above the flight plane. */
  readonly height: number;
  /** Camera Z relative to the bottom edge of the playfield (negative: behind it). */
  readonly back: number;
  /** Unit view direction (Y, Z); X is always 0. */
  readonly direction: readonly [y: number, z: number];
}

/** Frames a `screen`-sized playfield with a camera tilted by `look.tiltDeg`. */
export function framePlayfield(screen: LogicalScreen, look: PlayfieldCameraLook): PlayfieldFraming {
  const tilt = look.tiltDeg * DEG;
  const halfFov = (look.fovDeg * DEG) / 2;
  if (!(halfFov > 0) || tilt + halfFov >= Math.PI / 2 || tilt - halfFov <= -Math.PI / 2) {
    throw new RangeError('The camera must see the whole playfield below the horizon');
  }
  const height = screen.height / (Math.tan(tilt + halfFov) - Math.tan(tilt - halfFov));
  return {
    tilt,
    halfFov,
    height,
    back: -height * Math.tan(tilt - halfFov),
    direction: [-Math.cos(tilt), Math.sin(tilt)],
  };
}

/** The ground the camera can see, relative to the camera's Z. */
export interface GroundWindow {
  readonly zNear: number;
  readonly zFar: number;
  /** Half of the widest stretch of ground seen across X. */
  readonly halfWidth: number;
}

/**
 * The ground the camera can see when the ground lies between heights `low` and `high`, for a
 * screen of the given aspect ratio (width / height), with the camera `cameraY` high.
 */
export function visibleGround(
  framing: PlayfieldFraming,
  aspect: number,
  cameraY: number,
  low: number,
  high: number,
): GroundWindow {
  const bottomRay = Math.tan(framing.tilt - framing.halfFov);
  const topRay = framing.tilt + framing.halfFov;
  const nearHeights = [cameraY - high, cameraY - low].map((h) => Math.max(0, h) * bottomRay);
  const deepest = Math.max(0, cameraY - low);
  // The far top corners: range along the top ray, then depth along the view axis.
  const depth = (deepest / Math.cos(topRay)) * Math.cos(framing.halfFov);
  return {
    zNear: Math.min(...nearHeights),
    zFar: deepest * Math.tan(topRay),
    halfWidth: depth * Math.tan(framing.halfFov) * aspect,
  };
}

/**
 * Half of the playfield width seen on screen at height `y` of the playfield (logical pixels
 * from its bottom edge), for a screen of the given aspect ratio (width / height). With the tilted
 * camera, less of the playfield is seen at the bottom than at the top.
 */
export function visibleHalfWidth(framing: PlayfieldFraming, aspect: number, y: number): number {
  const [dy, dz] = framing.direction;
  // Depth of the point (0, flight plane, y) along the view axis, from the camera.
  const depth = -framing.height * dy + (y - framing.back) * dz;
  return depth * Math.tan(framing.halfFov) * aspect;
}

/** Height on the playfield (from its bottom edge) seen in the middle of the screen. */
export function screenCentreY(framing: PlayfieldFraming): number {
  return framing.back + framing.height * Math.tan(framing.tilt);
}

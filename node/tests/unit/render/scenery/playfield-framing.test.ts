import { describe, expect, it } from 'vitest';
import {
  framePlayfield,
  visibleGround,
  visibleHalfWidth,
} from '../../../../src/render/scenery/playfield-framing';

const SCREEN = { width: 480, height: 640 };
const LOOK = { tiltDeg: 35, fovDeg: 40, flightAltitude: 320 };
const DEG = Math.PI / 180;

describe('framePlayfield', () => {
  it('P04-R05: tilts the camera 35° from straight down, looking forward', () => {
    const framing = framePlayfield(SCREEN, LOOK);
    expect(framing.tilt).toBeCloseTo(35 * DEG);
    const [dy, dz] = framing.direction;
    expect(Math.acos(-dy) / DEG).toBeCloseTo(35);
    expect(dz).toBeGreaterThan(0);
  });

  it('P04-R05: the bottom and top of the screen pass through the bottom and top of the playfield', () => {
    const { height, back, tilt, halfFov } = framePlayfield(SCREEN, LOOK);
    expect(height).toBeGreaterThan(0);
    expect(back).toBeLessThan(0);
    // Where the bottom and top screen rays meet the flight plane, from the camera's Z.
    const bottom = back + height * Math.tan(tilt - halfFov);
    const top = back + height * Math.tan(tilt + halfFov);
    expect(bottom).toBeCloseTo(0);
    expect(top).toBeCloseTo(SCREEN.height);
  });

  it('rejects a camera that would see the horizon or behind itself', () => {
    expect(() => framePlayfield(SCREEN, { ...LOOK, tiltDeg: 80 })).toThrow(RangeError);
    expect(() => framePlayfield(SCREEN, { ...LOOK, tiltDeg: -80 })).toThrow(RangeError);
    expect(() => framePlayfield(SCREEN, { ...LOOK, fovDeg: 0 })).toThrow(RangeError);
  });
});

describe('visibleGround', () => {
  it('sees further and wider on lower ground, and nearer on higher ground', () => {
    const framing = framePlayfield(SCREEN, LOOK);
    const cameraY = LOOK.flightAltitude + framing.height;
    const flat = visibleGround(framing, 0.75, cameraY, 0, 0);
    const hilly = visibleGround(framing, 0.75, cameraY, 0, 250);
    expect(flat.zFar).toBeGreaterThan(flat.zNear);
    expect(hilly.zNear).toBeLessThan(flat.zNear);
    expect(visibleGround(framing, 0.75, cameraY, -100, 0).zFar).toBeGreaterThan(flat.zFar);
    expect(flat.halfWidth).toBeGreaterThan(SCREEN.width / 2);
    expect(visibleGround(framing, 1.5, cameraY, 0, 0).halfWidth).toBeCloseTo(flat.halfWidth * 2);
  });
});

describe('visibleHalfWidth', () => {
  it('P05-R11: less of the playfield is seen across at the bottom than at the top', () => {
    const framing = framePlayfield(SCREEN, LOOK);
    const aspect = SCREEN.width / SCREEN.height;
    const bottom = visibleHalfWidth(framing, aspect, 0);
    const top = visibleHalfWidth(framing, aspect, SCREEN.height);
    // About 293 of the 480 logical pixels at the bottom edge and 493 at the top (D-020).
    expect(bottom * 2).toBeCloseTo(293, -1);
    expect(top * 2).toBeCloseTo(493, -1);
  });
});

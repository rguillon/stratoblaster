import { describe, expect, it } from 'vitest';
import { muzzlePoint, seenOnPlayfield } from '../../../../src/core/entities/muzzle';

const DEG = Math.PI / 180;

describe('Muzzles', () => {
  it('phase 7 review: facing down, a muzzle is at its offset; it turns with the nose', () => {
    const body = { x: 100, y: 200, heading: Math.PI };
    expect(muzzlePoint(body, [5, -10, 3])).toEqual({ x: 105, y: 190, height: 3 });
    // Facing right (east), its nose (-Y facing down) points to +X, its right side (-X) down.
    const east = muzzlePoint({ ...body, heading: Math.PI / 2 }, [5, -10, 3]);
    expect(east.x).toBeCloseTo(110);
    expect(east.y).toBeCloseTo(205);
  });

  it('phase 7 review: rolling dips the side on the right of the screen, and lifts the left', () => {
    const body = { x: 0, y: 0, heading: Math.PI, roll: 10 * DEG };
    const right = muzzlePoint(body, [20, 0, 0]);
    const left = muzzlePoint(body, [-20, 0, 0]);
    expect(right.height).toBeCloseTo(-20 * Math.sin(10 * DEG));
    expect(left.height).toBeCloseTo(20 * Math.sin(10 * DEG));
    // A muzzle on top leans towards the side that dips.
    expect(muzzlePoint(body, [0, 0, 10]).x).toBeGreaterThan(0);
  });

  it('phase 7 review: a spin turns the muzzle clockwise on screen around the centre', () => {
    const point = muzzlePoint({ x: 0, y: 0, heading: Math.PI }, [0, 10, 0], Math.PI / 2);
    expect(point.x).toBeCloseTo(10);
    expect(point.y).toBeCloseTo(0);
  });

  it('phase 7 review: a raised point is seen further from the eye, on its line of sight', () => {
    const eye = { x: 240, y: -150, height: 550 };
    expect(seenOnPlayfield(undefined, { x: 10, y: 20, height: 9 })).toEqual({ x: 10, y: 20 });
    expect(seenOnPlayfield(eye, { x: 10, y: 20, height: 0 })).toEqual({ x: 10, y: 20 });
    const seen = seenOnPlayfield(eye, { x: 340, y: 450, height: 55 });
    // The eye, the raised point and the point seen are on one line.
    const k = 550 / (550 - 55);
    expect(seen.x).toBeCloseTo(240 + 100 * k);
    expect(seen.y).toBeCloseTo(-150 + 600 * k);
    expect(seen.y - 450).toBeCloseTo(600 * (k - 1));
  });
});

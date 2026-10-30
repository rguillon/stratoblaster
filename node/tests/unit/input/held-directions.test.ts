import { describe, expect, it } from 'vitest';
import { HeldDirections } from '../../../src/input/held-directions';

describe('HeldDirections', () => {
  it('P05-R11: arrows and WASD (by key position) give the direction to fly in', () => {
    const held = new HeldDirections();
    expect(held.direction).toEqual({ x: 0, y: 0 });
    expect(held.key('ArrowLeft', true)).toBe(true);
    expect(held.direction).toEqual({ x: -1, y: 0 });
    held.key('KeyW', true);
    expect(held.direction.x).toBeCloseTo(-Math.SQRT1_2);
    expect(held.direction.y).toBeCloseTo(Math.SQRT1_2);
    held.key('ArrowLeft', false);
    expect(held.direction).toEqual({ x: 0, y: 1 });
  });

  it('ignores other keys, cancels opposite keys, and forgets keys on clear', () => {
    const held = new HeldDirections();
    expect(held.key('KeyX', true)).toBe(false);
    held.key('KeyA', true);
    held.key('KeyD', true);
    expect(held.direction).toEqual({ x: 0, y: 0 });
    held.key('KeyS', true);
    expect(held.direction).toEqual({ x: 0, y: -1 });
    held.clear();
    expect(held.direction).toEqual({ x: 0, y: 0 });
  });
});

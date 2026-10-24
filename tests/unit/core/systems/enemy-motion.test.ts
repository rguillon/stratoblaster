import { describe, expect, it } from 'vitest';
import { approach, fanHeadings, Path } from '../../../../src/core/systems/enemy-motion';

describe('Path', () => {
  it('GD-45: starts and ends on its first and last control points', () => {
    const path = new Path([
      [0, 100],
      [50, 50],
      [0, 0],
    ]);
    expect(path.at(0)).toMatchObject({ x: 0, y: 100 });
    expect(path.at(path.length).x).toBeCloseTo(0);
    expect(path.at(path.length).y).toBeCloseTo(0);
    expect(path.at(-10)).toEqual(path.at(0));
    expect(path.at(path.length + 10)).toEqual(path.at(path.length));
  });

  it('GD-45: is measured by distance travelled, so a constant speed stays constant', () => {
    const line = new Path([
      [0, 0],
      [0, 100],
    ]);
    expect(line.length).toBeCloseTo(100);
    expect(line.at(25).y).toBeCloseTo(25);
    expect(line.at(25).heading).toBeCloseTo(0);
    const curve = new Path([
      [0, 0],
      [100, 100],
      [200, 0],
    ]);
    const a = curve.at(10);
    const b = curve.at(20);
    expect(Math.hypot(b.x - a.x, b.y - a.y)).toBeCloseTo(10, 0);
  });

  it('GD-45: gives the direction of travel (radians from +Y, positive to the right)', () => {
    const down = new Path([
      [0, 100],
      [0, 0],
    ]);
    expect(Math.abs(down.at(50).heading)).toBeCloseTo(Math.PI);
    const right = new Path([
      [0, 0],
      [100, 0],
    ]);
    expect(right.at(50).heading).toBeCloseTo(Math.PI / 2);
  });

  it('needs two points', () => {
    expect(() => new Path([[0, 0]])).toThrow(/2 points/);
  });
});

describe('fanHeadings', () => {
  it('P05-R04: spreads headings evenly around a centre', () => {
    const [a, b, c] = fanHeadings(Math.PI, 3, 0.25);
    expect(a).toBeCloseTo(Math.PI - 0.25);
    expect(b).toBeCloseTo(Math.PI);
    expect(c).toBeCloseTo(Math.PI + 0.25);
    expect(fanHeadings(1, 1, 5)).toEqual([1]);
  });
});

describe('approach', () => {
  it('moves towards a target without passing it', () => {
    expect(approach(0, 10, 3)).toBe(3);
    expect(approach(10, 0, 3)).toBe(7);
    expect(approach(9, 10, 3)).toBe(10);
  });
});

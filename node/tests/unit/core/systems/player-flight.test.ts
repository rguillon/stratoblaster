import { describe, expect, it } from 'vitest';
import { PlayerFlight, type FlightBounds } from '../../../../src/core/systems/player-flight';

/** A playfield 480 wide whose usable half width grows from 100 at the bottom to 200 at Y = 400. */
const BOUNDS: FlightBounds = {
  minY: 30,
  maxY: 400,
  centerX: 240,
  halfWidthAt: (y) => 100 + y / 4,
};

const fly = (ship: PlayerFlight, seconds: number, input: { x: number; y: number }) => {
  for (let t = 0; t < seconds - 1e-9; t += 1 / 60) ship.step(1 / 60, input, BOUNDS);
};

describe('PlayerFlight', () => {
  it('GD-10: reaches its top speed quickly, after the acceleration time', () => {
    const ship = new PlayerFlight({ x: 240, y: 100 }, 120, 0.1);
    ship.step(1 / 60, { x: 0, y: 1 }, BOUNDS);
    expect(ship.vy).toBeCloseTo(20);
    fly(ship, 0.1, { x: 0, y: 1 });
    expect(ship.vy).toBeCloseTo(120);
    fly(ship, 0.5, { x: 0, y: 1 });
    expect(ship.vy).toBeCloseTo(120);
    fly(ship, 0.1, { x: 0, y: 0 });
    expect(ship.vy).toBeCloseTo(0);
  });

  it('P06-R02: diagonals are no faster than straight lines', () => {
    const ship = new PlayerFlight({ x: 240, y: 100 }, 100, 0);
    ship.step(0.1, { x: 1, y: 1 }, BOUNDS);
    expect(Math.hypot(ship.vx, ship.vy)).toBeCloseTo(100);
  });

  it('P06-R02: pushed against an edge of the playfield, the ship stays inside', () => {
    const ship = new PlayerFlight({ x: 240, y: 100 }, 200, 0);
    fly(ship, 5, { x: -1, y: -1 });
    expect(ship.y).toBe(30);
    expect(ship.x).toBeCloseTo(240 - (100 + 30 / 4));
    expect([ship.vx, ship.vy]).toEqual([0, 0]);
    fly(ship, 5, { x: 1, y: 1 });
    expect(ship.y).toBe(400);
    expect(ship.x).toBeCloseTo(240 + 200);
  });

  it('rejects a ship that cannot move', () => {
    expect(() => new PlayerFlight({ x: 0, y: 0 }, 0, 0.1)).toThrow(RangeError);
    expect(() => new PlayerFlight({ x: 0, y: 0 }, 10, -1)).toThrow(RangeError);
  });
});

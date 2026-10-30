import { describe, expect, it } from 'vitest';
import { ShipJourney, type JourneyRules } from '../../../../src/core/systems/ship-journey';
import type { FlightBounds } from '../../../../src/core/systems/player-flight';

const RULES: JourneyRules = {
  arriveSeconds: 1,
  below: 100,
  freeSeconds: 2,
  leaveSpeed: 100,
  leaveAcceleration: 500,
  above: 50,
};
const BOUNDS: FlightBounds = { minY: 50, maxY: 500, centerX: 200, halfWidthAt: () => 180 };
const START = { x: 200, y: 80 };
const ship = (): { x: number; y: number; vx: number; vy: number } => ({ x: 0, y: 0, vx: 0, vy: 0 });

function run(j: ShipJourney, s: ReturnType<typeof ship>, seconds: number, ready = true): void {
  for (let t = 0; t < seconds; t += 1 / 60) j.step(1 / 60, s, BOUNDS, ready);
}

describe('ShipJourney (reviewer 2026-10-28: arrival and departure)', () => {
  it('rises from below the screen to its start, then the player flies it', () => {
    const j = new ShipJourney(RULES, START, 600);
    const s = ship();
    j.step(0, s, BOUNDS, false);
    expect(s.y).toBe(BOUNDS.minY - RULES.below);
    expect(j.scripted).toBe(true);
    run(j, s, 1.05);
    expect([j.stage, s.x, s.y]).toEqual(['flying', 200, 80]);
    expect(j.scripted).toBe(false);
  });

  it('a seek puts it at its start at once', () => {
    const j = new ShipJourney(RULES, START, 600);
    const s = ship();
    j.skipArrival(s);
    expect([j.stage, s.y]).toEqual(['flying', 80]);
  });

  it('once cleared, the player keeps it a while, then it flies off the top', () => {
    const j = new ShipJourney(RULES, START, 600);
    const s = ship();
    j.skipArrival(s);
    j.clear();
    run(j, s, 1.9);
    expect([j.stage, j.scripted]).toEqual(['free', false]);
    run(j, s, 0.2);
    expect(j.stage).toBe('leaving');
    run(j, s, 3);
    expect(j.stage).toBe('gone');
    expect(s.y).toBeGreaterThanOrEqual(650);
  });

  it('waits for the level to be ready before leaving', () => {
    const j = new ShipJourney(RULES, START, 600);
    const s = ship();
    j.skipArrival(s);
    j.clear();
    run(j, s, 5, false);
    expect(j.stage).toBe('free');
  });
});

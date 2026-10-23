import { describe, expect, it } from 'vitest';
import {
  advanceProjectile,
  headingTo,
  turnTowards,
  wrapAngle,
  type Projectile,
} from '../../../../src/core/systems/projectile-motion';
import type { ShotTarget } from '../../../../src/core/entities/shot-target';
import { testGun } from '../../../helpers/test-weapons';

const DEG = Math.PI / 180;

function shot(overrides: Partial<Projectile> = {}): Projectile {
  return {
    alive: true,
    weapon: testGun(),
    x: 0,
    y: 0,
    heading: 0,
    speed: 100,
    age: 0,
    ...overrides,
  };
}

describe('angles', () => {
  it('wraps into (-π, π]', () => {
    expect(wrapAngle(3 * Math.PI)).toBeCloseTo(Math.PI);
    expect(wrapAngle(-Math.PI)).toBeCloseTo(Math.PI);
    expect(wrapAngle(-Math.PI / 2)).toBeCloseTo(-Math.PI / 2);
  });

  it('measures headings from +Y, positive to the right', () => {
    expect(headingTo(0, 0, 0, 10)).toBeCloseTo(0);
    expect(headingTo(0, 0, 10, 0)).toBeCloseTo(Math.PI / 2);
    expect(headingTo(0, 0, -10, 0)).toBeCloseTo(-Math.PI / 2);
  });

  it('turns by at most the given step, the short way round', () => {
    expect(turnTowards(0, 1, 0.25)).toBeCloseTo(0.25);
    expect(turnTowards(0, 0.1, 0.25)).toBeCloseTo(0.1);
    expect(turnTowards(3, -3, 0.1)).toBeCloseTo(3.1);
  });
});

describe('advanceProjectile', () => {
  it('P03-R01: moves at constant velocity along its heading', () => {
    const s = shot({ heading: 10 * DEG });
    advanceProjectile(s, [], 0.5);
    expect(s.x).toBeCloseTo(Math.sin(10 * DEG) * 50);
    expect(s.y).toBeCloseTo(Math.cos(10 * DEG) * 50);
    expect(s.speed).toBe(100);
    expect(s.age).toBe(0.5);
  });

  it('P03-R03: accelerates at a constant rate up to the speed cap', () => {
    const weapon = testGun({ acceleration: 200, maxSpeed: 250 });
    const s = shot({ weapon, speed: 100 });
    advanceProjectile(s, [], 0.5);
    expect(s.speed).toBe(200);
    advanceProjectile(s, [], 0.5);
    expect(s.speed).toBe(250);
  });

  it('P03-R03: turns towards the closest living target at the homing rate', () => {
    const weapon = testGun({ homingTurnRateDeg: 90 });
    const right: ShotTarget = { id: 1, x: 100, y: 0, radius: 5, health: 1, maxHealth: 1 };
    const deadLeft: ShotTarget = { id: 2, x: -1, y: 0, radius: 5, health: 0, maxHealth: 1 };
    const s = shot({ weapon });
    advanceProjectile(s, [right, deadLeft], 0.5);
    expect(s.heading).toBeCloseTo(45 * DEG);
  });

  it('P03-R03: flies straight when there is no target', () => {
    const s = shot({ weapon: testGun({ homingTurnRateDeg: 90 }), heading: 0.2 });
    advanceProjectile(s, [], 1);
    expect(s.heading).toBe(0.2);
  });
});

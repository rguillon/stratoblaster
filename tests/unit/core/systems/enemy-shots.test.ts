import { describe, expect, it } from 'vitest';
import { seenOnPlayfield } from '../../../../src/core/entities/muzzle';
import { EnemyShots, rayToEdge } from '../../../../src/core/systems/enemy-shots';
import { Dropper } from '../../../fixtures/sample-enemies';

const OPTIONS = { width: 480, height: 640, cullMargin: 20 };
const BULLET = { speed: 100, radius: 3, style: 'red' };
const MISSILE = {
  speed: 100,
  turnRateDeg: 90,
  homingSeconds: 1,
  radius: 4,
  health: 10,
  style: 'r',
};
const LASER = { warningSeconds: 1, firingSeconds: 1.5, width: 8, style: 'l' };

describe('EnemyShots bullets', () => {
  it('GD-43: fly straight at constant speed, and are removed past the edge', () => {
    const shots = new EnemyShots(OPTIONS);
    shots.fireBullet(240, 320, Math.PI, BULLET);
    shots.step(1, 0, 0);
    const [bullet] = shots.bullets;
    expect(bullet?.x).toBeCloseTo(240);
    expect(bullet?.y).toBeCloseTo(220);
    expect(bullet?.style).toBe('red');
    expect(shots.count).toBe(1);
    shots.step(3, 0, 0);
    expect(bullet?.alive).toBe(false);
    expect(shots.count).toBe(0);
  });

  it('ENG-19: reuses free bullets', () => {
    const shots = new EnemyShots(OPTIONS);
    shots.fireBullet(0, 0, 0, BULLET);
    shots.clear();
    shots.fireBullet(5, 5, 0, BULLET);
    expect(shots.bullets).toHaveLength(1);
    expect(shots.bullets[0]).toMatchObject({ alive: true, x: 5 });
  });
});

describe('EnemyShots missiles', () => {
  it('P05-R08: turn towards the player no faster than their turn rate', () => {
    const shots = new EnemyShots(OPTIONS);
    shots.fireMissile(100, 500, Math.PI, MISSILE);
    // The player is straight to the right: the missile needs a 90° turn.
    shots.step(0.5, 400, 500);
    const [missile] = shots.missiles;
    expect(missile?.heading).toBeCloseTo(Math.PI - Math.PI / 4);
  });

  it('P05-R08: fly straight on once their homing time is over', () => {
    const shots = new EnemyShots(OPTIONS);
    shots.fireMissile(240, 600, Math.PI, MISSILE);
    for (let i = 0; i < 60; i++) shots.step(1 / 60, 240, 0);
    const heading = shots.missiles[0]?.heading;
    shots.step(0.5, 0, 600);
    expect(shots.missiles[0]?.heading).toBe(heading);
  });

  it('GD-43, P05-R08: are targets with health, and are removed once shot down', () => {
    const shots = new EnemyShots(OPTIONS);
    shots.fireMissile(240, 300, Math.PI, MISSILE);
    const [missile] = shots.missiles;
    expect(missile).toMatchObject({ health: 10, maxHealth: 10, radius: 4 });
    if (missile) missile.health = 0;
    shots.step(1 / 60, 0, 0);
    expect(missile?.alive).toBe(false);
  });

  it('gives each missile its own id', () => {
    const shots = new EnemyShots(OPTIONS);
    shots.fireMissile(0, 0, 0, MISSILE);
    shots.fireMissile(0, 0, 0, MISSILE);
    expect(shots.missiles[0]?.id).not.toBe(shots.missiles[1]?.id);
  });
});

describe('EnemyShots lasers', () => {
  it('GD-43, P05-R07: show a warning line for 1 s, then fire for 1.5 s on the same line', () => {
    const shots = new EnemyShots(OPTIONS);
    const owner = new Dropper(100, 500);
    shots.fireLaser(owner, LASER);
    expect(shots.lasers[0]).toMatchObject({ phase: 'warning', x: 100, y: 490, heading: Math.PI });
    expect(shots.lasers[0]?.length).toBeCloseTo(510);
    shots.step(0.99, 0, 0);
    expect(shots.lasers[0]?.phase).toBe('warning');
    shots.step(0.02, 0, 0);
    expect(shots.lasers[0]).toMatchObject({ phase: 'firing', x: 100, y: 490 });
    shots.step(1.5, 0, 0);
    expect(shots.lasers).toHaveLength(0);
  });

  it('phase 7 review: leave from where the camera sees a raised emitter', () => {
    const eye = { x: 240, y: -150, height: 550 };
    const shots = new EnemyShots({ ...OPTIONS, eye });
    const emitter = { x: 100, y: 480, height: 12 };
    shots.fireLaser({ emitter, heading: Math.PI, gone: false, health: 1 }, LASER);
    expect(shots.lasers[0]).toMatchObject(seenOnPlayfield(eye, emitter));
    expect(shots.lasers[0]?.y).toBeGreaterThan(480);
  });

  it('end when their owner is destroyed or gone', () => {
    const shots = new EnemyShots(OPTIONS);
    const owner = new Dropper(100, 500);
    shots.fireLaser(owner, LASER);
    owner.health = 0;
    shots.step(0.1, 0, 0);
    expect(shots.lasers).toHaveLength(0);
    expect(shots.count).toBe(0);
  });
});

describe('rayToEdge', () => {
  it('measures a ray to the edge of the playfield grown by a margin', () => {
    const box = { width: 100, height: 200 };
    expect(rayToEdge(50, 150, Math.PI, box, 10)).toBeCloseTo(160);
    expect(rayToEdge(50, 150, 0, box, 0)).toBeCloseTo(50);
    expect(rayToEdge(50, 150, Math.PI / 2, box, 0)).toBeCloseTo(50);
    expect(rayToEdge(50, 150, -Math.PI / 2, box, 0)).toBeCloseTo(50);
    expect(rayToEdge(500, 150, Math.PI / 2, box, 0)).toBe(0);
  });
});

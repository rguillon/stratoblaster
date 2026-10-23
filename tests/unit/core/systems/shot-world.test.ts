import { describe, expect, it } from 'vitest';
import { ShotWorld } from '../../../../src/core/systems/shot-world';
import type { ShotTarget } from '../../../../src/core/entities/shot-target';
import type { WeaponDefinition } from '../../../../src/core/entities/weapon';
import { testBeam, testGun } from '../../../helpers/test-weapons';

const OPTIONS = { width: 100, height: 200, cullMargin: 10 };

function target(id: number, x: number, y: number, health = 100): ShotTarget {
  return { id, x, y, radius: 5, health, maxHealth: health };
}

function world(weapon: WeaponDefinition = testGun(), level = 1): ShotWorld {
  const w = new ShotWorld(OPTIONS, weapon);
  w.select(weapon, level);
  w.muzzleX = 50;
  w.muzzleY = 10;
  return w;
}

describe('ShotWorld', () => {
  it('P03-R01: fires one volley per 1/shotsPerSecond, starting at once', () => {
    const w = world();
    w.step(0.05);
    expect(w.activeCount).toBe(1);
    w.step(0.04);
    expect(w.activeCount).toBe(1);
    w.step(0.02);
    expect(w.activeCount).toBe(2);
  });

  it('P03-R01: fires every stream of the level, from its offset', () => {
    const w = world(testGun(), 2);
    w.step(0.01);
    const xs = w.projectiles.filter((p) => p.alive).map((p) => p.x);
    expect(xs.sort((a, b) => a - b)).toEqual([46, 54]);
  });

  it('launches from the ship centre when the weapon says so, from the muzzle otherwise', () => {
    const w = world(testGun({ launchPoint: 'center' }), 2);
    w.centerX = 40;
    w.centerY = 2;
    w.step(0);
    const shots = w.projectiles.filter((p) => p.alive);
    expect(shots.map((p) => [p.x, p.y])).toEqual([
      [36, 2],
      [44, 2],
    ]);
    w.select(testGun(), 1);
    w.step(0);
    expect(w.projectiles.filter((p) => p.alive).map((p) => p.y)).toContain(10);
  });

  it('moves a new shot by the time since it was fired within the step', () => {
    const w = world();
    w.step(0.05);
    // Fired at the start of the step: 0.05 s at 100 px/s.
    expect(w.projectiles[0]?.y).toBeCloseTo(15);
  });

  it('clamps the level to the weapon levels', () => {
    const w = world();
    w.select(testGun(), 9);
    expect(w.level).toBe(2);
    w.select(testGun(), 0);
    expect(w.level).toBe(1);
  });

  it('P03-R01: a direct hit removes the shot and deals the weapon damage', () => {
    const w = world();
    const t = target(1, 50, 20);
    w.targets = [t];
    // The shot touches the target 3-4 px after leaving the muzzle; no second volley yet.
    for (let i = 0; i < 4; i++) w.step(0.01);
    expect(t.health).toBe(95);
    expect(w.totalDamage).toBe(5);
    expect(w.activeCount).toBe(0);
  });

  it('P03-R03: an impact damages every target within the blast radius', () => {
    const w = world(testGun({ blastRadius: 10, damage: 8 }));
    const hit = target(1, 50, 20);
    const near = target(2, 62, 20);
    const far = target(3, 80, 20);
    w.targets = [hit, near, far];
    let impacts = 0;
    for (let i = 0; i < 5; i++) {
      w.step(0.01);
      impacts += w.impacts.length;
    }
    expect(impacts).toBe(1);
    expect([hit.health, near.health, far.health]).toEqual([92, 92, 100]);
    expect(w.impacts).toEqual([]);
  });

  it('reports each impact with the weapon id and blast radius', () => {
    const w = world(testGun({ blastRadius: 10 }));
    w.targets = [target(1, 50, 16)];
    w.step(0.05);
    expect(w.impacts).toHaveLength(1);
    expect(w.impacts[0]).toMatchObject({ weaponId: 'gun', blastRadius: 10 });
  });

  it('removes shots that leave the playfield and reuses them', () => {
    const w = world();
    w.step(0.05);
    for (let i = 0; i < 25; i++) w.step(0.1);
    // 26 volleys were fired, but a shot leaves the playfield after about 2 s and its slot is
    // reused.
    expect(w.activeCount).toBeLessThanOrEqual(22);
    expect(w.projectiles.length).toBeLessThanOrEqual(22);
  });

  it('P03-R02: a beam damages what it touches by damage per second times dt', () => {
    const w = world(testBeam(), 2);
    const a = target(1, 50, 50);
    const b = target(2, 50, 100);
    w.targets = [a, b];
    w.step(0.5);
    // Level 2 touches a (20/s), then continues at level 1 to b (10/s).
    expect(a.health).toBe(90);
    expect(b.health).toBe(95);
    expect(w.totalDamage).toBe(15);
    expect(w.beam.map((s) => s.level)).toEqual([2, 1]);
    expect(w.activeCount).toBe(0);
  });

  it('keeps shots in flight when switching to a beam, and clears the beam when switching back', () => {
    const w = world();
    w.step(0.01);
    w.select(testBeam(), 1);
    w.step(0.01);
    expect(w.activeCount).toBe(1);
    expect(w.beam).toHaveLength(1);
    w.select(testGun(), 1);
    w.step(0.01);
    expect(w.beam).toEqual([]);
    expect(w.weapon.id).toBe('gun');
  });
});

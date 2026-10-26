import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { BOMB_LOOK } from '../../../../../src/game/config/bomb-look';
import {
  createBombRenderer,
  flashStrength,
  waveReach,
} from '../../../../../src/game/view/bombs/bomb-renderer';

function mesh(scene: Scene, name: string) {
  const found = scene.meshes.find((m) => m.name === name);
  if (!found) throw new Error(`no ${name}`);
  return found;
}

describe('bomb renderer (P11-R05)', () => {
  it('P11-R05: the shockwave grows fast then slows; the flash fades within its time', () => {
    expect([waveReach(-1), waveReach(0), waveReach(1), waveReach(2)]).toEqual([0, 0, 1, 1]);
    expect(waveReach(0.5)).toBeCloseTo(0.75);
    expect(flashStrength(0)).toBe(1);
    expect(flashStrength(BOMB_LOOK.flash.seconds / 2)).toBeCloseTo(0.5);
    expect(flashStrength(BOMB_LOOK.flash.seconds)).toBe(0);
    // One flash per bomb, a bomb at most once a second: under 3 flashes a second.
    expect(BOMB_LOOK.flash.seconds).toBeLessThan(1 / 3);
  });

  it('P11-R05: draws a ring growing from the bomb over the playfield, and a flash at its start', () => {
    const scene = new Scene(new NullEngine());
    const renderer = createBombRenderer(scene);
    const ring = mesh(scene, 'bomb-wave');
    const glow = mesh(scene, 'bomb-flash');
    renderer.sync({ bomb: undefined, dtSeconds: 0.1 });
    expect([ring.isEnabled(), glow.isEnabled()]).toEqual([false, false]);
    renderer.sync({ bomb: { x: 100, y: 50, age: 0.1, seconds: 1 }, dtSeconds: 0.1 });
    expect([ring.isEnabled(), glow.isEnabled()]).toEqual([true, true]);
    expect(ring.position.x).toBe(100);
    expect(ring.position.y).toBe(50);
    const early = ring.scaling.x;
    renderer.sync({ bomb: { x: 100, y: 50, age: 0.9, seconds: 1 }, dtSeconds: 0.1 });
    expect(ring.scaling.x).toBeGreaterThan(early);
    expect(ring.scaling.x).toBeGreaterThan(640);
    expect(glow.isEnabled()).toBe(false);
    renderer.sync({ bomb: undefined, dtSeconds: 0.1 });
    expect(ring.isEnabled()).toBe(false);
    renderer.dispose();
    expect(scene.meshes.filter((m) => m.name.startsWith('bomb-'))).toHaveLength(0);
  });
});

import { describe, expect, it } from 'vitest';
import { DummyTargets } from '../../../src/app/dummy-targets';

const OPTIONS = {
  radius: 10,
  maxHealth: 50,
  anchors: [
    { x: 100, y: 200 },
    { x: 300, y: 200 },
  ],
  swayAmplitude: 20,
  swayHz: 0.25,
  respawnSeconds: 1,
};

describe('DummyTargets', () => {
  it('P03-R10: places full-health targets on their anchors and sways them together', () => {
    const d = new DummyTargets(OPTIONS);
    expect(d.targets.map((t) => [t.id, t.x, t.y, t.health])).toEqual([
      [0, 100, 200, 50],
      [1, 300, 200, 50],
    ]);
    d.update(1);
    // A quarter period at 0.25 Hz: the full amplitude to the right.
    expect(d.targets.map((t) => t.x)).toEqual([120, 320]);
  });

  it('P03-R10: counts a destroyed target once and brings it back after the respawn delay', () => {
    const d = new DummyTargets(OPTIONS);
    const [first] = d.targets;
    if (!first) throw new Error('no target');
    first.health = 0;
    d.update(0.5);
    d.update(0.4);
    expect(d.kills).toBe(1);
    expect(first.health).toBe(0);
    d.update(0.2);
    expect(first.health).toBe(50);
  });

  it('removes all targets when disabled and restores them when enabled', () => {
    const d = new DummyTargets(OPTIONS);
    d.setEnabled(false);
    d.update(5);
    expect(d.enabled).toBe(false);
    expect(d.targets.every((t) => t.health === 0)).toBe(true);
    expect(d.kills).toBe(0);
    d.setEnabled(true);
    expect(d.targets.every((t) => t.health === 50)).toBe(true);
  });
});

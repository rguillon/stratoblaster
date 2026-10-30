import { describe, expect, it } from 'vitest';
import { createRng } from '../../../../src/core/math/rng';
import { BuildingIndex, overlap } from '../../../../src/core/scenery/ground-boxes';

describe('BuildingIndex (reviewer, 2026-10-28)', () => {
  it('tells a box clear exactly when no building around it comes closer than the gap', () => {
    const random = createRng(11);
    const box = (x: number, z: number, half: number) => ({
      placement: { kind: 'b', x, y: 0, z, rotation: 0, scale: 1 },
      halfX: half,
      halfZ: half * (0.5 + random()),
    });
    const index = new BuildingIndex();
    const placed = Array.from({ length: 300 }, () =>
      box(random() * 600 - 300, random() * 600, 2 + random() * (random() < 0.1 ? 40 : 10)),
    );
    for (const b of placed) index.add(b);
    let blocked = 0;
    for (let i = 0; i < 2000; i++) {
      const area = box(random() * 600 - 300, random() * 600, 1 + random() * 12);
      const gap = random() * 4;
      // Within two buckets around it, as before: what every building check looks at.
      const near = placed.filter(
        (b) =>
          Math.abs(Math.floor(b.placement.x / 32) - Math.floor(area.placement.x / 32)) <= 2 &&
          Math.abs(Math.floor(b.placement.z / 32) - Math.floor(area.placement.z / 32)) <= 2,
      );
      const clear = !near.some((b) => overlap(b, area, gap));
      if (!clear) blocked++;
      expect(index.clear(area, gap)).toBe(clear);
    }
    expect(blocked).toBeGreaterThan(100);
  });
});

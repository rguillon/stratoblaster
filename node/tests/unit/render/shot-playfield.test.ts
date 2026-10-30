import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import {
  buildPlayfieldGrid,
  buildStreamGuides,
  TargetMarkers,
} from '../../../src/render/shot-playfield';
import type { ShotTarget } from '../../../src/core/entities/shot-target';

const LOOK = {
  ring: { thickness: 2, color: [1, 0, 0], deadColor: [0.2, 0.2, 0.2] },
  healthBar: { width: 20, height: 2, gap: 4, color: [0, 1, 0], backColor: [0, 0, 0] },
} as const;

describe('shot playfield', () => {
  let scene: Scene | undefined;
  afterEach(() => {
    scene?.dispose();
  });
  const newScene = (): Scene => (scene = new Scene(new NullEngine()));

  it('draws a grid line every cell in both directions, at the given depth', () => {
    const grid = buildPlayfieldGrid(
      newScene(),
      { width: 100, height: 50 },
      25,
      200,
      [0.1, 0.1, 0.1],
    );
    // 5 vertical + 3 horizontal lines, 2 points each.
    expect(grid.getTotalVertices()).toBe((5 + 3) * 2);
    const zs = Array.from(grid.getVerticesData('position') ?? []).filter((_, i) => i % 3 === 2);
    expect(new Set(zs)).toEqual(new Set([200]));
  });

  it('P03-R10: draws a guide along each stream angle, from its offset', () => {
    const guides = buildStreamGuides(
      newScene(),
      { x: 50, y: 10 },
      [
        { offsetX: 0, angleDeg: 0 },
        { offsetX: 4, angleDeg: 90 },
      ],
      100,
      [1, 1, 0],
    );
    const positions = Array.from(guides.getVerticesData('position') ?? []);
    const expected = [50, 10, 0.5, 50, 110, 0.5, 54, 10, 0.5, 154, 10, 0.5];
    expect(positions).toHaveLength(expected.length);
    expected.forEach((v, i) => {
      expect(positions[i]).toBeCloseTo(v);
    });
  });

  it('P03-R10: shows each target with a health bar that shrinks, and dims dead ones', () => {
    const s = newScene();
    const targets: ShotTarget[] = [
      { id: 0, x: 10, y: 20, radius: 5, health: 10, maxHealth: 10 },
      { id: 1, x: 30, y: 20, radius: 5, health: 0, maxHealth: 10 },
    ];
    const markers = new TargetMarkers(s, targets, LOOK);
    const first = targets[0];
    if (first) first.health = 5;
    markers.sync(targets);
    expect(s.getTransformNodeByName('target-0')?.position.asArray()).toEqual([10, 20, 0]);
    expect(s.getMeshByName('target-0-health')?.scaling.x).toBeCloseTo(10);
    expect(s.getMeshByName('target-1-health')?.isEnabled()).toBe(false);
    expect(s.getMeshByName('target-1-ring')?.material?.name).toBe('target-ring-dead');
    expect(s.getMeshByName('target-0-ring')?.material?.name).toBe('target-ring');
  });
});

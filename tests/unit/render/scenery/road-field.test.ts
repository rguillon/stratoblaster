import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import type { Road } from '../../../../src/core/scenery/road-network';
import { createRoadMaterial } from '../../../../src/render/scenery/scenery-kit';
import { RoadLayers } from '../../../../src/render/scenery/road-field';

const LOOK = {
  main: [0.1, 0.1, 0.1],
  cross: [0.5, 0.4, 0.3],
  opacity: { main: 0.8, cross: 0.6 },
  shoulder: 1,
  streetShoulder: 0.5,
  wear: 0,
  lift: 0.5,
} as const;

const road = (index: number, kind: Road['kind']): Road => ({
  index,
  kind,
  width: 6,
  lanes: 1,
  points: [0, 10, 20].map((z) => ({ x: index * 20, z, width: 6 })),
});

describe('RoadLayers', () => {
  let scene: Scene | undefined;
  afterEach(() => {
    scene?.dispose();
  });

  function layers(): RoadLayers {
    scene = new Scene(new NullEngine());
    return new RoadLayers(scene, createRoadMaterial(scene));
  }

  it('draws the middles of the streets opaque where all roads are streets (reviewer, 2026-10-28)', () => {
    const roads = layers();
    const span = { zMin: -50, zMax: 50 };
    roads.setChunk(0, [road(0, 'street'), road(1, 'street')], { height: () => 0 }, span, LOOK);
    const streets = roads.streetsOf(0);
    const seeThrough = scene?.getMeshByName('roads-0');
    if (!streets?.material || !seeThrough?.material) throw new Error('no ribbons');
    expect(streets.hasVertexAlpha).toBe(false);
    expect(streets.material.disableDepthWrite).toBe(false);
    // Behind the see-through ribbons and markings in depth, so they stay on top.
    expect(seeThrough.hasVertexAlpha).toBe(true);
    expect(streets.material.zOffset).toBeGreaterThan(seeThrough.material.zOffset);
    roads.removeChunk(0);
    expect(roads.streetsOf(0)).toBeUndefined();
  });

  it('keeps every ribbon see-through where streets meet other roads or paths', () => {
    const roads = layers();
    const span = { zMin: -50, zMax: 50 };
    for (const other of ['main', 'cross'] as const) {
      roads.setChunk(0, [road(0, 'street'), road(1, other)], { height: () => 0 }, span, LOOK);
      expect(roads.streetsOf(0), other).toBeUndefined();
    }
  });
});

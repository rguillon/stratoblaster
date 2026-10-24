import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { Enemy } from '../../../src/core/entities/enemy';
import type { EnemyModel } from '../../../src/render/game-view';
import { EnemyLayer } from '../../../src/render/enemy-layer';
import { Dropper } from '../../fixtures/sample-enemies';

function setUp() {
  const scene = new Scene(new NullEngine());
  const pivot = (i: number) => scene.getTransformNodeByName(`enemy-cube-${String(i)}`);
  const synced: [Enemy, number][] = [];
  const cube = (s: Scene): EnemyModel => ({
    root: new TransformNode('cube-model', s),
    sync: (enemy, dt) => synced.push([enemy, dt]),
  });
  return { layer: new EnemyLayer(scene, { cube }), synced, pivot };
}

describe('EnemyLayer', () => {
  it('P05-R11: draws a model per enemy at its position, nose along its heading', () => {
    const { layer, synced, pivot } = setUp();
    const enemy = new Dropper(100, 200);
    enemy.heading = Math.PI / 2;
    layer.sync([enemy], 0.1);
    expect(layer.count).toBe(1);
    expect(synced).toEqual([[enemy, 0.1]]);
    expect(pivot(0)?.position.asArray()).toEqual([100, 200, 0]);
    expect(pivot(0)?.rotation.z).toBeCloseTo(-Math.PI / 2);
    expect(pivot(0)?.isEnabled()).toBe(true);
    layer.sync([], 0);
    expect(pivot(0)?.isEnabled()).toBe(false);
  });

  it('ENG-19: reuses the models of enemies that are gone', () => {
    const { layer } = setUp();
    const a = new Dropper(0, 0);
    layer.sync([a], 0);
    layer.sync([], 0);
    expect(layer.count).toBe(0);
    layer.sync([new Dropper(1, 1)], 0);
    expect(layer.modelCount).toBe(1);
    layer.sync([new Dropper(1, 1), new Dropper(2, 2)], 0);
    expect(layer.modelCount).toBe(2);
    layer.clear();
    expect(layer.count).toBe(0);
    layer.dispose();
  });

  it('throws for an enemy without a model', () => {
    const { layer } = setUp();
    const enemy = new Dropper(0, 0);
    Object.defineProperty(enemy, 'model', { value: 'nope' });
    expect(() => {
      layer.sync([enemy], 0);
    }).toThrow(/No model for enemy "nope"/);
  });
});

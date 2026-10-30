import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { NodePool } from '../../../src/render/node-pool';

describe('NodePool', () => {
  let scene: Scene | undefined;
  afterEach(() => {
    scene?.dispose();
  });

  it('creates nodes on demand, shows the first ones and hides the rest', () => {
    const s = (scene = new Scene(new NullEngine()));
    let created = 0;
    const pool = new NodePool((i) => {
      created++;
      return new TransformNode(`n${String(i)}`, s);
    });
    expect(pool.show(3)).toHaveLength(3);
    expect(pool.show(1).map((n) => n.name)).toEqual(['n0']);
    expect(pool.nodes.map((n) => n.isEnabled())).toEqual([true, false, false]);
    pool.show(2);
    expect(created).toBe(3);
    pool.dispose();
    expect(pool.nodes).toEqual([]);
    expect(s.getTransformNodeByName('n0')).toBeNull();
  });
});

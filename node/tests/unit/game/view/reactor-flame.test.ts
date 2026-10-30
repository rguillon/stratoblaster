import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import type { AbstractMesh } from '@babylonjs/core/Meshes/abstractMesh';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { stepModelAnimations } from '../../../../src/render/model-animation';
import { REACTOR_FLAME } from '../../../../src/game/config/ship-look';
import {
  flicker,
  puffOpacity,
  puffProgress,
  reactorPhase,
} from '../../../../src/game/view/reactor-flame';
import { buildReactor } from '../../../../src/game/view/ship-parts';
import { at } from '../../../helpers/at';

const SIZE = { radius: 0.2, length: 1.5 };

let scene: Scene;
beforeEach(() => {
  scene = new Scene(new NullEngine());
});
afterEach(() => {
  scene.dispose();
});

function mesh(root: TransformNode, suffix: string): AbstractMesh {
  const found = root.getChildMeshes(false, (n) => n.name.endsWith(suffix));
  return at(found, 0);
}

function puffs(root: TransformNode): AbstractMesh[] {
  return root.getChildMeshes(false, (n) => n.name.includes('-puff-'));
}

/** Everything the flame animation changes, to compare two frames. */
function snapshot(root: TransformNode): number[] {
  return root.getDescendants(false).flatMap((n) => {
    const node = n as AbstractMesh;
    return [...node.scaling.asArray(), node.position.z, node.visibility];
  });
}

describe('reactor flame', () => {
  it('GD-61: flicker stays in [-1, 1] and varies over time', () => {
    const hz = REACTOR_FLAME.flickerHz;
    const values = Array.from({ length: 200 }, (_, i) => flicker(i / 60, 0.3, hz));
    for (const v of values) {
      expect(v).toBeGreaterThanOrEqual(-1);
      expect(v).toBeLessThanOrEqual(1);
    }
    expect(Math.max(...values) - Math.min(...values)).toBeGreaterThan(0.5);
    expect(flicker(1, 0, [])).toBe(0);
  });

  it('gives reactors stable, distinct phases', () => {
    const a = reactorPhase('heavy-reactor-left');
    expect(reactorPhase('heavy-reactor-left')).toBe(a);
    expect(reactorPhase('heavy-reactor-right')).not.toBe(a);
    for (const name of ['', 'a', 'light-reactor-rear-right']) {
      expect(reactorPhase(name)).toBeGreaterThanOrEqual(0);
      expect(reactorPhase(name)).toBeLessThan(Math.PI * 2);
    }
  });

  it('spreads puffs along the exhaust and loops them', () => {
    expect([0, 1, 2].map((i) => puffProgress(0, i, 3, 1))).toEqual([0, 1 / 3, 2 / 3]);
    expect(puffProgress(0.25, 0, 2, 2)).toBeCloseTo(0.5);
    expect(puffProgress(1.25, 0, 2, 2)).toBeCloseTo(0.5);
    expect(puffProgress(-0.25, 0, 1, 1)).toBeCloseTo(0.75);
  });

  it('fades puffs in near the nozzle and out at the tip', () => {
    expect(puffOpacity(0)).toBe(0);
    expect(puffOpacity(0.5)).toBeCloseTo(0.5);
    expect(puffOpacity(0.99)).toBeLessThan(0.02);
    expect(puffOpacity(0.15)).toBeGreaterThan(puffOpacity(0.05));
  });

  it('GD-61: a reactor has an outer exhaust, a hotter inner flame and plasma puffs', () => {
    const root = buildReactor('r', SIZE, scene);
    expect(mesh(root, '-exhaust').material?.name).toBe('ship-reactor-exhaust');
    expect(mesh(root, '-flame').material?.name).toBe('ship-reactor-flame');
    expect(puffs(root)).toHaveLength(REACTOR_FLAME.puffCount);
    for (const puff of puffs(root)) expect(puff.position.z).toBeLessThan(-SIZE.length / 2);
  });

  it('GD-61: the flame moves and flickers as the model is animated', () => {
    const root = buildReactor('r', SIZE, scene);
    const exhaust = mesh(root, '-exhaust');
    const pivot = at(
      root.getChildTransformNodes(false, (n) => n.name.endsWith('-exhaust-pivot')),
      0,
    );
    const lengths = new Set<number>();
    const before = snapshot(root);
    for (let frame = 0; frame < 30; frame++) {
      stepModelAnimations(root, 1 / 60);
      lengths.add(pivot.scaling.z);
      const vis = exhaust.visibility;
      expect(vis).toBeGreaterThanOrEqual(1 - REACTOR_FLAME.brightnessFlicker - 1e-9);
      expect(vis).toBeLessThanOrEqual(1);
    }
    expect(snapshot(root)).not.toEqual(before);
    expect(lengths.size).toBeGreaterThan(20);
    for (const length of lengths) {
      expect(Math.abs(length - 1)).toBeLessThanOrEqual(REACTOR_FLAME.lengthFlicker + 1e-9);
    }
  });

  it('GD-61: puffs travel from the nozzle towards the flame tip', () => {
    const root = buildReactor('r', SIZE, scene);
    const puff = at(puffs(root), 0);
    const start = puff.position.z;
    stepModelAnimations(root, 0.1);
    expect(puff.position.z).toBeLessThan(start);
  });
});

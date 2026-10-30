import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Constants } from '@babylonjs/core/Engines/constants';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { CreateBox } from '@babylonjs/core/Meshes/Builders/boxBuilder';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { Scene } from '@babylonjs/core/scene';
import { OutlineLayer, outlineModel, outlineOf, setOutline } from '../../../src/render/outline';

describe('rims (P14-R03, R04)', () => {
  it('P14-R04: a mesh asks for a rim through its metadata, keeping what was there', () => {
    const scene = new Scene(new NullEngine());
    const box = CreateBox('box', {}, scene);
    expect(outlineOf(box)).toBeUndefined();
    box.metadata = { kind: 'hull' };
    setOutline(box, [1, 0, 1]);
    expect(outlineOf(box)).toEqual([1, 0, 1]);
    expect(box.metadata).toMatchObject({ kind: 'hull' });
    const bare = CreateBox('bare', {}, scene);
    bare.metadata = 'text';
    setOutline(bare, [0, 1, 1]);
    expect(outlineOf(bare)).toEqual([0, 1, 1]);
  });

  it('P14-R03: a model gets rims on its solid meshes, not on its glows or see-through parts', () => {
    const scene = new Scene(new NullEngine());
    const root = new TransformNode('ship', scene);
    const solid = CreateBox('solid', {}, scene);
    solid.material = new StandardMaterial('metal', scene);
    const glow = CreateBox('glow', {}, scene);
    glow.material = new StandardMaterial('glow', scene);
    glow.material.alphaMode = Constants.ALPHA_ADD;
    const glass = CreateBox('glass', {}, scene);
    glass.material = new StandardMaterial('glass', scene);
    glass.material.alpha = 0.5;
    const bare = CreateBox('bare', {}, scene);
    for (const m of [solid, glow, glass, bare]) m.parent = root;
    outlineModel(root, [0, 1, 1]);
    expect(outlineOf(solid)).toEqual([0, 1, 1]);
    for (const m of [glow, glass, bare]) expect(outlineOf(m)).toBeUndefined();
  });

  it('P14-R03, R04: the layer draws the rim, as wide whatever the mesh scale', () => {
    const scene = new Scene(new NullEngine());
    const layer = new OutlineLayer({ width: 1, intensity: 2 });
    const plain = CreateBox('plain', {}, scene);
    expect(layer.add(plain)).toBe(false);
    // Not turned on (Babylon leaves it unset until it is).
    expect(plain.renderOutline).toBeFalsy();
    const holder = new TransformNode('holder', scene);
    holder.scaling.setAll(4);
    const big = CreateBox('big', {}, scene);
    big.parent = holder;
    setOutline(big, [0.5, 0.25, 0]);
    expect(layer.add(big)).toBe(true);
    expect(big.renderOutline).toBe(true);
    expect(big.outlineWidth).toBeCloseTo(0.25);
    expect(big.outlineColor.asArray()).toEqual([1, 0.5, 0]);
  });
});

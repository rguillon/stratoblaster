import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { Matrix, Vector3 } from '@babylonjs/core/Maths/math.vector';
import { instanceMatrices, PropField } from '../../../../src/render/scenery/prop-field';
import type { PropPlacement } from '../../../../src/core/scenery/prop-placement';
import { SAMPLE_SCENERY } from '../../../fixtures/sample-scenery';

const place = (kind: string, x: number): PropPlacement => ({
  kind,
  x,
  y: 2,
  z: 5,
  rotation: Math.PI / 2,
  scale: 2,
});

describe('PropField', () => {
  let scene: Scene | undefined;
  afterEach(() => {
    scene?.dispose();
  });

  function field(onStructure?: () => void): PropField {
    scene = new Scene(new NullEngine());
    const materials = {
      structure: new StandardMaterial('s', scene),
      lights: new StandardMaterial('l', scene),
    };
    return new PropField(scene, SAMPLE_SCENERY.propModels, materials, onStructure);
  }

  it('P04-R04, ENG-104: draws every placement of a kind with thin instances of one mesh', () => {
    const props = field();
    props.setChunk(0, [place('block', 0), place('block', 10), place('stick', 3)]);
    props.setChunk(1, [place('block', 20)]);
    props.sync();
    expect(props.count).toBe(4);
    const block = props.structureOf('block');
    expect(block?.thinInstanceCount).toBe(3);
    expect(block?.isEnabled()).toBe(true);
    expect(props.lightMeshes.map((m) => m.name)).toEqual(['prop-block-lights']);
    expect(props.lightMeshes[0]?.thinInstanceCount).toBe(3);
    props.removeChunk(0);
    props.sync();
    expect(block?.thinInstanceCount).toBe(1);
    expect(props.structureOf('stick')?.isEnabled()).toBe(false);
    props.clear();
    props.sync();
    expect(props.count).toBe(0);
    expect(block?.isEnabled()).toBe(false);
  });

  it('P04 review: draws only the props near the view, uploading again when it moves away', () => {
    const props = field();
    const at = (z: number): PropPlacement => ({ ...place('block', 0), z });
    props.setChunk(0, [at(0), at(100), at(200), at(300)]);
    props.setWindow(90, 110, 50);
    props.sync();
    // The window is drawn 50 wider each way: Z 40..160.
    const block = props.structureOf('block');
    expect(block?.thinInstanceCount).toBe(1);
    expect(props.count).toBe(4);
    props.setWindow(120, 140, 50);
    props.sync();
    expect(block?.thinInstanceCount).toBe(1);
    // Past the range drawn: the window moves on, and the props are uploaded again.
    props.setWindow(190, 210, 50);
    props.sync();
    expect(block?.thinInstanceCount).toBe(1);
    // Z 140..260 drawn; a wider window gets 80..330.
    props.setWindow(130, 280, 50);
    props.sync();
    expect(block?.thinInstanceCount).toBe(3);
  });

  it('P04-R04: props cast shadows, and unknown kinds are refused', () => {
    let casters = 0;
    const props = field(() => {
      casters++;
    });
    expect(casters).toBe(2);
    expect(() => {
      props.setChunk(0, [place('ufo', 0)]);
    }).toThrow(/ufo/);
  });

  it('places, turns and scales each instance', () => {
    const [matrix] = [Matrix.FromArray(instanceMatrices([place('block', 7)]))];
    const point = Vector3.TransformCoordinates(new Vector3(1, 0, 0), matrix);
    expect(point.x).toBeCloseTo(7);
    expect(point.y).toBeCloseTo(2);
    // A quarter turn around Y sends +X to -Z (left-handed), scaled by 2.
    expect(point.z).toBeCloseTo(5 - 2);
  });
});

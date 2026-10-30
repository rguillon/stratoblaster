import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { Matrix, Vector3 } from '@babylonjs/core/Maths/math.vector';
import {
  checkPropModels,
  instanceMatrices,
  levelPropKinds,
  levelPropModels,
  PropField,
} from '../../../../src/render/scenery/prop-field';
import type { PropPlacement } from '../../../../src/core/scenery/prop-placement';
import type { SceneryLevel } from '../../../../src/core/scenery/scenery-level';
import { SAMPLE_SCENERY, SAMPLE_SCENERY_LEVEL } from '../../../fixtures/sample-scenery';

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

  it('P13-R04: uploads again only the kinds whose props drawn changed', () => {
    const props = field();
    props.setChunk(0, [place('block', 0), place('stick', 3)]);
    props.sync();
    const block = props.structureOf('block');
    const stick = props.structureOf('stick');
    const uploads = { block: 0, stick: 0 };
    if (!block || !stick) throw new Error('no meshes');
    const count = (mesh: typeof block, kind: keyof typeof uploads) => {
      const upload = mesh.thinInstanceSetBuffer.bind(mesh);
      mesh.thinInstanceSetBuffer = (...args) => {
        uploads[kind]++;
        upload(...args);
      };
    };
    count(block, 'block');
    count(stick, 'stick');
    props.setChunk(1, [place('block', 20)]);
    props.sync();
    expect(uploads).toEqual({ block: 1, stick: 0 });
    expect(block.thinInstanceCount).toBe(2);
    expect(stick.thinInstanceCount).toBe(1);
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

  it('draws its meshes always, without fitting bounds to their props (reviewer, 2026-10-28)', () => {
    const props = field();
    props.setChunk(0, [place('block', 100)]);
    props.sync();
    const block = props.structureOf('block');
    expect(block?.thinInstanceCount).toBe(1);
    // The box of the model, not moved to the prop at x = 100.
    expect(block?.getBoundingInfo().boundingBox.maximum.x).toBeCloseTo(2);
    for (const mesh of [block, ...props.lightMeshes]) {
      expect(mesh?.alwaysSelectAsActiveMesh).toBe(true);
    }
  });

  it('builds each model once, for every level (reviewer, 2026-10-28)', () => {
    let built = 0;
    const block = () => {
      built++;
      return (
        SAMPLE_SCENERY.propModels.block?.() ?? {
          structure: { positions: [], indices: [], colors: [] },
        }
      );
    };
    const scenes = [new Scene(new NullEngine()), new Scene(new NullEngine())];
    const fields = scenes.map((s) => {
      const materials = {
        structure: new StandardMaterial('s', s),
        lights: new StandardMaterial('l', s),
      };
      return new PropField(s, { block }, materials);
    });
    expect(built).toBe(1);
    const normals = fields.map((f) => f.structureOf('block')?.getVerticesData('normal'));
    expect(normals[1]).toEqual(normals[0]);
    for (const s of scenes) s.dispose();
  });

  it('draws the same matrices, made once per chunk, as the window moves', () => {
    const props = field();
    const at = (z: number, x: number): PropPlacement => ({ ...place('block', x), z });
    const placements = [at(0, 1), at(100, 2), at(200, 3), at(300, 4)];
    props.setChunk(0, placements);
    for (const [zMin, zMax] of [
      [90, 110],
      [190, 310],
      [-10, 120],
    ] as const) {
      props.setWindow(zMin, zMax, 0);
      props.sync();
      const shown = placements.filter((p) => p.z >= zMin && p.z <= zMax);
      const buffer = props
        .structureOf('block')
        ?.thinInstanceGetWorldMatrices()
        .flatMap((m) => [...m.asArray()]);
      expect(buffer).toEqual([...instanceMatrices(shown)]);
    }
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

describe('the props a level builds (reviewer, 2026-10-28)', () => {
  const kind = (id: string) => ({ id, weight: 1, footprint: 5, scale: [1, 1] as const });
  const { props, sections } = SAMPLE_SCENERY_LEVEL;
  const level: SceneryLevel = {
    ...SAMPLE_SCENERY_LEVEL,
    // Its sections allow its blocks, not its towers, and no trees.
    sections: sections.map((s) => ({ ...s, groups: ['blocks'], trees: [] })),
    props: {
      ...props,
      groups: [...props.groups, { id: 'towers', weight: 1, kinds: [kind('tower')] }],
      landmarks: [{ kind: 'dam', z: 100, footprint: 10 }],
      cars: { kinds: ['car'], density: 1, lift: 0, scale: 1, length: 4, speed: [1, 2] },
    },
  };
  // Only the ids matter here.
  const model = () => ({ structure: { positions: [], indices: [], colors: [] } });

  it('the kinds its sections allow and its set pieces, not its cars', () => {
    expect(levelPropKinds(level)).toEqual(new Set(['block', 'dam']));
    expect(levelPropKinds(SAMPLE_SCENERY_LEVEL)).toEqual(new Set(['block', 'stick']));
  });

  it('only their models are built; a missing one is refused, set pieces and cars too', () => {
    const models = { block: model, stick: model, tower: model, dam: model, car: model };
    expect(Object.keys(levelPropModels(level, models)).sort()).toEqual(['block', 'dam']);
    expect(() => {
      checkPropModels(level, models);
    }).not.toThrow();
    expect(() => {
      checkPropModels(level, { block: model, car: model });
    }).toThrow(/dam/);
    expect(() => {
      checkPropModels(level, { block: model, dam: model });
    }).toThrow(/car/);
  });
});

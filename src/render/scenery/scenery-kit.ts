import type { Scene } from '@babylonjs/core/scene';
import type { DirectionalLight } from '@babylonjs/core/Lights/directionalLight';
import type { Material } from '@babylonjs/core/Materials/material';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import type { AbstractMesh } from '@babylonjs/core/Meshes/abstractMesh';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import type { Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { PropMaterials } from './prop-field';
import type { CloudLayerLook, SceneryLook } from './scenery-look';

/** What a cloud layer shows on one frame. */
export interface CloudState {
  readonly coverage: number;
  readonly opacity: number;
  /** Drift of the pattern, in world units along X and Z. */
  readonly offsetX: number;
  readonly offsetZ: number;
}

/** The material of one cloud layer, driven frame by frame. */
export interface CloudMaterial {
  readonly material: Material;
  set(state: CloudState): void;
}

/** What the materials need to know on each frame. */
export interface SceneryKitFrame {
  /** Seconds since the scene started (animations, not the level time). */
  readonly time: number;
  readonly cameraPosition: Vector3;
  readonly seaEnabled: boolean;
}

/**
 * Materials, textures and shadows of a scenery scene. The real kit
 * (`scenery-kit.visual.ts`) needs a WebGL engine; {@link createPlainSceneryKit} works anywhere,
 * including the `NullEngine` of the unit tests.
 */
export interface SceneryKit {
  readonly terrain: Material;
  readonly sea: Material;
  readonly props: PropMaterials;
  cloud(look: CloudLayerLook): CloudMaterial;
  addShadowCaster(mesh: AbstractMesh): void;
  update(frame: SceneryKitFrame): void;
}

/** What a kit is built from. */
export interface SceneryKitContext {
  readonly look: SceneryLook;
  readonly sun: DirectionalLight;
  /** Height of the sea (0 when the level has none). */
  readonly seaLevel: number;
  /** Size of the sea plane, to repeat its waves at the right scale. */
  readonly seaSize: { readonly width: number; readonly length: number };
  /** Seed of the generated textures. */
  readonly seed: number;
}

export type SceneryKitFactory = (scene: Scene, context: SceneryKitContext) => SceneryKit;

type Rgb = readonly [number, number, number];

function plain(name: string, color: Rgb, scene: Scene): StandardMaterial {
  const mat = new StandardMaterial(name, scene);
  mat.diffuseColor = new Color3(...color);
  mat.specularColor = Color3.Black();
  return mat;
}

/** Vertex-coloured materials of the props: lit structure, and self-lit accents. */
export function createPropMaterials(scene: Scene, look: SceneryLook): PropMaterials {
  const structure = new StandardMaterial('prop-structure', scene);
  structure.diffuseColor = Color3.White();
  structure.specularColor = new Color3(
    look.props.specular,
    look.props.specular,
    look.props.specular,
  );
  const lights = new StandardMaterial('prop-lights', scene);
  const glow = look.props.lightIntensity;
  lights.emissiveColor = new Color3(glow, glow, glow);
  lights.diffuseColor = Color3.Black();
  lights.specularColor = Color3.Black();
  lights.disableLighting = true;
  return { structure, lights };
}

/** Flat-coloured stand-ins for every material, with no texture and no shadow. */
export const createPlainSceneryKit: SceneryKitFactory = (scene, { look }) => {
  const sea = plain('sea', look.sea.color, scene);
  sea.alpha = look.sea.alpha;
  return {
    terrain: plain('terrain', look.terrain.ground.colors[1], scene),
    sea,
    props: createPropMaterials(scene, look),
    cloud: (cloud) => {
      const material = plain(`cloud-${String(cloud.altitude)}`, cloud.color, scene);
      return {
        material,
        set: (state) => {
          material.alpha = state.coverage > 0 ? state.opacity : 0;
        },
      };
    },
    addShadowCaster: () => undefined,
    update: () => undefined,
  };
};

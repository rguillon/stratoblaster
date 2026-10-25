import type { Scene } from '@babylonjs/core/scene';
import type { DirectionalLight } from '@babylonjs/core/Lights/directionalLight';
import type { Material } from '@babylonjs/core/Materials/material';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import type { AbstractMesh } from '@babylonjs/core/Meshes/abstractMesh';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import type { Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { Atmosphere } from '../../core/scenery/atmosphere';
import type { AuroraMaterial } from './aurora-layer';
import type { PropMaterials } from './prop-field';
import type { WeatherMaterialFactory } from './weather-layer';
import type { CloudLayerLook, SceneryLook } from './scenery-look';

type Rgb = readonly [number, number, number];

/** What a cloud layer shows on one frame. */
export interface CloudState {
  readonly coverage: number;
  readonly opacity: number;
  /** Its colours (P08-R04: they follow the time of day) and the haze it fades into. */
  readonly color: Rgb;
  readonly shade: Rgb;
  readonly fog: { readonly color: Rgb; readonly start: number; readonly end: number };
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
  /** The level's look here (P08-R04): shadows' darkness, ground lights. */
  readonly atmosphere: Atmosphere;
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
  readonly roads: Material;
  cloud(look: CloudLayerLook): CloudMaterial;
  /** The material of a weather kind's particles (P08-R05). */
  readonly weather: WeatherMaterialFactory;
  /** The aurora's material (P08-R04). */
  aurora(): AuroraMaterial;
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

function plain(name: string, color: Rgb, scene: Scene): StandardMaterial {
  const mat = new StandardMaterial(name, scene);
  mat.diffuseColor = new Color3(...color);
  mat.specularColor = Color3.Black();
  return mat;
}

/**
 * Sets how bright the props' self-lit accents (windows, neon, street and car lights) are
 * (P08-R04: off by day, on at dusk and night).
 */
export function setGroundLights(materials: PropMaterials, glow: number): void {
  if (materials.lights instanceof StandardMaterial)
    materials.lights.emissiveColor.set(glow, glow, glow);
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

/**
 * Vertex-coloured, lit, see-through material of the road ribbons (their vertex alpha fades the
 * edges), pulled towards the camera in depth so they never flicker against the terrain.
 */
export function createRoadMaterial(scene: Scene): StandardMaterial {
  const roads = new StandardMaterial('roads', scene);
  roads.diffuseColor = Color3.White();
  roads.specularColor = Color3.Black();
  roads.backFaceCulling = false;
  roads.zOffset = -2;
  // Blended over the ground: overlapping ribbons (crossings) must not hide each other.
  roads.disableDepthWrite = true;
  return roads;
}

/** Flat-coloured stand-ins for every material, with no texture and no shadow. */
export const createPlainSceneryKit: SceneryKitFactory = (scene, { look }) => {
  const sea = plain('sea', look.sea.color, scene);
  sea.alpha = look.sea.alpha;
  const props = createPropMaterials(scene, look);
  return {
    terrain: plain('terrain', look.terrain.ground.colors[1], scene),
    sea,
    props,
    roads: createRoadMaterial(scene),
    cloud: (cloud) => {
      const material = plain(`cloud-${String(cloud.altitude)}`, cloud.color, scene);
      return {
        material,
        set: (state) => {
          material.alpha = state.coverage > 0 ? state.opacity : 0;
          material.diffuseColor.set(...state.color);
        },
      };
    },
    weather: (_scene, kind) => {
      const material = plain('weather', kind.color, scene);
      material.alpha = kind.alpha;
      return { material, set: () => undefined };
    },
    aurora: () => {
      const material = plain('aurora', [0.2, 1, 0.5], scene);
      material.alpha = 0.3;
      return { material, set: () => undefined };
    },
    addShadowCaster: () => undefined,
    update: (frame) => {
      setGroundLights(props, frame.atmosphere.groundLights);
    },
  };
};

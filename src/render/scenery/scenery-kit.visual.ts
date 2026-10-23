import type { Scene } from '@babylonjs/core/scene';
import { Constants } from '@babylonjs/core/Engines/constants';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { PBRMaterial } from '@babylonjs/core/Materials/PBR/pbrMaterial';
import { RawTexture } from '@babylonjs/core/Materials/Textures/rawTexture';
import { Texture } from '@babylonjs/core/Materials/Textures/texture';
import { ShadowGenerator } from '@babylonjs/core/Lights/Shadows/shadowGenerator';
import '@babylonjs/core/Lights/Shadows/shadowGeneratorSceneComponent';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import { createCloudMaterial } from './cloud-material.visual';
import { buildGroundTexture, buildNoiseTexture, buildWaterNormalMap } from './procedural-textures';
import { createPropMaterials, createRoadMaterial, type SceneryKitFactory } from './scenery-kit';
import type { SceneryLook } from './scenery-look';
import { TerrainBlendPlugin, type TerrainBlendState } from './terrain-blend-plugin.visual';

/** Noise cycles across the blending and cloud noise textures. */
const NOISE_FREQUENCY = 8;
const ANISOTROPY = 8;

function rawTexture(scene: Scene, pixels: Uint8Array, size: number): RawTexture {
  const texture = new RawTexture(
    pixels,
    size,
    size,
    Constants.TEXTUREFORMAT_RGBA,
    scene,
    true,
    false,
    Texture.TRILINEAR_SAMPLINGMODE,
  );
  texture.wrapU = Texture.WRAP_ADDRESSMODE;
  texture.wrapV = Texture.WRAP_ADDRESSMODE;
  texture.anisotropicFilteringLevel = ANISOTROPY;
  return texture;
}

function terrainMaterial(
  scene: Scene,
  look: SceneryLook,
  state: TerrainBlendState,
  seed: number,
): StandardMaterial {
  const t = look.terrain;
  const ground = (layer: SceneryLook['terrain']['low'], n: number) =>
    rawTexture(scene, buildGroundTexture(t.textureSize, layer, seed + n), t.textureSize);
  const material = new StandardMaterial('terrain', scene);
  material.diffuseColor = Color3.White();
  material.specularColor = new Color3(t.specular, t.specular, t.specular);
  new TerrainBlendPlugin(
    material,
    t,
    {
      low: ground(t.low, 1),
      ground: ground(t.ground, 2),
      steep: ground(t.steep, 3),
      high: ground(t.high, 4),
      noise: rawTexture(
        scene,
        buildNoiseTexture(t.textureSize, NOISE_FREQUENCY, seed + 5),
        t.textureSize,
      ),
    },
    state,
  );
  return material;
}

function seaMaterial(
  scene: Scene,
  look: SceneryLook,
  size: { width: number; length: number },
  seed: number,
): PBRMaterial {
  const { sea } = look;
  const material = new PBRMaterial('sea', scene);
  material.albedoColor = new Color3(...sea.color);
  material.metallic = 0;
  material.roughness = sea.roughness;
  material.alpha = sea.alpha;
  material.transparencyMode = PBRMaterial.PBRMATERIAL_ALPHABLEND;
  material.directIntensity = sea.sunGlint;
  const normals = rawTexture(
    scene,
    buildWaterNormalMap(sea.normalMap.size, sea.normalMap, seed + 6),
    sea.normalMap.size,
  );
  normals.uScale = size.width / sea.tileSize;
  normals.vScale = size.length / sea.tileSize;
  material.bumpTexture = normals;
  return material;
}

/**
 * The real scenery kit: generated terrain textures blended in the terrain shader, a sea with
 * drifting generated waves that reflect the sky and the sun, generated cloud layers, and the
 * sun's shadows (PCF, ENG-103). Needs a WebGL engine.
 */
export const createSceneryKit: SceneryKitFactory = (scene, context) => {
  const { look, sun, seaLevel, seaSize, seed } = context;
  const state: TerrainBlendState = { seaLevel, seaEnabled: true, time: 0 };
  const sea = seaMaterial(scene, look, seaSize, seed);
  const cloudTexture = rawTexture(
    scene,
    buildNoiseTexture(look.terrain.textureSize, NOISE_FREQUENCY / 2, seed + 7),
    look.terrain.textureSize,
  );
  const shadows = new ShadowGenerator(look.sun.shadow.mapSize, sun);
  shadows.usePercentageCloserFiltering = true;
  shadows.filteringQuality = ShadowGenerator.QUALITY_MEDIUM;
  shadows.bias = look.sun.shadow.bias;
  shadows.normalBias = look.sun.shadow.normalBias;
  shadows.setDarkness(look.sun.shadow.darkness);
  let camera = Vector3.Zero();
  const fog = { color: look.sky.haze, start: look.fog.start, end: look.fog.end };
  return {
    terrain: terrainMaterial(scene, look, state, seed),
    sea,
    props: createPropMaterials(scene, look),
    roads: createRoadMaterial(scene),
    cloud: (cloud) => createCloudMaterial(scene, cloud, cloudTexture, fog, () => camera),
    addShadowCaster: (mesh) => {
      shadows.addShadowCaster(mesh, false);
    },
    update: (frame) => {
      camera = frame.cameraPosition;
      state.time = frame.time;
      state.seaEnabled = frame.seaEnabled;
      const bump = sea.bumpTexture;
      if (bump instanceof Texture) {
        bump.uOffset = (frame.time * look.sea.drift[0]) / look.sea.tileSize;
        bump.vOffset = (frame.time * look.sea.drift[1]) / look.sea.tileSize;
      }
    },
  };
};

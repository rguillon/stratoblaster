import type { Scene } from '@babylonjs/core/scene';
import { RawCubeTexture } from '@babylonjs/core/Materials/Textures/rawCubeTexture';
import { Constants } from '@babylonjs/core/Engines/constants';
import { ImageProcessingConfiguration } from '@babylonjs/core/Materials/imageProcessingConfiguration';
import { GlowLayer } from '@babylonjs/core/Layers/glowLayer';
import { buildGradientCubeFaces, type GradientStop } from './gradient-cube';

/** Look settings for {@link applyShowcaseEnvironment}. */
export interface ShowcaseEnvironmentOptions {
  readonly cubeSize: number;
  readonly intensity: number;
  readonly stops: readonly GradientStop[];
  readonly glow: {
    readonly intensity: number;
    readonly blurKernelSize: number;
    /** Resolution of the glow image, as a share of the screen's; Babylon's 0.5 when omitted. */
    readonly ratio?: number;
    /** Samples per pixel of the glow image (antialiasing); Babylon's 1 when omitted. */
    readonly samples?: number;
  };
}

/**
 * Gives a scene image-based lighting from a procedural sky gradient (no asset download),
 * ACES tone mapping and a glow layer for emissive parts (ENG-103). Returns the glow layer.
 */
export function applyShowcaseEnvironment(
  scene: Scene,
  options: ShowcaseEnvironmentOptions,
): GlowLayer {
  const faces = buildGradientCubeFaces(options.cubeSize, options.stops);
  scene.environmentTexture = new RawCubeTexture(
    scene,
    faces,
    options.cubeSize,
    Constants.TEXTUREFORMAT_RGBA,
    Constants.TEXTURETYPE_UNSIGNED_BYTE,
    true,
  );
  scene.environmentIntensity = options.intensity;
  scene.imageProcessingConfiguration.toneMappingEnabled = true;
  scene.imageProcessingConfiguration.toneMappingType =
    ImageProcessingConfiguration.TONEMAPPING_ACES;
  const { blurKernelSize, ratio, samples } = options.glow;
  const glow = new GlowLayer('glow', scene, {
    blurKernelSize,
    ...(ratio === undefined ? {} : { mainTextureRatio: ratio }),
    ...(samples === undefined ? {} : { mainTextureSamples: samples }),
  });
  glow.intensity = options.glow.intensity;
  return glow;
}

/**
 * Gives the scene's sky lighting the gradient `stops` and `intensity` (P08-R04: they follow the
 * time of day). The cube is only rebuilt when the gradient changed since the last call.
 */
export function updateSkyEnvironment(
  scene: Scene,
  cubeSize: number,
  stops: readonly GradientStop[],
  intensity: number,
): void {
  scene.environmentIntensity = intensity;
  const texture = scene.environmentTexture;
  const key = stops.map((s) => s.color.map((c) => Math.round(c * 255)).join(',')).join(';');
  if (!(texture instanceof RawCubeTexture) || LAST_SKY.get(scene) === key) return;
  LAST_SKY.set(scene, key);
  texture.update(
    buildGradientCubeFaces(cubeSize, stops),
    Constants.TEXTUREFORMAT_RGBA,
    Constants.TEXTURETYPE_UNSIGNED_BYTE,
    true,
  );
}

const LAST_SKY = new WeakMap<Scene, string>();

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
  readonly glow: { readonly intensity: number; readonly blurKernelSize: number };
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
  const glow = new GlowLayer('glow', scene, { blurKernelSize: options.glow.blurKernelSize });
  glow.intensity = options.glow.intensity;
  return glow;
}

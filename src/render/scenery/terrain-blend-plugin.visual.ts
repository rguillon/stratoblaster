import type { BaseTexture } from '@babylonjs/core/Materials/Textures/baseTexture';
import type { Material } from '@babylonjs/core/Materials/material';
import type { MaterialDefines } from '@babylonjs/core/Materials/materialDefines';
import { MaterialPluginBase } from '@babylonjs/core/Materials/materialPluginBase';
import type { UniformBuffer } from '@babylonjs/core/Materials/uniformBuffer';
import type { TerrainLook } from './scenery-look';

/** Textures the terrain blends between, plus a noise texture (R fine, G coarse). */
export interface TerrainTextures {
  readonly low: BaseTexture;
  readonly ground: BaseTexture;
  readonly steep: BaseTexture;
  readonly high: BaseTexture;
  readonly noise: BaseTexture;
}

/** Values that change while the scene runs. */
export interface TerrainBlendState {
  seaLevel: number;
  seaEnabled: boolean;
  time: number;
}

const SAMPLERS = [
  'terrainLow',
  'terrainGround',
  'terrainSteep',
  'terrainHigh',
  'terrainNoise',
] as const;

const UNIFORMS = [
  { name: 'terrainHeights', size: 4, type: 'vec4' },
  { name: 'terrainSlope', size: 4, type: 'vec4' },
  { name: 'terrainScale', size: 4, type: 'vec4' },
  { name: 'terrainTintA', size: 3, type: 'vec3' },
  { name: 'terrainTintB', size: 3, type: 'vec3' },
  { name: 'terrainSea', size: 4, type: 'vec4' },
  { name: 'terrainFoam', size: 4, type: 'vec4' },
] as const;

const FRAGMENT_DEFINITIONS = /* glsl */ `
#ifdef TERRAIN_BLEND
uniform sampler2D terrainLow;
uniform sampler2D terrainGround;
uniform sampler2D terrainSteep;
uniform sampler2D terrainHigh;
uniform sampler2D terrainNoise;

// Samples a ground texture from the three axis planes, weighted by the normal, so steep
// slopes are not stretched.
vec3 terrainTriplanar(sampler2D tex, vec3 p, vec3 w) {
  float s = terrainScale.x;
  return texture2D(tex, p.zy * s).rgb * w.x + texture2D(tex, p.xz * s).rgb * w.y
    + texture2D(tex, p.xy * s).rgb * w.z;
}

vec3 terrainColor(vec3 p, vec3 n) {
  vec3 w = pow(abs(n), vec3(4.0));
  w /= (w.x + w.y + w.z);
  vec4 noise = texture2D(terrainNoise, p.xz * terrainScale.y);
  float jitter = noise.r - 0.5;
  float h = p.y + jitter * terrainSlope.z;
  float slope = 1.0 - clamp(n.y, 0.0, 1.0) + jitter * terrainSlope.w;
  float tint = smoothstep(0.3, 0.7, texture2D(terrainNoise, p.xz * terrainScale.z).g);
  vec3 ground = terrainTriplanar(terrainGround, p, w) * mix(terrainTintA, terrainTintB, tint);
  float blend = terrainHeights.z;
  vec3 color = mix(terrainTriplanar(terrainLow, p, w), ground,
    smoothstep(terrainHeights.x - blend, terrainHeights.x + blend, h));
  color = mix(color, terrainTriplanar(terrainHigh, p, w),
    smoothstep(terrainHeights.y - blend, terrainHeights.y + blend, h));
  color = mix(color, terrainTriplanar(terrainSteep, p, w),
    smoothstep(terrainSlope.x, terrainSlope.y, slope));
  if (terrainSea.y > 0.5) {
    // Surf: a band around the sea level that swells and breaks with time.
    float swell = sin(terrainSea.z * 1.7 + noise.g * 18.0) * 0.5 + 0.5;
    float d = abs(p.y - terrainSea.x - swell * terrainFoam.w * 0.5);
    float foam = (1.0 - smoothstep(0.0, terrainFoam.w, d)) * smoothstep(0.35, 0.65, noise.r + swell * 0.3);
    color = mix(color, terrainFoam.rgb, foam * 0.8);
  }
  return color;
}
#endif
`;

const UPDATE_DIFFUSE = /* glsl */ `
#ifdef TERRAIN_BLEND
  baseColor.rgb = terrainColor(vPositionW, normalW);
#endif
`;

/**
 * Turns a `StandardMaterial` into a terrain material (P04-R01): the colour comes from four
 * generated textures blended by altitude and slope, with noise so the borders wander, large
 * tinted patches, and surf where the ground meets the sea. Lighting, shadows and fog stay the
 * standard material's.
 */
export class TerrainBlendPlugin extends MaterialPluginBase {
  constructor(
    material: Material,
    private readonly look: TerrainLook,
    private readonly textures: TerrainTextures,
    private readonly state: TerrainBlendState,
  ) {
    super(material, 'TerrainBlend', 200, { TERRAIN_BLEND: false });
    this._enable(true);
  }

  override getClassName(): string {
    return 'TerrainBlendPlugin';
  }

  override prepareDefines(defines: MaterialDefines): void {
    defines.TERRAIN_BLEND = true;
  }

  override getSamplers(samplers: string[]): void {
    samplers.push(...SAMPLERS);
  }

  override getUniforms() {
    return {
      ubo: UNIFORMS.map((u) => ({ ...u })),
      fragment: `#ifdef TERRAIN_BLEND\n${UNIFORMS.map((u) => `uniform ${u.type} ${u.name};`).join('\n')}\n#endif`,
    };
  }

  override bindForSubMesh(ubo: UniformBuffer): void {
    const { look, state, textures } = this;
    ubo.updateFloat4('terrainHeights', look.lowHeight, look.highHeight, look.heightBlend, 0);
    ubo.updateFloat4(
      'terrainSlope',
      look.steepSlope[0],
      look.steepSlope[1],
      look.jitter.height,
      look.jitter.slope,
    );
    ubo.updateFloat4(
      'terrainScale',
      1 / look.tileSize,
      1 / look.noiseTileSize,
      1 / look.tintTileSize,
      0,
    );
    ubo.updateFloat3('terrainTintA', ...look.tints[0]);
    ubo.updateFloat3('terrainTintB', ...look.tints[1]);
    ubo.updateFloat4('terrainSea', state.seaLevel, state.seaEnabled ? 1 : 0, state.time, 0);
    ubo.updateFloat4('terrainFoam', ...look.foam.color, look.foam.width);
    ubo.setTexture('terrainLow', textures.low);
    ubo.setTexture('terrainGround', textures.ground);
    ubo.setTexture('terrainSteep', textures.steep);
    ubo.setTexture('terrainHigh', textures.high);
    ubo.setTexture('terrainNoise', textures.noise);
  }

  override getCustomCode(shaderType: string): Record<string, string> | null {
    if (shaderType !== 'fragment') return null;
    return {
      CUSTOM_FRAGMENT_DEFINITIONS: FRAGMENT_DEFINITIONS,
      CUSTOM_FRAGMENT_UPDATE_DIFFUSE: UPDATE_DIFFUSE,
    };
  }
}

import type { BaseTexture } from '@babylonjs/core/Materials/Textures/baseTexture';
import type { Material } from '@babylonjs/core/Materials/material';
import type { MaterialDefines } from '@babylonjs/core/Materials/materialDefines';
import { MaterialPluginBase } from '@babylonjs/core/Materials/materialPluginBase';
import type { UniformBuffer } from '@babylonjs/core/Materials/uniformBuffer';
import type { LavaLook, TerrainLook } from './scenery-look';
import { SURFACE_SCALE } from './terrain-geometry';

/** Textures the terrain blends between, plus a noise texture (R fine, G coarse). */
export interface TerrainTextures {
  readonly low: BaseTexture;
  readonly ground: BaseTexture;
  readonly steep: BaseTexture;
  readonly high: BaseTexture;
  readonly lush: BaseTexture;
  readonly paved: BaseTexture;
  readonly sand: BaseTexture;
  readonly noise: BaseTexture;
}

/** Values that change while the scene runs. */
export interface TerrainBlendState {
  seaLevel: number;
  seaEnabled: boolean;
  time: number;
  /** Phase 10: the sea is lava; the rock by it glows (P10-R05). */
  lava?: LavaLook;
  /** How the ground is drawn: its colours follow the ground, not the world (`GroundTransform`). */
  ground?: { readonly scale: number; readonly offsetZ: number };
}

const SAMPLERS = [
  'terrainLow',
  'terrainGround',
  'terrainSteep',
  'terrainHigh',
  'terrainLush',
  'terrainPaved',
  'terrainSandy',
  'terrainNoise',
] as const;

const UNIFORMS = [
  { name: 'terrainHeights', size: 4, type: 'vec4' },
  { name: 'terrainSlope', size: 4, type: 'vec4' },
  { name: 'terrainScale', size: 4, type: 'vec4' },
  { name: 'terrainTintA', size: 3, type: 'vec3' },
  { name: 'terrainTintB', size: 3, type: 'vec3' },
  { name: 'terrainSea', size: 4, type: 'vec4' },
  { name: 'terrainSand', size: 4, type: 'vec4' },
  { name: 'terrainShallow', size: 4, type: 'vec4' },
  { name: 'terrainDeep', size: 3, type: 'vec3' },
  { name: 'terrainFoam', size: 4, type: 'vec4' },
  { name: 'terrainSurf', size: 4, type: 'vec4' },
  { name: 'terrainLava', size: 4, type: 'vec4' },
  { name: 'terrainGroundFrame', size: 4, type: 'vec4' },
] as const;

const FRAGMENT_DEFINITIONS = /* glsl */ `
#ifdef TERRAIN_BLEND
uniform sampler2D terrainLow;
uniform sampler2D terrainGround;
uniform sampler2D terrainSteep;
uniform sampler2D terrainHigh;
uniform sampler2D terrainLush;
uniform sampler2D terrainPaved;
uniform sampler2D terrainSandy;
uniform sampler2D terrainNoise;

// Planes and layers weighing less than this are not read (reviewer, 2026-10-28): they would change
// the colour by less than half a step. On flat paved ground, one texture read instead of 21.
const float TERRAIN_SKIP = 1.0 / 512.0;

// Samples a ground texture from the three axis planes, weighted by the normal, so steep
// slopes are not stretched.
vec3 terrainTriplanar(sampler2D tex, vec3 p, vec3 w) {
  float s = terrainScale.x;
  vec3 color = vec3(0.0);
  if (w.x > 0.0) color += texture2D(tex, p.zy * s).rgb * w.x;
  if (w.y > 0.0) color += texture2D(tex, p.xz * s).rgb * w.y;
  if (w.z > 0.0) color += texture2D(tex, p.xy * s).rgb * w.z;
  return color;
}

// A layer of the ground: its texture times its share \`k\` of the colour, and that share; none
// when too small to show.
vec4 terrainLayer(sampler2D tex, vec3 p, vec3 w, float k) {
  if (k <= TERRAIN_SKIP) return vec4(0.0);
  return vec4(terrainTriplanar(tex, p, w) * k, k);
}

// Where the ground meets the sea: a sand beach above the water, the ground under it tinted by
// the water from turquoise shallows to the deep, and surf (phase 5 review). The sea plane over
// it is mostly see-through, so it only adds the waves' glints: no hard line where they meet.
vec3 terrainShore(vec3 color, vec3 p, vec4 noise, float slope) {
  float time = terrainSea.z;
  float fine = texture2D(terrainNoise, p.xz * terrainScale.y * 7.0).r;
  float depth = terrainSea.x - p.y + (noise.r - 0.5) * 0.8;
  float gentle = 1.0 - smoothstep(terrainSlope.x, terrainSlope.y, slope);
  // Beach: dry sand fading into the ground, darker where the swash wets it.
  vec3 sand = terrainSand.rgb * (0.9 + 0.2 * fine);
  float beach = 1.0 - smoothstep(terrainSand.w * 0.4, terrainSand.w, -depth + (noise.g - 0.5) * 3.0);
  color = mix(color, sand, beach * gentle);
  color *= 1.0 - 0.3 * (1.0 - smoothstep(-1.2, 0.0, -depth)) * gentle;
  // Water: the deeper, the darker, up to the colour of the open sea.
  float deep = smoothstep(0.0, terrainShallow.w, depth);
  vec3 water = mix(terrainShallow.rgb, terrainDeep, sqrt(deep));
  color = mix(color, water, smoothstep(0.0, 1.2, depth) * mix(0.55, 1.0, deep));
  // Surf: a broken line of foam swashing up and down the beach, and bands rolling in.
  float swash = sin(time * 0.9 + noise.g * 14.0) * terrainFoam.w;
  float edge = 1.0 - smoothstep(0.0, terrainFoam.w, abs(depth - swash));
  edge *= smoothstep(0.25, 0.55, fine + noise.r * 0.3);
  float roll = fract(depth / terrainSurf.x + time * terrainSurf.y + noise.g * 1.5);
  float band = smoothstep(0.82, 0.95, roll) * (1.0 - smoothstep(0.92, 1.0, roll) * 0.6);
  band *= smoothstep(0.0, 0.8, depth) * (1.0 - smoothstep(0.0, terrainSurf.z, depth));
  band *= smoothstep(0.4, 0.7, fine);
  return mix(color, terrainFoam.rgb, clamp(edge * 0.9 + band * 0.7, 0.0, 1.0));
}

// Phase 10: where the rock meets lava (P10-R05), it is scorched dark under a hot glowing edge.
vec3 terrainScorch(vec3 color, vec3 p) {
  float above = p.y - terrainSea.x;
  return color * mix(vec3(0.55, 0.42, 0.38), vec3(1.0), smoothstep(0.0, terrainLava.w * 4.0, above));
}

// The glow of the rock by the lava: a bright edge at its level and glowing cracks a little above.
// The ground point drawn at world point \`p\` (the ground may be drawn scaled and moved).
vec3 groundPoint(vec3 p) {
  return vec3(p.x, p.y, p.z - terrainGroundFrame.y) / terrainGroundFrame.x;
}

vec3 terrainHeat(vec3 p) {
  if (terrainSea.w < 0.5 || terrainSea.y < 0.5) return vec3(0.0);
  float above = p.y - terrainSea.x;
  vec4 noise = texture2D(terrainNoise, p.xz * terrainScale.y * 5.0);
  float flicker = 0.8 + 0.2 * sin(terrainSea.z * 2.3 + noise.g * 12.0);
  float edge = 1.0 - smoothstep(0.0, terrainLava.w * (0.7 + 0.6 * noise.r), above);
  float crack = 1.0 - smoothstep(0.0, 0.035, abs(noise.r - 0.5));
  crack *= 1.0 - smoothstep(0.0, terrainSurf.w, above);
  return terrainLava.rgb * clamp(edge * 1.4 + crack * 0.8, 0.0, 1.6) * flicker;
}

vec3 terrainColor(vec3 p, vec3 n) {
  vec3 w = pow(abs(n), vec3(4.0));
  w /= (w.x + w.y + w.z);
  w *= step(vec3(TERRAIN_SKIP), w);
  w /= (w.x + w.y + w.z);
  vec4 noise = texture2D(terrainNoise, p.xz * terrainScale.y);
  float jitter = noise.r - 0.5;
  float h = p.y + jitter * terrainSlope.z;
  float slope = 1.0 - clamp(n.y, 0.0, 1.0) + jitter * terrainSlope.w;
  float blend = terrainHeights.z;
  // The ground above the low layer, the high layer over them, and the steep layer over all.
  float above = smoothstep(terrainHeights.x - blend, terrainHeights.x + blend, h);
  float high = smoothstep(terrainHeights.y - blend, terrainHeights.y + blend, h);
  float steep = smoothstep(terrainSlope.x, terrainSlope.y, slope);
  float sandy = 0.0;
  float lush = 0.0;
  float paved = 0.0;
#ifdef VERTEXCOLOR
  // Ground cover of the section, from the vertex colour (see terrain-geometry.ts).
  float lushCover = clamp((1.0 - vColor.r) / ${SURFACE_SCALE.toFixed(4)}, 0.0, 1.0);
  float pavedCover = clamp((1.0 - vColor.b) / ${SURFACE_SCALE.toFixed(4)}, 0.0, 1.0);
  float sandyCover = clamp((1.0 - vColor.g) / ${SURFACE_SCALE.toFixed(4)}, 0.0, 1.0);
  // Cover fades in with noise, in patches rather than as a flat gradient: sand over the ground,
  // grass over that, paving over all.
  float patchy = clamp(noise.g * 0.6 + 0.2, 0.0, 1.0);
  sandy = smoothstep(patchy - 0.25, patchy + 0.25, sandyCover);
  lush = smoothstep(patchy - 0.25, patchy + 0.25, lushCover);
  paved = smoothstep(patchy - 0.25, patchy + 0.25, pavedCover);
#endif
  // Each texture's share of the colour, from the layers laid one over the other.
  float ground = above * (1.0 - high) * (1.0 - steep);
  float bare = ground * (1.0 - sandy) * (1.0 - lush) * (1.0 - paved);
  vec4 sum = terrainLayer(terrainLow, p, w, (1.0 - above) * (1.0 - high) * (1.0 - steep));
  if (bare > TERRAIN_SKIP) {
    float tint = smoothstep(0.3, 0.7, texture2D(terrainNoise, p.xz * terrainScale.z).g);
    sum += terrainLayer(terrainGround, p, w, bare) * vec4(mix(terrainTintA, terrainTintB, tint), 1.0);
  }
  sum += terrainLayer(terrainSandy, p, w, ground * sandy * (1.0 - lush) * (1.0 - paved));
  sum += terrainLayer(terrainLush, p, w, ground * lush * (1.0 - paved));
  sum += terrainLayer(terrainPaved, p, w, ground * paved);
  sum += terrainLayer(terrainHigh, p, w, high * (1.0 - steep));
  sum += terrainLayer(terrainSteep, p, w, steep);
  // What was not read is shared out among what was.
  vec3 color = sum.rgb / sum.a;
  if (terrainSea.y > 0.5 && terrainSea.w > 0.5) return terrainScorch(color, p);
  if (terrainSea.y > 0.5) color = terrainShore(color, p, noise, slope);
  return color;
}
#endif
`;

const UPDATE_DIFFUSE = /* glsl */ `
#ifdef TERRAIN_BLEND
  baseColor.rgb = terrainColor(groundPoint(vPositionW), normalW);
#endif
`;

const BEFORE_FOG = /* glsl */ `
#ifdef TERRAIN_BLEND
  color.rgb += terrainHeat(groundPoint(vPositionW));
#endif
`;

/**
 * Turns a `StandardMaterial` into a terrain material (P04-R01): the colour comes from four
 * generated textures blended by altitude and slope, with noise so the borders wander, large
 * tinted patches, and a beach, shallows and surf where the ground meets the sea (phase 10: or,
 * by lava, scorched rock with a glowing edge and cracks). Lighting, shadows and fog stay the
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
    const lava = state.lava;
    ubo.updateFloat4(
      'terrainSea',
      state.seaLevel,
      state.seaEnabled ? 1 : 0,
      state.time,
      lava ? 1 : 0,
    );
    const edge = lava?.edge ?? { color: [0, 0, 0] as const, width: 1, cracks: 1 };
    ubo.updateFloat4('terrainLava', ...edge.color, edge.width);
    const ground = state.ground ?? { scale: 1, offsetZ: 0 };
    ubo.updateFloat4('terrainGroundFrame', ground.scale, ground.offsetZ, 0, 0);
    const { shore } = look;
    ubo.updateFloat4('terrainSand', ...shore.sand, shore.beach);
    ubo.updateFloat4('terrainShallow', ...shore.shallow, shore.depth);
    ubo.updateFloat3('terrainDeep', ...shore.deep);
    ubo.updateFloat4('terrainFoam', ...shore.foam.color, shore.foam.width);
    const { spacing, speed, reach } = shore.foam;
    ubo.updateFloat4('terrainSurf', spacing, speed, reach, edge.cracks);
    ubo.setTexture('terrainLow', textures.low);
    ubo.setTexture('terrainGround', textures.ground);
    ubo.setTexture('terrainSteep', textures.steep);
    ubo.setTexture('terrainHigh', textures.high);
    ubo.setTexture('terrainLush', textures.lush);
    ubo.setTexture('terrainPaved', textures.paved);
    ubo.setTexture('terrainSandy', textures.sand);
    ubo.setTexture('terrainNoise', textures.noise);
  }

  override getCustomCode(shaderType: string): Record<string, string> | null {
    if (shaderType !== 'fragment') return null;
    return {
      CUSTOM_FRAGMENT_DEFINITIONS: FRAGMENT_DEFINITIONS,
      CUSTOM_FRAGMENT_UPDATE_DIFFUSE: UPDATE_DIFFUSE,
      CUSTOM_FRAGMENT_BEFORE_FOG: BEFORE_FOG,
    };
  }
}

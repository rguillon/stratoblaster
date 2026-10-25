import type { Scene } from '@babylonjs/core/scene';
import type { BaseTexture } from '@babylonjs/core/Materials/Textures/baseTexture';
import { ShaderMaterial } from '@babylonjs/core/Materials/shaderMaterial';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import { Vector2, Vector3, Vector4 } from '@babylonjs/core/Maths/math.vector';
import type { CloudMaterial } from './scenery-kit';
import type { CloudLayerLook } from './scenery-look';

const VERTEX = /* glsl */ `
precision highp float;
attribute vec3 position;
uniform mat4 world;
uniform mat4 viewProjection;
varying vec3 vWorld;
void main() {
  vec4 p = world * vec4(position, 1.0);
  vWorld = p.xyz;
  gl_Position = viewProjection * p;
}
`;

// cloudParams: coverage, opacity, softness, 1 / tile size. The texture holds evenly spread
// noise (R fine, G coarse), so a coverage of 0.3 covers about 30 % of the sky.
const FRAGMENT = /* glsl */ `
precision highp float;
varying vec3 vWorld;
uniform sampler2D cloudTexture;
uniform vec4 cloudParams;
uniform vec2 cloudOffset;
uniform vec3 cloudColor;
uniform vec3 cloudShade;
uniform vec3 fogColor;
uniform vec2 fogRange;
uniform vec3 cameraPosition;
void main() {
  vec2 uv = (vWorld.xz + cloudOffset) * cloudParams.w;
  float density = texture2D(cloudTexture, uv).g * 0.65 + texture2D(cloudTexture, uv * 3.1 + 0.37).r * 0.35;
  float threshold = 1.0 - cloudParams.x;
  float edge = smoothstep(threshold - cloudParams.z, threshold + cloudParams.z, density);
  float core = smoothstep(threshold, threshold + cloudParams.z * 4.0, density);
  vec3 color = mix(cloudShade, cloudColor, core);
  float fog = clamp((distance(vWorld, cameraPosition) - fogRange.x) / (fogRange.y - fogRange.x), 0.0, 1.0);
  gl_FragColor = vec4(mix(color, fogColor, fog), edge * cloudParams.y);
}
`;

/**
 * A cloud layer material (P04-R03): a generated noise texture cut at a threshold set by the
 * coverage, with soft edges, faded by the opacity and the fog. Drawn blended, without writing
 * depth.
 */
export function createCloudMaterial(
  scene: Scene,
  look: CloudLayerLook,
  texture: BaseTexture,
  cameraPosition: () => Vector3,
): CloudMaterial {
  const material = new ShaderMaterial(
    `cloud-${String(look.altitude)}`,
    scene,
    { vertexSource: VERTEX, fragmentSource: FRAGMENT },
    {
      attributes: ['position'],
      uniforms: [
        'world',
        'viewProjection',
        'cloudParams',
        'cloudOffset',
        'cloudColor',
        'cloudShade',
        'fogColor',
        'fogRange',
        'cameraPosition',
      ],
      samplers: ['cloudTexture'],
      needAlphaBlending: true,
    },
  );
  material.backFaceCulling = false;
  material.disableDepthWrite = true;
  material.setTexture('cloudTexture', texture);
  const params = new Vector4();
  const offset = new Vector2();
  const fogRange = new Vector2();
  const [color, shade, fogColor] = [new Color3(), new Color3(), new Color3()];
  return {
    material,
    set: (state) => {
      params.set(state.coverage, state.opacity, look.softness, 1 / look.tileSize);
      offset.set(state.offsetX, state.offsetZ);
      // P08-R04: the clouds' colours follow the time of day, and fade into its haze.
      material.setColor3('cloudColor', color.set(...state.color));
      material.setColor3('cloudShade', shade.set(...state.shade));
      material.setColor3('fogColor', fogColor.set(...state.fog.color));
      material.setVector2('fogRange', fogRange.set(state.fog.start, state.fog.end));
      material.setVector4('cloudParams', params);
      material.setVector2('cloudOffset', offset);
      material.setVector3('cameraPosition', cameraPosition());
    },
  };
}

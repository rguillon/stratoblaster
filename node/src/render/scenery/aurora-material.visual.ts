import type { Scene } from '@babylonjs/core/scene';
import { Constants } from '@babylonjs/core/Engines/constants';
import { ShaderMaterial } from '@babylonjs/core/Materials/shaderMaterial';
import { Vector2 } from '@babylonjs/core/Maths/math.vector';
import type { AuroraMaterial } from './aurora-layer';

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

// Two curtains (green, violet) along slowly bending bands, with fine rays along them. auroraParams:
// time, strength. Everything moves over tens of seconds: nothing flashes (photosensitivity).
const FRAGMENT = /* glsl */ `
precision highp float;
varying vec3 vWorld;
uniform vec2 auroraParams;
uniform vec2 fogRange;
uniform vec3 cameraPosition;
void main() {
  float t = auroraParams.x;
  vec2 p = vWorld.xz / 520.0;
  float a = sin(p.x * 2.1 + sin(p.y * 0.9 + t * 0.07) * 1.8 + t * 0.05);
  float b = sin(p.x * 1.4 - p.y * 0.6 + sin(p.y * 1.7 - t * 0.06) * 1.5 - t * 0.04 + 2.0);
  float green = smoothstep(0.5, 1.0, a);
  float violet = smoothstep(0.62, 1.0, b);
  float rays = 0.6 + 0.4 * sin(p.x * 38.0 + sin(p.y * 3.0) * 4.0 + t * 0.25);
  float far = smoothstep(fogRange.x * 0.5, fogRange.y, distance(vWorld, cameraPosition));
  vec3 color = (vec3(0.15, 1.0, 0.5) * green + vec3(0.6, 0.25, 1.0) * violet) * rays;
  gl_FragColor = vec4(color * auroraParams.y * (0.2 + 0.8 * far) * 0.5, 1.0);
}
`;

/** The aurora's material (P08-R04): curtains added on top of the scene, no depth written. */
export function createAuroraMaterial(scene: Scene): AuroraMaterial {
  const material = new ShaderMaterial(
    'aurora',
    scene,
    { vertexSource: VERTEX, fragmentSource: FRAGMENT },
    {
      attributes: ['position'],
      uniforms: ['world', 'viewProjection', 'auroraParams', 'fogRange', 'cameraPosition'],
      needAlphaBlending: true,
    },
  );
  material.alphaMode = Constants.ALPHA_ADD;
  material.backFaceCulling = false;
  material.disableDepthWrite = true;
  const [params, fog] = [new Vector2(), new Vector2()];
  return {
    material,
    set: (frame) => {
      material.setVector2('auroraParams', params.set(frame.time, frame.strength));
      material.setVector2('fogRange', fog.set(frame.fog.start, frame.fog.end));
      material.setVector3('cameraPosition', frame.cameraPosition);
    },
  };
}

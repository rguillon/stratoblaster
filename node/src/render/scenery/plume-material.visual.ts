import type { Scene } from '@babylonjs/core/scene';
import { ShaderMaterial } from '@babylonjs/core/Materials/shaderMaterial';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import { Vector2, Vector4 } from '@babylonjs/core/Maths/math.vector';
import type { PlumeKind } from '../../config/plumes';
import type { PlumeMaterial } from './plume-layer';

// motion: time, seconds to rise, height, lean. size: bottom, top.
const VERTEX = /* glsl */ `
precision highp float;
attribute vec3 position;
attribute vec4 puff;
attribute float puffScale;
#include<instancesDeclaration>
uniform mat4 viewProjection;
uniform vec3 cameraPosition;
uniform vec3 cameraRight;
uniform vec3 cameraUp;
uniform vec4 motion;
uniform vec2 size;
varying vec2 vCorner;
varying float vFade;
varying float vDistance;
void main() {
#include<instancesVertex>
  // Each placed prop puffs out of step with the others.
  float offset = fract(dot(finalWorld[3].xz, vec2(0.0131, 0.0173)));
  float age = fract(motion.x / motion.y + puff.w + offset);
  float scale = length(finalWorld[0].xyz) * puffScale;
  vec3 foot = (finalWorld * vec4(puff.xyz, 1.0)).xyz;
  vec3 centre = foot + vec3(motion.w * age * age, motion.z * age, 0.0) * scale;
  float across = mix(size.x, size.y, sqrt(age)) * scale;
  vec3 p = centre + (cameraRight * position.x + cameraUp * position.y) * across;
  vCorner = position.xy * 2.0;
  vFade = smoothstep(0.0, 0.12, age) * (1.0 - smoothstep(0.5, 1.0, age));
  vDistance = distance(p, cameraPosition);
  gl_Position = viewProjection * vec4(p, 1.0);
}
`;

const FRAGMENT = /* glsl */ `
precision highp float;
varying vec2 vCorner;
varying float vFade;
varying float vDistance;
uniform vec3 plumeColor;
uniform float plumeAlpha;
uniform vec3 fogColor;
uniform vec2 fogRange;
void main() {
  float r = length(vCorner);
  // A soft, slightly lumpy puff.
  float lumps = 0.85 + 0.15 * sin(atan(vCorner.y, vCorner.x) * 5.0 + vFade * 3.0);
  float soft = 1.0 - smoothstep(0.25 * lumps, lumps, r);
  float fog = clamp((vDistance - fogRange.x) / (fogRange.y - fogRange.x), 0.0, 1.0);
  gl_FragColor = vec4(mix(plumeColor, fogColor, fog), soft * vFade * plumeAlpha * (1.0 - 0.6 * fog));
}
`;

const UNIFORMS = [
  'world',
  'viewProjection',
  'cameraPosition',
  'cameraRight',
  'cameraUp',
  'motion',
  'size',
  'plumeColor',
  'plumeAlpha',
  'fogColor',
  'fogRange',
] as const;

/**
 * The material of a kind of plume (phase 10, P10-R08): soft puffs facing the camera, rising from
 * the column's foot, growing, bending with the wind and fading out at the top, lit by the scene
 * (a little self-lit, as if from the fire below at night). Blended without writing depth, so the
 * ground in front hides it but it never hides what is drawn after it (the playfield).
 */
export function createPlumeMaterial(scene: Scene, kind: PlumeKind): PlumeMaterial {
  const material = new ShaderMaterial(
    'plume',
    scene,
    { vertexSource: VERTEX, fragmentSource: FRAGMENT },
    {
      attributes: ['position', 'puff', 'puffScale'],
      uniforms: [...UNIFORMS],
      needAlphaBlending: true,
    },
  );
  material.backFaceCulling = false;
  material.disableDepthWrite = true;
  material.setVector4('motion', new Vector4(0, kind.seconds, kind.height, kind.lean));
  material.setVector2('size', new Vector2(kind.size[0], kind.size[1]));
  material.setFloat('plumeAlpha', kind.alpha);
  const [motion, color, fogColor, fogRange] = [
    new Vector4(0, kind.seconds, kind.height, kind.lean),
    new Color3(),
    new Color3(),
    new Vector2(),
  ];
  return {
    material,
    set: (frame) => {
      motion.x = frame.time;
      material.setVector4('motion', motion);
      const lit = (i: 0 | 1 | 2) =>
        kind.color[i] * Math.max(kind.selfLit, Math.min(1, frame.light[i]));
      material.setColor3('plumeColor', color.set(lit(0), lit(1), lit(2)));
      material.setVector3('cameraPosition', frame.cameraPosition);
      material.setVector3('cameraRight', frame.right);
      material.setVector3('cameraUp', frame.up);
      material.setColor3('fogColor', fogColor.set(...frame.fog.color));
      material.setVector2('fogRange', fogRange.set(frame.fog.start, frame.fog.end));
    },
  };
}

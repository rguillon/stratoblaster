import { Scene } from '@babylonjs/core/scene';
import { FreeCamera } from '@babylonjs/core/Cameras/freeCamera';
import { HemisphericLight } from '@babylonjs/core/Lights/hemisphericLight';
import { DirectionalLight } from '@babylonjs/core/Lights/directionalLight';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { Color3, Color4 } from '@babylonjs/core/Maths/math.color';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import { createRng } from '../../core/math/rng';
import type { MenuBackdrop } from '../../render/game-view';
import { buildGradientRect, type ColoredGeometry } from '../../render/geometry/gradient-shapes';
import { stepModelAnimations } from '../../render/model-animation';
import { TITLE_LOOK as LOOK } from '../config/title-look';
import { buildBalancedShip } from './balanced-ship';
import { buildCityChunk, buildRain, buildSkyline } from './city-geometry';

function selfLit(name: string, scene: Scene, fog: boolean, intensity: number): StandardMaterial {
  const mat = new StandardMaterial(name, scene);
  // Vertex colours times a grey emissive: the mesh shows its vertex colours, unlit.
  mat.emissiveColor = new Color3(intensity, intensity, intensity);
  mat.diffuseColor = Color3.Black();
  mat.specularColor = Color3.Black();
  mat.disableLighting = true;
  mat.backFaceCulling = false;
  mat.fogEnabled = fog;
  return mat;
}

function coloredMesh(
  name: string,
  geo: ColoredGeometry,
  scene: Scene,
  fog: boolean,
  intensity = 1,
): Mesh {
  const mesh = new Mesh(name, scene);
  const data = new VertexData();
  data.positions = geo.positions;
  data.indices = geo.indices;
  data.colors = geo.colors;
  data.applyToMesh(mesh);
  mesh.material = selfLit(name, scene, fog, intensity);
  return mesh;
}

/** The sky and the distant skyline; returns the meshes that must not glow. */
function buildSky(scene: Scene, random: () => number): Mesh[] {
  const { sky, skyline } = LOOK;
  const skyMesh = coloredMesh(
    'title-sky',
    buildGradientRect(sky.width, sky.height, sky.stops),
    scene,
    false,
  );
  skyMesh.position.set(0, sky.centerY, sky.z);
  const towers = buildSkyline(skyline, random);
  const skylineMesh = coloredMesh('title-skyline', towers.structure, scene, false);
  const skylineLights = coloredMesh(
    'title-skyline-lights',
    towers.lights,
    scene,
    false,
    LOOK.neonIntensity,
  );
  for (const mesh of [skylineMesh, skylineLights]) mesh.position.set(0, skyline.y, skyline.z);
  return [skyMesh, skylineMesh];
}

/** Two copies of a city chunk, end to end, under one node that scrolls towards the camera. */
function buildCity(scene: Scene, random: () => number): { city: TransformNode; structure: Mesh[] } {
  const chunk = buildCityChunk(LOOK.city, random);
  const city = new TransformNode('title-city', scene);
  const structure = coloredMesh('title-city-structure', chunk.structure, scene, true);
  const lights = coloredMesh('title-city-lights', chunk.lights, scene, true, LOOK.neonIntensity);
  structure.parent = city;
  lights.parent = city;
  const structureCopy = structure.clone('title-city-structure-2', city);
  const lightsCopy = lights.clone('title-city-lights-2', city);
  structureCopy.position.z = LOOK.city.length;
  lightsCopy.position.z = LOOK.city.length;
  return { city, structure: [structure, structureCopy] };
}

function setUpScene(scene: Scene): void {
  const [r, g, b] = LOOK.horizon;
  scene.clearColor = new Color4(r, g, b, 1);
  scene.fogMode = Scene.FOGMODE_LINEAR;
  scene.fogColor = new Color3(r, g, b);
  scene.fogStart = LOOK.fog.start;
  scene.fogEnd = LOOK.fog.end;
  const camera = new FreeCamera('title-camera', new Vector3(...LOOK.camera.position), scene);
  camera.setTarget(new Vector3(...LOOK.camera.target));
  camera.fov = LOOK.camera.fov;
  new HemisphericLight('title-ambient', Vector3.Up(), scene).intensity = LOOK.lights.ambient;
  const key = new DirectionalLight('title-key', new Vector3(...LOOK.lights.keyDirection), scene);
  key.intensity = LOOK.lights.key;
}

/**
 * Darksynth backdrop of the menus (P01-R05, D-103): a night street between dark towers with lit
 * windows, neon signs and roof trims, scrolling towards the camera, a distant skyline, haze,
 * rain, and the balanced ship floating and turning above the street. Everything is generated
 * in code from a fixed seed. The ship is hidden on the ship select screen, which shows the
 * ships itself.
 */
export function buildTitleBackdrop(scene: Scene): MenuBackdrop {
  setUpScene(scene);
  const random = createRng(LOOK.seed);
  const sky = buildSky(scene, random);
  const { city, structure } = buildCity(scene, random);
  const rain = coloredMesh('title-rain', buildRain(LOOK.rain, random), scene, true);
  rain.position.y = LOOK.rain.y;
  const pivot = new TransformNode('title-ship', scene);
  pivot.position.set(...LOOK.ship.position);
  const ship = buildBalancedShip(scene);
  ship.parent = pivot;
  let time = 0;

  return {
    glowExcludedMeshes: [...sky, ...structure, rain],
    update: (dt) => {
      time += dt;
      const { city: c, rain: r, ship: s } = LOOK;
      city.position.z = -((time * c.scrollSpeed) % c.length);
      rain.position.y = r.y - ((time * r.speed) % r.height);
      pivot.rotation.y += s.rotationSpeedRadPerSec * dt;
      pivot.position.y = s.position[1] + s.bobAmplitude * Math.sin(2 * Math.PI * s.bobHz * time);
      stepModelAnimations(ship, dt);
    },
    showScreen: (screen) => {
      pivot.setEnabled(screen !== 'ship-select');
    },
  };
}

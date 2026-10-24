import type { Scene } from '@babylonjs/core/scene';
import type { Material } from '@babylonjs/core/Materials/material';
import { PBRMaterial } from '@babylonjs/core/Materials/PBR/pbrMaterial';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import type { Enemy } from '../../../core/entities/enemy';
import type { ColoredGeometry } from '../../../render/geometry/gradient-shapes';
import { SolidBuilder } from '../../../render/geometry/solids';
import type { EnemyModel } from '../../../render/game-view';
import { stepModelAnimations } from '../../../render/model-animation';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { buildReactorFlame, type FlameMaterials } from '../reactor-flame';

type Rgb = readonly [number, number, number];

interface EnemyMaterials {
  /** Dark metal, tinted by the vertex colours. */
  readonly hull: PBRMaterial;
  /** Unlit neon, coloured by the vertex colours. */
  readonly neon: StandardMaterial;
}

const CACHE = new WeakMap<Scene, EnemyMaterials>();

function unlit(name: string, scene: Scene): StandardMaterial {
  const mat = new StandardMaterial(name, scene);
  mat.emissiveColor = Color3.White();
  mat.diffuseColor = Color3.Black();
  mat.specularColor = Color3.Black();
  mat.disableLighting = true;
  return mat;
}

/** The scene's enemy materials, created on first use. */
export function enemyMaterials(scene: Scene): EnemyMaterials {
  let mats = CACHE.get(scene);
  if (!mats) {
    const hull = new PBRMaterial('enemy-hull', scene);
    hull.albedoColor = Color3.White();
    hull.metallic = ENEMY_LOOK.hull.metallic;
    hull.roughness = ENEMY_LOOK.hull.roughness;
    mats = { hull, neon: unlit('enemy-neon', scene) };
    CACHE.set(scene, mats);
  }
  return mats;
}

/** A flat-shaded, vertex-coloured mesh. */
export function meshOf(name: string, geo: ColoredGeometry, material: Material, scene: Scene): Mesh {
  const mesh = new Mesh(name, scene);
  const data = new VertexData();
  data.positions = geo.positions;
  data.indices = geo.indices;
  data.colors = geo.colors;
  const normals: number[] = [];
  VertexData.ComputeNormals(geo.positions, geo.indices, normals);
  data.normals = normals;
  data.applyToMesh(mesh);
  mesh.material = material;
  mesh.isPickable = false;
  return mesh;
}

/** Builders for the three parts of an enemy model. */
export interface EnemyParts {
  /** Dark metal (use the `ENEMY_LOOK.hull` shades). */
  readonly hull: SolidBuilder;
  /** Neon lights, always lit. */
  readonly neon: SolidBuilder;
  /** Lights that brighten as the next attack charges (`Enemy.charge`); white, tinted by `charge`. */
  readonly charge: SolidBuilder;
  /**
   * Adds a reactor whose nozzle opens at `at`, thrusting towards -Z (phase 5 review): a dark
   * nozzle, a glowing core and an animated flame, light blue on every enemy.
   */
  readonly reactor: (at: Vec3, radius: number) => void;
}

type Vec3 = readonly [number, number, number];

interface Reactor {
  readonly at: Vec3;
  readonly radius: number;
}

const FLAME_CACHE = new WeakMap<Scene, Map<string, FlameMaterials>>();

function glowing(name: string, color: Rgb, alpha: number, scene: Scene): StandardMaterial {
  const mat = unlit(name, scene);
  mat.emissiveColor = new Color3(...color);
  mat.alpha = alpha;
  mat.backFaceCulling = false;
  return mat;
}

/** Flame materials in `color`, shared by the scene's reactors of that colour. */
function flameMaterials(scene: Scene, color: Rgb): FlameMaterials {
  const look = ENEMY_LOOK.reactor;
  const byColor = FLAME_CACHE.get(scene) ?? new Map<string, FlameMaterials>();
  FLAME_CACHE.set(scene, byColor);
  const key = color.join(',');
  let mats = byColor.get(key);
  if (!mats) {
    const hot = color.map((c) => c + (1 - c) * look.whiten) as unknown as Rgb;
    mats = {
      exhaust: glowing(`enemy-exhaust-${key}`, color, look.exhaustAlpha, scene),
      flame: glowing(`enemy-flame-${key}`, hot, look.flameAlpha, scene),
      plasma: glowing(`enemy-plasma-${key}`, color, look.plasmaAlpha, scene),
    };
    byColor.set(key, mats);
  }
  return mats;
}

/** Nozzles in the hull, cores in the neon, and an animated flame per reactor under `root`. */
function addReactors(
  name: string,
  reactors: readonly Reactor[],
  parts: EnemyParts,
  root: TransformNode,
): void {
  const look = ENEMY_LOOK.reactor;
  const { color } = look;
  const behind = -Math.PI / 2;
  reactors.forEach(({ at: [x, y, z], radius }, i) => {
    const depth = radius * look.depth;
    // Pitched back, a band standing on `at` runs towards -Z: an open nozzle (no caps), with a
    // flat neon core across its mouth, facing back.
    const place = { at: [x, y, z + depth] as Vec3, pitch: behind };
    parts.hull.ring(radius, depth, look.sides, ENEMY_LOOK.hull.dark, place);
    const core = Array.from({ length: look.sides }, (_, k): Vec3 => {
      // Counter-clockwise seen from behind (-Z), so the face points back, out of the nozzle.
      const a = (-2 * Math.PI * k) / look.sides;
      return [x + Math.cos(a) * radius * look.core, y + Math.sin(a) * radius * look.core, z];
    });
    parts.neon.face(core, color);
    const node = new TransformNode(`${name}-reactor-${String(i)}`, root.getScene());
    node.position.set(x, y, 0);
    node.parent = root;
    buildReactorFlame(
      node.name,
      {
        nozzleZ: z - 0.05,
        length: radius * look.flameLength,
        diameter: radius * 2 * look.core * look.flameWidth,
        puffDiameter: radius * look.puffSize,
        sides: look.flameSides,
        light: { puffs: look.puffs },
      },
      node,
      flameMaterials(root.getScene(), color),
    );
  });
}

/**
 * Builds an enemy model from the parts `build` draws (logical pixels, nose +Z, Y up). The
 * charge lights get their own material, brightened to `chargeColor` by the enemy's charge.
 */
export function buildEnemyModel(
  name: string,
  scene: Scene,
  chargeColor: Rgb,
  build: (parts: EnemyParts) => void,
): EnemyModel {
  const reactors: Reactor[] = [];
  const parts: EnemyParts = {
    hull: new SolidBuilder(),
    neon: new SolidBuilder(),
    charge: new SolidBuilder(),
    reactor: (at, radius) => reactors.push({ at, radius }),
  };
  build(parts);
  const mats = enemyMaterials(scene);
  const root = new TransformNode(name, scene);
  addReactors(name, reactors, parts, root);
  for (const [part, material] of [
    [parts.hull, mats.hull],
    [parts.neon, mats.neon],
  ] as const) {
    if (part.geometry.positions.length > 0) {
      meshOf(`${name}-${material.name}`, part.geometry, material, scene).parent = root;
    }
  }
  const chargeMat = unlit(`${name}-charge`, scene);
  if (parts.charge.geometry.positions.length > 0) {
    meshOf(`${name}-charge`, parts.charge.geometry, chargeMat, scene).parent = root;
  }
  return {
    root,
    sync: (enemy: Enemy, dt: number) => {
      stepModelAnimations(root, dt);
      const k = ENEMY_LOOK.chargeIdle + (1 - ENEMY_LOOK.chargeIdle) * enemy.charge;
      chargeMat.emissiveColor.set(chargeColor[0] * k, chargeColor[1] * k, chargeColor[2] * k);
    },
  };
}

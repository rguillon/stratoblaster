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
import { ENEMY_LOOK } from '../../config/enemy-look';

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
  const parts: EnemyParts = {
    hull: new SolidBuilder(),
    neon: new SolidBuilder(),
    charge: new SolidBuilder(),
  };
  build(parts);
  const mats = enemyMaterials(scene);
  const root = new TransformNode(name, scene);
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
    sync: (enemy: Enemy) => {
      const k = ENEMY_LOOK.chargeIdle + (1 - ENEMY_LOOK.chargeIdle) * enemy.charge;
      chargeMat.emissiveColor.set(chargeColor[0] * k, chargeColor[1] * k, chargeColor[2] * k);
    },
  };
}

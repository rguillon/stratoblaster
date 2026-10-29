import type { Scene } from '@babylonjs/core/scene';
import type { Material } from '@babylonjs/core/Materials/material';
import { PBRMaterial } from '@babylonjs/core/Materials/PBR/pbrMaterial';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import type { ColoredGeometry } from '../../../render/geometry/gradient-shapes';
import { foldIntoFamily } from '../../../core/math/color';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { READABILITY } from '../../config/readability';
import type { FlameMaterials } from '../reactor-flame';

// The materials of the enemy models (P05, P14-R02, P16-R01).

type Rgb = readonly [number, number, number];

/** `color` moved into the enemies' colour family (P14-R02). */
export function enemyColor(color: Rgb): Rgb {
  return foldIntoFamily(color, READABILITY.families.enemy);
}

/** `geo` with its vertex colours moved into the enemies' colour family (P14-R02). */
export function inEnemyFamily(geo: ColoredGeometry): ColoredGeometry {
  const colors = [...geo.colors];
  for (let i = 0; i + 3 < colors.length; i += 4) {
    const rgb = enemyColor([colors[i] ?? 0, colors[i + 1] ?? 0, colors[i + 2] ?? 0]);
    [colors[i], colors[i + 1], colors[i + 2]] = rgb;
  }
  return { ...geo, colors };
}

export interface EnemyMaterials {
  /** Dark metal, tinted by the vertex colours. */
  readonly hull: PBRMaterial;
  /** Dark, waxy flesh (P16-R01), tinted by the vertex colours. */
  readonly flesh: PBRMaterial;
  /** Unlit neon, coloured by the vertex colours. */
  readonly neon: StandardMaterial;
}

const CACHE = new WeakMap<Scene, EnemyMaterials>();

export function unlit(name: string, scene: Scene): StandardMaterial {
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
    mats = {
      hull: metal('enemy-hull', Color3.White(), scene),
      flesh: fleshOf('enemy-flesh', Color3.White(), scene),
      neon: unlit('enemy-neon', scene),
    };
    CACHE.set(scene, mats);
  }
  return mats;
}

export function metal(name: string, albedo: Color3, scene: Scene): PBRMaterial {
  const hull = new PBRMaterial(name, scene);
  hull.albedoColor = albedo;
  hull.metallic = ENEMY_LOOK.hull.metallic;
  hull.roughness = ENEMY_LOOK.hull.roughness;
  hull.directIntensity = READABILITY.hullLight.direct;
  hull.environmentIntensity = READABILITY.hullLight.environment;
  return hull;
}

/** A waxy, barely metallic flesh (P16-R01), lit as the hulls are. */
export function fleshOf(name: string, albedo: Color3, scene: Scene): PBRMaterial {
  const mat = metal(name, albedo, scene);
  mat.metallic = ENEMY_LOOK.flesh.metallic;
  mat.roughness = ENEMY_LOOK.flesh.roughness;
  return mat;
}

/** The materials that show an enemy's body, flashed white when a boss part is hit. */
export const BODY_MATERIALS: ReadonlySet<string> = new Set(['enemy-hull', 'enemy-flesh']);

const TINTED_CACHE = new WeakMap<Scene, Map<string, PBRMaterial>>();

/**
 * The dark metal of an enemy whose neon is `neon` (phase 5 review: enemies easier to see on the
 * ground): tinted towards its neon colour, and faintly lit by it.
 */
export function tintedHull(scene: Scene, neon: Rgb, flesh = false): PBRMaterial {
  const look = ENEMY_LOOK.hull;
  const byColor = TINTED_CACHE.get(scene) ?? new Map<string, PBRMaterial>();
  TINTED_CACHE.set(scene, byColor);
  const key = `${flesh ? 'flesh' : 'hull'}:${neon.join(',')}`;
  let mat = byColor.get(key);
  if (!mat) {
    const tint = flesh ? ENEMY_LOOK.flesh.tint : look.tint;
    const [r, g, b] = neon.map((c) => 1 + (c - 1) * tint);
    const albedo = new Color3(r, g, b);
    mat = flesh ? fleshOf('enemy-flesh', albedo, scene) : metal('enemy-hull', albedo, scene);
    mat.emissiveColor = new Color3(...neon).scale(look.selfLight);
    byColor.set(key, mat);
  }
  return mat;
}

/** The rim colour of an enemy whose neon is `neon` (P14-R04). */
export function rimOf(neon: Rgb): Rgb {
  const { whiten, strength } = READABILITY.enemyOutline;
  const lift = (c: number) => (c + (1 - c) * whiten) * strength;
  return [lift(neon[0]), lift(neon[1]), lift(neon[2])];
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

const FLAME_CACHE = new WeakMap<Scene, Map<string, FlameMaterials>>();

export function glowing(name: string, color: Rgb, alpha: number, scene: Scene): StandardMaterial {
  const mat = unlit(name, scene);
  mat.emissiveColor = new Color3(...color);
  mat.alpha = alpha;
  mat.backFaceCulling = false;
  return mat;
}

/** Flame materials in `color`, shared by the scene's reactors of that colour. */
export function flameMaterials(scene: Scene, color: Rgb): FlameMaterials {
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

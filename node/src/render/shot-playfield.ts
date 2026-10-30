import type { Scene } from '@babylonjs/core/scene';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { CreateLineSystem } from '@babylonjs/core/Meshes/Builders/linesBuilder';
import { CreatePlane } from '@babylonjs/core/Meshes/Builders/planeBuilder';
import { CreateTorus } from '@babylonjs/core/Meshes/Builders/torusBuilder';
import type { LinesMesh } from '@babylonjs/core/Meshes/linesMesh';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { ShotTarget } from '../core/entities/shot-target';
import type { ShotStream } from '../core/entities/weapon';

type Rgb = readonly [number, number, number];

/*
 * Plumbing of a top-down playfield: XY plane at Z = 0, one world unit per logical pixel,
 * Y up, seen from -Z.
 */

function flatMaterial(name: string, color: Rgb, scene: Scene): StandardMaterial {
  const mat = new StandardMaterial(name, scene);
  mat.emissiveColor = new Color3(...color);
  mat.diffuseColor = Color3.Black();
  mat.specularColor = Color3.Black();
  mat.disableLighting = true;
  mat.backFaceCulling = false;
  return mat;
}

/**
 * A grid of lines every `cell` pixels over a `width × height` playfield, at `depth` behind the
 * playfield plane, so it stays behind the ships and the shots.
 */
export function buildPlayfieldGrid(
  scene: Scene,
  size: { readonly width: number; readonly height: number },
  cell: number,
  depth: number,
  color: Rgb,
): LinesMesh {
  const { width, height } = size;
  const lines: Vector3[][] = [];
  for (let x = 0; x <= width; x += cell) {
    lines.push([new Vector3(x, 0, depth), new Vector3(x, height, depth)]);
  }
  for (let y = 0; y <= height; y += cell) {
    lines.push([new Vector3(0, y, depth), new Vector3(width, y, depth)]);
  }
  const grid = CreateLineSystem('playfield-grid', { lines }, scene);
  grid.color = new Color3(...color);
  grid.isPickable = false;
  return grid;
}

/** Straight lines from the launch point along each stream (angles from +Y, positive to the right). */
export function buildStreamGuides(
  scene: Scene,
  muzzle: { readonly x: number; readonly y: number },
  streams: readonly ShotStream[],
  length: number,
  color: Rgb,
): LinesMesh {
  const lines = streams.map((s) => {
    const a = (s.angleDeg * Math.PI) / 180;
    const start = new Vector3(muzzle.x + s.offsetX, muzzle.y, 0.5);
    return [start, start.add(new Vector3(Math.sin(a) * length, Math.cos(a) * length, 0))];
  });
  const guides = CreateLineSystem('stream-guides', { lines }, scene);
  guides.color = new Color3(...color);
  guides.isPickable = false;
  return guides;
}

export interface TargetMarkerLook {
  readonly ring: { readonly thickness: number; readonly color: Rgb; readonly deadColor: Rgb };
  readonly healthBar: {
    readonly width: number;
    readonly height: number;
    readonly gap: number;
    readonly color: Rgb;
    readonly backColor: Rgb;
  };
}

interface Marker {
  readonly root: TransformNode;
  readonly ring: Mesh;
  readonly bar: Mesh;
  readonly back: Mesh;
}

/** A ring per target with a health bar under it; dead targets are drawn dim, without a bar. */
export class TargetMarkers {
  readonly #markers: Marker[];
  readonly #alive: StandardMaterial;
  readonly #dead: StandardMaterial;

  constructor(
    scene: Scene,
    targets: readonly ShotTarget[],
    private readonly look: TargetMarkerLook,
  ) {
    this.#alive = flatMaterial('target-ring', look.ring.color, scene);
    this.#dead = flatMaterial('target-ring-dead', look.ring.deadColor, scene);
    const barMat = flatMaterial('target-health', look.healthBar.color, scene);
    const backMat = flatMaterial('target-health-back', look.healthBar.backColor, scene);
    this.#markers = targets.map((target) => {
      const root = new TransformNode(`target-${String(target.id)}`, scene);
      const ring = CreateTorus(
        `target-${String(target.id)}-ring`,
        { diameter: target.radius * 2, thickness: look.ring.thickness, tessellation: 32 },
        scene,
      );
      ring.rotation.x = Math.PI / 2;
      const bar = CreatePlane(`target-${String(target.id)}-health`, { size: 1 }, scene);
      const back = CreatePlane(`target-${String(target.id)}-health-back`, { size: 1 }, scene);
      bar.material = barMat;
      back.material = backMat;
      for (const mesh of [ring, bar, back]) {
        mesh.parent = root;
        mesh.isPickable = false;
      }
      return { root, ring, bar, back };
    });
  }

  /** Moves the markers to their targets and shows their health. */
  sync(targets: readonly ShotTarget[]): void {
    const { healthBar: hb } = this.look;
    this.#markers.forEach((marker, i) => {
      const target = targets[i];
      if (!target) return;
      const alive = target.health > 0;
      const fraction = Math.max(0, target.health / target.maxHealth);
      marker.root.position.set(target.x, target.y, 0);
      marker.ring.material = alive ? this.#alive : this.#dead;
      const barY = -target.radius - hb.gap;
      marker.back.position.set(0, barY, 0.2);
      marker.back.scaling.set(hb.width, hb.height, 1);
      marker.bar.position.set((-hb.width * (1 - fraction)) / 2, barY, 0.1);
      marker.bar.scaling.set(Math.max(0.001, hb.width * fraction), hb.height, 1);
      marker.bar.setEnabled(alive);
      marker.back.setEnabled(alive);
    });
  }
}

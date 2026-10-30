import type { Material } from '@babylonjs/core/Materials/material';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { CreateCylinder } from '@babylonjs/core/Meshes/Builders/cylinderBuilder';
import { CreatePolyhedron } from '@babylonjs/core/Meshes/Builders/polyhedronBuilder';
import { addModelAnimation } from '../../render/model-animation';
import { REACTOR_FLAME as FLAME } from '../config/ship-look';
import { getShipMaterials } from './ship-materials';

// GD-61: the blue light behind each reactor is a living flame: an outer exhaust cone and a
// hotter inner cone that flicker in length, width and brightness, and plasma puffs that flow
// from the nozzle down the exhaust.

const TAU = Math.PI * 2;
/** Puffs fade in over this first fraction of their travel, then fade out. */
const PUFF_FADE_IN = 0.15;
/** `CreatePolyhedron` types. */
const TETRAHEDRON = 0;
const ICOSAHEDRON = 3;
/** Size of a puff at the end of its travel, relative to its size at the nozzle. */
const PUFF_END_SCALE = 0.3;

/** Irregular flicker in [-1, 1]: the mean of sines at the given frequencies, phase-shifted. */
export function flicker(timeSec: number, phase: number, hz: readonly number[]): number {
  let sum = 0;
  hz.forEach((f, i) => {
    sum += Math.sin(TAU * f * timeSec + phase * (i + 1));
  });
  return hz.length > 0 ? sum / hz.length : 0;
}

/** Stable phase in [0, 2π) derived from a name, so that reactors do not flicker in sync. */
export function reactorPhase(name: string): number {
  let hash = 2166136261; // FNV-1a
  for (let i = 0; i < name.length; i++) {
    hash = Math.imul(hash ^ name.charCodeAt(i), 16777619) >>> 0;
  }
  return (hash / 2 ** 32) * TAU;
}

/** How far puff `index` (of `count`) has travelled down the exhaust, in [0, 1). */
export function puffProgress(timeSec: number, index: number, count: number, speed: number): number {
  const p = (timeSec * speed + index / count) % 1;
  return p < 0 ? p + 1 : p;
}

/** Opacity of a puff at `progress`: fades in near the nozzle, then out towards the tip. */
export function puffOpacity(progress: number): number {
  return Math.min(1, progress / PUFF_FADE_IN) * (1 - progress);
}

/** Maps a flicker value in [-1, 1] to a factor in [1 - amount, 1 + amount]. */
function around(value: number, amount: number): number {
  return 1 + amount * value;
}

/** Maps a flicker value in [-1, 1] to a visibility in [1 - amount, 1]. */
function dimmed(value: number, amount: number): number {
  return 1 - (amount * (1 - value)) / 2;
}

interface Cone {
  /** At the nozzle; scaling it stretches the cone from the nozzle. */
  readonly pivot: TransformNode;
  readonly mesh: Mesh;
}

function cone(
  name: string,
  size: {
    readonly length: number;
    readonly diameter: number;
    readonly sides: number;
    readonly caps?: boolean;
  },
  material: Material,
  parent: TransformNode,
): Cone {
  const scene = parent.getScene();
  const pivot = new TransformNode(`${name}-pivot`, scene);
  pivot.parent = parent;
  const mesh = CreateCylinder(
    name,
    {
      height: size.length,
      diameterTop: 0,
      diameterBottom: size.diameter,
      tessellation: size.sides,
      ...(size.caps === false ? { cap: Mesh.NO_CAP } : {}),
    },
    scene,
  );
  // The cylinder grows along +Y; -90° around X points its tip towards -Z.
  mesh.rotation.x = -Math.PI / 2;
  mesh.position.z = -size.length / 2;
  mesh.material = material;
  mesh.isPickable = false;
  mesh.parent = pivot;
  return { pivot, mesh };
}

/** Exhaust flame of a reactor: starts at `nozzleZ` in `parent`'s space and points to -Z. */
export interface FlameSize {
  readonly nozzleZ: number;
  readonly length: number;
  /** Exhaust cone diameter at the nozzle. */
  readonly diameter: number;
  readonly puffDiameter: number;
  /** Number of sides of the flame cones (matches the polygonal nozzle). */
  readonly sides: number;
  /**
   * Lighter flames (enemies, phase 5 review): no caps on the cones (the base is hidden by the
   * nozzle, the tip is a point), this many puffs, and tetrahedra instead of icosahedra.
   * Player ships keep the defaults.
   */
  readonly light?: { readonly puffs: number };
}

/** Materials of a flame: the outer exhaust cone, the hot inner cone and the plasma puffs. */
export interface FlameMaterials {
  readonly exhaust: Material;
  readonly flame: Material;
  readonly plasma: Material;
}

/** Plasma puffs of a flame; the animation places them along the exhaust. */
function buildPuffs(
  name: string,
  diameter: number,
  material: Material,
  parent: TransformNode,
  light?: { readonly puffs: number },
): Mesh[] {
  const scene = parent.getScene();
  return Array.from({ length: light ? light.puffs : FLAME.puffCount }, (_, i) => {
    // An icosahedron (20 triangles): small, translucent and moving, it reads as a blob. Light
    // flames use a tetrahedron (4 triangles).
    const puff = CreatePolyhedron(
      `${name}-puff-${String(i)}`,
      { type: light ? TETRAHEDRON : ICOSAHEDRON, size: diameter / 2 },
      scene,
    );
    puff.material = material;
    puff.isPickable = false;
    puff.parent = parent;
    return puff;
  });
}

/** The player ships' blue flame materials (GD-61). */
function playerFlame(parent: TransformNode): FlameMaterials {
  const mats = getShipMaterials(parent.getScene());
  return { exhaust: mats.reactorExhaust, flame: mats.reactorFlame, plasma: mats.reactorPlasma };
}

/**
 * Builds an animated reactor flame (GD-61) under `parent`, named after `name`, blue like the
 * player ships' unless other `materials` are given (enemies, phase 5 review).
 */
export function buildReactorFlame(
  name: string,
  size: FlameSize,
  parent: TransformNode,
  materials: FlameMaterials = playerFlame(parent),
): void {
  const { sides } = size;
  const caps = !size.light;
  const outer = cone(`${name}-exhaust`, { ...size, caps }, materials.exhaust, parent);
  const inner = cone(
    `${name}-flame`,
    {
      length: size.length * FLAME.coreLength,
      diameter: size.diameter * FLAME.coreWidth,
      sides,
      caps,
    },
    materials.flame,
    parent,
  );
  for (const { pivot } of [outer, inner]) pivot.position.z = size.nozzleZ;

  const puffs = buildPuffs(name, size.puffDiameter, materials.plasma, parent, size.light);

  const phase = reactorPhase(name);
  const hz = FLAME.flickerHz;
  let time = 0;
  const apply = (): void => {
    const [outerLength, innerLength, width, brightness] = [0, 1, 2, 3].map((k) =>
      flicker(time, phase + k * 1.7, hz),
    ) as [number, number, number, number];
    const w = around(width, FLAME.widthFlicker);
    outer.pivot.scaling.set(w, w, around(outerLength, FLAME.lengthFlicker));
    inner.pivot.scaling.set(w, w, around(innerLength, FLAME.lengthFlicker));
    outer.mesh.visibility = dimmed(brightness, FLAME.brightnessFlicker);
    inner.mesh.visibility = dimmed(-brightness, FLAME.brightnessFlicker);
    puffs.forEach((puff, i) => {
      const p = puffProgress(time, i, puffs.length, FLAME.puffSpeed);
      // Nudged off the nozzle plane so the puff always sits behind it.
      puff.position.z = size.nozzleZ - 0.01 - p * size.length;
      const s = 1 - (1 - PUFF_END_SCALE) * p;
      puff.scaling.set(s, s, s * 1.6);
      puff.visibility = puffOpacity(p);
    });
  };
  apply();
  addModelAnimation(parent, (dtSeconds) => {
    time += dtSeconds;
    apply();
  });
}

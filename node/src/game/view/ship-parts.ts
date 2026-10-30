import type { Scene } from '@babylonjs/core/scene';
import type { Material } from '@babylonjs/core/Materials/material';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { CreateDisc } from '@babylonjs/core/Meshes/Builders/discBuilder';
import { CreatePolyhedron } from '@babylonjs/core/Meshes/Builders/polyhedronBuilder';
import type { Vector3 } from '@babylonjs/core/Maths/math.vector';
import { createFacetedLatheAlongZ, type LatheSection } from '../../render/geometry/lathe-z';
import type { OutlinePoint } from '../../render/geometry/outline';
import { createPrism } from '../../render/geometry/prism';
import { REACTOR_FLAME } from '../config/ship-look';
import { buildReactorFlame } from './reactor-flame';
import { getShipMaterials } from './ship-materials';

/** Sides of polygonal parts (nacelles, canopies, intakes, pods): a hexagonal section. */
export const PART_FACETS = 6;
/** Section of fuselages: a smooth, finely faceted top over a low-poly 3-facet belly. */
export const BODY_SECTION: LatheSection = { upper: 20, lower: 3 };

/** Semantic role of a ship node, stored in `node.metadata.part` (used by tests and future FX). */
export type ShipPart = 'body' | 'canopy' | 'wing' | 'tail' | 'reactor' | 'light';

/** Tags a node with its ship part and returns it. */
export function tagPart<T extends TransformNode>(node: T, part: ShipPart): T {
  node.metadata = { part };
  return node;
}

/** Returns the ship part a node was tagged with, if any. */
export function partOf(node: TransformNode): ShipPart | undefined {
  const metadata = node.metadata as { part?: ShipPart } | null;
  return metadata?.part;
}

/** Mirrors a planform outline across the ship's centre line (X = 0). */
export function mirrorX(outline: readonly OutlinePoint[]): OutlinePoint[] {
  return outline.map(([x, z]) => [-x, z]);
}

/** Creates a flat panel (wing, tail...) with the given material, parented to `parent`. */
export function panel(
  name: string,
  outline: readonly OutlinePoint[],
  thickness: number,
  material: Material,
  parent: TransformNode,
): Mesh {
  const mesh = createPrism(name, outline, thickness, parent.getScene());
  mesh.material = material;
  mesh.parent = parent;
  return mesh;
}

/** Creates a thin panel lying `y` above (or below, if negative) its parent's plane: trim, stripes. */
export function plate(
  name: string,
  outline: readonly OutlinePoint[],
  y: number,
  material: Material,
  parent: TransformNode,
): Mesh {
  const mesh = panel(name, outline, PLATE_THICKNESS, material, parent);
  mesh.position.y = y;
  return mesh;
}

/** Creates a small blue light (tagged `light`) at `position` in `parent`'s space. */
export function navLight(name: string, position: Vector3, parent: TransformNode): Mesh {
  const scene = parent.getScene();
  const mesh = tagPart(
    // An octahedron (8 triangles): at this size and glowing, it reads as a round light.
    CreatePolyhedron(name, { type: 1, size: NAV_LIGHT_SIZE / 2 }, scene),
    'light',
  );
  mesh.material = getShipMaterials(scene).navLight;
  mesh.position.copyFrom(position);
  mesh.parent = parent;
  return mesh;
}

/** Creates a polygonal bar along Z (4 sides: a diamond section), centred on `position`. */
export function facetedRod(
  name: string,
  size: { readonly length: number; readonly radius: number },
  position: Vector3,
  material: Material,
  parent: TransformNode,
  sides = 4,
): Mesh {
  const { length: l, radius: r } = size;
  const mesh = createFacetedLatheAlongZ(
    name,
    [
      [l / 2, 0],
      [l / 2, r],
      [-l / 2, r],
      [-l / 2, 0],
    ],
    sides,
    parent.getScene(),
  );
  mesh.position.copyFrom(position);
  mesh.material = material;
  mesh.parent = parent;
  return mesh;
}

const PLATE_THICKNESS = 0.012;
const NAV_LIGHT_SIZE = 0.07;

/** Size of a reactor: nacelle radius and length, in world units. */
export interface ReactorSize {
  readonly radius: number;
  readonly length: number;
}

const EXHAUST_LENGTH = 0.8; // relative to the nacelle length
const EXHAUST_WIDTH = 1.5; // relative to the nacelle radius
const CORE_RADIUS = 0.8; // relative to the nacelle radius

/** Accent rings around the front of the nacelle and its nozzle. */
function addReactorRings(name: string, size: ReactorSize, root: TransformNode): void {
  const scene = root.getScene();
  const { radius: r, length: l } = size;
  const half = r * 0.09; // half the ring's width and thickness
  for (const [ring, z, scale] of [
    ['front', l * 0.3, 1.02],
    ['rear', -l / 2, 0.9],
  ] as const) {
    // A polygonal band: an open lathe around the nacelle. Closed loop; the outer side runs
    // towards +Z so its faces point outward.
    const mesh = createFacetedLatheAlongZ(
      `${name}-${ring}-ring`,
      [
        [half, r * scale - half],
        [-half, r * scale - half],
        [-half, r * scale + half],
        [half, r * scale + half],
        [half, r * scale - half],
      ],
      PART_FACETS,
      scene,
    );
    mesh.position.z = z;
    mesh.material = getShipMaterials(scene).accent;
    mesh.parent = root;
  }
}

/**
 * Builds a reactor centred on its origin, thrusting towards -Z: a hexagonal metal nacelle,
 * a glowing blue core at the nozzle and an animated blue flame behind it.
 */
export function buildReactor(name: string, size: ReactorSize, scene: Scene): TransformNode {
  const mats = getShipMaterials(scene);
  const { radius: r, length: l } = size;
  const root = tagPart(new TransformNode(name, scene), 'reactor');

  const profile = [
    [l / 2, 0],
    [l / 2, r * 0.75],
    [l * 0.3, r],
    [-l * 0.4, r * 0.95],
    [-l / 2, r * 0.85],
    [-l / 2, 0],
  ] as const;
  const nacelle = createFacetedLatheAlongZ(`${name}-nacelle`, profile, PART_FACETS, scene);
  nacelle.material = mats.nozzle;
  nacelle.parent = root;

  addReactorRings(name, size, root);

  const core = CreateDisc(
    `${name}-core`,
    { radius: r * CORE_RADIUS, tessellation: PART_FACETS },
    scene,
  );
  core.convertToFlatShadedMesh();
  core.position.z = -l / 2 - 0.01;
  core.material = mats.reactorCore;
  core.parent = root;

  buildReactorFlame(
    name,
    {
      nozzleZ: core.position.z,
      length: l * EXHAUST_LENGTH,
      diameter: r * EXHAUST_WIDTH,
      puffDiameter: r * REACTOR_FLAME.puffSize,
      sides: PART_FACETS,
    },
    root,
  );
  return root;
}

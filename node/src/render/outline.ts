import { Constants } from '@babylonjs/core/Engines/constants';
import type { AbstractMesh } from '@babylonjs/core/Meshes/abstractMesh';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import '@babylonjs/core/Rendering/outlineRenderer';

type Rgb = readonly [number, number, number];

/** What a mesh's `metadata` holds when it asks for a rim glow (see {@link setOutline}). */
interface OutlineMetadata {
  readonly outline: Rgb;
}

function isOutlined(metadata: unknown): metadata is OutlineMetadata {
  return typeof metadata === 'object' && metadata !== null && 'outline' in metadata;
}

/**
 * Asks for a rim glow of `color` round `mesh`'s silhouette (phase 14, P14-R03, R04), drawn by an
 * {@link OutlineLayer} wherever the mesh is shown. Keeps the mesh's other metadata.
 */
export function setOutline(mesh: AbstractMesh, color: Rgb): void {
  const old: unknown = mesh.metadata;
  mesh.metadata = { ...(typeof old === 'object' && old !== null ? old : {}), outline: color };
}

/** The rim glow `mesh` asks for, if any. */
export function outlineOf(mesh: AbstractMesh): Rgb | undefined {
  const metadata: unknown = mesh.metadata;
  return isOutlined(metadata) ? metadata.outline : undefined;
}

/** Whether `mesh` is solid: not added on nor see-through (glows and flames get no rim). */
function isSolid(mesh: AbstractMesh): boolean {
  const material = mesh.material;
  if (!material || mesh.hasVertexAlpha) return false;
  return material.alpha >= 1 && material.alphaMode !== Constants.ALPHA_ADD;
}

/** Asks for a rim glow of `color` round every solid mesh of the model under `root`. */
export function outlineModel(root: TransformNode, color: Rgb): void {
  for (const mesh of root.getChildMeshes(false)) if (isSolid(mesh)) setOutline(mesh, color);
}

/** How the rim glows look: width in world units (logical pixels on the playfield), strength. */
export interface OutlineLook {
  readonly width: number;
  readonly intensity: number;
}

/**
 * Draws a thin rim round the silhouette of the meshes that ask for one (phase 14): each such
 * mesh is drawn a second time, a little fatter, in its rim colour, behind itself, so its shape
 * stands out from whatever is behind it. No screen-wide pass: one more draw per mesh.
 */
export class OutlineLayer {
  constructor(private readonly look: OutlineLook) {}

  /** Gives `mesh` its rim if it asks for one. Returns whether it did. */
  add(mesh: AbstractMesh): boolean {
    const color = outlineOf(mesh);
    if (!color || !(mesh instanceof Mesh)) return false;
    // The rim is pushed out in the mesh's own space: undo its scale, so it is as wide on all.
    mesh.computeWorldMatrix(true);
    const scale = Math.abs(mesh.absoluteScaling.x) || 1;
    const [r, g, b] = color;
    mesh.renderOutline = true;
    mesh.outlineColor = new Color3(r, g, b).scale(this.look.intensity);
    mesh.outlineWidth = this.look.width / scale;
    return true;
  }
}

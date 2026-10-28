import type { Scene } from '@babylonjs/core/scene';
import type { Material } from '@babylonjs/core/Materials/material';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { Color3, Color4 } from '@babylonjs/core/Maths/math.color';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import { CreateGround } from '@babylonjs/core/Meshes/Builders/groundBuilder';
import { CreateLineSystem } from '@babylonjs/core/Meshes/Builders/linesBuilder';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { TileRules } from '../core/scenery/scenery-level';
import type { ColoredGeometry } from '../render/geometry/gradient-shapes';
import { meshOf } from '../render/scenery/prop-field';
import { addPiece, type TileRoadLook } from '../render/scenery/tile-road-geometry';
import { PROP_VIEWER_CONFIG as CFG } from '../config/prop-viewer';
import type { TileLayout } from './prop-viewer-layout';

// The ground of the `props/` page (phase 15): a plain floor over the layout, the lines of the
// grid of tiles over it, and the road tiles of the layout.

/** The grid of tiles and the look of its roads. */
export interface ViewerTiles {
  readonly tile: TileRules;
  /** None: no road is drawn. */
  readonly look?: TileRoadLook;
}

const flat = (): number => 0;

/** [x0, x1, z0, z1], in world units. */
type Bounds = readonly [number, number, number, number];

function floor(scene: Scene, [x0, x1, z0, z1]: Bounds, parent: TransformNode): void {
  const ground = CreateGround('props-ground', { width: x1 - x0, height: z1 - z0 }, scene);
  ground.position.set((x0 + x1) / 2, 0, (z0 + z1) / 2);
  const material = new StandardMaterial('props-ground', scene);
  material.diffuseColor = new Color3(...CFG.ground.color);
  material.specularColor = Color3.Black();
  ground.material = material;
  ground.isPickable = false;
  ground.parent = parent;
}

/** Lines along every tile edge of [x0, x1] × [z0, z1] (world units), a little above the roads. */
function gridLines(
  scene: Scene,
  [x0, x1, z0, z1]: Bounds,
  size: number,
  parent: TransformNode,
): void {
  const y = CFG.grid.height;
  const lines: Vector3[][] = [];
  for (let x = x0; x <= x1 + 1e-6; x += size)
    lines.push([new Vector3(x, y, z0), new Vector3(x, y, z1)]);
  for (let z = z0; z <= z1 + 1e-6; z += size)
    lines.push([new Vector3(x0, y, z), new Vector3(x1, y, z)]);
  const color = new Color4(...CFG.grid.color, 1);
  const mesh = CreateLineSystem(
    'props-tile-grid',
    { lines, colors: lines.map((l) => l.map(() => color)) },
    scene,
  );
  mesh.isPickable = false;
  mesh.parent = parent;
}

/**
 * The floor, the grid and the roads of `layout`, under one node; the floor reaches `margin`
 * tiles beyond the layout.
 */
export function buildViewerGround(
  scene: Scene,
  layout: TileLayout,
  tiles: ViewerTiles,
  material: Material,
): TransformNode {
  const root = new TransformNode('props-floor', scene);
  const t = tiles.tile.size;
  const m = CFG.ground.margin;
  const [bx0, bx1, bz0, bz1] = layout.bounds;
  const bounds: Bounds = [(bx0 - m) * t, (bx1 + m) * t, (bz0 - m) * t, (bz1 + m) * t];
  floor(scene, bounds, root);
  gridLines(scene, bounds, t, root);
  const { look } = tiles;
  if (look && layout.roads.length > 0) {
    const geo: ColoredGeometry = { positions: [], indices: [], colors: [] };
    for (const piece of layout.roads) addPiece(geo, piece, tiles.tile, look, flat);
    const roads = meshOf('props-roads', geo, material, scene);
    roads.parent = root;
    roads.setEnabled(true);
  }
  return root;
}

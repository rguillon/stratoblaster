import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import { Scene } from '@babylonjs/core/scene';
import { ArcRotateCamera } from '@babylonjs/core/Cameras/arcRotateCamera';
import { HemisphericLight } from '@babylonjs/core/Lights/hemisphericLight';
import { DirectionalLight } from '@babylonjs/core/Lights/directionalLight';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { Color3, Color4 } from '@babylonjs/core/Maths/math.color';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { GameDefinition } from '../core/content/game-definition';
import type { GameView, PropGroup } from '../render/game-view';
import { applyShowcaseEnvironment } from '../render/environment/showcase-environment.visual';
import type { ColoredGeometry } from '../render/geometry/gradient-shapes';
import { meshOf } from '../render/scenery/prop-field';
import { PropViewerPanel, type PropViewerSelection } from '../ui/prop-viewer-panel';
import { PROP_VIEWER_CONFIG as CFG } from '../config/prop-viewer';
import { buildViewerGround, type ViewerTiles } from './prop-viewer-ground';
import { tileLayout } from './prop-viewer-layout';

/** Options of {@link startPropViewer}. */
export interface PropViewerOptions {
  /** Procedural image-based lighting and glow. Needs a real WebGL engine. */
  readonly environment: boolean;
  readonly doc: Pick<Document, 'createElement'>;
  readonly panelParent: HTMLElement;
  /** Where the arrow keys are listened to. None when omitted. */
  readonly keyboardTarget?: Pick<Window, 'addEventListener'>;
  /** Runs the engine's render loop (off in e2e tests, which render on demand). */
  readonly renderLoop: boolean;
}

/** One prop laid out on the grid. */
export interface ShownProp {
  readonly id: string;
  readonly root: TransformNode;
  readonly triangles: number;
  /** Width (X) and depth (Z) of its footprint, and its height. */
  readonly size: readonly [number, number, number];
}

/** Handle on a running props viewer. */
export interface RunningPropViewer {
  readonly scene: Scene;
  readonly camera: ArcRotateCamera;
  readonly panel: PropViewerPanel;
  readonly groups: readonly PropGroup[];
  /** The props of the shown group. */
  readonly props: readonly ShownProp[];
  select(selection: PropViewerSelection): void;
  dispose(): void;
}

/** Extent of `geo` along each axis: [min x, max x, max y, min z, max z]. */
function extent(geo: ColoredGeometry): [number, number, number, number, number] {
  const e: [number, number, number, number, number] = [0, 0, 0, 0, 0];
  for (let i = 0; i < geo.positions.length; i += 3) {
    const [x, y, z] = [geo.positions[i] ?? 0, geo.positions[i + 1] ?? 0, geo.positions[i + 2] ?? 0];
    e[0] = Math.min(e[0], x);
    e[1] = Math.max(e[1], x);
    e[2] = Math.max(e[2], y);
    e[3] = Math.min(e[3], z);
    e[4] = Math.max(e[4], z);
  }
  return e;
}

function materials(scene: Scene): { structure: StandardMaterial; lights: StandardMaterial } {
  const structure = new StandardMaterial('prop-structure', scene);
  structure.diffuseColor = Color3.White();
  structure.specularColor = new Color3(0.1, 0.1, 0.1);
  const lights = new StandardMaterial('prop-lights', scene);
  lights.emissiveColor = new Color3(CFG.lightIntensity, CFG.lightIntensity, CFG.lightIntensity);
  lights.diffuseColor = Color3.Black();
  lights.specularColor = Color3.Black();
  lights.disableLighting = true;
  return { structure, lights };
}

function addLights(scene: Scene): void {
  const { lights } = CFG;
  new HemisphericLight('props-ambient', Vector3.Up(), scene).intensity = lights.ambientIntensity;
  const key = new DirectionalLight('props-key', new Vector3(...lights.keyDirection), scene);
  key.intensity = lights.keyIntensity;
}

/** The props of one group, each on whole tiles of the grid of the ground (phase 15). */
class PropGrid {
  props: readonly ShownProp[] = [];
  /** Index of the group shown; -1 before the first. */
  group = -1;
  readonly #materials;
  #ground: TransformNode | undefined;

  constructor(
    private readonly scene: Scene,
    private readonly models: GameView['scenery']['propModels'],
    private readonly tiles: ViewerTiles,
  ) {
    this.#materials = materials(scene);
  }

  /** Shows the props of `group` (index `index`) in place of the ones shown. */
  show(group: PropGroup | undefined, index: number): void {
    for (const p of this.props) p.root.dispose();
    this.#ground?.dispose();
    const built = (group?.ids ?? []).flatMap((id) => this.#build(id));
    const t = this.tiles.tile.size;
    const tilesOf = (v: number): number => Math.max(1, Math.ceil(v / t - 1e-6));
    const streets = group?.streets === true && this.tiles.look !== undefined;
    const layout = tileLayout(
      built.map(({ prop }) => [tilesOf(prop.size[0]), tilesOf(prop.size[1])] as const),
      streets ? 1 : Math.ceil(CFG.gap / t),
      streets,
    );
    built.forEach(({ prop, mid }, i) => {
      const [cx, cz] = layout.centres[i] ?? [0, 0];
      prop.root.position.set(cx * t - mid[0], 0, cz * t - mid[1]);
    });
    this.props = built.map((b) => b.prop);
    this.#ground = buildViewerGround(this.scene, layout, this.tiles, this.#materials.structure);
    this.group = index;
  }

  /** The prop `id`, and the middle of its footprint in its own frame. */
  #build(id: string): { prop: ShownProp; mid: [number, number] }[] {
    const factory = this.models[id];
    if (!factory) return [];
    const geometry = factory();
    const root = new TransformNode(`prop-${id}`, this.scene);
    for (const [geo, material] of [
      [geometry.structure, this.#materials.structure],
      [geometry.lights, this.#materials.lights],
    ] as const) {
      if (!geo || geo.indices.length === 0) continue;
      const mesh = meshOf(id, geo, material, this.scene);
      mesh.parent = root;
      mesh.isPickable = true;
      mesh.setEnabled(true);
    }
    const [x0, x1, height, z0, z1] = extent(geometry.structure);
    const triangles =
      (geometry.structure.indices.length + (geometry.lights?.indices.length ?? 0)) / 3;
    const prop: ShownProp = { id, root, triangles, size: [x1 - x0, z1 - z0, height] };
    return [{ prop, mid: [(x0 + x1) / 2, (z0 + z1) / 2] }];
  }
}

function createCamera(scene: Scene): ArcRotateCamera {
  const { alpha, beta, fov } = CFG.camera;
  const camera = new ArcRotateCamera('props-camera', alpha, beta, 100, Vector3.Zero(), scene);
  camera.fov = fov;
  camera.minZ = 0.5;
  camera.maxZ = 5000;
  camera.wheelDeltaPercentage = 0.01;
  if (scene.getEngine().getRenderingCanvas()) camera.attachControl(true);
  return camera;
}

/** Centres `camera` on `prop` and returns its readout. */
function frame(camera: ArcRotateCamera, prop: ShownProp): string {
  const [w, d, h] = prop.size;
  camera.setTarget(prop.root.position.add(new Vector3(0, h / 2, 0)));
  camera.radius = (Math.max(w, d, h, 1) * CFG.camera.framingMargin) / Math.tan(camera.fov / 2);
  return describe(prop);
}

/** The readout of `prop`: its id, size and triangle count. */
export function describe({ id, size, triangles }: ShownProp): string {
  const [w, d, h] = size.map((v) => String(Math.round(v)));
  return `${id} — ${w ?? ''} × ${d ?? ''} × ${h ?? ''} — ${String(triangles)} triangles`;
}

/** Picks a prop on a click on the scene, or the next or previous one with the arrow keys. */
function listenPicks(
  scene: Scene,
  grid: PropGrid,
  panel: PropViewerPanel,
  select: (selection: PropViewerSelection) => void,
  keys: PropViewerOptions['keyboardTarget'],
): void {
  scene.onPointerDown = (_event, pick) => {
    const picked = pick.pickedMesh?.parent;
    const index = grid.props.findIndex((p) => p.root === picked);
    if (index >= 0) select({ group: grid.group, prop: index });
  };
  keys?.addEventListener('keydown', (event) => {
    const step = { ArrowRight: 1, ArrowLeft: -1 }[event.key];
    const count = grid.props.length;
    if (!step || count === 0) return;
    select({ group: grid.group, prop: (panel.selection.prop + step + count) % count });
  });
}

/**
 * The props viewer page (`props/`, reviewer 2026-10-28): the prop models of one group laid out
 * on the grid of tiles of a plain ground (with road tiles around the models made for the grid), a turning camera, and a panel to pick the group and a prop, which
 * the camera then centres on.
 */
export function startPropViewer(
  engine: AbstractEngine,
  game: GameDefinition<GameView>,
  options: PropViewerOptions,
): RunningPropViewer {
  const { propModels } = game.view.scenery;
  const groups = game.view.scenery.propGroups ?? [{ label: 'Props', ids: Object.keys(propModels) }];
  const scene = new Scene(engine);
  scene.clearColor = new Color4(...CFG.clearColor);
  addLights(scene);
  if (options.environment) applyShowcaseEnvironment(scene, { ...CFG.environment, glow: CFG.glow });
  const camera = createCamera(scene);
  const tiles = game.view.scenery.propTiles ?? { tile: CFG.tile };
  const grid = new PropGrid(scene, propModels, tiles);

  const select = (selection: PropViewerSelection): void => {
    if (selection.group !== grid.group) grid.show(groups[selection.group], selection.group);
    panel.update(selection);
    const prop = grid.props[selection.prop];
    if (prop) panel.setReadout(frame(camera, prop));
  };

  const panel = new PropViewerPanel({
    doc: options.doc,
    parent: options.panelParent,
    groups,
    initial: { group: 0, prop: 0 },
    onChange: select,
  });
  select(panel.selection);

  listenPicks(scene, grid, panel, select, options.keyboardTarget);
  if (options.renderLoop) {
    engine.runRenderLoop(() => {
      scene.render();
    });
  }

  return {
    scene,
    camera,
    panel,
    groups,
    get props() {
      return grid.props;
    },
    select,
    dispose: () => {
      engine.stopRenderLoop();
      panel.root.remove();
      scene.dispose();
    },
  };
}

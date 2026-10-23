import type { Scene } from '@babylonjs/core/scene';
import { FreeCamera } from '@babylonjs/core/Cameras/freeCamera';
import type { DirectionalLight } from '@babylonjs/core/Lights/directionalLight';
import { CreateGround } from '@babylonjs/core/Meshes/Builders/groundBuilder';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { LogicalScreen } from '../../core/content/game-definition';
import { HeightField } from '../../core/scenery/height-field';
import { PropPlacer } from '../../core/scenery/prop-placement';
import { levelRoads } from '../../core/scenery/road-network';
import type { SceneryLevel } from '../../core/scenery/scenery-level';
import {
  framePlayfield,
  visibleGround,
  type GroundWindow,
  type PlayfieldFraming,
} from './playfield-framing';
import { checkPropModels, PropField } from './prop-field';
import type { CloudMaterial, SceneryKit, SceneryKitFactory } from './scenery-kit';
import type {
  CloudLayerLook,
  PlayfieldCameraLook,
  PropModelFactory,
  SceneryLook,
} from './scenery-look';
import { lightScenery, snappedLightPosition } from './scenery-lighting';
import { TerrainChunks } from './terrain-chunks';
import { RoadLayers } from './road-field';

/** Engine settings of a {@link SceneryStage}. */
export interface SceneryStageConfig {
  /** Terrain chunk length along Z and grid cell size. */
  readonly chunkLength: number;
  readonly cell: number;
  /** Extra ground generated around what the camera sees. */
  readonly margin: number;
  /** Smallest gap between the highest ground and a cloud layer. */
  readonly cloudClearance: number;
  /** How far behind the scene the sun is placed, for its shadows. */
  readonly sunDistance: number;
  /** Far clipping distance of the camera. */
  readonly farClip: number;
}

export interface SceneryStageOptions {
  readonly screen: LogicalScreen;
  readonly camera: PlayfieldCameraLook;
  readonly level: SceneryLevel;
  readonly look: SceneryLook;
  readonly propModels: Readonly<Record<string, PropModelFactory>>;
  readonly kit: SceneryKitFactory;
  readonly config: SceneryStageConfig;
}

/** Group of all but the clouds, drawn next: a glow composed after it stays under them. */
export const BELOW_CLOUDS_GROUP = 0;

/** A cloud layer's live settings (P04-R03). */
export interface CloudLayerState {
  enabled: boolean;
  coverage: number;
  opacity: number;
}

interface CloudLayer {
  readonly look: CloudLayerLook;
  /** Z of the middle of what the camera sees at the layer's altitude, relative to the camera. */
  readonly middle: number;
  readonly mesh: Mesh;
  readonly material: CloudMaterial;
  readonly state: CloudLayerState;
}

/** Lowest ground of a level: its sea, or the lowest relief. */
function lowestGround(level: SceneryLevel): number {
  const lows = level.sections.map((s) => s.relief.base - s.relief.amplitude);
  return level.sea ? level.sea.level : Math.min(...lows);
}

/**
 * The ground of a scrolling level seen by the tilted playfield camera (P04): sculpted terrain
 * in chunks, an optional sea, cloud layers and props, lit by a low sun. {@link update} moves
 * everything to a distance along the level.
 */
export class SceneryStage {
  readonly camera: FreeCamera;
  readonly framing: PlayfieldFraming;
  readonly sun: DirectionalLight;
  readonly kit: SceneryKit;
  readonly clouds: readonly CloudLayerState[];
  #field: HeightField;
  #placer: PropPlacer;
  #seed: number;
  readonly #chunks: TerrainChunks;
  readonly #props: PropField;
  readonly #roads: RoadLayers;
  readonly #sea: Mesh | undefined;
  readonly #cloudLayers: CloudLayer[];
  readonly #ground: GroundWindow;
  readonly #xHalf: number;
  #seaEnabled: boolean;
  #time = 0;

  constructor(
    readonly scene: Scene,
    private readonly options: SceneryStageOptions,
  ) {
    const { level, look, config } = options;
    checkPropModels(level, options.propModels);
    this.#seed = level.seed;
    this.#field = new HeightField(level, this.#seed);
    this.#placer = this.#newPlacer();
    this.framing = framePlayfield(options.screen, options.camera);
    const cameraY = options.camera.flightAltitude + this.framing.height;
    this.#ground = visibleGround(
      this.framing,
      options.screen.width / options.screen.height,
      cameraY,
      lowestGround(level),
      options.camera.flightAltitude,
    );
    this.#xHalf = Math.ceil((this.#ground.halfWidth + config.margin) / config.cell) * config.cell;
    this.camera = this.#setUpCamera();
    this.sun = lightScenery(scene, look);
    // One more wave tile: the sea plane moves by whole tiles (see `update`).
    const seaLength =
      this.#ground.zFar - this.#ground.zNear + 2 * config.margin + look.sea.tileSize;
    this.kit = options.kit(scene, {
      look,
      sun: this.sun,
      seaLevel: level.sea?.level ?? 0,
      seaSize: { width: this.#xHalf * 2, length: seaLength },
      seed: level.seed,
    });
    this.#chunks = this.#buildChunks();
    this.#roads = new RoadLayers(scene, this.kit.roads);
    this.#props = new PropField(scene, options.propModels, this.kit.props, (mesh) => {
      this.kit.addShadowCaster(mesh);
    });
    this.#sea = level.sea ? this.#buildSea(level.sea.level, seaLength) : undefined;
    this.#seaEnabled = this.#sea !== undefined;
    scene.setRenderingAutoClearDepthStencil(BELOW_CLOUDS_GROUP + 1, false, false);
    this.#cloudLayers = look.clouds.map((cloud, i) => this.#buildCloudLayer(cloud, i));
    this.clouds = this.#cloudLayers.map((c) => c.state);
  }

  /** The level's ground. */
  get field(): HeightField {
    return this.#field;
  }

  get seed(): number {
    return this.#seed;
  }

  get hasSea(): boolean {
    return this.#sea !== undefined;
  }

  get seaEnabled(): boolean {
    return this.#seaEnabled;
  }

  /** Number of props and terrain chunks in the scene. */
  get stats(): { readonly props: number; readonly chunks: number; readonly roads: number } {
    return { props: this.#props.count, chunks: this.#chunks.count, roads: this.#roads.count };
  }

  /** Meshes of the props' self-lit accents (for a glow layer). */
  get glowingMeshes(): Mesh[] {
    return this.#props.lightMeshes;
  }

  /** Regenerates the terrain and the props from another seed. */
  setSeed(seed: number): void {
    this.#seed = seed;
    this.#field = new HeightField(this.options.level, seed);
    this.#placer = this.#newPlacer();
    this.#chunks.rebuild(this.#field);
    this.#props.clear();
    this.#roads.clear();
    for (const index of this.#chunks.meshes.keys()) this.#placeChunk(index);
  }

  /** Shows or hides the sea; a level without a sea stays without one (P04-R02). */
  setSeaEnabled(enabled: boolean): void {
    this.#seaEnabled = enabled && this.#sea !== undefined;
    this.#sea?.setEnabled(this.#seaEnabled);
  }

  /** World position of a playfield point (logical pixels, origin at its bottom left). */
  playfieldPoint(x: number, y: number, distance: number): Vector3 {
    const { screen, camera } = this.options;
    return new Vector3(x - screen.width / 2, camera.flightAltitude, distance + y);
  }

  /** Moves the camera, the terrain, the sea and the clouds to `distance` along the level. */
  update(distance: number, dt: number): void {
    this.#time += dt;
    const { margin } = this.options.config;
    const camera = this.camera.position;
    camera.set(
      0,
      this.options.camera.flightAltitude + this.framing.height,
      distance + this.framing.back,
    );
    const [dy, dz] = this.framing.direction;
    this.camera.setTarget(new Vector3(0, camera.y + dy, camera.z + dz));
    const changes = this.#chunks.cover(
      camera.z + this.#ground.zNear - margin,
      camera.z + this.#ground.zFar + margin,
    );
    for (const index of changes.removed) {
      this.#props.removeChunk(index);
      this.#roads.removeChunk(index);
    }
    for (const span of changes.added) this.#placeChunk(span.index);
    this.#props.sync();
    const middle = camera.z + (this.#ground.zNear + this.#ground.zFar) / 2;
    if (this.#sea) {
      const tile = this.options.look.sea.tileSize;
      // Whole tiles only, so the waves stay put on the ground while the plane follows the camera.
      this.#sea.position.z = Math.round(middle / tile) * tile;
    }
    for (const layer of this.#cloudLayers) this.#updateCloud(layer);
    const { mapSize, frustum } = this.options.look.sun.shadow;
    this.sun.position = snappedLightPosition(
      this.sun.direction,
      new Vector3(0, 0, middle),
      this.options.config.sunDistance,
      frustum / mapSize,
    );
    this.kit.update({ time: this.#time, cameraPosition: camera, seaEnabled: this.#seaEnabled });
  }

  #newPlacer(): PropPlacer {
    const { level } = this.options;
    const roads = levelRoads(this.#field, level.roads, this.#seed);
    return new PropPlacer(this.#field, level.props, this.#seed, roads);
  }

  #placeChunk(index: number): void {
    const span = this.#chunks.span(index);
    this.#roads.setChunk(
      index,
      this.#placer.roads.roads,
      this.#field,
      span,
      this.options.look.roads,
    );
    this.#props.setChunk(
      index,
      this.#placer.place({
        xMin: -this.#xHalf,
        xMax: this.#xHalf,
        zMin: span.zMin,
        zMax: span.zMax,
      }),
    );
  }

  #buildChunks(): TerrainChunks {
    const { cell, chunkLength } = this.options.config;
    return new TerrainChunks(
      this.scene,
      this.kit.terrain,
      { length: chunkLength, cell, xMin: -this.#xHalf, columns: (2 * this.#xHalf) / cell },
      this.#field,
      (mesh) => {
        this.kit.addShadowCaster(mesh);
      },
    );
  }

  #setUpCamera(): FreeCamera {
    const camera = new FreeCamera('scenery-camera', Vector3.Zero(), this.scene);
    camera.fov = this.framing.halfFov * 2;
    camera.minZ = 1;
    camera.maxZ = this.options.config.farClip;
    this.scene.activeCamera = camera;
    return camera;
  }

  #buildSea(level: number, length: number): Mesh {
    const sea = CreateGround(
      'sea',
      { width: this.#xHalf * 2, height: length, subdivisions: 1 },
      this.scene,
    );
    sea.position.y = level;
    sea.material = this.kit.sea;
    sea.isPickable = false;
    sea.receiveShadows = true;
    sea.alphaIndex = 0;
    return sea;
  }

  /**
   * Height of a cloud layer: its look's altitude, raised if needed to stay `cloudClearance` above
   * the highest ground, so clouds never pass through the terrain (phase 4 review).
   */
  cloudAltitude(look: CloudLayerLook): number {
    return Math.max(look.altitude, this.#field.ceiling + this.options.config.cloudClearance);
  }

  #buildCloudLayer(look: CloudLayerLook, index: number): CloudLayer {
    const cameraY = this.options.camera.flightAltitude + this.framing.height;
    const altitude = this.cloudAltitude(look);
    const seen = visibleGround(
      this.framing,
      this.options.screen.width / this.options.screen.height,
      cameraY,
      altitude,
      altitude,
    );
    const { margin } = this.options.config;
    const mesh = CreateGround(
      `cloud-layer-${String(index)}`,
      {
        width: 2 * (seen.halfWidth + margin),
        height: seen.zFar - seen.zNear + 2 * margin,
        subdivisions: 1,
      },
      this.scene,
    );
    mesh.position.y = altitude;
    const material = this.kit.cloud(look);
    mesh.material = material.material;
    mesh.isPickable = false;
    mesh.renderingGroupId = BELOW_CLOUDS_GROUP + 1;
    // Lower layers are drawn first, after the sea.
    mesh.alphaIndex = index + 1;
    return {
      look,
      middle: (seen.zNear + seen.zFar) / 2,
      mesh,
      material,
      state: { enabled: true, coverage: look.coverage, opacity: look.opacity },
    };
  }

  #updateCloud(layer: CloudLayer): void {
    const { look, mesh, material, state } = layer;
    mesh.position.z = this.camera.position.z + layer.middle;
    const visible = state.enabled && state.coverage > 0 && state.opacity > 0;
    mesh.setEnabled(visible);
    material.set({
      coverage: state.coverage,
      opacity: state.opacity,
      offsetX: look.drift[0] * this.#time,
      offsetZ: look.drift[1] * this.#time,
    });
  }
}

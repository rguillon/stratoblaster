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
import { checkPropModels, PropField, propDrifts, type PropDrift } from './prop-field';
import { TrafficLayer } from './traffic-layer';
import type { SceneryKit, SceneryKitFactory } from './scenery-kit';
import { ABOVE_CLOUDS_GROUP, BELOW_CLOUDS_GROUP, type CloudLayerState } from './cloud-layers';
import type {
  CloudLayerLook,
  PlayfieldCameraLook,
  PropModelFactory,
  SceneryLook,
} from './scenery-look';
import { snappedLightPosition } from './scenery-lighting';
import type { Atmosphere } from '../../core/scenery/atmosphere';
import type { AtmosphereOptions } from './atmosphere-of';
import { SkyLayers } from './sky-layers';
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
  /**
   * How far before and past the ground in view props are drawn (tall ones show from further),
   * and by how much the drawn range is widened, so it is uploaded again only now and then.
   */
  readonly propReach: readonly [near: number, far: number];
  readonly propStep: number;
}

export interface SceneryStageOptions {
  readonly screen: LogicalScreen;
  readonly camera: PlayfieldCameraLook;
  readonly level: SceneryLevel;
  readonly look: SceneryLook;
  readonly propModels: Readonly<Record<string, PropModelFactory>>;
  readonly kit: SceneryKitFactory;
  readonly config: SceneryStageConfig;
  /** Debug choices on the level's look (P08-R12): a forced time of day, no weather. */
  readonly atmosphere?: AtmosphereOptions;
}

export { ABOVE_CLOUDS_GROUP, BELOW_CLOUDS_GROUP, type CloudLayerState } from './cloud-layers';

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
  readonly #traffic: TrafficLayer;
  readonly #roads: RoadLayers;
  readonly #sea: Mesh | undefined;
  readonly #ground: GroundWindow;
  readonly #drifts: Readonly<Record<string, PropDrift>>;
  readonly #xHalf: number;
  #seaEnabled: boolean;
  #time = 0;
  readonly #sky: SkyLayers;

  constructor(
    readonly scene: Scene,
    private readonly options: SceneryStageOptions,
  ) {
    const { level, look, config } = options;
    checkPropModels(level, options.propModels);
    this.#seed = level.seed;
    this.#field = new HeightField(level, this.#seed);
    this.#placer = this.#newPlacer();
    this.#drifts = propDrifts(level);
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
    // P08-R04: the time of day, clouds and weather along the level.
    this.#sky = new SkyLayers(scene, look, [level.scrollSpeed, options.atmosphere]);
    this.sun = this.#sky.sun;
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
    const { propModels } = options;
    this.#traffic = new TrafficLayer(scene, propModels, this.kit.props, level.props.cars);
    this.#sea = level.sea ? this.#buildSea(level.sea.level, seaLength) : undefined;
    this.#seaEnabled = this.#sea !== undefined;
    this.clouds = this.#attachSky();
  }

  /** The clouds, weather and aurora above the ground, drawn keeping the ground's depth. */
  #attachSky(): readonly CloudLayerState[] {
    for (const group of [BELOW_CLOUDS_GROUP + 1, ABOVE_CLOUDS_GROUP]) {
      this.scene.setRenderingAutoClearDepthStencil(group, false, false);
    }
    this.#sky.attach(this.kit, {
      windowAt: (altitude) => this.#windowAt(altitude),
      altitudeOf: (cloud) => this.cloudAltitude(cloud),
      flightAltitude: this.options.camera.flightAltitude,
      margin: this.options.config.margin,
    });
    return this.#sky.clouds;
  }

  /** The level's look where the view is now (P08-R04). */
  get atmosphere(): Atmosphere {
    return this.#sky.atmosphere;
  }

  /** Weather particles drawn on the last frame (P08-R05). */
  get weatherParticles(): number {
    return this.#sky.weatherParticles;
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
    return [...this.#props.lightMeshes, ...this.#traffic.lightMeshes];
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
    const [zMin, zMax] = [
      camera.z + this.#ground.zNear - margin,
      camera.z + this.#ground.zFar + margin,
    ];
    const changes = this.#chunks.cover(zMin, zMax);
    for (const index of changes.removed) {
      this.#props.removeChunk(index);
      this.#roads.removeChunk(index);
    }
    for (const span of changes.added) this.#placeChunk(span.index);
    this.#updateProps(camera.z, [zMin, zMax]);
    const middle = camera.z + (this.#ground.zNear + this.#ground.zFar) / 2;
    if (this.#sea) {
      const tile = this.options.look.sea.tileSize;
      // Whole tiles only, so the waves stay put on the ground while the plane follows the camera.
      this.#sea.position.z = Math.round(middle / tile) * tile;
    }
    const atmosphere = this.#sky.update(distance, [this.#time, this.camera, zMin]);
    const { mapSize, frustum } = this.options.look.sun.shadow;
    this.sun.position = snappedLightPosition(
      this.sun.direction,
      new Vector3(0, 0, middle),
      this.options.config.sunDistance,
      frustum / mapSize,
    );
    this.kit.update({
      time: this.#time,
      cameraPosition: camera,
      seaEnabled: this.#seaEnabled,
      atmosphere,
    });
  }

  /** The props in view near the camera at `cameraZ`, drifting, and the cars on the ground. */
  #updateProps(cameraZ: number, [zMin, zMax]: readonly [number, number]): void {
    const [near, far] = this.options.config.propReach;
    const [zNear, zFar] = [cameraZ + this.#ground.zNear - near, cameraZ + this.#ground.zFar + far];
    this.#props.setWindow(zNear, zFar, this.options.config.propStep);
    this.#props.sync();
    this.#props.drift(this.#drifts, this.#time);
    const height = (x: number, z: number): number => this.#field.height(x, z);
    const traffic = { roads: this.#placer.roads.roads, height, seed: this.#seed };
    const area = { xMin: -this.#xHalf, xMax: this.#xHalf, zMin, zMax };
    this.#traffic.update(this.#time, area, traffic);
  }

  #newPlacer(): PropPlacer {
    const { level } = this.options;
    const roads = levelRoads(this.#field, level.roads, this.#seed);
    return new PropPlacer(this.#field, level.props, this.#seed, roads, level.sea?.level);
  }

  #placeChunk(index: number): void {
    const span = this.#chunks.span(index);
    const { roads } = this.#placer.roads;
    this.#roads.setChunk(index, roads, this.#field, span, this.options.look.roads);
    const area = { xMin: -this.#xHalf, xMax: this.#xHalf, zMin: span.zMin, zMax: span.zMax };
    this.#props.setChunk(index, this.#placer.place(area));
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

  /** What the camera sees of the plane at `altitude`. */
  #windowAt(altitude: number): GroundWindow {
    const { screen, camera } = this.options;
    const cameraY = camera.flightAltitude + this.framing.height;
    return visibleGround(this.framing, screen.width / screen.height, cameraY, altitude, altitude);
  }
}

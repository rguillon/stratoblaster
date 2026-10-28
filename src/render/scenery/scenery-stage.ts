import type { Scene } from '@babylonjs/core/scene';
import type { FreeCamera } from '@babylonjs/core/Cameras/freeCamera';
import type { DirectionalLight } from '@babylonjs/core/Lights/directionalLight';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { HeightField } from '../../core/scenery/height-field';
import type { PropPlacer } from '../../core/scenery/prop-placement';
import { levelGround } from './level-ground';
import {
  framePlayfield,
  visibleGround,
  type GroundWindow,
  type PlayfieldFraming,
} from './playfield-framing';
import { levelPropModels, PropField, propDrifts, type PropDrift } from './prop-field';
import { TrafficLayer } from './traffic-layer';
import type { SceneryKit } from './scenery-kit';
import { ABOVE_CLOUDS_GROUP, BELOW_CLOUDS_GROUP, type CloudLayerState } from './cloud-layers';
import type { CloudLayerLook } from './scenery-look';
import { snappedLightPosition } from './scenery-lighting';
import type { Atmosphere } from '../../core/scenery/atmosphere';
import { plumeLight } from './plume-layer';
import { RainRings } from './rain-rings';
import { seaPlane, stageCamera, TerrainWatch } from './stage-parts';
import { SkyLayers } from './sky-layers';
import { TerrainChunks } from './terrain-chunks';
import { RoadLayers } from './road-field';
import { GroundRoot, groundWindowOf } from './ground-root';
import type { SceneryStageOptions } from './scenery-stage-options';

export type { SceneryStageConfig, SceneryStageOptions } from './scenery-stage-options';

export { ABOVE_CLOUDS_GROUP, BELOW_CLOUDS_GROUP, type CloudLayerState } from './cloud-layers';

/**
 * How far before the runout its streets and buildings can change what a chunk shows: the trees
 * keep clear of the buildings (reviewer, 2026-10-28).
 */
const RUNOUT_REACH = 64;

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
  /** P09-R05: rain rings on the water, when the level has water. */
  readonly #rings: RainRings | undefined;
  readonly #terrain = new TerrainWatch();
  /** The ground, drawn bigger when flying lower (`PlayfieldCameraLook.groundScale`). */
  readonly #groundRoot: GroundRoot;
  /** Whether the chunks were placed with the runout's streets and buildings (they come later). */
  #withRunout = false;

  constructor(
    readonly scene: Scene,
    private readonly options: SceneryStageOptions,
  ) {
    const { level, look, config } = options;
    const models = levelPropModels(level, options.propModels);
    this.#seed = level.seed;
    ({ field: this.#field, placer: this.#placer } = levelGround(level, this.#seed));
    this.#drifts = propDrifts(level);
    this.framing = framePlayfield(options.screen, options.camera);
    this.#groundRoot = new GroundRoot(scene, options.camera.groundScale ?? 1);
    this.#ground = groundWindowOf(options, this.framing, this.#groundRoot.scale);
    this.#xHalf = Math.ceil((this.#ground.halfWidth + config.margin) / config.cell) * config.cell;
    this.camera = stageCamera(scene, this.framing.halfFov, config.farClip);
    // P08-R04: the time of day, clouds and weather along the level.
    this.#sky = new SkyLayers(scene, look, [level.scrollSpeed, options.atmosphere, level.seed]);
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
    const adopt = <T>(create: () => T): T => this.#groundRoot.adopt(create);
    this.#chunks = adopt(() => this.#buildChunks());
    this.#roads = new RoadLayers(scene, this.kit.roads);
    this.#props = adopt(() => this.#buildProps(models));
    const { propModels } = options;
    this.#traffic = adopt(
      () => new TrafficLayer(scene, propModels, this.kit.props, level.props.cars),
    );
    const seaSize = [this.#xHalf * 2, seaLength] as const;
    this.#sea = level.sea
      ? adopt(() => seaPlane(scene, [...seaSize, level.sea?.level ?? 0], this.kit.sea))
      : undefined;
    this.#seaEnabled = this.#sea !== undefined;
    this.#rings = level.sea
      ? adopt(
          () =>
            new RainRings(scene, this.kit.rings, [
              level.sea?.level ?? 0,
              this.#xHalf * 2,
              seaLength,
            ]),
        )
      : undefined;
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

  /** Strength of the rain rings drawn on the water on the last frame (P09-R05; 0 = none). */
  get rainRings(): number {
    return this.#rings?.shown ?? 0;
  }

  /** How bright the lightning was on the last frame (P09-R05; 0 = no flash). */
  get lightningFlash(): number {
    return this.#sky.flash;
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

  /**
   * Meshes that hide the glowing ones behind them (reviewer, 2026-10-28): the props and the cars.
   * A glow layer draws them black; the terrain chunks come through {@link watchTerrain}.
   */
  get glowOccluders(): Mesh[] {
    return [...this.#props.structureMeshes, ...this.#traffic.structureMeshes];
  }

  /**
   * Phase 10: the lava (P10-R05), when the level's liquid is lava: drawn in a glow layer with its
   * own material, the terrain hiding it there ({@link watchTerrain}).
   */
  get lava(): Mesh | undefined {
    return this.options.look.sea.lava ? this.#sea : undefined;
  }

  /** Plume meshes drawn on the last frame (phase 10: smoke and steam). */
  get plumes(): number {
    return this.#props.plumeCount;
  }

  /** Calls `watch` with every terrain chunk mesh, now and as new ones are made. */
  watchTerrain(watch: (mesh: Mesh) => void): void {
    this.#terrain.watch(watch);
  }

  /** Regenerates the terrain and the props from another seed. */
  setSeed(seed: number): void {
    this.#seed = seed;
    ({ field: this.#field, placer: this.#placer } = levelGround(this.options.level, seed));
    this.#groundRoot.adopt(() => {
      this.#chunks.rebuild(this.#field);
      this.#props.clear();
      this.#roads.clear();
      for (const index of this.#chunks.meshes.keys()) this.#placeChunk(index);
    });
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
    // The ground's Z under the camera, and the ground in view (ground units).
    const ground = this.#groundRoot;
    ground.moveTo(distance);
    const cameraZ = ground.toGround(camera.z);
    const [zMin, zMax] = [
      cameraZ + this.#ground.zNear - margin,
      cameraZ + this.#ground.zFar + margin,
    ];
    ground.adopt(() => {
      this.#cover(zMin, zMax);
    });
    this.#updateProps(cameraZ, [zMin, zMax]);
    const middle = cameraZ + (this.#ground.zNear + this.#ground.zFar) / 2;
    if (this.#sea) {
      const tile = this.options.look.sea.tileSize;
      // Whole tiles only, so the waves stay put on the ground while the plane follows the camera.
      this.#sea.position.z = Math.round(middle / tile) * tile;
    }
    const atmosphere = this.#sky.update(distance, [this.#time, this.camera, ground.toWorld(zMin)]);
    this.#rings?.update(atmosphere, [this.#time, middle, this.#seaEnabled]);
    this.#updatePlumes(atmosphere);
    const { mapSize, frustum } = this.options.look.sun.shadow;
    this.sun.position = snappedLightPosition(
      this.sun.direction,
      new Vector3(0, 0, ground.toWorld(middle)),
      this.options.config.sunDistance,
      frustum / mapSize,
    );
    this.kit.update({
      time: this.#time,
      cameraPosition: camera,
      seaEnabled: this.#seaEnabled,
      atmosphere,
      ground: ground.transform,
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

  /** Phase 10: the props' smoke and steam, lit and fogged by `atmosphere`. */
  #updatePlumes(atmosphere: Atmosphere): void {
    this.#props.updatePlumes({
      time: this.#time,
      cameraPosition: this.camera.position,
      right: this.camera.getDirection(Vector3.Right()),
      up: this.camera.getDirection(Vector3.Up()),
      light: plumeLight(atmosphere),
      fog: { color: atmosphere.sky.haze, ...atmosphere.fog },
    });
  }

  /** Keeps the chunks over [zMin, zMax], with their roads and props. */
  #cover(zMin: number, zMax: number): void {
    this.#takeRunout();
    const changes = this.#chunks.cover(zMin, zMax);
    for (const index of changes.removed) {
      this.#props.removeChunk(index);
      this.#roads.removeChunk(index);
    }
    for (const span of changes.added) this.#placeChunk(span.index);
  }

  /**
   * Once the runout's streets and buildings come (generated after the rest, reviewer
   * 2026-10-28), places again the chunks they show in.
   */
  #takeRunout(): void {
    const placed = this.#placer.runoutPlaced;
    if (placed === this.#withRunout) return;
    this.#withRunout = placed;
    const from = (this.#placer.roads.runoutFrom ?? Infinity) - RUNOUT_REACH;
    for (const index of this.#chunks.meshes.keys()) {
      if (this.#chunks.span(index).zMax > from) this.#placeChunk(index);
    }
  }

  #placeChunk(index: number): void {
    const span = this.#chunks.span(index);
    const { roads } = this.#placer.roads;
    this.#roads.setChunk(index, roads, this.#field, span, this.options.look.roads);
    const area = { xMin: -this.#xHalf, xMax: this.#xHalf, zMin: span.zMin, zMax: span.zMax };
    this.#props.setChunk(index, this.#placer.place(area));
  }

  /** The props of the level, of `models`, casting shadows. */
  #buildProps(models: SceneryStageOptions['propModels']): PropField {
    const { kit } = this;
    const shadow = (mesh: Mesh) => {
      kit.addShadowCaster(mesh);
    };
    return new PropField(this.scene, models, kit.props, shadow, kit.plume);
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
        this.#terrain.add(mesh);
      },
    );
  }

  /**
   * Height of a cloud layer: its look's altitude, raised if needed to stay `cloudClearance` above
   * the highest ground, so clouds never pass through the terrain (phase 4 review).
   */
  cloudAltitude(look: CloudLayerLook): number {
    const ceiling = this.#field.ceiling * this.#groundRoot.scale;
    return Math.max(look.altitude, ceiling + this.options.config.cloudClearance);
  }

  /** What the camera sees of the plane at `altitude`. */
  #windowAt(altitude: number): GroundWindow {
    const { screen, camera } = this.options;
    const cameraY = camera.flightAltitude + this.framing.height;
    return visibleGround(this.framing, screen.width / screen.height, cameraY, altitude, altitude);
  }
}

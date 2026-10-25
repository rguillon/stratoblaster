import type { Scene } from '@babylonjs/core/scene';
import type { DirectionalLight } from '@babylonjs/core/Lights/directionalLight';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { Camera } from '@babylonjs/core/Cameras/camera';
import type { Atmosphere } from '../../core/scenery/atmosphere';
import { atmosphereTrack, type AtmosphereAlong, type AtmosphereOptions } from './atmosphere-of';
import { AuroraLayer } from './aurora-layer';
import {
  buildCloudLayer,
  updateCloudLayer,
  type CloudLayer,
  type CloudLayerState,
} from './cloud-layers';
import type { GroundWindow } from './playfield-framing';
import type { SceneryKit } from './scenery-kit';
import { applyAtmosphere, lightScenery, type SceneryLights } from './scenery-lighting';
import type { CloudLayerLook, SceneryLook } from './scenery-look';
import { WeatherLayer } from './weather-layer';

/** The aurora's sheet flies this far above the highest cloud layer, under the ships. */
const AURORA_ABOVE_CLOUDS = 8;

/** Where the sky's layers go: what the camera sees at a height, and the flight altitude. */
export interface SkyPlacement {
  readonly windowAt: (altitude: number) => GroundWindow;
  readonly altitudeOf: (look: CloudLayerLook) => number;
  readonly flightAltitude: number;
  readonly margin: number;
}

/**
 * The sky of a scenery stage (P04-R03, P08-R04, R05): the level's look along its length, the sun
 * and ambient light it sets, and the cloud layers, the weather and the aurora above the ground.
 * Built in two steps, as the scenery kit needs the sun first ({@link attach}).
 */
export class SkyLayers {
  readonly #track: AtmosphereAlong;
  readonly #lights: SceneryLights;
  /** Whether the clouds' cover follows the look (a look with a time of day). */
  readonly #follow: boolean;
  #atmosphere: Atmosphere;
  #clouds: CloudLayer[] = [];
  #weather: WeatherLayer | undefined;
  #aurora: AuroraLayer | undefined;

  constructor(
    private readonly scene: Scene,
    private readonly look: SceneryLook,
    [scrollSpeed, options]: readonly [number, AtmosphereOptions | undefined],
  ) {
    this.#track = atmosphereTrack(look, scrollSpeed, options);
    this.#atmosphere = this.#track.at(0);
    this.#lights = lightScenery(scene, this.#atmosphere);
    this.#follow = look.atmosphere !== undefined || options?.timeOfDay !== undefined;
  }

  get sun(): DirectionalLight {
    return this.#lights.sun;
  }

  get atmosphere(): Atmosphere {
    return this.#atmosphere;
  }

  /** The cloud layers' live settings. */
  get clouds(): readonly CloudLayerState[] {
    return this.#clouds.map((c) => c.state);
  }

  /** Weather particles drawn on the last frame. */
  get weatherParticles(): number {
    return this.#weather?.drawn ?? 0;
  }

  /** Builds the cloud layers, the weather and the aurora with `kit`'s materials. */
  attach(kit: SceneryKit, place: SkyPlacement): void {
    this.#clouds = this.look.clouds.map((cloud, i) => {
      const altitude = place.altitudeOf(cloud);
      const window = place.windowAt(altitude);
      return buildCloudLayer(this.scene, cloud, kit.cloud(cloud), i, [
        window,
        altitude,
        place.margin,
      ]);
    });
    this.#weather = new WeatherLayer(this.scene, kit.weather);
    const top = Math.max(0, ...this.look.clouds.map(place.altitudeOf));
    const altitude = Math.min(place.flightAltitude - 4, top + AURORA_ABOVE_CLOUDS);
    const window = place.windowAt(altitude);
    this.#aurora = new AuroraLayer(this.scene, kit.aurora(), [window, altitude, place.margin]);
  }

  /**
   * The look at `distance` along the level, seen from `camera` at `time`: light, haze, clouds,
   * weather (in the box of air from `zMin`) and aurora.
   */
  update(distance: number, [time, camera, zMin]: readonly [number, Camera, number]): Atmosphere {
    const atmosphere = this.#track.at(distance);
    this.#atmosphere = atmosphere;
    applyAtmosphere(this.scene, this.#lights, atmosphere);
    const at = camera.position;
    this.#clouds.forEach((layer, i) => {
      updateCloudLayer(layer, [at.z, time], [atmosphere, atmosphere.clouds[i], this.#follow]);
    });
    this.#weather?.update(atmosphere, {
      time,
      cameraPosition: at,
      right: camera.getDirection(Vector3.Right()),
      up: camera.getDirection(Vector3.Up()),
      start: zMin,
    });
    this.#aurora?.update(atmosphere, time, at);
    return atmosphere;
  }
}

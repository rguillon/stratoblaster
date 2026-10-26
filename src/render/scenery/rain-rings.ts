import type { Scene } from '@babylonjs/core/scene';
import type { Material } from '@babylonjs/core/Materials/material';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { CreateGround } from '@babylonjs/core/Meshes/Builders/groundBuilder';
import { WEATHER_KINDS, type WeatherKind } from '../../config/weather';
import type { Atmosphere } from '../../core/scenery/atmosphere';

type Rings = NonNullable<WeatherKind['rings']>;
type Rgb = readonly [number, number, number];

/** What the rain rings show on one frame (P09-R05). */
export interface RingsFrame {
  readonly time: number;
  /** 0..1: how many rings there are and how strong they show. */
  readonly strength: number;
  readonly fog: { readonly color: Rgb; readonly start: number; readonly end: number };
}

/** The material of the rings of a weather kind, driven frame by frame. */
export interface RingsMaterial {
  readonly material: Material;
  set(frame: RingsFrame): void;
}

/** Builds the material of the rings `rings`. */
export type RingsMaterialFactory = (scene: Scene, rings: Rings) => RingsMaterial;

/** Draw order among the see-through meshes: right after the water. */
const RINGS_ALPHA_INDEX = 1;
/** The rings lie this far above the water, so they never flicker against it. */
const LIFT = 0.05;

/**
 * Faint rings spreading on the water where raindrops land (P09-R05): a plane at the water level
 * that follows the view, the rings drawn by its material in cells of the ground. The terrain
 * above the water hides it, so the rings only show on the sea, the rivers, the swamps and the
 * lakes. It shows the rings of the weather kind of the atmosphere, if it has any.
 */
export class RainRings {
  readonly #plane: Mesh;
  readonly #materials = new Map<string, RingsMaterial>();
  #shown = 0;

  constructor(
    private readonly scene: Scene,
    private readonly materials: RingsMaterialFactory,
    [level, width, length]: readonly [number, number, number],
    private readonly kinds: Readonly<Record<string, WeatherKind>> = WEATHER_KINDS,
  ) {
    this.#plane = CreateGround('rain-rings', { width, height: length }, scene);
    this.#plane.position.y = level + LIFT;
    this.#plane.isPickable = false;
    this.#plane.alphaIndex = RINGS_ALPHA_INDEX;
    this.#plane.setEnabled(false);
  }

  /** Strength of the rings drawn on the last frame (0 when none). */
  get shown(): number {
    return this.#shown;
  }

  /**
   * Shows the rings of `atmosphere`'s weather at `time`, the plane centred at `z`; none while
   * the water is hidden (`water` false).
   */
  update(atmosphere: Atmosphere, [time, z, water]: readonly [number, number, boolean]): void {
    const { weather } = atmosphere;
    const rings = this.kinds[weather.kind]?.rings;
    const strength = Math.min(1, Math.max(0, weather.strength));
    this.#shown = rings && water && strength > 0 ? strength : 0;
    this.#plane.setEnabled(this.#shown > 0);
    if (!rings || this.#shown === 0) return;
    const material = this.#material(weather.kind, rings);
    this.#plane.material = material.material;
    this.#plane.position.z = z;
    material.set({ time, strength, fog: { color: atmosphere.sky.haze, ...atmosphere.fog } });
  }

  #material(id: string, rings: Rings): RingsMaterial {
    let material = this.#materials.get(id);
    if (!material) {
      material = this.materials(this.scene, rings);
      this.#materials.set(id, material);
    }
    return material;
  }
}

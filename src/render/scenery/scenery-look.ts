import type { SkyScript } from '../../core/scenery/sky-look';
import type { GradientStop } from '../environment/gradient-cube';
import type { ColoredGeometry } from '../geometry/gradient-shapes';
import type { RoadLook } from './road-geometry';

type Rgb = readonly [number, number, number];

/** A tiling texture generated in code: fractal noise between three colours, plus speckles. */
export interface TextureLook {
  /** Colour at the low, middle and high noise values. */
  readonly colors: readonly [dark: Rgb, base: Rgb, light: Rgb];
  /** Noise cycles across the texture (first octave). */
  readonly frequency: number;
  readonly octaves: number;
  /** Share (0..1) of pixels turned into small speckles of `speckleColor`. */
  readonly speckle: number;
  readonly speckleColor: Rgb;
  /** Strength (0..1) of horizontal bands across the texture, like rock strata. */
  readonly strata: number;
  /** Strength (0..1) of thin dark crack lines across it, as in lake ice (phase 8). */
  readonly cracks?: number;
}

/**
 * Generated ground textures blended by altitude and slope (P04-R01): `low` under `lowHeight`
 * (shores, sea bed), `ground` in between, `high` above `highHeight` (snow), `steep` on slopes.
 */
export interface TerrainLook {
  readonly textureSize: number;
  /** World units covered by one repeat of the ground textures. */
  readonly tileSize: number;
  readonly low: TextureLook;
  readonly ground: TextureLook;
  readonly steep: TextureLook;
  readonly high: TextureLook;
  /**
   * Ground of the sections covered with grass, pavement and sand (`TerrainSection.surface`).
   * The cover replaces the `ground` layer only, so it still gives way to rock on slopes.
   */
  readonly lush: TextureLook;
  readonly paved: TextureLook;
  readonly sand: TextureLook;
  readonly lowHeight: number;
  readonly highHeight: number;
  /** Half-width (in height) of the fade between two altitude layers. */
  readonly heightBlend: number;
  /** Slope (0 = flat, 1 = vertical) where the steep layer starts, and where it is full. */
  readonly steepSlope: readonly [number, number];
  /** Noise added to the height (world units) and the slope before blending, so borders wander. */
  readonly jitter: { readonly height: number; readonly slope: number };
  /** World units covered by one repeat of the blending noise. */
  readonly noiseTileSize: number;
  /** Large patches of the ground layer are tinted between these two colours. */
  readonly tints: readonly [Rgb, Rgb];
  readonly tintTileSize: number;
  /** Where the ground meets the sea (phase 5 review): beach, shallows and surf. */
  readonly shore: ShoreLook;
  readonly specular: number;
}

/**
 * The shore, painted on the terrain around the sea level (phase 5 review): a sand beach up to
 * `beach` above the water, ground under the water tinted from `shallow` to `deep` over `depth`,
 * and surf: a broken foam line at the water's edge and bands of foam rolling in.
 */
export interface ShoreLook {
  readonly sand: Rgb;
  /** Height above the sea level where the beach gives way to the ground. */
  readonly beach: number;
  readonly shallow: Rgb;
  readonly deep: Rgb;
  /** Depth where the water reaches its `deep` colour. */
  readonly depth: number;
  readonly foam: {
    readonly color: Rgb;
    /** Half-height of the foam line at the water's edge. */
    readonly width: number;
    /** Depth between two bands of rolling foam, how fast they roll in (bands per second)
     * and the depth they start at. */
    readonly spacing: number;
    readonly speed: number;
    readonly reach: number;
  };
}

/** Water with a generated, drifting normal map that catches the sun (P04-R02). */
export interface SeaLook {
  readonly color: Rgb;
  readonly alpha: number;
  readonly roughness: number;
  /** Strength of the sun's direct light on the water: above 1, the glint is brighter. */
  readonly sunGlint: number;
  readonly normalMap: {
    readonly size: number;
    readonly frequency: number;
    readonly octaves: number;
    /** Slope of the waves in the normal map. */
    readonly strength: number;
  };
  /** World units covered by one repeat of the normal map. */
  readonly tileSize: number;
  /** World units per second the waves drift, along X and Z. */
  readonly drift: readonly [number, number];
}

/** A layer of clouds under the flight altitude (P04-R03). */
export interface CloudLayerLook {
  readonly altitude: number;
  /** Share (0..1) of the sky covered by this layer: its intensity. */
  readonly coverage: number;
  /** 0 = invisible, 1 = opaque. */
  readonly opacity: number;
  /** World units covered by one repeat of the cloud pattern. */
  readonly tileSize: number;
  /** World units per second the layer drifts, along X and Z, on top of the scrolling. */
  readonly drift: readonly [number, number];
  /** Fade width (0..1) of the cloud edges. */
  readonly softness: number;
  readonly color: Rgb;
  /** Colour of the thin edges. */
  readonly shade: Rgb;
}

/** How a scenery level looks: sky, light, terrain, sea, clouds and props. */
export interface SceneryLook {
  readonly sky: {
    /** Clear and fog colour. */
    readonly haze: Rgb;
    /** Sky gradient used for reflections (sea, metal). */
    readonly stops: readonly GradientStop[];
    readonly environmentIntensity: number;
  };
  /** Linear fog, in world units from the camera. */
  readonly fog: { readonly start: number; readonly end: number };
  readonly sun: {
    /** Height of the sun above the horizon. */
    readonly elevationDeg: number;
    /** 0 = straight ahead (+Z), positive towards +X. */
    readonly azimuthDeg: number;
    readonly color: Rgb;
    readonly intensity: number;
    readonly shadow: {
      readonly mapSize: number;
      /**
       * Size of the square of ground the shadow map covers, centred on the view. Fixed, and moved
       * by whole shadow texels, so shadows do not shimmer as the view scrolls.
       */
      readonly frustum: number;
      readonly bias: number;
      readonly normalBias: number;
      /** 0 = black shadows, 1 = no shadows. */
      readonly darkness: number;
    };
  };
  readonly ambient: { readonly sky: Rgb; readonly ground: Rgb; readonly intensity: number };
  readonly terrain: TerrainLook;
  readonly sea: SeaLook;
  readonly clouds: readonly CloudLayerLook[];
  /** Colours of the roads and paths (P04-R07). */
  readonly roads: RoadLook;
  readonly props: {
    readonly specular: number;
    /** Brightness of the self-lit accents (neon, windows). */
    readonly lightIntensity: number;
  };
  readonly glow: { readonly intensity: number; readonly blurKernelSize: number };
  /**
   * Its time of day, clouds and weather along the level (phase 8, P08-R04): when set, they
   * replace the fixed sky, fog, sun, ambient light, cloud cover and ground lights above.
   */
  readonly atmosphere?: SkyScript;
}

/** Raw geometry of a prop: its lit structure (casts shadows) and its self-lit accents. */
export interface PropGeometry {
  readonly structure: ColoredGeometry;
  readonly lights?: ColoredGeometry;
}

/** Builds the geometry of one kind of prop, standing on Y = 0, centred on the origin. */
export type PropModelFactory = () => PropGeometry;

/** The camera above the playfield (P04-R05). */
export interface PlayfieldCameraLook {
  /** Tilt from straight down; the camera stands behind the playfield and looks forward. */
  readonly tiltDeg: number;
  /** Vertical field of view. */
  readonly fovDeg: number;
  /** Height of the playfield plane, where the ships fly. */
  readonly flightAltitude: number;
}

import type { GradientStop } from '../environment/gradient-cube';
import type { ColoredGeometry } from '../geometry/gradient-shapes';

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
  /** Surf on the shore line: colour and half-height of the band around the sea level. */
  readonly foam: { readonly color: Rgb; readonly width: number };
  readonly specular: number;
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
  readonly props: {
    readonly specular: number;
    /** Brightness of the self-lit accents (neon, windows). */
    readonly lightIntensity: number;
  };
  readonly glow: { readonly intensity: number; readonly blurKernelSize: number };
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

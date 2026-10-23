import type { SceneryLevel, TerrainSection } from '../../src/core/scenery/scenery-level';
import { SolidBuilder } from '../../src/render/geometry/solids';
import type { SceneryBindings } from '../../src/render/game-view';
import type { SceneryLook, TextureLook } from '../../src/render/scenery/scenery-look';

const flat = (name: string, seconds: number, base: number): TerrainSection => ({
  name,
  seconds,
  relief: { base, amplitude: 2, frequency: 1 / 100, octaves: 2, style: 'smooth' },
  buildingDensity: 1,
  treeDensity: 1,
});

/**
 * A tiny scenery level: two flat sections of 10 s at 20 units/s, a sea, one straight road along
 * X = 0 with a straight path every 100 units, and two prop kinds.
 */
export const SAMPLE_SCENERY_LEVEL: SceneryLevel = {
  id: 'sample-ground',
  name: 'Sample ground',
  seed: 7,
  scrollSpeed: 20,
  transition: 40,
  sections: [flat('low', 10, 10), flat('high', 10, 30)],
  sea: { level: 0 },
  roads: {
    mainRoads: 1,
    spread: 0,
    meander: { amplitude: [0, 0], wavelength: [100, 100] },
    crossSpacing: [100, 100],
    crossLength: [80, 80],
    crossBend: 0,
    mainWidth: 6,
    crossWidth: 4,
    minHeight: 1,
    maxSlope: 0.5,
    minRun: 3,
    step: 5,
    slotSpacing: 20,
    setback: 1,
  },
  props: {
    cellSize: 40,
    treeClearance: 1,
    maxSlope: 0.5,
    treeMaxSlope: 1,
    minHeight: 1,
    zoneFrequency: 1 / 200,
    groups: [
      { id: 'blocks', weight: 1, kinds: [{ id: 'block', weight: 1, footprint: 5, scale: [1, 1] }] },
    ],
    trees: [{ id: 'stick', weight: 1, footprint: 1, scale: [1, 2] }],
    treesPerCell: 2,
  },
};

const texture: TextureLook = {
  colors: [
    [0, 0, 0],
    [0.5, 0.5, 0.5],
    [1, 1, 1],
  ],
  frequency: 2,
  octaves: 2,
  speckle: 0,
  speckleColor: [0, 0, 0],
  strata: 0,
};

/** Look of {@link SAMPLE_SCENERY_LEVEL}, with one cloud layer. */
export const SAMPLE_SCENERY_LOOK: SceneryLook = {
  sky: {
    haze: [0.5, 0.5, 0.6],
    stops: [
      { at: -1, color: [0, 0, 0] },
      { at: 1, color: [1, 1, 1] },
    ],
    environmentIntensity: 1,
  },
  fog: { start: 100, end: 1000 },
  sun: {
    elevationDeg: 45,
    azimuthDeg: 0,
    color: [1, 1, 1],
    intensity: 1,
    shadow: { mapSize: 256, bias: 0.001, normalBias: 0, darkness: 0.5 },
  },
  ambient: { sky: [1, 1, 1], ground: [0.2, 0.2, 0.2], intensity: 0.5 },
  terrain: {
    textureSize: 16,
    tileSize: 50,
    low: texture,
    ground: texture,
    steep: texture,
    high: texture,
    lowHeight: 5,
    highHeight: 100,
    heightBlend: 2,
    steepSlope: [0.3, 0.6],
    jitter: { height: 1, slope: 0.1 },
    noiseTileSize: 100,
    tints: [
      [1, 1, 1],
      [0.9, 0.9, 0.9],
    ],
    tintTileSize: 500,
    foam: { color: [1, 1, 1], width: 1 },
    specular: 0,
  },
  sea: {
    color: [0, 0.2, 0.4],
    alpha: 0.8,
    roughness: 0.1,
    sunGlint: 1,
    normalMap: { size: 16, frequency: 2, octaves: 2, strength: 4 },
    tileSize: 40,
    drift: [1, 2],
  },
  clouds: [
    {
      altitude: 60,
      coverage: 0.4,
      opacity: 0.6,
      tileSize: 200,
      drift: [2, 0],
      softness: 0.1,
      color: [1, 1, 1],
      shade: [0.8, 0.8, 0.8],
    },
  ],
  roads: {
    main: [0.2, 0.2, 0.2],
    cross: [0.5, 0.4, 0.3],
    opacity: { main: 1, cross: 0.5 },
    shoulder: 1,
    wear: 0,
    lift: 0.5,
  },
  props: { specular: 0, lightIntensity: 1 },
  glow: { intensity: 0.2, blurKernelSize: 8 },
};

/** Scenery bindings of the sample game: a block with a lit roof, and a stick. */
export const SAMPLE_SCENERY: SceneryBindings = {
  camera: { tiltDeg: 30, fovDeg: 40, flightAltitude: 100 },
  looks: { [SAMPLE_SCENERY_LEVEL.id]: SAMPLE_SCENERY_LOOK },
  propModels: {
    block: () => ({
      structure: new SolidBuilder().box([4, 4, 4], [0.5, 0.5, 0.5]).geometry,
      lights: new SolidBuilder().box([2, 0.2, 2], [1, 0, 1], { at: [0, 4, 0] }).geometry,
    }),
    stick: () => ({ structure: new SolidBuilder().cylinder(0.5, 6, 4, [0.3, 0.2, 0.1]).geometry }),
  },
};

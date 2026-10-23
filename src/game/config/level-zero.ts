import type { PropRules, SceneryLevel, TerrainSection } from '../../core/scenery/scenery-level';

/*
 * Level Zero (P04): a test level that shows every terrain tool. Heights in world units
 * (logical pixels) above the sea level (0); the flight altitude is 320 (`playfield-camera.ts`),
 * so no peak goes above 250.
 */

/** Ground speed under the playfield, in logical pixels per second (GD-01). */
export const LEVEL_ZERO_SCROLL_SPEED = 60;
/** The highest a peak may reach. */
export const LEVEL_ZERO_MAX_HEIGHT = 250;

/** Ids of this game's prop models. */
export const PROP_IDS = {
  factory: 'factory',
  tanks: 'storage-tanks',
  warehouse: 'warehouse',
  coolingTower: 'cooling-tower',
  radar: 'radar-dish',
  antenna: 'antenna-mast',
  observatory: 'observatory',
  cubeHome: 'cube-home',
  domeHome: 'dome-home',
  stiltPod: 'stilt-pod',
  deadTree: 'dead-tree',
  forkedTree: 'forked-tree',
} as const;

const BUILDING_SCALE = [1.1, 1.4] as const;

const PROP_RULES: PropRules = {
  cellSize: 80,
  jitter: 0.35,
  maxSlope: 0.12,
  treeMaxSlope: 0.45,
  minHeight: 4,
  zoneFrequency: 1 / 700,
  groups: [
    {
      id: 'industrial',
      weight: 4,
      kinds: [
        { id: PROP_IDS.factory, weight: 3, footprint: 30, scale: BUILDING_SCALE },
        { id: PROP_IDS.tanks, weight: 2, footprint: 22, scale: BUILDING_SCALE },
        { id: PROP_IDS.warehouse, weight: 3, footprint: 30, scale: BUILDING_SCALE },
        { id: PROP_IDS.coolingTower, weight: 1, footprint: 20, scale: BUILDING_SCALE },
      ],
    },
    {
      id: 'science',
      weight: 2,
      kinds: [
        { id: PROP_IDS.radar, weight: 2, footprint: 12, scale: BUILDING_SCALE },
        { id: PROP_IDS.antenna, weight: 1, footprint: 9, scale: BUILDING_SCALE },
        { id: PROP_IDS.observatory, weight: 2, footprint: 15, scale: BUILDING_SCALE },
      ],
    },
    {
      id: 'homes',
      weight: 3,
      kinds: [
        { id: PROP_IDS.cubeHome, weight: 2, footprint: 13, scale: BUILDING_SCALE },
        { id: PROP_IDS.domeHome, weight: 2, footprint: 13, scale: BUILDING_SCALE },
        { id: PROP_IDS.stiltPod, weight: 1, footprint: 11, scale: BUILDING_SCALE },
      ],
    },
  ],
  trees: [
    { id: PROP_IDS.deadTree, weight: 2, footprint: 3, scale: [0.9, 1.5] },
    { id: PROP_IDS.forkedTree, weight: 1, footprint: 3, scale: [0.9, 1.5] },
  ],
  treesPerCell: 4,
};

const smooth = (base: number, amplitude: number, wavelength: number, octaves: number) =>
  ({ base, amplitude, frequency: 1 / wavelength, octaves, style: 'smooth' }) as const;

/** The sections, in flight order; their `seconds` add up to 180 (P04-R06). */
const SECTIONS: readonly TerrainSection[] = [
  {
    name: 'plains',
    seconds: 20,
    relief: smooth(22, 14, 520, 4),
    buildingDensity: 0.4,
    treeDensity: 0.6,
  },
  {
    name: 'hills',
    seconds: 18,
    relief: smooth(40, 55, 420, 5),
    buildingDensity: 0.15,
    treeDensity: 0.8,
  },
  {
    name: 'plateau',
    seconds: 20,
    relief: smooth(70, 60, 380, 5),
    flatten: {
      path: { x: 0, amplitude: 120, wavelength: 2600 },
      halfWidth: 250,
      edge: 120,
      height: 60,
      roughness: 1.5,
    },
    buildingDensity: 0.6,
    treeDensity: 0.3,
  },
  {
    name: 'mountains',
    seconds: 26,
    relief: {
      base: 10,
      amplitude: 235,
      frequency: 1 / 600,
      octaves: 6,
      style: 'ridged',
      maxHeight: LEVEL_ZERO_MAX_HEIGHT,
    },
    buildingDensity: 0.05,
    treeDensity: 0.25,
  },
  {
    name: 'canyon',
    seconds: 26,
    relief: smooth(130, 35, 360, 5),
    channel: {
      path: { x: 0, amplitude: 150, wavelength: 1900 },
      halfWidth: 45,
      wall: 120,
      floor: -12,
    },
    buildingDensity: 0.15,
    treeDensity: 0.3,
  },
  {
    name: 'coast',
    seconds: 22,
    relief: smooth(26, 18, 480, 4),
    shore: {
      path: { x: -60, amplitude: 160, wavelength: 2600 },
      landSide: -1,
      width: 240,
      seabed: -55,
    },
    buildingDensity: 0.4,
    treeDensity: 0.4,
  },
  {
    name: 'open sea',
    seconds: 24,
    relief: smooth(-28, 75, 520, 5),
    buildingDensity: 0.25,
    treeDensity: 0.5,
  },
  {
    name: 'landing',
    seconds: 12,
    relief: smooth(26, 18, 480, 4),
    shore: {
      path: { x: 80, amplitude: 140, wavelength: 2200 },
      landSide: 1,
      width: 240,
      seabed: -55,
    },
    buildingDensity: 0.4,
    treeDensity: 0.4,
  },
  {
    name: 'plains',
    seconds: 12,
    relief: smooth(22, 14, 520, 4),
    buildingDensity: 0.45,
    treeDensity: 0.6,
  },
];

/** Level Zero: about 3 minutes over every kind of ground, with a sea (P04-R01..R06). */
export const LEVEL_ZERO_CONFIG: SceneryLevel = {
  id: 'level-zero',
  name: 'Level Zero',
  seed: 4242,
  scrollSpeed: LEVEL_ZERO_SCROLL_SPEED,
  transition: 420,
  sections: SECTIONS,
  sea: { level: 0 },
  props: PROP_RULES,
};

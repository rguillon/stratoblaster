import type {
  PropRules,
  RoadRules,
  SceneryLevel,
  TerrainSection,
} from '../../core/scenery/scenery-level';
import {
  CITY_VARIANTS,
  INDUSTRIAL_VARIANTS,
  familyRules,
  type PartFamily,
} from './building-families';

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
  containerYard: 'container-yard',
  refinery: 'refinery',
  glassTower: 'glass-tower',
  officeBlock: 'office-block',
  apartmentBlock: 'apartment-block',
  steppedTower: 'stepped-tower',
  conifer: 'conifer',
  broadleaf: 'broadleaf-tree',
  bush: 'bush',
} as const;

/** Building groups of the wasteland sections, and of the city centre. */
const GROUP_IDS = {
  industrial: 'industrial',
  heavyIndustry: 'heavy-industry',
  science: 'science',
  homes: 'homes',
  city: 'city',
} as const;

/**
 * Props are drawn small next to the ships so the ground reads as far below the playfield
 * (phase 4 review). Footprints are the model radius at the largest scale.
 */
const BUILDING_SCALE = [0.5, 0.65] as const;
const TREE_SCALE = [0.45, 0.75] as const;

/** One rule per variant of a family of buildings made of parts, at the building scale. */
const variants = (family: PartFamily, count: number, weight: number) =>
  familyRules(family, count, weight, BUILDING_SCALE);

const PROP_RULES: PropRules = {
  cellSize: 50,
  treeClearance: 3,
  maxSlope: 0.12,
  treeMaxSlope: 0.45,
  minHeight: 4,
  zoneFrequency: 1 / 700,
  groups: [
    {
      id: GROUP_IDS.industrial,
      weight: 4,
      kinds: [
        { id: PROP_IDS.factory, weight: 3, footprint: 15, scale: BUILDING_SCALE },
        { id: PROP_IDS.tanks, weight: 2, footprint: 10, scale: BUILDING_SCALE },
        { id: PROP_IDS.warehouse, weight: 3, footprint: 15.5, scale: BUILDING_SCALE },
        { id: PROP_IDS.coolingTower, weight: 1, footprint: 9.5, scale: BUILDING_SCALE },
        { id: PROP_IDS.containerYard, weight: 2, footprint: 8.5, scale: BUILDING_SCALE },
        { id: PROP_IDS.refinery, weight: 2, footprint: 7.5, scale: BUILDING_SCALE },
        ...variants('industrial-complex', INDUSTRIAL_VARIANTS, 1.5),
      ],
    },
    {
      // Only in the industrial zone: mostly large plants that fill its blocks (review).
      id: GROUP_IDS.heavyIndustry,
      weight: 1,
      kinds: [
        ...variants('industrial-plant', INDUSTRIAL_VARIANTS, 6),
        ...variants('industrial-works', INDUSTRIAL_VARIANTS, 3),
        ...variants('industrial-complex', INDUSTRIAL_VARIANTS, 1),
        { id: PROP_IDS.containerYard, weight: 0.5, footprint: 8.5, scale: BUILDING_SCALE },
        { id: PROP_IDS.refinery, weight: 0.5, footprint: 7.5, scale: BUILDING_SCALE },
      ],
    },
    {
      id: GROUP_IDS.science,
      weight: 2,
      kinds: [
        { id: PROP_IDS.radar, weight: 2, footprint: 7, scale: BUILDING_SCALE },
        { id: PROP_IDS.antenna, weight: 1, footprint: 6, scale: BUILDING_SCALE },
        { id: PROP_IDS.observatory, weight: 2, footprint: 7, scale: BUILDING_SCALE },
      ],
    },
    {
      id: GROUP_IDS.homes,
      weight: 3,
      kinds: [
        { id: PROP_IDS.cubeHome, weight: 2, footprint: 7.5, scale: BUILDING_SCALE },
        { id: PROP_IDS.domeHome, weight: 2, footprint: 7, scale: BUILDING_SCALE },
        { id: PROP_IDS.stiltPod, weight: 1, footprint: 5, scale: BUILDING_SCALE },
      ],
    },
    {
      // Only in the city centre (phase 4 review).
      id: GROUP_IDS.city,
      weight: 1,
      kinds: [
        // Mostly large blocks that fill the city's blocks (review).
        ...variants('city-block', CITY_VARIANTS, 6),
        ...variants('city-tower', CITY_VARIANTS, 3),
        ...variants('city-building', CITY_VARIANTS, 1),
        { id: PROP_IDS.glassTower, weight: 2, footprint: 7, scale: BUILDING_SCALE },
        { id: PROP_IDS.officeBlock, weight: 2, footprint: 9, scale: BUILDING_SCALE },
        { id: PROP_IDS.apartmentBlock, weight: 2, footprint: 10, scale: BUILDING_SCALE },
        { id: PROP_IDS.steppedTower, weight: 2, footprint: 8.5, scale: BUILDING_SCALE },
      ],
    },
  ],
  trees: [
    { id: PROP_IDS.deadTree, weight: 2, footprint: 1.5, scale: TREE_SCALE },
    { id: PROP_IDS.forkedTree, weight: 1, footprint: 1.5, scale: TREE_SCALE },
    { id: PROP_IDS.conifer, weight: 3, footprint: 2.5, scale: TREE_SCALE },
    { id: PROP_IDS.broadleaf, weight: 3, footprint: 3.5, scale: TREE_SCALE },
    { id: PROP_IDS.bush, weight: 2, footprint: 3.5, scale: TREE_SCALE },
  ],
  treesPerCell: 4,
};

/**
 * P04-R07: two winding roads along the level, and paths branching off them every 260-560 units
 * out to the screen edge. Buildings stand only along them, in slots every 24 units on both sides. Roads
 * start and end beyond X = ±420: the camera sees about ±390 at most (phase 4 review).
 */
const ROAD_RULES: RoadRules = {
  mainRoads: 2,
  spread: 220,
  meander: { amplitude: [80, 180], wavelength: [1300, 2600] },
  crossSpacing: [260, 560],
  crossBend: 40,
  mainWidth: 6,
  crossWidth: 4,
  junction: { width: 14, length: 28 },
  offscreenX: 420,
  turnRate: 0.05,
  minHeight: 3,
  maxSlope: 0.5,
  minRun: 6,
  step: 8,
  slotSpacing: 24,
  setback: 2,
};

const smooth = (base: number, amplitude: number, wavelength: number, octaves: number) =>
  ({ base, amplitude, frequency: 1 / wavelength, octaves, style: 'smooth' }) as const;

/** Dead trees and scattered buildings of the wasteland sections. */
const WASTELAND = {
  trees: [PROP_IDS.deadTree, PROP_IDS.forkedTree],
  groups: [GROUP_IDS.industrial, GROUP_IDS.science, GROUP_IDS.homes],
} as const;

/** The sections, in flight order; their `seconds` add up to 180 (P04-R06). */
const SECTIONS: readonly TerrainSection[] = [
  {
    name: 'plains',
    seconds: 14,
    relief: smooth(22, 14, 520, 4),
    buildingDensity: 0.28,
    treeDensity: 0.6,
    ...WASTELAND,
  },
  {
    name: 'hills',
    seconds: 12,
    relief: smooth(40, 55, 420, 5),
    buildingDensity: 0.105,
    treeDensity: 0.8,
    ...WASTELAND,
  },
  {
    name: 'plateau',
    seconds: 14,
    relief: smooth(70, 60, 380, 5),
    flatten: {
      path: { x: 0, amplitude: 120, wavelength: 2600 },
      halfWidth: 250,
      edge: 120,
      height: 60,
      roughness: 1.5,
    },
    buildingDensity: 0.42,
    treeDensity: 0.3,
    ...WASTELAND,
  },
  {
    name: 'mountains',
    seconds: 18,
    relief: {
      base: 10,
      amplitude: 235,
      frequency: 1 / 600,
      octaves: 6,
      style: 'ridged',
      maxHeight: LEVEL_ZERO_MAX_HEIGHT,
    },
    buildingDensity: 0.035,
    treeDensity: 0.25,
    ...WASTELAND,
  },
  {
    name: 'canyon',
    seconds: 18,
    relief: smooth(130, 35, 360, 5),
    channel: {
      path: { x: 0, amplitude: 150, wavelength: 1900 },
      halfWidth: 45,
      wall: 120,
      floor: -12,
    },
    buildingDensity: 0.105,
    treeDensity: 0.3,
    ...WASTELAND,
  },
  {
    name: 'coast',
    seconds: 14,
    relief: smooth(26, 18, 480, 4),
    shore: {
      path: { x: -60, amplitude: 160, wavelength: 2600 },
      landSide: -1,
      width: 240,
      seabed: -55,
    },
    buildingDensity: 0.28,
    treeDensity: 0.4,
    ...WASTELAND,
  },
  {
    name: 'open sea',
    seconds: 14,
    relief: smooth(-28, 75, 520, 5),
    buildingDensity: 0.175,
    treeDensity: 0.5,
    ...WASTELAND,
  },
  {
    name: 'landing',
    seconds: 10,
    relief: smooth(26, 18, 480, 4),
    shore: {
      path: { x: 80, amplitude: 140, wavelength: 2200 },
      landSide: 1,
      width: 240,
      seabed: -55,
    },
    buildingDensity: 0.28,
    treeDensity: 0.4,
    surface: { lush: 0.5 },
    trees: [PROP_IDS.deadTree, PROP_IDS.bush],
    groups: WASTELAND.groups,
  },
  {
    // Phase 4 review: green ground, grass and living trees, a few homes and labs.
    name: 'meadows',
    seconds: 22,
    relief: smooth(30, 25, 450, 4),
    buildingDensity: 0.21,
    treeDensity: 1,
    surface: { lush: 1 },
    trees: [PROP_IDS.conifer, PROP_IDS.broadleaf, PROP_IDS.bush],
    groups: [GROUP_IDS.homes, GROUP_IDS.science],
  },
  {
    // Phase 4 review: a maze of straight streets packed with industrial buildings.
    name: 'industrial zone',
    seconds: 22,
    relief: smooth(32, 4, 600, 3),
    buildingDensity: 1,
    treeDensity: 0.05,
    surface: { paved: 0.7 },
    streets: { rows: [45, 90], columns: [50, 110], links: 0.6 },
    trees: [PROP_IDS.deadTree],
    groups: [GROUP_IDS.heavyIndustry],
  },
  {
    // Phase 4 review: the city centre, the same maze of straight streets as the industrial zone,
    // packed with buildings made of varied lots (towers, slabs, courtyards, L-shaped blocks).
    name: 'city centre',
    seconds: 22,
    relief: smooth(32, 2, 600, 2),
    buildingDensity: 1,
    treeDensity: 0.1,
    surface: { paved: 1 },
    streets: { rows: [45, 90], columns: [50, 110], links: 0.6 },
    trees: [PROP_IDS.broadleaf],
    groups: [GROUP_IDS.city],
    // Review: every part of every block gets a building, side by side, so no ground shows.
    blocks: { podiums: [], podiumHeight: [0, 0], towers: [16, 16] },
  },
];

/**
 * Level Zero: about 3 minutes over every kind of ground, with a sea (P04-R01..R06), ending with
 * green meadows, an industrial zone and a city centre (phase 4 review).
 */
export const LEVEL_ZERO_CONFIG: SceneryLevel = {
  id: 'level-zero',
  name: 'Level Zero',
  seed: 4242,
  scrollSpeed: LEVEL_ZERO_SCROLL_SPEED,
  transition: 420,
  sections: SECTIONS,
  sea: { level: 0 },
  roads: ROAD_RULES,
  props: PROP_RULES,
};

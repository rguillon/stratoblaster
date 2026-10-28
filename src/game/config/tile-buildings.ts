import type { PropKindRule, TileRules } from '../../core/scenery/scenery-level';
import { model, type TileModel } from './tile-model';

export type { TileArchetype, TileModel } from './tile-model';

/*
 * Phase 15 (reviewer, 2026-10-28): the districts are laid on a grid of 10 m tiles. A one-lane-
 * each-way street with its two sidewalks is one tile; every building stands on whole tiles.
 */

/** P15-R01, R02: tiles of 10 world units, sidewalks of 2 (a 6-unit roadway, two 3-unit lanes). */
export const TILE: TileRules = { size: 10, sidewalk: 2 };

/** P15-R07: gap from a model to the edges of its tiles. */
export const BUILDING_MARGIN = 0.5;

/** A building group made for the grid: its models and the footprints it allows (P15-R09). */
export interface TileGroup {
  /** Smallest and largest footprints, either way round. */
  readonly range: readonly [readonly [number, number], readonly [number, number]];
  readonly models: readonly TileModel[];
}

const HOMES = [
  [1, 1],
  [2, 2],
] as const;
const FLATS = [
  [1, 2],
  [2, 3],
] as const;
const CITY = [
  [2, 2],
  [3, 3],
] as const;
const WORKS = [
  [1, 1],
  [3, 4],
] as const;
const INDUSTRY = [
  [2, 2],
  [3, 4],
] as const;

/** The building groups of the districts and their models (P15-R09, footprint table). */
export const TILE_GROUPS = {
  heavyIndustry: {
    range: [
      [3, 3],
      [4, 6],
    ],
    models: [
      model('foundry', 3, 3),
      model('foundry', 4, 4),
      model('plant', 3, 4),
      model('plant', 4, 6),
      model('foundry', 3, 5, 2),
      model('plant', 4, 4, 2),
    ],
  },
  desertHomes: {
    range: HOMES,
    models: [
      model('adobe', 1, 1),
      model('adobe', 1, 1, 2),
      model('adobe', 1, 2),
      model('courtyard', 2, 2),
      model('adobe', 2, 2, 3),
    ],
  },
  outposts: {
    range: HOMES,
    models: [
      model('waterTower', 1, 1),
      model('solar', 1, 2),
      model('radio', 1, 1),
      model('depot', 2, 2),
      model('depot', 1, 2, 2),
    ],
  },
  villages: {
    range: [
      [1, 1],
      [2, 3],
    ],
    models: [
      model('cottage', 1, 1),
      model('house', 1, 2),
      model('farmhouse', 2, 2),
      model('greenhouse', 1, 2),
      model('barn', 2, 3),
    ],
  },
  workerHomes: {
    range: [
      [1, 1],
      [2, 3],
    ],
    models: [
      model('cottage', 1, 1, 2),
      model('terrace', 1, 3),
      model('flats', 2, 2),
      model('flats', 2, 3),
      model('house', 1, 2, 2),
    ],
  },
  mines: {
    range: WORKS,
    models: [
      model('headframe', 2, 2),
      model('oreSilos', 1, 2),
      model('mineWorks', 3, 3),
      model('mineWorks', 2, 3, 2),
      model('headframe', 3, 3, 2),
    ],
  },
  oil: {
    range: WORKS,
    models: [
      model('pumpjack', 1, 1),
      model('pumpjack', 1, 2, 2),
      model('oilTanks', 2, 2),
      model('oilTanks', 2, 3, 2),
      model('flare', 1, 1),
    ],
  },
  refinery: {
    range: WORKS,
    models: [
      model('tanks', 2, 2),
      model('tanks', 3, 3, 2),
      model('refinery', 2, 3),
      model('refinery', 3, 4, 2),
      model('flare', 1, 1, 2),
      model('tanks', 1, 2, 5),
    ],
  },
  industrial: {
    range: INDUSTRY,
    models: [
      model('factory', 2, 3),
      model('factory', 3, 4),
      model('warehouse', 2, 3),
      model('containers', 2, 2),
      model('coolingTower', 3, 3),
      model('tanks', 2, 2, 3),
    ],
  },
  docks: {
    range: WORKS,
    models: [
      model('containers', 2, 3),
      model('dockCrane', 1, 3),
      model('warehouse', 2, 4, 2),
      model('tanks', 2, 2, 4),
      model('containers', 3, 3, 2),
    ],
  },
  workshops: {
    range: FLATS,
    models: [
      model('workshop', 1, 2),
      model('workshop', 2, 2),
      model('workshop', 2, 3),
      model('warehouse', 2, 2, 3),
      model('workshop', 2, 3, 2),
    ],
  },
  workerFlats: {
    range: FLATS,
    models: [
      model('flats', 1, 2),
      model('flats', 2, 3, 3),
      model('flats', 2, 2, 2),
      model('flats', 2, 3, 2),
      model('flats', 2, 2, 3),
    ],
  },
  terraces: {
    range: [
      [1, 2],
      [1, 4],
    ],
    models: [
      model('terrace', 1, 2),
      model('terrace', 1, 3, 2),
      model('terrace', 1, 4),
      model('terrace', 1, 4, 2),
      model('terrace', 1, 3, 3),
    ],
  },
  suburbs: {
    range: HOMES,
    models: [
      model('house', 1, 1),
      model('house', 1, 2, 3),
      model('villa', 2, 2),
      model('villa', 1, 2, 2),
      model('house', 2, 2, 2),
    ],
  },
  townCentre: {
    range: CITY,
    models: [
      model('midrise', 2, 2, 2),
      model('midrise', 2, 3),
      model('midrise', 3, 3),
      model('flats', 2, 3, 4),
      model('office', 3, 3, 4),
    ],
  },
  midrise: {
    range: CITY,
    models: [
      model('midrise', 2, 2, 3),
      model('midrise', 2, 3, 2),
      model('midrise', 3, 3, 2),
      model('office', 2, 3, 2),
      model('midrise', 2, 2),
    ],
  },
  offices: {
    range: CITY,
    models: [
      model('office', 2, 2, 3),
      model('office', 2, 3, 3),
      model('office', 3, 3, 2),
      model('tower', 2, 2, 2),
      model('office', 3, 3),
    ],
  },
  towers: {
    range: CITY,
    models: [
      model('tower', 2, 2, 3),
      model('tower', 3, 3, 2),
      model('tower', 2, 3),
      model('tower', 2, 2),
      model('skyscraper', 3, 3),
    ],
  },
  skyscrapers: {
    range: CITY,
    models: [
      model('skyscraper', 2, 2),
      model('skyscraper', 3, 3, 2),
      model('skyscraper', 2, 3),
      model('skyscraper', 3, 3),
      model('skyscraper', 2, 2, 2),
    ],
  },
  downtown: {
    range: [
      [3, 3],
      [4, 4],
    ],
    models: [
      model('skyscraper', 3, 3, 3),
      model('skyscraper', 3, 4),
      model('skyscraper', 4, 4),
      model('skyscraper', 3, 3, 4),
      model('skyscraper', 4, 4, 2),
    ],
  },
} as const satisfies Record<string, TileGroup>;

export type TileGroupId = keyof typeof TILE_GROUPS;

/** P15-R09: the lots, for the tiles no building fits, in every world. */
export const LOT_MODELS: readonly TileModel[] = [
  model('carPark', 1, 2),
  model('yard', 1, 1),
  model('plaza', 2, 2),
  model('park', 2, 2),
  model('park', 1, 1, 2),
];

/** Every model made for the grid, once each. */
export const TILE_MODELS: readonly TileModel[] = [
  ...new Map(
    [...Object.values(TILE_GROUPS).flatMap((g) => g.models), ...LOT_MODELS].map((m) => [m.id, m]),
  ).values(),
];

/** The placement rule of a model made for the grid (P15-R07: scale 1, its tiles). */
export function tileKind(m: TileModel, weight: number): PropKindRule {
  const [w, d] = m.tiles;
  return {
    id: m.id,
    weight,
    footprint: (Math.hypot(w, d) * TILE.size) / 2,
    scale: [1, 1],
    tiles: m.tiles,
  };
}

/** The kinds of group `id`, sharing `weight` between them. */
export function tileKinds(id: TileGroupId, weight = 1): PropKindRule[] {
  const models = TILE_GROUPS[id].models;
  return models.map((m) => tileKind(m, weight / models.length));
}

/** P15-R08: the lots of every world. */
export const LOT_KINDS: readonly PropKindRule[] = LOT_MODELS.map((m) => tileKind(m, 1));

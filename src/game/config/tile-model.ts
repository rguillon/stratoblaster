// Phase 15 (P15-R09): what a model made for the grid of tiles is, split out of
// `tile-buildings.ts`.

/** The kinds of models made for the grid; each is built for any W × D tiles. */
export type TileArchetype =
  | 'house'
  | 'villa'
  | 'cottage'
  | 'terrace'
  | 'flats'
  | 'workshop'
  | 'farmhouse'
  | 'greenhouse'
  | 'barn'
  | 'adobe'
  | 'courtyard'
  | 'waterTower'
  | 'solar'
  | 'radio'
  | 'depot'
  | 'headframe'
  | 'oreSilos'
  | 'mineWorks'
  | 'pumpjack'
  | 'oilTanks'
  | 'flare'
  | 'refinery'
  | 'factory'
  | 'warehouse'
  | 'containers'
  | 'coolingTower'
  | 'tanks'
  | 'foundry'
  | 'plant'
  | 'dockCrane'
  | 'midrise'
  | 'office'
  | 'tower'
  | 'skyscraper'
  | 'carPark'
  | 'yard'
  | 'plaza'
  | 'park';

/** A model made for the grid: what it is, its tiles (X × Z, front -Z) and its variant. */
export interface TileModel {
  readonly id: string;
  readonly archetype: TileArchetype;
  readonly tiles: readonly [number, number];
  readonly seed: number;
}

export const model = (archetype: TileArchetype, w: number, d: number, seed = 1): TileModel => ({
  id: `tile-${archetype}-${String(w)}x${String(d)}${seed > 1 ? `-${String(seed)}` : ''}`,
  archetype,
  tiles: [w, d],
  seed,
});

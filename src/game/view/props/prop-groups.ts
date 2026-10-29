import type { PropGroup } from '../../../render/game-view';
import { CAR_IDS } from '../../config/cars';
import { PROP_IDS } from '../../config/prop-ids';
import { WORLD_1_PROP_IDS } from '../../config/world-1/props';
import { PROP_MODELS } from './prop-models';
import { LOT_MODELS, TILE_GROUPS, type TileModel } from '../../config/tile-buildings';
import { ROAD_KIT, ROAD_KIT_NOTES, ROAD_SAMPLE_ID } from './road-kit';

/** P15-R10: the tiles a model of the grid stands on, after its name. */
const tileNotes = (models: readonly TileModel[]): Record<string, string> =>
  Object.fromEntries(
    models.map((m) => [m.id, `${String(m.tiles[0])}×${String(m.tiles[1])} tiles`]),
  );

/** P15-R10: the road kit and its sample, then the models of the grid, by building group. */
const TILE_PAGE: readonly PropGroup[] = [
  {
    label: 'Road kit',
    ids: [...ROAD_KIT.map((p) => p.id), ROAD_SAMPLE_ID],
    notes: { ...ROAD_KIT_NOTES, [ROAD_SAMPLE_ID]: 'every piece joined to straights' },
  },
  ...Object.entries(TILE_GROUPS).map(([id, group]) => ({
    label: `Tiles: ${id}`,
    ids: group.models.map((m) => m.id),
    notes: tileNotes(group.models),
    streets: true,
  })),
  {
    label: 'Tiles: lots',
    ids: LOT_MODELS.map((m) => m.id),
    notes: tileNotes(LOT_MODELS),
    streets: true,
  },
];

/** The props named by each world, then the buildings made of parts, then the cars. */
const NAMED: readonly [string, Readonly<Record<string, string>>][] = [
  ['Shared', PROP_IDS],
  ['World 1', WORLD_1_PROP_IDS],
  ['Cars', CAR_IDS],
];

/** How the `props/` page groups the prop models (reviewer, 2026-10-28; phase 15: the road kit and the tiles). */
export const PROP_GROUPS: readonly PropGroup[] = (() => {
  const models = new Set(Object.keys(PROP_MODELS));
  const named = NAMED.map(([label, ids]) => ({
    label,
    ids: [...new Set(Object.values(ids))].filter((id) => models.has(id)),
  }));
  const taken = new Set([...named, ...TILE_PAGE].flatMap((g) => g.ids));
  const buildings = [...models].filter((id) => !taken.has(id));
  const cars = named.splice(-1);
  return [...named, ...TILE_PAGE, { label: 'Buildings', ids: buildings }, ...cars].filter(
    (g) => g.ids.length > 0,
  );
})();

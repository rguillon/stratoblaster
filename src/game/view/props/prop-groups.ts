import type { PropGroup } from '../../../render/game-view';
import { CAR_IDS } from '../../config/cars';
import { PROP_IDS } from '../../config/level-zero';
import { WORLD_1_PROP_IDS } from '../../config/world-1/props';
import { WORLD_2_PROP_IDS } from '../../config/world-2/props';
import { WORLD_3_PROP_IDS } from '../../config/world-3/props';
import { PROP_MODELS } from './prop-models';

/** The props named by each world, then the buildings made of parts, then the cars. */
const NAMED: readonly [string, Readonly<Record<string, string>>][] = [
  ['Level Zero', PROP_IDS],
  ['World 1', WORLD_1_PROP_IDS],
  ['World 2', WORLD_2_PROP_IDS],
  ['World 3', WORLD_3_PROP_IDS],
  ['Cars', CAR_IDS],
];

/** How the `props/` page groups the prop models (reviewer, 2026-10-28). */
export const PROP_GROUPS: readonly PropGroup[] = (() => {
  const models = new Set(Object.keys(PROP_MODELS));
  const named = NAMED.map(([label, ids]) => ({
    label,
    ids: [...new Set(Object.values(ids))].filter((id) => models.has(id)),
  }));
  const taken = new Set(named.flatMap((g) => g.ids));
  const buildings = [...models].filter((id) => !taken.has(id));
  const cars = named.splice(-1);
  return [...named, { label: 'Buildings', ids: buildings }, ...cars].filter(
    (g) => g.ids.length > 0,
  );
})();
